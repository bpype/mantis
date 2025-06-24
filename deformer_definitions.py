import bpy
from bpy.types import NodeTree, Node, NodeSocket
from .base_definitions import MantisUINode, DeformerNode, get_signature_from_edited_tree
from.deformer_socket_templates import *

from .utilities import (prRed, prGreen, prPurple, prWhite, prOrange,
                        wrapRed, wrapGreen, wrapPurple, wrapWhite,
                        wrapOrange,)


def TellClasses():
    return [
             DeformerArmatureNode,
             DeformerHook,
             DeformerMorphTargetDeform,
             DeformerMorphTarget,
             DeformerSurfaceDeform,
             DeformerMeshDeform,
           ]


def default_traverse(self, socket):
        if (socket == self.outputs["Deformer"]):
            return self.inputs["Deformer"]
        if (socket == self.inputs["Deformer"]):
            return self.outputs["Deformer"]
        return None

class DeformerArmatureNode(Node, DeformerNode):
    '''A node representing an Armature Deformer'''
    bl_idname = 'DeformerArmature'
    bl_label = "Armature Deform"
    bl_icon = 'MOD_ARMATURE'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname

    def init(self, context):
        # self.inputs.new ("RelationshipSocket", "Input Relationship")
        self.inputs.new('xFormSocket', "Armature Object")
        self.inputs.new('StringSocket', "Blend Vertex Group")
        # self.inputs.new('StringSocket', "Preserve Volume Vertex Group") #TODO figure out the right UX for automatic dual-quat blending
        self.inputs.new('BooleanSocket', "Invert Vertex Group")
        
        self.inputs.new('BooleanSocket', "Preserve Volume")
        # TODO: make the above controlled by a vertex group instead.
        self.inputs.new('BooleanSocket', "Use Multi Modifier")# might just set this auto
        self.inputs.new('BooleanSocket', "Use Envelopes")
        self.inputs.new('BooleanSocket', "Use Vertex Groups")
        
        self.inputs.new("DeformerSocket", "Deformer")

        s = self.inputs.new("xFormSocket", "Copy Skin Weights From")
        s.hide = True
        self.inputs.new("EnumSkinning", "Skinning Method")
        
        self.outputs.new('DeformerSocket', "Deformer")
        self.initialized = True
    
    def display_update(self, parsed_tree, context):
        self.inputs["Copy Skin Weights From"].hide = True
        node_tree = context.space_data.path[0].node_tree
        nc = parsed_tree.get(get_signature_from_edited_tree(self, context))
        if nc:
            self.inputs["Copy Skin Weights From"].hide = not (nc.evaluate_input("Skinning Method") == "COPY_FROM_OBJECT")
                

class DeformerHook(Node, DeformerNode):
    '''A node representing a Hook Deformer'''
    bl_idname = 'DeformerHook'
    bl_label = "Hook Deform"
    bl_icon = 'HOOK'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(HookSockets)
        self.initialized = True
    
    def display_update(self, parsed_tree, context):
        curve_sockets = [
            self.inputs["Affect Curve Radius"],
            self.inputs['Auto-Bezier'],
            self.inputs['Spline Index'],
        ]
        is_curve_hook=True
        if self.outputs["Deformer"].is_linked:
            from bpy.types import Object
            if (mantis_node := parsed_tree.get(get_signature_from_edited_tree(self, context))):
                if (xforms := mantis_node.GetxForm()):
                    for xF_node in xforms:
                        if (ob := xF_node.bObject) and isinstance (xF_node, Object):
                            if ob.type != 'CURVE': is_curve_hook=False
        for socket in curve_sockets:
            socket.hide=not is_curve_hook


from .utilities import get_socket_maps, relink_socket_map

# TODO this should probably not be in this file but intstead in Utilities or something
def simple_do_relink(node, map, in_out='INPUT'):
    from bpy.types import NodeSocket
    for key, val in map.items():
        s = node.inputs.get(key) if in_out == "INPUT" else node.outputs.get(key)
        if s is None:
            if in_out == "INPUT":
                if node.num_targets > 0:
                    s = node.inputs["Target."+str(node.num_targets-1).zfill(3)]
                else:
                    continue
        if isinstance(val, list):
            for sub_val in val:
                if isinstance(sub_val, NodeSocket):
                    if in_out =='INPUT':
                        node.id_data.links.new(input=sub_val, output=s)
                    else:
                        node.id_data.links.new(input=s, output=sub_val)
        else:
            try:
                s.default_value = val
            except (AttributeError, ValueError, TypeError): # must be readonly or maybe it doesn't have a d.v.. TypeError if the d.v. is None at this point
                pass


# Dynamic
#   - each Morph Target gets a MT input
#   - each Morph Target gets an influence input
class DeformerMorphTargetDeform(Node, DeformerNode):
    '''A node representing a Morph Target Deformer'''
    bl_idname = 'DeformerMorphTargetDeform'
    bl_label = "Morph Deform"
    bl_icon = 'MOD_ARMATURE'
    initialized : bpy.props.BoolProperty(default = False)
    num_targets : bpy.props.IntProperty(default = 0)
    mantis_node_class_name=bl_idname


    def init(self, context):
        self.id_data.do_live_update = False
        self.inputs.new('DeformerSocket', 'Deformer', )
        self.inputs.new('BooleanSocket', 'Use Shape Key', )
        s = self.inputs.new('BooleanSocket', 'Use Offset', )
        s.default_value = True
        self.inputs.new('WildcardSocket', '', identifier='__extend__')
        self.outputs.new('DeformerSocket', "Deformer")
        self.update_morph_deformer()

    def update_morph_deformer(self, force=False):
        self.initialized = False
        # use_offset = self.inputs["Use Offset"].default_value
        socket_maps = get_socket_maps(self)
        if socket_maps is None:
            return
        input_map = socket_maps[0]
        # checc to see if targets have been removed... then modify the input map if necessary
        targets_deleted = 0 # this should usually be either 0 or 1
        for i in range(self.num_targets):
            name = "Target."+str(i).zfill(3); inf_name = "Value."+str(i).zfill(3)
            if self.inputs[name].is_linked == False:
                del input_map[name]; del input_map[inf_name]
                targets_deleted+=1
            elif targets_deleted: # move it back
                new_name = "Target."+str(i-targets_deleted).zfill(3); new_inf_name = "Value."+str(i-targets_deleted).zfill(3)
                input_map[new_name] = input_map[name]; input_map[new_inf_name] = input_map[inf_name]
                del input_map[name]; del input_map[inf_name]
        self.num_targets-=targets_deleted
        if self.inputs[-1].is_linked and self.inputs[-1].bl_idname == 'WildcardSocket':
            self.num_targets+=1
        self.inputs.clear()
        self.inputs.new('DeformerSocket', 'Deformer', )
        self.inputs.new('BooleanSocket', 'Use Shape Key', )
        self.inputs.new('BooleanSocket', 'Use Offset', )
        for i in range(self.num_targets):
            self.inputs.new("MorphTargetSocket", "Target."+str(i).zfill(3))
            self.inputs.new("FloatSocket", "Value."+str(i).zfill(3))
        simple_do_relink(self, input_map, in_out='INPUT')
        if self.inputs[-1].bl_idname not in ["WildcardSocket"]:
            self.inputs.new('WildcardSocket', '', identifier='__extend__')
        self.initialized = True

    def update(self):
        if self.id_data.is_exporting:
            return # so that we don't update it while saving/loading the tree
        self.update_morph_deformer(force=False)
    
    def display_update(self, parsed_tree, context):
        if self.inputs["Deformer"].is_linked:
            if self.inputs["Deformer"].links[0].from_node.bl_idname not in [self.bl_idname, "NodeGroupInput"]:
                self.inputs["Use Shape Key"].default_value = False
                self.inputs["Use Shape Key"].hide = True
            elif self.inputs["Deformer"].links[0].from_node.inputs["Use Shape Key"].default_value == False:
                self.inputs["Use Shape Key"].default_value = False
                self.inputs["Use Shape Key"].hide = True
        if self.inputs["Use Offset"] == False:
                self.inputs["Use Shape Key"].hide = True
                self.inputs["Use Shape Key"].default_value = False


# TODO: there is no reason for this to be a separate node!
class DeformerMorphTarget(Node, DeformerNode):
    '''A node representing a single Morph Target'''
    bl_idname = 'DeformerMorphTarget'
    bl_label = "Morph Target"
    bl_icon = 'SHAPEKEY_DATA'
    initialized : bpy.props.BoolProperty(default = False)
    num_targets : bpy.props.IntProperty(default = 0)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.inputs.new('xFormSocket', "Relative to")
        self.inputs.new('xFormSocket', "Object")
        self.inputs.new('StringSocket', "Vertex Group")
        self.outputs.new('MorphTargetSocket', "Morph Target")

        self.initialized = True


class DeformerSurfaceDeform(Node, DeformerNode):
    '''A node representing a Surface Deform modifier'''
    bl_idname = 'DeformerSurfaceDeform'
    bl_label = "Surface Deform"
    bl_icon = 'MOD_SOFT'
    initialized : bpy.props.BoolProperty(default = False)
    num_targets : bpy.props.IntProperty(default = 0)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(SurfaceDeformSockets)
        self.initialized = True

class DeformerMeshDeform(Node, DeformerNode):
    '''A node representing a Mesh Deform modifier'''
    bl_idname = 'DeformerMeshDeform'
    bl_label = "Mesh Deform"
    bl_icon = 'MOD_SOFT'
    initialized : bpy.props.BoolProperty(default = False)
    num_targets : bpy.props.IntProperty(default = 0)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(MeshDeformSockets)
        self.initialized = True


# Set up the class property that ties the UI classes to the Mantis classes.
for cls in TellClasses():
    cls.set_mantis_class()
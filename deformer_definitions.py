import bpy
from bpy.types import NodeTree, Node, NodeSocket
from .base_definitions import MantisNode, DeformerNode, get_signature_from_edited_tree

from .utilities import (prRed, prGreen, prPurple, prWhite, prOrange,
                        wrapRed, wrapGreen, wrapPurple, wrapWhite,
                        wrapOrange,)


def TellClasses():
    return [
             DeformerArmatureNode,
             DeformerMorphTargetDeform,
             DeformerMorphTarget,
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
# this node creates a GN deformer that ADDS the position deltas (from the base position)
# Value has to scale the delta
class DeformerMorphTargetDeform(Node, DeformerNode):
    '''A node representing a Morph Target Deformer'''
    bl_idname = 'DeformerMorphTargetDeform'
    bl_label = "Morph Deform"
    bl_icon = 'MOD_ARMATURE'
    initialized : bpy.props.BoolProperty(default = False)
    num_targets : bpy.props.IntProperty(default = 0)


    def init(self, context):
        self.id_data.do_live_update = False
        self.inputs.new('DeformerSocket', 'Previous Deformer', )
        self.inputs.new('WildcardSocket', '', identifier='__extend__')
        self.outputs.new('DeformerSocket', "Deformer")
        self.update()

    def update(self):
        if self.id_data.is_executing:
            return # so that we don't update it while saving/loading the tree
        self.initialized = False
        input_map = get_socket_maps(self)[0]
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
        self.inputs.new('DeformerSocket', 'Previous Deformer', )
        # have to do this manually to avoid making things harder elsewhere
        # input_map
        for i in range(self.num_targets):
            self.inputs.new("MorphTargetSocket", "Target."+str(i).zfill(3))
            self.inputs.new("FloatSocket", "Value."+str(i).zfill(3))
        # if self.num_targets > 0:
        simple_do_relink(self, input_map, in_out='INPUT')
        if len(self.inputs)<1 or self.inputs[-1].bl_idname not in ["WildcardSocket"]:
            self.inputs.new('WildcardSocket', '', identifier='__extend__')
        self.initialized = True

# TODO: there is no reason for this to be a separate node!
class DeformerMorphTarget(Node, DeformerNode):
    '''A node representing a single Morph Target'''
    bl_idname = 'DeformerMorphTarget'
    bl_label = "Morph Target"
    bl_icon = 'SHAPEKEY_DATA'
    initialized : bpy.props.BoolProperty(default = False)
    num_targets : bpy.props.IntProperty(default = 0)

    def init(self, context):
        self.inputs.new('xFormSocket', "Relative to")
        self.inputs.new('xFormSocket', "Object")
        self.inputs.new('StringSocket', "Vertex Group")
        self.outputs.new('MorphTargetSocket', "Morph Target")

        self.initialized = True
    
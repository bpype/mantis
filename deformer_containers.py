from .node_container_common import *
from .xForm_containers import xFormGeometryObject
from bpy.types import Node
from .base_definitions import MantisNode

def TellClasses():
             
    return [ 
             DeformerArmature,
           ]



def default_evaluate_input(nc, input_name):
    # duped from link_containers... should be common?
    # should catch 'Target', 'Pole Target' and ArmatureConstraint targets, too
    if ('Target' in input_name) and input_name != "Target Space":
        socket = nc.inputs.get(input_name)
        if socket.is_linked:
            return socket.links[0].from_node
        return None
        
    else:
        return evaluate_input(nc, input_name)


# semi-duplicated from link_containers
def GetxForm(nc):
    trace = trace_single_line_up(nc, "Deformer")
    for node in trace[0]:
        if (node.__class__ in [xFormGeometryObject]):
            return node
    raise GraphError("%s is not connected to a downstream xForm" % nc)

class DeformerArmature:
    '''A node representing an armature deformer'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
          "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
          "Target"             : NodeSocket(is_input = True, name = "Target", node = self,),
          "Vertex Group"       : NodeSocket(is_input = True, name = "Vertex Group", node = self),
          "Preserve Volume"    : NodeSocket(is_input = True, name = "Preserve Volume", node = self),
          "Use Multi Modifier" : NodeSocket(is_input = True, name = "Use Multi Modifier", node = self),
          "Use Envelopes"      : NodeSocket(is_input = True, name = "Use Envelopes", node = self),
          "Use Vertex Groups"  : NodeSocket(is_input = True, name = "Use Vertex Groups", node = self),
          "Skinning Method"    : NodeSocket(is_input = True, name = "Skinning Method", node = self),
        }
        self.outputs = {
          "Deformer" : NodeSocket(is_input = False, name = "Deformer", node=self), }
        self.parameters = {
          "Name"               : None,
          "Target"             : None,
          "Vertex Group"       : None,
          "Preserve Volume"    : None,
          "Use Multi Modifier" : None,
          "Use Envelopes"      : None,
          "Use Vertex Groups"  : None,
          "Skinning Method"    : None,
        }
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Deformer"])
        self.outputs["Deformer"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = "LINK"

    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)

    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, bContext = None,):
        prGreen("Executing Armature Deform Node\n")
        print(self.GetxForm())
        prOrange("My object: %s\n" % (self.GetxForm().bGetObject()))
        prepare_parameters(self)
        d = self.GetxForm().bGetObject().modifiers.new(self.evaluate_input("Name"), type='ARMATURE')
        self.bObject = d
        get_target_and_subtarget(self, d)
        props_sockets = {
        'vertex_group'       : ("Vertex Group", ""),
        'use_deform_preserve_volume' : ("Preserve Volume", False),
        'use_multi_modifier' : ("Use Multi Modifier", False),
        'use_bone_envelopes' : ("Use Envelopes", False),
        'use_vertex_groups' : ("Use Vertex Groups", False),
        }
        evaluate_sockets(self, d, props_sockets)   
    
    def initialize_vgroups(self, use_existing = False):
        ob = self.GetxForm().bGetObject()
        if use_existing == False:
            ob.vertex_groups.clear()
        armOb = self.evaluate_input("Target").bGetObject()
        deform_bones = []
        for b in armOb.data.bones:
            if b.use_deform == True:
                deform_bones.append(b)
        for b in deform_bones:
            vg = ob.vertex_groups.get(b.name)
            if not vg:
                vg = ob.vertex_groups.new(name=b.name)
                num_verts = len(ob.data.vertices)
                vg.add(range(num_verts), 0, 'REPLACE')
            
    
    def bFinalize(self, bContext=None):
        if (skin_method := self.evaluate_input("Skinning Method")) == "AUTOMATIC_HEAT":
            # This is reatarded and leads to somewhat unpredictable
            #  behaviour, e.g. what object will be selected? What mode?
            # also bpy.ops is ugly and prone to error when used in
            #  scripts. I don't intend to use bpy.ops when I can avoid it.
            import bpy
            self.initialize_vgroups()
            bContext.view_layer.depsgraph.update()
            ob = self.GetxForm().bGetObject()
            armOb = self.evaluate_input("Target").bGetObject()
            deform_bones = []
            for pb in armOb.pose.bones:
                if pb.bone.use_deform == True:
                    deform_bones.append(pb)
            
            context_override = {
                                  'active_object':ob,
                                  'selected_objects':[ob, armOb],
                                  'active_pose_bone':deform_bones[0],
                                  'selected_pose_bones':deform_bones,}
            #
            with bContext.temp_override(**{'active_object':armOb}):
                bpy.ops.object.mode_set(mode='POSE')
                bpy.ops.pose.select_all(action='SELECT')
            with bContext.temp_override(**context_override):
                bpy.ops.paint.weight_paint_toggle()
                bpy.ops.paint.weight_from_bones(type='AUTOMATIC')
                bpy.ops.paint.weight_paint_toggle()
                #
            with bContext.temp_override(**{'active_object':armOb}):
                bpy.ops.object.mode_set(mode='POSE')
                bpy.ops.pose.select_all(action='DESELECT') 
                bpy.ops.object.mode_set(mode='OBJECT')
            # TODO: modify Blender to make this available as a Python API function.
        if skin_method == "EXISTING_GROUPS":
            self.initialize_vgroups(use_existing = True)

        
    def __repr__(self):
        return self.signature.__repr__()

    def fill_parameters(self):
        fill_parameters(self)

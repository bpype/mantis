import bpy
from .base_definitions import xFormNode
from bpy.types import Node
from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)
from .base_definitions import get_signature_from_edited_tree
from .xForm_socket_templates import *

def TellClasses():
    return [
        # xFormNullNode,
        xFormBoneNode,
        xFormArmatureNode,
        xFormGeometryObjectNode,
        xFormObjectInstance,
        xFormCurvePin,
        ]

def default_traverse(self, socket):
    if (socket == self.outputs["xForm Out"]):
        return self.inputs["Relationship"]
    if (socket == self.inputs["Relationship"]):
        return self.outputs["xForm Out"]
    return None

# Representing an Empty or non-armature-Object
# class xFormNullNode(Node, xFormNode):
#     '''A node representing a Null node'''
#     bl_idname = 'xFormNullNode'
#     bl_label = "Null"
#     bl_icon = 'EMPTY_AXIS'

#     # === Optional Functions ===
#     def init(self, context):
#         self.inputs.new('StringSocket', "Name")
#         self.inputs.new('RelationshipSocket', "Relationship")
#         self.inputs.new('RotationOrderSocket', "Rotation Order")
#         self.inputs.new('MatrixSocket', "Matrix")
#         self.outputs.new('xFormSocket', "xForm Out")


def check_if_connected(start, end, line):
    started=False
    for path_mantis_node in line:
        prWhite("    ", path_mantis_node.signature)
        if path_mantis_node.signature == start.signature:
            started = True
        elif path_mantis_node.signature == end.signature:
            break
        if started:
            if path_mantis_node.inputs.get("Connected"):
                if path_mantis_node.evaluate_input("Connected") == False:
                    return False
    else:
        return False
    return True


def main_draw_label(self): # this will prefer a user-set label, or return the evaluated name
    if self.label:
        return self.label
    if self.inputs['Name'].display_text:
        return self.inputs['Name'].display_text
    return self.name


# I had chat gpt flip these so they may be a little innacurate
# always visible
main_names = {
"Name":'StringSocket',
"Rotation Order":'RotationOrderSocket',
"Relationship":'RelationshipSocket',
"Matrix":'MatrixSocket',}

# IK SETTINGS
ik_names = {
"IK Stretch":'FloatFactorSocket',
"Lock IK":'BooleanThreeTupleSocket',
"IK Stiffness":'NodeSocketVector',
"Limit IK":'BooleanThreeTupleSocket',
"X Min":'NodeSocketFloatAngle',
"X Max":'NodeSocketFloatAngle',
"Y Min":'NodeSocketFloatAngle',
"Y Max":'NodeSocketFloatAngle',
"Z Min":'NodeSocketFloatAngle',
"Z Max":'NodeSocketFloatAngle',
}

#display settings
display_names = {
"Bone Collection":'BoneCollectionSocket',
"Custom Object":'xFormSocket',
"Custom Object xForm Override":'xFormSocket',
"Custom Object Scale to Bone Length":'BooleanSocket',
"Custom Object Wireframe":'BooleanSocket',
"Custom Object Scale":'VectorScaleSocket',
"Custom Object Translation":'VectorSocket',
"Custom Object Rotation":'VectorEulerSocket',
"Color":'ColorSetSocket',
"Inherit Color":'BooleanSocket',
}

# deform_names
deform_names = {
"Deform":'BooleanSocket',
"Envelope Distance":'FloatPositiveSocket',
"Envelope Weight":'FloatFactorSocket',
"Envelope Multiply":'BooleanSocket',
"Envelope Head Radius":'FloatPositiveSocket',
"Envelope Tail Radius":'FloatPositiveSocket',
}

bbone_names = {
    "BBone Segments":"IntSocket", # BONE
    "BBone X Size":"FloatSocket", # BONE
    "BBone Z Size":"FloatSocket", # BONE
    # "bbone_mapping_mode":"StringSocket", <== BONE
    "BBone HQ Deformation":"BooleanSocket", # BONE bbone_mapping_mode
    "BBone X Curve-In":"FloatSocket", # BONE AND POSE
    "BBone Z Curve-In":"FloatSocket", # BONE AND POSE
    "BBone X Curve-Out":"FloatSocket", # BONE AND POSE
    "BBone Z Curve-Out":"FloatSocket", # BONE AND POSE
    "BBone Roll-In":"FloatSocket", # BONE AND POSE
    "BBone Roll-Out":"FloatSocket", # BONE AND POSE
    "BBone Inherit End Roll":"BooleanSocket", # BONE
    "BBone Scale-In":"VectorSocket", # BONE AND POSE
    "BBone Scale-Out":"VectorSocket", # BONE AND POSE
    "BBone Ease-In":"FloatSocket", # BONE AND POSE
    "BBone Ease-Out":"FloatSocket", # BONE AND POSE
    "BBone Easing":"BooleanSocket", # BONE
    "BBone Start Handle Type":"EnumBBoneHandleType", # BONE
    "BBone Custom Start Handle":"StringSocket", # BONE
    "BBone Start Handle Scale":"BooleanThreeTupleSocket", # BONE
    "BBone Start Handle Ease":"BooleanSocket", # BONE
    "BBone End Handle Type":"EnumBBoneHandleType", # BONE
    "BBone Custom End Handle":"StringSocket", # BONE
    "BBone End Handle Scale":"BooleanThreeTupleSocket", # BONE
    "BBone End Handle Ease":"BooleanSocket", # BONE

}

other_names = {
    "Lock Location":'BooleanThreeTupleSocket',
    "Lock Rotation":'BooleanThreeTupleSocket',
    "Lock Scale":'BooleanThreeTupleSocket',
    "Hide":'HideSocket',
}

from mathutils import Color
xFormColor = Color((0.093172, 0.047735, 0.028036)).from_scene_linear_to_srgb()



class xFormBoneNode(Node, xFormNode):
    '''A node representing a Bone'''
    bl_idname = 'xFormBoneNode'
    bl_label = "Bone"
    bl_icon = 'BONE_DATA'
    
    display_ik_settings : bpy.props.BoolProperty(default=False)
    display_vp_settings : bpy.props.BoolProperty(default=False)
    display_def_settings : bpy.props.BoolProperty(default=False)
    display_bb_settings : bpy.props.BoolProperty(default=False)
    socket_count : bpy.props.IntProperty()
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname[:-4]
    
    def init(self, context):

        for name, sock_type in main_names.items():
            self.inputs.new(sock_type, name)

        for name, sock_type in ik_names.items():
            s = self.inputs.new(sock_type, name)
            s.hide = True

        for name, sock_type in display_names.items():
            if name == 'Bone Collection': # HACK because I am not using Socket Templates yet
                s = self.inputs.new(sock_type, name, use_multi_input=True)
            else:
                s = self.inputs.new(sock_type, name)
            if s.name in ['Custom Object', 'Bone Collection']:
                continue
            s.hide = True
        
        for name, sock_type in deform_names.items():
            s = self.inputs.new(sock_type, name)
            if s.name == 'Deform':
                continue
            s.hide = True
        
        for name, sock_type in bbone_names.items():
            s = self.inputs.new(sock_type, name)
            if s.name == "BBone Segments":
                continue
            s.hide = True

        for name, sock_type in other_names.items():
            self.inputs.new(sock_type, name)
        # could probably simplify this further with iter_tools.chain() but meh

        self.socket_count = len(self.inputs)
        #
        self.outputs.new('xFormSocket', "xForm Out")


        # set up some defaults...
        self.inputs['Rotation Order'].default_value = "XYZ"
        self.inputs['Lock Location'].default_value[0] = True
        self.inputs['Lock Location'].default_value[1] = True
        self.inputs['Lock Location'].default_value[2] = True
        self.inputs['Lock Rotation'].default_value[0] = True
        self.inputs['Lock Rotation'].default_value[1] = True
        self.inputs['Lock Rotation'].default_value[2] = True
        self.inputs['Lock Scale'].default_value[0] = True
        self.inputs['Lock Scale'].default_value[1] = True
        self.inputs['Lock Scale'].default_value[2] = True
        self.inputs['Inherit Color'].default_value = True
        
        # color
        self.use_custom_color = True
        self.color = xFormColor
        #
        self.initialized=True
    
    def draw_buttons(self, context, layout):
        # return
        layout.operator("mantis.add_custom_property", text='+Add Custom Parameter')
        # layout.label(text="Edit Parameter ... not implemented")
        if (len(self.inputs) > self.socket_count):
            layout.operator("mantis.edit_custom_property", text=' Edit Custom Parameter')
            layout.operator("mantis.remove_custom_property", text='-Remove Custom Parameter')
        else:
            layout.label(text="")
    
    def draw_label(self): # this will prefer a user-set label, or return the evaluated name
        return main_draw_label(self)

        
    def display_update(self, parsed_tree, context):
        if context.space_data:
            mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
            self.display_ik_settings = False
            if mantis_node and (pb := mantis_node.bGetObject(mode='POSE')):
                self.display_ik_settings = pb.is_in_ik_chain
            
            self.inputs['Name'].display_text = ""
            if mantis_node:
                try:
                    self.inputs['Name'].display_text = mantis_node.evaluate_input("Name")
                    self.display_vp_settings = mantis_node.inputs["Custom Object"].is_connected
                    self.display_def_settings = mantis_node.evaluate_input("Deform")
                    self.display_bb_settings = mantis_node.evaluate_input("BBone Segments") > 1
                except KeyError:
                    return # the tree isn't ready yet.
            
            for name in ik_names.keys():
                self.inputs[name].hide = not self.display_ik_settings
            
            for name in display_names.keys():
                if name in ['Custom Object', 'Bone Collection']: continue
                self.inputs[name].hide = not self.display_vp_settings
            
            for name in deform_names.keys():
                if name in ['Deform']: continue
                self.inputs[name].hide = not self.display_def_settings

            for name in bbone_names.keys():
                if name in ['BBone Segments']: continue
                self.inputs[name].hide = not self.display_bb_settings

class xFormArmatureNode(Node, xFormNode):
    '''A node representing an Armature object node'''
    bl_idname = 'xFormArmatureNode'
    bl_label = "Armature"
    bl_icon = 'OUTLINER_OB_ARMATURE'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname[:-4]

    def init(self, context):
        self.init_sockets(xFormArmatureSockets)
        self.use_custom_color = True
        self.color = xFormColor
        self.initialized=True

    def draw_label(self): # this will prefer a user-set label, or return the evaluated name
        return main_draw_label(self)
    
    def display_update(self, parsed_tree, context):
        if context.space_data:
            mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
            self.inputs['Name'].display_text = ""
            if mantis_node:
                self.inputs['Name'].display_text = mantis_node.evaluate_input("Name")

class xFormGeometryObjectNode(Node, xFormNode):
    """Represents a curve or mesh object."""
    bl_idname = "xFormGeometryObject"
    bl_label = "Geometry Object"
    bl_icon = "EMPTY_AXIS"
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(xFormGeometryObjectSockets)
        self.use_custom_color = True
        self.color = xFormColor
        self.initialized=True

    def draw_label(self): # this will prefer a user-set label, or return the evaluated name
        return main_draw_label(self)
    
    def display_update(self, parsed_tree, context):
        if context.space_data:
            mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
            self.inputs['Name'].display_text = ""
            if mantis_node:
                self.inputs['Name'].display_text = mantis_node.evaluate_input("Name")

class xFormObjectInstance(Node, xFormNode):
    """Represents an instance of an existing geometry object."""
    bl_idname = "xFormObjectInstance"
    bl_label = "Object Instance"
    bl_icon = "EMPTY_AXIS"
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(xFormGeometryObjectInstanceSockets)
        self.use_custom_color = True
        self.color = xFormColor
        self.initialized=True

    def draw_label(self): # this will prefer a user-set label, or return the evaluated name
        return main_draw_label(self)
    
    def display_update(self, parsed_tree, context):
        if context.space_data:
            mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
            self.inputs['Name'].display_text = ""
            if mantis_node:
                self.inputs['Name'].display_text = mantis_node.evaluate_input("Name")

from .xForm_nodes import xFormCurvePinSockets
class xFormCurvePin(Node, xFormNode):
    """"A node representing a curve pin"""
    bl_idname = "xFormCurvePin"
    bl_label = "Curve Pin"
    bl_icon = "FORCE_CURVE"
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(xFormCurvePinSockets)
        self.use_custom_color = True
        self.color = xFormColor
        self.initialized = True

for cls in TellClasses():
    cls.set_mantis_class()
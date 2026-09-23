import bpy
from .base_definitions import MantisMathUINode
from bpy.types import Node
from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)
from .base_definitions import get_signature_from_edited_tree

from .math_nodes_socket_templates import *

def TellClasses():
    return [
     MathStaticInt,
     MathStaticFloatNode,
     MathStaticVectorNode,
    ]

class MathStaticInt(Node, MantisMathUINode):
    """A node that performs mathematical operations on float numbers as a preprocess step before generating the rig."""
    bl_idname = "MathStaticInt"
    bl_label = "Static Int Math"
    bl_icon = "NODE"
    mantis_node_class_name=bl_idname
    socket_templates = StaticIntSockets

    def display_update(self, parsed_tree, context):
        if context.space_data:
            node_tree = context.space_data.path[0].node_tree
            mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
            op = mantis_node.evaluate_input("Operation")
            if op in ['ABSOLUTE']:
                self.inputs["Int B"].hide = True
            else:
                self.inputs["Int B"].hide = False

class MathStaticFloatNode(Node, MantisMathUINode):
    """A node that performs mathematical operations on float numbers as a preprocess step before generating the rig."""
    bl_idname = "MathStaticFloat"
    bl_label = "Static Float Math"
    bl_icon = "NODE"
    mantis_node_class_name=bl_idname
    socket_templates = StaticFloatSockets

    def display_update(self, parsed_tree, context):
        if context.space_data:
            node_tree = context.space_data.path[0].node_tree
            mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
            op = mantis_node.evaluate_input("Operation")
            if op in ['ABSOLUTE', 'FLOOR', 'CEIL', 'ROUND']:
                self.inputs["Float B"].hide = True
            else:
                self.inputs["Float B"].hide = False

class MathStaticVectorNode(Node, MantisMathUINode):
    """Performs a vector math operation as a preprocess before executing the tree."""
    bl_idname = "MathStaticVector"
    bl_label = "Static Vector Math"
    bl_icon = "NODE"
    mantis_node_class_name=bl_idname
    socket_templates = StaticVectorSockets

    def display_update(self, parsed_tree, context):
        if context.space_data:
            node_tree = context.space_data.path[0].node_tree
            mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
            op = mantis_node.evaluate_input("Operation")
            # Scalar output
            if op in ['LENGTH', 'DOT']:
                self.outputs["Result Vector"].hide = True
                self.outputs["Result Float"].hide = False
            else: # Vector output
                self.outputs["Result Vector"].hide = False
                self.outputs["Result Float"].hide = True
            
            # Single Vector and Scalar input
            if op in ['SCALE', ]:
                self.inputs["Vector B"].hide = True
                self.inputs["Scalar A"].hide = False
            elif op in ['LENGTH', 'NORMALIZE']: # only a vector input
                self.inputs["Vector B"].hide = True
                self.inputs["Scalar A"].hide = True
            elif op in ['LINEAR_INTERP']: # both inputs
                self.inputs["Vector B"].hide = False
                self.inputs["Scalar A"].hide = False
            else:
                self.inputs["Vector B"].hide = False
                self.inputs["Scalar A"].hide = True

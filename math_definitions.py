import bpy
from .base_definitions import MantisNode
from bpy.types import Node
from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)
from .base_definitions import get_signature_from_edited_tree


def TellClasses():
    return [
     MathStaticInt,
     MathStaticFloatNode,
     MathStaticVectorNode,
        ]


        

class MathStaticInt(Node, MantisNode):
    """A node that performs mathematical operations on float numbers as a preprocess step before generating the rig."""
    bl_idname = "MathStaticInt"
    bl_label = "Static Int Math"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)


    def init(self, context):
        self.inputs.new("MathFloatOperation", "Operation")
        self.inputs.new("IntSocket", "Int A")
        self.inputs.new("IntSocket", "Int B")
        self.outputs.new("IntSocket", "Result Int")
        self.initialized = True
    

    def display_update(self, parsed_tree, context):
        if context.space_data:
            node_tree = context.space_data.path[0].node_tree
            nc = parsed_tree.get(get_signature_from_edited_tree(self, context))
            op = nc.evaluate_input("Operation")
            if op in ['ABSOLUTE']:
                self.inputs["Int B"].hide = True
            else:
                self.inputs["Int B"].hide = False

    def traverse(self, socket):
        return default_traverse(self,socket)
                   


# do... make the operations now
class MathStaticFloatNode(Node, MantisNode):
    """A node that performs mathematical operations on float numbers as a preprocess step before generating the rig."""
    bl_idname = "MathStaticFloat"
    bl_label = "Static Float Math"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)


    def init(self, context):
        self.inputs.new("MathFloatOperation", "Operation")
        self.inputs.new("FloatSocket", "Float A")
        self.inputs.new("FloatSocket", "Float B")
        self.outputs.new("FloatSocket", "Result Float")
        self.initialized = True
    

    def display_update(self, parsed_tree, context):
        if context.space_data:
            node_tree = context.space_data.path[0].node_tree
            nc = parsed_tree.get(get_signature_from_edited_tree(self, context))
            op = nc.evaluate_input("Operation")
            if op in ['ABSOLUTE']:
                self.inputs["Float B"].hide = True
            else:
                self.inputs["Float B"].hide = False

    def traverse(self, socket):
        return default_traverse(self,socket)


class MathStaticVectorNode(Node, MantisNode):
    """Performs a vector math operation as a preprocess before executing the tree."""
    bl_idname = "MathStaticVector"
    bl_label = "Static Vector Math"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("MathVectorOperation", "Operation")
        self.inputs.new("VectorSocket", "Vector A")
        self.inputs.new("VectorSocket", "Vector B")
        h = self.inputs.new("FloatSocket", "Scalar A"); h.hide=True
        self.outputs.new("VectorSocket", "Result Vector")
        h = self.outputs.new("FloatSocket", "Result Float"); h.hide=True
        self.initialized = True

    def display_update(self, parsed_tree, context):
        if context.space_data:
            node_tree = context.space_data.path[0].node_tree
            nc = parsed_tree.get(get_signature_from_edited_tree(self, context))
            op = nc.evaluate_input("Operation")
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

    
    def traverse(self, socket):
        return default_traverse(self,socket)

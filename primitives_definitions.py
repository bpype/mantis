import bpy
from bpy.types import NodeTree, Node, NodeSocket
from .base_definitions import MantisNode

def TellClasses():
    return [
             GeometryCirclePrimitive,
           ]

def default_traverse(self,socket):
    return None


class GeometryCirclePrimitive(Node, MantisNode):
    '''A node representing a circle primitive'''
    bl_idname = 'GeometryCirclePrimitive'
    bl_label = "Circle Primitive"
    bl_icon = 'NODE'

    def init(self, context):
        self.inputs.new('StringSocket', "Name")
        self.inputs.new('FloatPositiveSocket', "Radius")
        self.inputs.new('IntSocket', "Number of Points")
        self.outputs.new('GeometrySocket', "Circle")

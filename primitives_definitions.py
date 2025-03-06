import bpy
from bpy.types import NodeTree, Node, NodeSocket
from .base_definitions import MantisUINode

def TellClasses():
    return [
             GeometryCirclePrimitive,
           ]

def default_traverse(self,socket):
    return None


class GeometryCirclePrimitive(Node, MantisUINode):
    '''A node representing a circle primitive'''
    bl_idname = 'GeometryCirclePrimitive'
    bl_label = "Circle Primitive"
    bl_icon = 'NODE'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name="CirclePrimitive"

    def init(self, context):
        self.inputs.new('StringSocket', "Name")
        self.inputs.new('FloatPositiveSocket', "Radius")
        self.inputs.new('IntSocket', "Number of Points")
        self.outputs.new('GeometrySocket', "Circle")
        self.initialized = True

for cls in TellClasses():
    cls.mantis_node_library='.primitives_containers'
    cls.set_mantis_class()
import bpy
from bpy.types import Node
from .base_definitions import GeometryPrimitiveNode
from .primitives_sockets import *

def TellClasses():
    return [
             GeometryCirclePrimitive,
             GeometryLattice,
           ]

def default_traverse(self,socket):
    return None

class GeometryCirclePrimitive(Node, GeometryPrimitiveNode):
    '''A node representing a circle primitive'''
    bl_idname = 'GeometryCirclePrimitive'
    bl_label = "Circle Primitive"
    bl_icon = 'NODE'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name="CirclePrimitive"
    socket_templates = CirclePrimitiveSockets

from .primitives_sockets import LatticeSockets
class GeometryLattice(Node, GeometryPrimitiveNode):
    '''A node representing a lattice geometry'''
    bl_idname = "GeometryLattice"
    bl_label = "Lattice"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname
    socket_templates = LatticeSockets
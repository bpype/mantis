from .node_container_common import *
from .base_definitions import MantisNode, NodeSocket

def TellClasses():
    return [
             # Primitives
             CirclePrimitive,
            ]

#*#-------------------------------#++#-------------------------------#*#
# P R I M I T I V E S
#*#-------------------------------#++#-------------------------------#*#



class CirclePrimitive(MantisNode):
    '''A node representing a Circle Primitive mesh'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Name",
          "Radius",
          "Number of Points",
        ]
        outputs = [
          "Circle",
        ]
        additional_parameters = {}
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters(additional_parameters=additional_parameters)
        self.node_type = "UTILITY"
        self.prepared = True



    def bGetObject(self):
        from bpy import data
        # first try Curve, then try Mesh
        bObject = data.curves.get(self.evaluate_input("Name"))
        if not bObject:
            bObject = data.meshes.get(self.evaluate_input("Name"))
        return bObject
        
    def bExecute(self, bContext = None,):
        # Get the datablock
        data = self.bGetObject()
        import bpy
        if not data:
            data = bpy.data.meshes.new( self.evaluate_input("Name") )
        # make the circle
        import bmesh; bm = bmesh.new()
        bmesh.ops.create_circle( # lazy but easy
            bm,
            cap_ends=False,
            radius=max(self.evaluate_input("Radius"), 0.0001),
            segments=min( max( self.evaluate_input("Number of Points"), 3), 1024),
            )
        # this is rotated 90 degrees, we need Y-up instead of Z-up
        from mathutils import Matrix
        from math import pi
        for v in bm.verts:
            v.co = Matrix.Rotation(pi/2, 4, 'X') @ v.co
        # done with this, push it to the data and free the bmesh.
        bm.to_mesh(data); bm.free()
        self.executed = True

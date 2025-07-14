# gonna start putting the UI operators in here so
# that the nodegroup operators file is more focused

import bpy
from bpy.types import Operator
from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

def TellClasses():
    return [
        ColorPalleteAddSocket,
        ColorPalleteRemoveSocket,
    ]

class ColorPalleteAddSocket(Operator):
    """Add a Color Set socket to the node"""
    bl_idname = "mantis.color_pallete_socket_add"
    bl_label = "Add Color Set"
    bl_options = {'REGISTER', 'UNDO'}

    tree_invoked : bpy.props.StringProperty(options ={'HIDDEN'})
    node_invoked : bpy.props.StringProperty(options ={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        n = bpy.data.node_groups[self.tree_invoked].nodes[self.node_invoked]
        # the name doesn't matter, will probably be Color Set.001 or something instead
        n.outputs.new("ColorSetSocket", "Color Set")
        return {'FINISHED'}

class ColorPalleteRemoveSocket(Operator):
    """Remove a Color Set socket from the node"""
    bl_idname = "mantis.color_pallete_socket_remove"
    bl_label = "X"
    bl_options = {'REGISTER', 'UNDO'}

    tree_invoked : bpy.props.StringProperty(options   = {'HIDDEN'})
    node_invoked : bpy.props.StringProperty(options   = {'HIDDEN'})
    socket_invoked : bpy.props.StringProperty(options = {'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        n = bpy.data.node_groups[self.tree_invoked].nodes[self.node_invoked]
        # the name doesn't matter, will probably be Color Set.001 or something instead
        for s in n.outputs:
            if s.identifier == self.socket_invoked:
                break
        n.outputs.remove(s)
        return {'FINISHED'}
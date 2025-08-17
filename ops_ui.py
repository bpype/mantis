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
        MantisAddComponent,
        ColorPalleteAddSocket,
        ColorPalleteRemoveSocket,
    ]

def poll_in_mantis_tree(context):
    if not context.space_data:
        return False
    if not hasattr(context.space_data, "path"):
        return False
    try:
        node_tree = context.space_data.path[0].node_tree
    except IndexError: # not in the UI, for example, in a script instead.
        return False
    if node_tree is None: # because the space is right but there is no selected tree.
        return False
    return True

class MantisAddComponent(Operator):
    """Add a component group into the scene"""
    bl_idname = "mantis.add_component"
    bl_label = "Add Component Group"
    bl_options = {'REGISTER', 'UNDO'}

    node_group_tree_name : bpy.props.StringProperty()
    tree_invoked : bpy.props.StringProperty(options ={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return poll_in_mantis_tree(context)

    def invoke(self, context, event):
        return self.execute(context)
    
    def execute (self, context):
        from bpy import data
        tree = bpy.data.node_groups[self.tree_invoked]
        for node in tree.nodes:
            node.select = False
        tree = bpy.data.node_groups[self.tree_invoked]
        node_group = data.node_groups.get(self.node_group_tree_name)
        node_group_type = "MantisNodeGroup"
        if node_group.bl_idname == 'SchemaTree':
            node_group_type = "MantisSchemaGroup"
        node = tree.nodes.new(node_group_type)
        node.select = True
        tree.nodes.active = node
        node.node_tree = node_group
        node.location = context.space_data.cursor_location
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT',)
                # TRANSFORM_OT_translate={ "value":
                #                         (context.space_data.cursor_location[0]*1.25,
                #                          context.space_data.cursor_location[1]*1.25, 0)})
# TODO: figure out how to make this feel nice in the UI
# bpy.ops.node.translate_attach_remove_on_cancel(TRANSFORM_OT_translate={"value":(-59.247, -5.7344, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'GRID'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":True, "use_duplicated_keyframes":False, "view2d_edge_pan":True, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False, "translate_origin":False}, NODE_OT_attach={})

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
        #name them uniquely
        number=0
        for o in n.outputs:
            if int(o.name[-3:]) == number:
                number = int(o.name[-3:]) + 1
            else: # my intention is to use the first number that isn't used
                break # so break here because we have reached the end or a 'gap'
        n.outputs.new("ColorSetSocket", "Color Set."+str(number).zfill(3))
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
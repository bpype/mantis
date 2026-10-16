from .utilities.utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

# the first step is to get selection syncing working
import bpy
from bpy import context
from .base_definitions import get_signature_from_edited_tree 

from bpy.types import Bone, PoseBone
# just to prevent confusing with Python object:
from bpy.types import Object as bpy_object

SELECTION_POLL_RATE = 0.01
ENABLED = True
cached_selection_state = {}

import bpy

# The following node types represent objects that can be selected.
WATCH_FOR_SELECTION = [ 'xFormBoneNode', 'xFormArmatureNode',
        'xFormGeometryObject', 'xFormObjectInstance', 'xFormCurvePin',
        'xFormGetBone', 'InputExistingGeometryObject']


def get_signature_from_space(node, space):
    sig_path=[None,]
    for item in space.path[:-1]:
        if item.node_tree.nodes.active:
            sig_path.append(item.node_tree.nodes.active.name)
        else:
            return () # can't be determined, should not happen in normal use.
    if node:
        return tuple(sig_path+[node.name])
    else: # it's also necessary to do this if there is no path at all.
        return ()

def get_visible_space_data(space_types={'NODE_EDITOR'}):
    visible_spaces = []
    for wm in bpy.data.window_managers:
        for window in wm.windows:
            for area in window.screen.areas:
                if area.type in space_types:
                    if area.spaces.active:
                        visible_spaces.append(area.spaces.active)
                        
    return visible_spaces

# Example usage: Get all active 3D Viewport space_data objects
spaces = get_visible_space_data('VIEW_3D')

for space in spaces:
    print(f"Found 3D Viewport: shading mode = {space.shading.type}")

# TODO: now that I have this working...
#  - Selection State should be tracked and handled on a per-object basis
#     so Mantis should update selection state one item at a time
#  - finally, I want to extend this selection sync to show active constraints and modifiers
#     and to link up with viewport gizmo tools.
#  - Serialize this so that it sticks around when saving/loading file
# Eventually:
#  - sync scene/object selection to node graph. I have the structure in place
#     but I still have to write the selection tracking code.
# Potential small BUG?
#  - I am not ensuring the base/root tree is the same for the space and the nodes
#  - because I straight up do not store that in the selection_sync dicts
#  - easy to fix, will do it when clearing TODO's here.

def timer_update_selection_sync():
    try:
        if not ENABLED: return None
        root_tree = None
        tree_path = None
        parsed_tree = None
        spaces = get_visible_space_data()
        if not spaces:
            return SELECTION_POLL_RATE

        selection_state_start = cached_selection_state.copy()
        selection_state = cached_selection_state.copy()
        current_tree_selected_total = 0

        # we can't get UI context in this function so we have to checc all of them
        #maybe the tree itself can load the timer when it is opened in the node editor?
        for space in spaces:
            # if we are in the node editor, manage node selection
            if space.type == "NODE_EDITOR":
                if not space.path:
                    return SELECTION_POLL_RATE # empty tree
                root_tree = space.path[0].node_tree
                if root_tree is None:
                    return SELECTION_POLL_RATE
                if root_tree.bl_idname != 'MantisTree':
                    return SELECTION_POLL_RATE
                tree_path = [path_item.node_tree for path_item in space.path]
                if len(tree_path[-1].nodes) == 0:
                    return SELECTION_POLL_RATE # empty graph
                parsed_tree = root_tree.parsed_tree
                if tree_path[-1].nodes.active is not None:
                    active_ui_signature = (get_signature_from_space(tree_path[-1].nodes.active, space))
                else:
                    active_ui_signature = None
                for n in tree_path[-1].nodes:
                    if n.bl_idname not in WATCH_FOR_SELECTION: continue
                    selection_state[ui_signature := get_signature_from_space(n, space)] = n.select
                    current_tree_selected_total += int(n.select)
        
        if parsed_tree is None:
            return SELECTION_POLL_RATE
        cached_selection_state.update(selection_state)
        # We only fire the update if things have changed.
        if selection_state != selection_state_start:
            from bpy import context
            view_layer = context.view_layer
            deselect = not bool(current_tree_selected_total)
            try:
                update_scene_selection_from_node_graph_selection_sync(
                    active_ui_signature, view_layer,
                    selection_state, deselect)
            except Exception as e:
                prRed ("Error in Selection Sync")
                prRed (e)
                return SELECTION_POLL_RATE
    except Exception as e:
        from .__init__ import DOERROR
        if DOERROR:
            prRed ("Error in Selection Sync")
            prRed (e)
            raise e
    return SELECTION_POLL_RATE

from .utilities.utilities import set_bone_selection

def update_scene_selection_from_node_graph_selection_sync(
        active_ui_signature, view_layer,
        selection_state, deselect ):
    from .base_definitions import selection_sync_node_to_object
    # prWhite("Updating Scene Selection from Node Graph Selection")
    deselect_do_once = []
    for ui_signature, selected in selection_state.items():
        this_one_is_active = False
        if ui_signature == active_ui_signature: this_one_is_active = True
        for object_key in selection_sync_node_to_object.get(ui_signature, []):
            id_data = bpy.data.objects.get(object_key[0])
            if object_key[1]: # we have a sub_value, it's a bone
                if deselect:
                    if object_key[0] not in deselect_do_once:
                        for pb in id_data.pose.bones:
                            set_bone_selection(pb, False)
                        deselect_do_once.append(object_key[0])
                else:
                    pb = id_data.pose.bones[object_key[1]]
                    set_bone_selection(pb, selected)
                    if this_one_is_active: # set the active bone
                        id_data.data.bones.active = pb.bone
                    # now do its parent object...
                    if selected:
                        id_data.select_set(True, view_layer=view_layer)
                        if this_one_is_active:
                            view_layer.objects.active = id_data
            else: # or the sub_value is None, this is an object
                ob = id_data
                if deselect: selected = False
                ob.select_set(selected, view_layer=view_layer)
                if this_one_is_active and not deselect:
                    view_layer.objects.active = ob
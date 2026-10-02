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
        sig_path.append(item.node_tree.nodes.active.name)
    return tuple(sig_path+[node.name])

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
#  - every object should be kept in the cache at all times.
#  - a deselect event should check only the current tree for empty selection
#  - but deselect should deselect anything that is tracked by Mantis
#  - Mantis node <==> UI node relationships should be cached instead of using the
#     tree cache, and ideally, saved in the Scene object or something
#  - I'll probably do like a JSON or something for that, maybe a pickle
#  - anyhow the important thing is I need a bi-directional dictionary so I can
#     make the selection sync happen both ways
#  - finally, I want to extend this selection sync to show active constraints and modifiers
#     and to link up with viewport gizmo tools.

def timer_update_selection_sync():
    if not ENABLED: return None
    root_tree = None
    tree_path = None
    parsed_tree = None
    spaces = get_visible_space_data()
    if not spaces:
        return SELECTION_POLL_RATE

    selection_state_start = cached_selection_state.copy()
    selection_state = cached_selection_state.copy()
    ui_signatures = list(cached_selection_state.keys())
    current_tree_selected_total = 0

    # we can't get UI context in this function so we have to checc all of them
    #maybe the tree itself can load the timer when it is opened in the node editor?
    for space in spaces:
        # if we are in the node editor, manage node selection
        if space.type == "NODE_EDITOR":
            root_tree = space.path[0].node_tree
            parsed_tree = root_tree.parsed_tree
            tree_path = [path_item.node_tree for path_item in space.path]
            if root_tree is None:
                return SELECTION_POLL_RATE
            if root_tree.bl_idname != 'MantisTree':
                return SELECTION_POLL_RATE
            active_ui_signature = (get_signature_from_space(tree_path[-1].nodes.active, space))
            for n in tree_path[-1].nodes:
                if n.bl_idname not in WATCH_FOR_SELECTION: continue
                ui_signatures.append( ui_signature := get_signature_from_space(n, space))
                selection_state[ui_signature] = n.select
                current_tree_selected_total += int(n.select)
    
    if parsed_tree is None:
        return SELECTION_POLL_RATE
    cached_selection_state.update(selection_state)
    # We only fire the update if things have changed.
    if selection_state != selection_state_start:
        
        from bpy import context
        view_layer = context.view_layer
        deselect = bool(current_tree_selected_total)
        try:
            update_scene_selection_from_selection_sync(
                parsed_tree, ui_signatures, active_ui_signature, view_layer,
                selection_state, deselect)
        except Exception as e:
            prRed (e)
            return SELECTION_POLL_RATE
    return SELECTION_POLL_RATE


# 1 get the selected nodes
# 2 find mantis nodes that have the ui_signature of the node
# 3 get their b-objects and select them
def update_scene_selection_from_selection_sync(
        parsed_tree, ui_signatures, active_ui_signature, view_layer,
        selection_state, deselect ):
    # first check if this is a deselect event.
    # if it is, do not change the active object!
    # that makes the armature switch modes, it's annoying
    deselect=False
    if sum(selection_state.values()) == 0:
        deselect=True
    prWhite("Updating Scene Selection from Node Graph Selection")
    for mantis_node in parsed_tree.values():
        this_one_is_active = False
        if not hasattr(mantis_node, 'bGetObject'): continue
        if mantis_node.node_type != 'XFORM': continue
        if mantis_node.ui_signature in ui_signatures:
            selected = selection_state[mantis_node.ui_signature]
            if mantis_node.ui_signature == active_ui_signature:
                this_one_is_active = True
            ob = mantis_node.bGetObject()
            if isinstance(ob, PoseBone):
                if deselect:
                    ob.select = False
                    continue
                ob.select = selected
                if this_one_is_active: # set the active bone
                    ob.id_data.data.bones.active = ob.bone
                # now do its parent object...
                if selected:
                    if ob.id_data.select_get(view_layer=view_layer) == False:
                        ob.id_data.select_set(True, view_layer=view_layer)
                    if this_one_is_active:
                        view_layer.objects.active = ob.id_data
            elif isinstance(ob, bpy_object):
                if ob.select_get(view_layer=view_layer) != selected:
                    ob.select_set(selected, view_layer=view_layer)
                if this_one_is_active and not deselect:
                    view_layer.objects.active = ob


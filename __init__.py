from . import ( ops_nodegroup,
                ops_ui,
                base_definitions,
                socket_definitions,
                link_nodes_ui,
                xForm_nodes_ui,
                misc_nodes_ui,
                primitives_nodes_ui,
                deformer_nodes_ui,
                math_nodes_ui,
                i_o,
                schema_nodes_ui,
                menu_classes,
              )
from .ops_generate_tree import GenerateMantisTree

from .utilities import prRed

from .base_definitions import (MANTIS_VERSION_MAJOR,
                               MANTIS_VERSION_MINOR,
                               MANTIS_VERSION_SUB)

classLists = [module.TellClasses() for module in [
 link_nodes_ui,
 xForm_nodes_ui,
 misc_nodes_ui,
 socket_definitions,
 ops_nodegroup,
 ops_ui,
 primitives_nodes_ui,
 deformer_nodes_ui,
 math_nodes_ui,
 i_o,
 schema_nodes_ui,
 base_definitions,
 menu_classes,
]]
classLists.append( [GenerateMantisTree] )
#
classes = []
while (classLists):
    classes.extend(classLists.pop())

interface_classes = []

from .preferences import MantisPreferences
classes.append(MantisPreferences)

from os import environ
if environ.get("ENABLEVIS"):
    from .visualize import MantisVisualizeNode, MantisVisualizeOutput, MantisVisualizeTree
    classes.extend([MantisVisualizeTree, MantisVisualizeNode, MantisVisualizeOutput, ])

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class MantisNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return (context.space_data.tree_type in ['MantisTree', 'SchemaTree'])

class SchemaNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return (context.space_data.path[len(context.space_data.path)-1].node_tree.bl_idname == 'SchemaTree')


class MantisGroupCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return (context.space_data.path[len(context.space_data.path)-1].node_tree.bl_idname in ['MantisTree'] and len(context.space_data.path)>1)

input_category=[
            NodeItem("InputFloatNode"),
            NodeItem("InputVectorNode"),
            NodeItem("InputBooleanNode"),
            NodeItem("InputBooleanThreeTupleNode"),
            NodeItem("InputStringNode"),
            NodeItem("InputIntNode"),
            NodeItem("InputMatrixNode"),
            NodeItem("InputWidget"),
            NodeItem("InputExistingGeometryObject"),
            NodeItem("InputExistingGeometryData"),
            NodeItem("UtilityDeclareCollections"),
            NodeItem("InputThemeBoneColorSets"),
            NodeItem("InputColorSetPallete"),
    ]
link_transform_category = [
        NodeItem("LinkCopyLocation"),
        NodeItem("LinkCopyRotation"),
        NodeItem("LinkCopyScale"),
        NodeItem("LinkCopyTransforms"),
        NodeItem("LinkLimitLocation"),
        NodeItem("LinkLimitScale"),
        NodeItem("LinkLimitRotation"),
        NodeItem("LinkLimitDistance"),
        NodeItem("LinkTransformation"),
        NodeItem("LinkFloor"),
    ]
link_tracking_category = [
        NodeItem("LinkInverseKinematics"),
        NodeItem("LinkSplineIK"),
        NodeItem("LinkStretchTo"),
        NodeItem("LinkDampedTrack"),
        NodeItem("LinkLockedTrack"),
        NodeItem("LinkTrackTo"),
        NodeItem("LinkShrinkWrap"),
    ]
link_relationship_category = [
        NodeItem("linkInherit"),
        NodeItem("LinkInheritConstraint"),
        NodeItem("LinkArmature"),
    ]
deformer_category=[NodeItem(cls.bl_idname) for cls in deformer_nodes_ui.TellClasses()]
xForm_category = [
        NodeItem("xFormGeometryObject"),
        NodeItem("xFormBoneNode"),
        NodeItem("xFormArmatureNode"),
        NodeItem("xFormObjectInstance"),
        NodeItem("xFormCurvePin"),
    ]
driver_category = [
        NodeItem("UtilityCustomProperty"),
        NodeItem("LinkDrivenParameter"),
        NodeItem("UtilityFCurve"),
        NodeItem("UtilityBoneProperties"),
        NodeItem("UtilityDriverVariable"),
        NodeItem("UtilitySwitch"),
        NodeItem("UtilityDriver"),
        NodeItem("UtilityKeyframe"),
    ]
geometry_category = [
        NodeItem("GeometryCirclePrimitive"),
        NodeItem("GeometryLattice"),
    ]
utility_category = [
        NodeItem("MathStaticInt"),
        NodeItem("MathStaticFloat"),
        NodeItem("MathStaticVector"),
        NodeItem("UtilityCatStrings"),
        NodeItem("UtilityCollectionJoin"),
        NodeItem("UtilityCollectionHierarchy"),
        NodeItem("UtilityGeometryOfXForm"),
        NodeItem("UtilityNameOfXForm"),
        NodeItem("UtilityCombineThreeBool"),
        NodeItem("UtilityCombineVector"),
        NodeItem("UtilityIntToString"),
        NodeItem("UtilityArrayGet"),
        NodeItem("UtilityArrayLength"),
        NodeItem("UtilityChoose"),
        NodeItem("UtilityCompare"),
        NodeItem("UtilityPrint"),
        NodeItem("UtilitySeparateVector"),
        NodeItem("UtilityGetNearestFactorOnCurve"),
        NodeItem("UtilityKDChoosePoint"),
        NodeItem("UtilityKDChooseXForm"),
    ]
matrix_category = [
        NodeItem("UtilityMetaRig"),
        NodeItem("UtilityMatrixFromCurve"),
        NodeItem("UtilityMatricesFromCurve"),
        NodeItem("UtilityNumberOfCurveSegments"),
        NodeItem("UtilityMatrixFromCurveSegment"),
        NodeItem("UtilityPointFromCurve"),
        NodeItem("UtilityGetCurvePoint"),
        NodeItem("UtilityNumberOfSplines"),
        NodeItem("UtilityPointFromBoneMatrix"),
        NodeItem("UtilitySetBoneLength"),
        NodeItem("UtilityGetBoneLength"),
        NodeItem("UtilityBoneMatrixHeadTailFlip"),
        NodeItem("UtilityMatrixSetLocation"),
        NodeItem("UtilityMatrixFromXForm"),
        NodeItem("UtilityAxesFromMatrix"),
        NodeItem("UtilityMatrixTransform"),
        NodeItem("UtilityMatrixInvert"),
        NodeItem("UtilityMatrixCompose"),
        NodeItem("UtilityMatrixAlignRoll"),
        NodeItem("UtilityTransformationMatrix"),
        NodeItem("UtilitySetBoneMatrixTail"),
    ]
groups_category = [
        NodeItem("MantisNodeGroup"),
        NodeItem("MantisSchemaGroup"),
    ]
group_interface_category = [
        NodeItem("NodeGroupInput"),
        NodeItem("NodeGroupOutput"),
    ]

node_categories = [
    # identifier, label, items list
    MantisNodeCategory('INPUT', "Input", items=input_category),
    MantisNodeCategory('LINK_TRANSFORM', "Link (Transform)", items=link_transform_category),
    MantisNodeCategory('LINK_TRACKING', "Link (Tracking)", items=link_tracking_category),
    MantisNodeCategory('LINK_RELATIONSHIP', "Link (Inheritance)", items=link_relationship_category),
    MantisNodeCategory('DEFORMER', "Deformer", items=deformer_category),
    MantisNodeCategory('XFORM', "Transform", items=xForm_category),
    MantisNodeCategory('DRIVER', "Driver", items=driver_category),
    MantisNodeCategory('GEOMETRY', "Geometry", items =geometry_category),
    MantisNodeCategory('UTILITIES', "Utility", items=utility_category),
    MantisNodeCategory('MATRIX', "Matrix", items=matrix_category),
    MantisNodeCategory('GROUPS', "Groups", items=groups_category),
    MantisGroupCategory('GROUP_INTERFACE', "Group In/Out", items=group_interface_category),
]

schema_category=[NodeItem(cls.bl_idname) for cls in schema_nodes_ui.TellClasses()]
schema_categories = [
    SchemaNodeCategory('SCHEMA_SCHEMA', "Schema", items=schema_category),
]

import bpy
def init_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name="Node Generic", space_type='NODE_EDITOR')
    kmi = [
        # Normal operation
        km.keymap_items.new("mantis.group_nodes", 'G', 'PRESS', ctrl=True),
        km.keymap_items.new("mantis.edit_group", 'TAB', 'PRESS'),
        km.keymap_items.new("mantis.execute_node_tree", 'E', 'PRESS'),
        km.keymap_items.new("mantis.mute_node", 'M', 'PRESS'),
        km.keymap_items.new("mantis.nodes_cleanup", "C", 'PRESS', shift=True,),
        # Testing
        km.keymap_items.new("mantis.query_sockets", 'Q', 'PRESS'),
        km.keymap_items.new("mantis.test_operator", 'T', 'PRESS'),
        km.keymap_items.new("mantis.visualize_output", 'V', 'PRESS'),
        # Saving, Loading, Reloading, etc.
        km.keymap_items.new("mantis.export_save_choose", "S", 'PRESS', alt=True,),
        km.keymap_items.new("mantis.export_save_as", "S", 'PRESS', alt=True, shift=True),
        km.keymap_items.new("mantis.reload_tree", "R", 'PRESS', alt=True,),
        km.keymap_items.new("mantis.import_tree", "O", 'PRESS', ctrl=True,),
    ]
    return km, kmi

addon_keymaps = []

# handlers! these have to be persistent
from bpy.app.handlers import persistent
from .base_definitions import hash_tree
@persistent
def update_handler(scene):
    # return
    context=bpy.context
    if context.space_data:
        if not hasattr(context.space_data, "path"):
            return
        trees = [p.node_tree for p in context.space_data.path]
        if not trees: return
        if (node_tree := trees[0]).bl_idname in ['MantisTree']:
            if node_tree.is_exporting:
                return
            if node_tree.prevent_next_exec : pass
            elif node_tree.do_live_update and not (node_tree.is_executing):
                node_tree.update_tree(context)

@persistent
def execute_handler(scene):
    context = bpy.context
    if context.space_data:
        if not hasattr(context.space_data, "path"):
            return
        trees = [p.node_tree for p in context.space_data.path]
        if not trees: return
        if (node_tree := trees[0]).bl_idname in ['MantisTree']:
            # check here instead of in execute_tree because these  values can be
            #  modified at weird times and checking from the handler is more consistent
            if ( node_tree.tree_valid) and ( node_tree.do_live_update ):
                node_tree.execute_tree(context)
                node_tree.tree_valid=False

from .versioning import versioning_tasks
def node_version_update(node, do_once):
    from .xForm_nodes_ui import xFormNode
    for bl_idname, task, required_kwargs in versioning_tasks:
        arg_map = {}
        if 'node' in required_kwargs:
            arg_map['node']=node
        if 'node_tree' in required_kwargs:
            arg_map['node_tree']=node.id_data
        # we'll match all, or categories, or specific bl_idname as needed.
        if ('ALL' in bl_idname) or \
                ('XFORM' in bl_idname) and isinstance(node, xFormNode) or\
                node.bl_idname in bl_idname:
            if do_once:
                print (f"Updating tree {node.id_data.name} to "
                       f"{MANTIS_VERSION_MAJOR}.{MANTIS_VERSION_MINOR}.{MANTIS_VERSION_SUB}")
            task(**arg_map)

def do_version_update(node_tree):
    # set updating status for dynamic nodes to prevent bugs in socket remapping
    do_once = True
    for node in node_tree.nodes:
        if hasattr(node, 'is_updating'):
            node.is_updating = True
    # start by doing tree versioning tasks
    for affected_bl_idnames, task, arguments_needed in versioning_tasks:
        if node_tree.bl_idname not in affected_bl_idnames: continue # this is a node task.
        arguments = {}
        if 'tree' in arguments_needed:
            arguments['tree']=node_tree
        task(**arguments)
    # run the updates that have no prerequisites
    for node in node_tree.nodes:
        node_version_update(node, do_once)
        do_once = False
    # NOTE: if future versoning tasks have prerequisites, resolve them here and update again
    # reset the updating status for dynamic nodes
    for node in node_tree.nodes:
        if hasattr(node, 'is_updating'):
            node.is_updating = False
    # increment the version at the end
    node_tree.mantis_version[0] = MANTIS_VERSION_MAJOR
    node_tree.mantis_version[1] = MANTIS_VERSION_MINOR
    node_tree.mantis_version[2] = MANTIS_VERSION_SUB

@persistent
def version_update_handler(filename):
    for node_tree in bpy.data.node_groups: # ensure it can update again after file load.
        if node_tree.bl_idname in ["MantisTree", "SchemaTree"]:
                node_tree.is_exporting=False; node_tree.is_executing=False
    for node_tree in bpy.data.node_groups:
        if node_tree.bl_idname in ["MantisTree", "SchemaTree"]:
            if (node_tree.mantis_version[0] < MANTIS_VERSION_MAJOR) or \
               (node_tree.mantis_version[1] < MANTIS_VERSION_MINOR) or \
               (node_tree.mantis_version[2] < MANTIS_VERSION_SUB):
                do_version_update(node_tree)

@persistent
def autoload_components(filename):
    # this should not be blocking or slow!
    print("Auto-loading components")
    from os import path as os_path
    from .utilities import get_component_library_items, get_default_collection
    from .i_o import do_import
    from .preferences import get_bl_addon_object
    import json
    from bpy import context, data
    bl_addon_object = get_bl_addon_object()
    unlink_curves = True
    unlink_armatures = True
    if data.collections.get(bl_addon_object.preferences.CurveDefaultCollection):
        unlink_curves=False
    if data.collections.get(bl_addon_object.preferences.MetaArmatureDefaultCollection):
        unlink_armatures=False
    base_path = bl_addon_object.preferences.ComponentsAutoLoadFolder
    components = get_component_library_items(path='AUTOLOAD')
    for autoload_component in components:
        path = os_path.join(base_path, autoload_component[0])
        with open(path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            do_import(json_data, context,
                       search_multi_files=True, filepath=path,
                       skip_existing=True)
            # let's get the node trees and assign a fake user
            for tree_name in json_data.keys():
                tree = data.node_groups.get(tree_name)
                tree.use_fake_user = True

    # now we need to unlink the collections, and add fake users to them
    curves_collection = get_default_collection(collection_type="CURVE")
    armature_collection = get_default_collection(collection_type="ARMATURE")
    if unlink_curves and (curves_collection := data.collections.get(
            bl_addon_object.preferences.CurveDefaultCollection)):
        context.scene.collection.children.unlink(curves_collection)
    if unlink_armatures and (armature_collection := data.collections.get(
            bl_addon_object.preferences.MetaArmatureDefaultCollection)):
        context.scene.collection.children.unlink(armature_collection)

# I'll need to do some fiddling here when it comes time to try
#   and make rig definitions animatable.
@persistent
def on_animation_playback_pre_handler(scene,depsgraph):
    for t in bpy.data.node_groups:
        if t.bl_idname in ['MantisTree', 'SchemaTree']:
            t.is_executing = True
@persistent
def on_animation_playback_post_handler(scene,depsgraph):
    for t in bpy.data.node_groups:
        if t.bl_idname in ['MantisTree', 'SchemaTree']:
            t.is_executing = False

@persistent
def on_undo_post_handler(scene): # the undo will trigger a depsgraph update
    for t in bpy.data.node_groups: # so we enable prevent_next_exec.
        if t.bl_idname in ['MantisTree', 'SchemaTree']:
            t.prevent_next_exec = True
            t.hash=""
            # set the tree to invalid to trigger a tree update
            # since the context data is wiped by an undo.

from .menu_classes import (node_context_menu_draw, node_add_menu_draw,
                           armature_add_menu_draw, import_menu_draw)

from .socket_definitions import generate_custom_interface_types
generated_classes = generate_custom_interface_types()
classes.extend(generated_classes)

def register():
    from bpy.utils import register_class

    for cls in classes:
        try:
            register_class(cls)
        except RuntimeError as e:
            prRed(f"Registration error for class: {cls.__name__}")
            raise e
    nodeitems_utils.register_node_categories('MantisNodeCategories', node_categories)
    nodeitems_utils.register_node_categories('SchemaNodeCategories', schema_categories)
    bpy.types.NODE_MT_context_menu.append(node_context_menu_draw)
    bpy.types.NODE_MT_add.append(node_add_menu_draw)
    bpy.types.VIEW3D_MT_armature_add.append(armature_add_menu_draw)
    bpy.types.TOPBAR_MT_file_import.append(import_menu_draw)



    km, kmi = init_keymaps()
    for k in kmi:
        k.active = True
        addon_keymaps.append((km, k))
    # add the handlers
    bpy.app.handlers.depsgraph_update_pre.insert(0, update_handler)
    bpy.app.handlers.depsgraph_update_post.insert(0, execute_handler)
    bpy.app.handlers.load_post.insert(0, autoload_components)
    bpy.app.handlers.load_post.insert(0, version_update_handler)
    bpy.app.handlers.animation_playback_pre.insert(0, on_animation_playback_pre_handler)
    bpy.app.handlers.animation_playback_post.insert(0, on_animation_playback_post_handler)
    bpy.app.handlers.undo_post.insert(0, on_undo_post_handler)
    # I'm adding mine in first to ensure other addons don't mess up mine
    # but I am a good citizen! so my addon won't mess up yours! probably...



def unregister():
    bpy.types.NODE_MT_context_menu.remove(node_context_menu_draw)
    for tree in bpy.data.node_groups: # ensure it doesn't try to update while quitting.
        if tree.bl_idname in ['MantisTree, SchemaTree']:
            tree.is_exporting=True; tree.is_executing=True
    nodeitems_utils.unregister_node_categories('MantisNodeCategories')
    nodeitems_utils.unregister_node_categories('SchemaNodeCategories')

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

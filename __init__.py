from . import ( ops_nodegroup,
                base_definitions,
                socket_definitions,
                link_definitions,
                xForm_definitions,
                misc_nodes_ui,
                primitives_definitions,
                deformer_definitions,
                math_definitions,
                i_o,
                schema_definitions,
                menu_classes,
              )
from .ops_generate_tree import GenerateMantisTree

from .utilities import prRed

MANTIS_VERSION_MAJOR=0
MANTIS_VERSION_MINOR=11
MANTIS_VERSION_SUB=17

classLists = [module.TellClasses() for module in [
 link_definitions,
 xForm_definitions,
 misc_nodes_ui,
 socket_definitions,
 ops_nodegroup,
 primitives_definitions,
 deformer_definitions,
 math_definitions,
 i_o,
 schema_definitions,
 base_definitions,
 menu_classes,
]]
classLists.append( [GenerateMantisTree] )
#
classes = []
while (classLists):
    classes.extend(classLists.pop())

interface_classes = []


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
            NodeItem("InputStringNode"),
            NodeItem("InputIntNode"),
            NodeItem("InputMatrixNode"),
            NodeItem("InputExistingGeometryObject"),
            NodeItem("InputExistingGeometryData"),
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
    ]
link_relationship_category = [
        NodeItem("linkInherit"),
        NodeItem("LinkInheritConstraint"),
        NodeItem("LinkArmature"),
    ]
deformer_category=[NodeItem(cls.bl_idname) for cls in deformer_definitions.TellClasses()]
xForm_category = [
        NodeItem("xFormGeometryObject"),
        NodeItem("xFormBoneNode"),
        NodeItem("xFormArmatureNode"),
        NodeItem("xFormObjectInstance"),
        NodeItem("xFormCurvePin"),
    ]
driver_category = [
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

schema_category=[NodeItem(cls.bl_idname) for cls in schema_definitions.TellClasses()]
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

versioning_node_tasks = [
    #relevant bl_idnames      # task
    #(['LinkTransformation'], transformation_constraint_radians_to_degrees)
]


def do_version_update(node_tree):
    from .base_definitions import NODES_REMOVED, SOCKETS_REMOVED, SOCKETS_RENAMED, SOCKETS_ADDED
    for n in node_tree.nodes:
        rename_jobs = []

        if n.bl_idname in NODES_REMOVED:
            print(f"INFO: removing node {n.name} of type {n.bl_idname} because it has been deprecated.")
            n.inputs.remove(socket)
            continue
        for i, socket in enumerate(n.inputs.values()):
            if (n.bl_idname, socket.identifier) in SOCKETS_REMOVED:
                print(f"INFO: removing socket {socket.identifier} of node {n.name} of type {n.bl_idname} because it has been deprecated.")
                n.inputs.remove(socket)
            for old_class, old_bl_idname, old_name, new_bl_idname, new_name, multi in SOCKETS_RENAMED:
                if (n.bl_idname == old_class and socket.bl_idname == old_bl_idname and socket.name == old_name):
                    rename_jobs.append((socket, i, new_bl_idname, new_name, multi))
        for i, socket in enumerate(n.outputs.values()):
            if (n.bl_idname, socket.identifier) in SOCKETS_REMOVED:
                print(f"INFO: removing socket {socket.identifier} of node {n.name} of type {n.bl_idname} because it has been deprecated.")
                n.outputs.remove(socket)
            for old_class, old_bl_idname, old_name, new_bl_idname, new_name, multi in SOCKETS_RENAMED:
                if (n.bl_idname == old_class and socket.bl_idname == old_bl_idname and socket.name == old_name):
                    rename_jobs.append((socket, i, new_bl_idname, new_name, multi))

        for bl_idname, in_out, socket_type, socket_name, index, use_multi_input, default_val in SOCKETS_ADDED:
            if n.bl_idname != bl_idname:
                continue
            if in_out == 'INPUT' and n.inputs.get(socket_name) is None:
                print(f"INFO: adding socket \"{socket_name}\" of type {socket_type} to node {n.name} of type {n.bl_idname}.")
                s = n.inputs.new(socket_type, socket_name, use_multi_input=use_multi_input)
                s.default_value = default_val
                n.inputs.move(len(n.inputs)-1, index)
        socket_map = None
        if rename_jobs:
            from .utilities import get_socket_maps
            socket_maps = get_socket_maps(n)
        for socket, socket_index, new_bl_idname, new_name, multi in rename_jobs:
            old_id = socket.identifier
            print (f"Renaming socket {socket.identifier} to {new_name} in node {n.name}")
            from .utilities import do_relink
            if socket.is_output:
                index = 1
                in_out = "OUTPUT"
                n.outputs.remove(socket)
                s = n.outputs.new(new_bl_idname, new_name, identifier=new_name, use_multi_input=multi)
                n.outputs.move(len(n.outputs)-1, socket_index)
                socket_map = socket_maps[1]
            else:
                index = 0
                in_out = "INPUT"
                n.inputs.remove(socket)
                s = n.inputs.new(new_bl_idname, new_name, identifier=new_name, use_multi_input=multi)
                n.inputs.move(len(n.inputs)-1, socket_index)
                socket_map = socket_maps[0]
            socket_map[new_name] = socket_map[old_id]
            if new_name != old_id: del socket_map[old_id] # sometimes rename just changes the socket type or multi
            do_relink(n, s, socket_map)
        for bl_idname, task in versioning_node_tasks:
            if n.bl_idname in bl_idname: task(n)
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
                print (f"Updating tree {node_tree.name} to {MANTIS_VERSION_MAJOR}.{MANTIS_VERSION_MINOR}.{MANTIS_VERSION_SUB}")
                do_version_update(node_tree)
                

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


    km, kmi = init_keymaps()
    for k in kmi:
        k.active = True
        addon_keymaps.append((km, k))
    # add the handlers
    bpy.app.handlers.depsgraph_update_pre.insert(0, update_handler)
    bpy.app.handlers.depsgraph_update_post.insert(0, execute_handler)
    bpy.app.handlers.load_post.insert(0, version_update_handler)
    bpy.app.handlers.animation_playback_pre.insert(0, on_animation_playback_pre_handler)
    bpy.app.handlers.animation_playback_post.insert(0, on_animation_playback_post_handler)
    bpy.app.handlers.undo_post.insert(0, on_undo_post_handler)
    # I'm adding mine in first to ensure other addons don't mess up mine
    # but I am a good citizen! so my addon won't mess up yours! probably...



def unregister():
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
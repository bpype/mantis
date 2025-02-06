from . import ( ops_nodegroup,
                base_definitions,
                socket_definitions,
                link_definitions,
                xForm_definitions,
                nodes_generic,
                primitives_definitions,
                deformer_definitions,
                math_definitions,
                i_o,
                schema_definitions,
              )
from .ops_generate_tree import GenerateMantisTree
from bpy.types import NodeSocket

from .utilities import prRed

MANTIS_VERSION_MAJOR=0
MANTIS_VERSION_MINOR=9
MANTIS_VERSION_SUB=4


classLists = [module.TellClasses() for module in [
 link_definitions,
 xForm_definitions,
 base_definitions,
 nodes_generic,
 socket_definitions,
 ops_nodegroup,
 primitives_definitions,
 deformer_definitions,
 math_definitions,
 i_o,
 schema_definitions,
]]
classLists.append( [GenerateMantisTree] )
#
classes = []
while (classLists):
    classes.extend(classLists.pop())

interface_classes = []
from bpy import app

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
    ]
utility_category = [
        NodeItem("MathStaticInt"),
        NodeItem("MathStaticFloat"),
        NodeItem("MathStaticVector"),
        NodeItem("UtilityCatStrings"),
        NodeItem("UtilityCombineThreeBool"),
        NodeItem("UtilityCombineVector"),
        NodeItem("UtilityIntToString"),
        NodeItem("UtilityArrayGet"),
        NodeItem("UtilityChoose"),
        NodeItem("UtilityCompare"),
        NodeItem("UtilityPrint"),
    ]
matrix_category = [
        NodeItem("UtilityMetaRig"),
        NodeItem("UtilityMatrixFromCurve"),
        NodeItem("UtilityMatricesFromCurve"),
        NodeItem("UtilityPointFromCurve"),
        NodeItem("UtilityPointFromBoneMatrix"),
        NodeItem("UtilitySetBoneLength"),
        NodeItem("UtilityGetBoneLength"),
        NodeItem("UtilityBoneMatrixHeadTailFlip"),
        NodeItem("UtilityMatrixSetLocation"),
        NodeItem("UtilityMatrixFromXForm"),
        NodeItem("UtilityAxesFromMatrix"),
        NodeItem("UtilityMatrixTransform"),
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
@persistent
def update_handler(scene):
    context=bpy.context
    if context.space_data:
        if not hasattr(context.space_data, "path"):
            return
        trees = [p.node_tree for p in context.space_data.path]
        if not trees: return
        if (node_tree := trees[0]).bl_idname in ['MantisTree']:
            if node_tree.do_live_update and not (node_tree.is_executing or node_tree.is_exporting):
                prev_links = node_tree.num_links
                node_tree.num_links = len(node_tree.links)
                if (prev_links == -1):
                    return
                if prev_links != node_tree.num_links:
                    node_tree.tree_valid = False
                if node_tree.tree_valid == False:
                        scene.render.use_lock_interface = True
                        node_tree.update_tree(context)
                        scene.render.use_lock_interface = False

@persistent
def execute_handler(scene):
    context = bpy.context
    if context.space_data:
        if not hasattr(context.space_data, "path"):
            return
        trees = [p.node_tree for p in context.space_data.path]
        if not trees: return
        if (node_tree := trees[0]).bl_idname in ['MantisTree']:
            if node_tree.tree_valid and node_tree.do_live_update and not (node_tree.is_executing or node_tree.is_exporting):
                scene.render.use_lock_interface = True
                node_tree.execute_tree(context)
                scene.render.use_lock_interface = False
                node_tree.tree_valid = False


@persistent
def version_update_handler(filename):
    from .base_definitions import NODES_REMOVED, SOCKETS_REMOVED
    for node_tree in bpy.data.node_groups:
        if node_tree.bl_idname in ["MantisTree", "SchemaTree"]:
            if (node_tree.mantis_version[0] < MANTIS_VERSION_MAJOR) or \
               (node_tree.mantis_version[1] < MANTIS_VERSION_MINOR) or \
               (node_tree.mantis_version[2] < MANTIS_VERSION_SUB):
                print (f"Updating tree {node_tree.name} to {MANTIS_VERSION_MAJOR}.{MANTIS_VERSION_MINOR}.{MANTIS_VERSION_SUB}")
                node_tree.mantis_version[0] = MANTIS_VERSION_MAJOR
                node_tree.mantis_version[1] = MANTIS_VERSION_MINOR
                node_tree.mantis_version[2] = MANTIS_VERSION_SUB
                for n in node_tree.nodes:
                    if n.bl_idname in NODES_REMOVED:
                        print(f"INFO: removing node {n.name} of type {n.bl_idname} because it has been deprecated.")
                        n.inputs.remove(socket)
                        continue
                    for socket in n.inputs.values():
                        if (n.bl_idname, socket.identifier) in SOCKETS_REMOVED:
                            print(f"INFO: removing socket {socket.identifier} of node {n.name} of type {n.bl_idname} because it has been deprecated.")
                            n.inputs.remove(socket)
                    for socket in n.outputs.values():
                        if (n.bl_idname, socket.identifier) in SOCKETS_REMOVED:
                            print(f"INFO: removing socket {socket.identifier} of node {n.name} of type {n.bl_idname} because it has been deprecated.")
                            n.outputs.remove(socket)
                
                




def register():
    if bpy.app.version >= (4, 4):
        raise NotImplementedError("Blender 4.4 is not supported at this time.")

    from bpy.utils import register_class
    
    for cls in classes:
        try:
            register_class(cls)
        except RuntimeError as e:
            prRed(cls.__name__)
            raise e

    nodeitems_utils.register_node_categories('MantisNodeCategories', node_categories)
    nodeitems_utils.register_node_categories('SchemaNodeCategories', schema_categories)


    km, kmi = init_keymaps()
    for k in kmi:
        k.active = True
        addon_keymaps.append((km, k))
    # add the handlers
    bpy.app.handlers.depsgraph_update_pre.append(update_handler)
    bpy.app.handlers.depsgraph_update_post.append(execute_handler)
    bpy.app.handlers.load_post.append(version_update_handler)


    

def unregister():
    nodeitems_utils.unregister_node_categories('MantisNodeCategories')
    nodeitems_utils.unregister_node_categories('SchemaNodeCategories')

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

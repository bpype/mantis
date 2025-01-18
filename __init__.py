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
# lol
classLists.append( [GenerateMantisTree] )
#
classes = []
while (classLists):
    classes.extend(classLists.pop())

interface_classes = []
from bpy import app
# if app.version[0]  == 3:
#     for cls in [cls for cls in socket_definitions.TellClasses() if issubclass(cls, NodeSocket)]:
#         name = cls.__name__+"Interface"
#         from bpy.types import NodeSocketInterface
#         def default_draw_color(self, context,):
#             return self.color
#         def default_draw(self, context, layout):
#             return
#         interface = type(
#                       name,
#                       (NodeSocketInterface,),
#                       {
#                           "color"            : cls.color,
#                           "draw_color"       : default_draw_color,
#                           "draw"             : default_draw,
#                           "bl_idname"        : name,
#                           "bl_socket_idname" : cls.__name__,
#                       },
#                   )
#         interface_classes.append(interface)

#     classes.extend(interface_classes)

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class MantisNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return (context.space_data.tree_type in ['MantisTree', 'SchemaTree'])

class SchemaNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        # doesn't seem to work tho
        try:
            return (context.space_data.path[len(path)-1].node_tree.bl_idname == 'SchemaTree')
        except:
            return True


input_category=[
            NodeItem("InputFloatNode"),
            NodeItem("InputVectorNode"),
            NodeItem("InputBooleanNode"),
            # NodeItem("InputBooleanThreeTupleNode"),
            # NodeItem("InputRotationOrderNode"),
            # NodeItem("InputTransformSpaceNode"),
            NodeItem("InputStringNode"),
            NodeItem("InputIntNode"),
            # NodeItem("InputQuaternionNode"),
            # NodeItem("InputQuaternionNodeAA"),
            NodeItem("InputMatrixNode"),
            NodeItem("InputLayerMaskNode"),
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
        # NodeItem("xFormNullNode"),
        NodeItem("xFormBoneNode"),
        NodeItem("xFormRootNode"),
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

# THIS is stupid, should be filled out automatically
node_categories = [
    # identifier, label, items list
    MantisNodeCategory('INPUT', "Input", items=input_category),
    # MantisNodeCategory('LINK', "Link", items=[]),
    # MantisNodeCategory('LINK_TRACKING', "Link", items=[]),
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



def register():
    from bpy.utils import register_class
    
    for cls in classes:
        try:
            register_class(cls)
        except RuntimeError as e:
            prRed(cls.__name__)
            raise e

    nodeitems_utils.register_node_categories('MantisNodeCategories', node_categories)
    nodeitems_utils.register_node_categories('SchemaNodeCategories', schema_categories)


    if (not bpy.app.background):
        km, kmi = init_keymaps()
        for k in kmi:
            k.active = True
            addon_keymaps.append((km, k))

    

def unregister():
    nodeitems_utils.unregister_node_categories('MantisNodeCategories')
    nodeitems_utils.unregister_node_categories('SchemaNodeCategories')

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

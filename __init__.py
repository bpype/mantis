from . import ( ops_nodegroup,
                base_definitions,
                socket_definitions,
                link_definitions,
                xForm_definitions,
                nodes_generic,
                primitives_definitions,
                deformer_definitions,
              )
from .ops_generate_tree import CreateMantisTree
from bpy.types import NodeSocket



classLists = [module.TellClasses() for module in [
 link_definitions,
 xForm_definitions,
 base_definitions,
 nodes_generic,
 socket_definitions,
 ops_nodegroup,
 primitives_definitions,
                deformer_definitions,
]]
# lol
classLists.append( [CreateMantisTree] )
#
classes = []
while (classLists):
    classes.extend(classLists.pop())

interface_classes = []
from bpy import app
if app.version[0]  == 3:
    for cls in [cls for cls in socket_definitions.TellClasses() if issubclass(cls, NodeSocket)]:
        name = cls.__name__+"Interface"
        from bpy.types import NodeSocketInterface
        def default_draw_color(self, context,):
            return self.color
        def default_draw(self, context, layout):
            return
        interface = type(
                      name,
                      (NodeSocketInterface,),
                      {
                          "color"            : cls.color,
                          "draw_color"       : default_draw_color,
                          "draw"             : default_draw,
                          "bl_idname"        : name,
                          "bl_socket_idname" : cls.__name__,
                      },
                  )
        interface_classes.append(interface)

    classes.extend(interface_classes)

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class AllNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return (context.space_data.tree_type == 'MantisTree')



# THIS is stupid, should be filled out automatically
node_categories = [
    # identifier, label, items list
    AllNodeCategory('INPUT', "Input", items=[
            NodeItem("UtilityMetaRig"),
            NodeItem("InputFloatNode"),
            NodeItem("InputVectorNode"),
            NodeItem("InputBooleanNode"),
            # NodeItem("InputBooleanThreeTupleNode"),
            # NodeItem("InputRotationOrderNode"),
            # NodeItem("InputTransformSpaceNode"),
            NodeItem("InputStringNode"),
            # NodeItem("InputQuaternionNode"),
            # NodeItem("InputQuaternionNodeAA"),
            NodeItem("InputMatrixNode"),
            NodeItem("InputLayerMaskNode"),
            NodeItem("InputExistingGeometryObject"),
            NodeItem("InputExistingGeometryData"),
    ]),
    # AllNodeCategory('LINK', "Link", items=[]),
    # AllNodeCategory('LINK_TRACKING', "Link", items=[]),
    AllNodeCategory('LINK_TRANSFORM', "Link (Transform)", items=[
        NodeItem("LinkCopyLocation"),
        NodeItem("LinkCopyRotation"),
        NodeItem("LinkCopyScale"),
        NodeItem("LinkCopyTransforms"),
        NodeItem("LinkLimitLocation"),
        NodeItem("LinkLimitScale"),
        NodeItem("LinkLimitRotation"),
        NodeItem("LinkLimitDistance"),
        NodeItem("LinkTransformation"),
    ]),
    AllNodeCategory('LINK_TRACKING', "Link (Tracking)", items=[
        NodeItem("LinkInverseKinematics"),
        NodeItem("LinkSplineIK"),
        NodeItem("LinkStretchTo"),
        NodeItem("LinkDampedTrack"),
        NodeItem("LinkLockedTrack"),
        NodeItem("LinkTrackTo"),
    ]),
    AllNodeCategory('LINK_RELATIONSHIP', "Link (Inheritance)", items=[
        NodeItem("linkInherit"),
        NodeItem("LinkInheritConstraint"),
        NodeItem("LinkArmature"),
    ]),
    AllNodeCategory('DEFORMER', "Deformer", items=[
            NodeItem("DeformerArmature"),
    ]),
    AllNodeCategory('XFORM', "Transform", items=[
         NodeItem("xFormGeometryObject"),
        # NodeItem("xFormNullNode"),
        NodeItem("xFormBoneNode"),
        NodeItem("xFormRootNode"),
        NodeItem("xFormArmatureNode"),
    ]),
    AllNodeCategory('DRIVER', "Driver", items=[
        NodeItem("UtilityFCurve"),
        NodeItem("UtilityBoneProperties"),
        NodeItem("LinkDrivenParameter"),
        NodeItem("UtilityDriverVariable"),
        NodeItem("UtilitySwitch"),
        NodeItem("UtilityDriver"),
    ]),
    AllNodeCategory('GEOMETRY', "Geometry", items = [
        NodeItem("GeometryCirclePrimitive"),
    ]),
    AllNodeCategory('UTILITIES', "Utility", items=[
        NodeItem("UtilityCatStrings"),
        NodeItem("UtilityCombineThreeBool"),
        NodeItem("UtilityCombineVector"),
    ]),
    AllNodeCategory('GROUPS', "Groups", items=[
        NodeItem("MantisNodeGroup"),
    ]),
]

import bpy
def init_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name="Node Generic", space_type='NODE_EDITOR')
    kmi = [
        # km.keymap_items.new("sorcar.execute_node", 'E', 'PRESS'),
        km.keymap_items.new("mantis.group_nodes", 'G', 'PRESS', ctrl=True),
        km.keymap_items.new("mantis.edit_group", 'TAB', 'PRESS'),
        km.keymap_items.new("mantis.query_sockets", 'Q', 'PRESS'),
        km.keymap_items.new("mantis.execute_node_tree", 'E', 'PRESS'),
        km.keymap_items.new("mantis.mute_node", 'M', 'PRESS'),
        km.keymap_items.new("mantis.test_operator", 'T', 'PRESS'),
        km.keymap_items.new("mantis.nodes_cleanup", "C", 'PRESS', shift=True,)
    ]
    return km, kmi

addon_keymaps = []

def register():
    from bpy.utils import register_class
    
    for cls in classes:
        register_class(cls)


    nodeitems_utils.register_node_categories('AllNodeCategories', node_categories)


    if (not bpy.app.background):
        km, kmi = init_keymaps()
        for k in kmi:
            k.active = True
            addon_keymaps.append((km, k))


def unregister():
    nodeitems_utils.unregister_node_categories('AllNodeCategories')

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

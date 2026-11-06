import bpy
from bpy.types import NodeSocket, NodeSocketStandard

# Classes which do not have default_value
# needed to detect when there is an error updating dynamic nodes
no_default_value= frozenset({
            'MantisSocket',
            'RelationshipSocket',
            'DeformerSocket',
            'xFormSocket',
            'GeometrySocket',
            'GenericRotationSocket',
            'CustomPropSocket',
            'FCurveSocket',
            'DriverSocket',
            'DriverVariableSocket',
            'xFormParameterSocket',
            'MorphTargetSocket',
            'KeyframeSocket',
            'WildcardSocket',
})
# the sockets that do not have this field do not transfer data.
# instead, it is the link itself which is meaningful.
from bpy.app import version as bpy_version
parent_classes = (NodeSocket)
if bpy_version == (4,5,0): # THere is a bug that requires the socket type to inherit from a Blender class
    from bpy.types import NodeSocketGeometry # so we will just inherit from NodeSocketGeometry
    parent_classes = (NodeSocketGeometry, NodeSocket)

class MantisSocket(parent_classes):
    is_valid_interface_type=False
    enum_display_type="TABS" # TABS or DROPDOWN
    category : bpy.props.StringProperty()
    @property
    def interface_type(self):
        # this is stupid but it is the fastest way to implement this
        # TODO: refactor this, it should be a class property
        if hasattr(self, "color"):
            return map_color_to_socket_type(self.color)
        return map_color_to_socket_type(self.color_simple)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

def socket_update_get_root_tree(self, context):
    context = bpy.context
    if not context.space_data:
        return None
    if not hasattr(context.space_data, "path"):
        return None
    try:
        root_tree = context.space_data.path[0].node_tree
    except IndexError: # not in the UI, for example, in a script instead.
        return None
    if root_tree is None:
        return None
    if root_tree.is_executing or root_tree.is_exporting or not root_tree.do_live_update:
        return None
    return root_tree

def overlay_toggle_update(self, context):
    root_tree = socket_update_get_root_tree(self, context)
    if root_tree is None: return
    parsed_tree = self.node.id_data.parsed_tree
    if hasattr(self.node, "display_update"):
        self.node.display_update(parsed_tree=parsed_tree, context=context)
    root_tree.update_tree(context, force = True)
    # and we need to mark the node as un-prepared.
    # For now I am not gonna try to resolve the overlay value from the UI.
    
def overlay_text_update(self, context):
    root_tree = socket_update_get_root_tree(self, context)
    if root_tree is None: return
    # have to check each one. see default_update NOTE
    handled = True
    for mantis_node in root_tree.parsed_tree.values():
        handled = try_update_mantis_node_for_socket(mantis_node, root_tree, self) and handled
    if not handled:
        root_tree.update_tree(context, force = True)
        root_tree.execute_tree(context)

class MantisSocketOverlayEnabled(MantisSocket):
    # this class just needs a couple properties
    use_overlay: bpy.props.BoolProperty( default=False, update=overlay_toggle_update)
    overlay_text: bpy.props.StringProperty( default="", update=overlay_text_update)
    def draw(self, context, layout, node, text):
        is_simple_out = ((hasattr(self, "default_value")) and (hasattr(self, "input") and getattr(self, "input")))
        if self.is_linked and not is_simple_out:
            layout.label( text=text, )
        elif hasattr(self, "default_value"):
            row = layout.row(align=True)
            # We'll show the property or the overlay field here
            prop_field = "overlay_text" if self.use_overlay else "default_value"
            row.prop(self, prop_field,text=self.name)
            # and the button to choose whether or not to use the overlay field
            row.prop(self, "use_overlay", text="", icon='CONSOLE', toggle=True)
        else:
            layout.label(text=self.name)

from .utilities.utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

transform_spaces_bone_to = (('WORLD', "World", "World Space"),
                            ('LOCAL', "Local", "Local Space"),
                            ('POSE', "Pose", "Pose Space"),
                            ('CUSTOM', "Custom", "Custom Space"),
                            ('LOCAL_WITH_PARENT', "Local (With Parent)", "Local Space"),
                            ('LOCAL_OWNER_ORIENT', "Local (Owner Orientation)", "Local Space"),)

transform_spaces_bone_from = (('WORLD', "World", "World Space"),
                              ('LOCAL', "Local", "Local Space"),
                              ('POSE', "Pose", "Pose Space"),
                              ('CUSTOM', "Custom", "Custom Space"),
                              ('LOCAL_WITH_PARENT', "Local (With Parent)", "Local Space"),)


transform_spaces_bone_object = (('WORLD', "World", "World Space"),
                                ('LOCAL', "Local", "Local Space"),
                                ('POSE', "Pose", "Pose Space"),
                                ('CUSTOM', "Custom", "Custom Space"),)
transform_spaces_object = (('WORLD', "World", "World Space"),
                           ('LOCAL', "Local", "Local Space"),
                           ('CUSTOM', "Custom", "Custom Space"),)

enumRotationOrder =(('AUTO', 'Auto', 'Auto'),
                    ('XYZ', "XYZ", "XYZ"),
                    ('XZY', "XZY", "XZY"),
                    ('ZXY', "ZXY", "ZXY"),
                    ('ZYX', "ZYX", "ZYX"),
                    ('YXZ', "YXZ", "YXZ"),
                    ('YZX', "YZX", "YZX"),
                    ('QUATERNION', "Quaternion", "Quaternion"),
                    ('AXIS_ANGLE', "Axis Angle", "Axis Angle"),)

eMatrixFromCurveModes = (('DIVISIONS', "Divisions", "Get a matrix from the curve automattically "
                                                    "based on dividing it into pieces."),
                         ('FACTOR', "Spline Factor", "Get a matrix from a specific factor"
                                                     " along the spline."),
                         ('FACTOR_WITH_TAIL', "Spline Factor (With Tail)",
                          "Get a matrix from a specific factor along the spline, "
                          "and place the tail on the curve at a specific factor. "))

eMatrixComposeModes = (('BASIS', "Basis Vectors", "Compose a matrix from basis vectors. "
                                                  "Mantis will not automatically orthonormalize them."),
# TODO: Implement #    ('BASIS_AUTO', "Basis Ortho Vectors", "Compose a matrix from basis vectors. "
#       this feature! #                            "Mantis will automatically orthonormalize them."),
                       ('CHANNELS', "Transform Channels", "Compose a matrix from translation, rotation, "
                                                          "and scale transform channels."))


# node socket colors:
cFloat          = (0.631373, 0.631373, 0.631373, 1.000000)
cColor          = (0.780392, 0.780392, 0.160784, 1.000000)
cVector         = (0.388235, 0.388235, 0.780392, 1.000000)
cShader         = (0.388235, 0.780392, 0.388235, 1.000000)
cInt            = (0.058824, 0.521569, 0.149020, 1.000000)
cString         = (0.388235, 0.388235, 0.388235, 1.000000)
# cBool           = (0.698039, 0.650980, 0.188235, 1.000000)
cParameter      = (0.48, 0.24, 0.24, 1.0)
cDriver         = (0.88, 0.11, 0.88, 1.0)
cDriverVariable = (0.66, 0.33, 0.04, 1.0)
cFCurve         = (0.77, 0.77, 0.11, 1.0)
cKeyframe       = (0.06, 0.22, 0.88, 1.0)
cEnable         = (0.92, 0.92, 0.92, 1.0)
cBoneCollection = (0.82, 0.82, 0.82, 1.0)
cDeformer       = (0.05, 0.08, 0.45, 1.0)
cShapeKey       = (0.95, 0.32, 0.05, 1.0)

# custom colors:
cIK             = (0.596078, 0.596078, 0.364706, 1.000000) #because it's yellow in Blender
cRelationship   = (0.352941, 0.584314, 0.431373, 1.000000) #constraint color
cMatrix         = (0.0, 1.0, 0.75, 1)
cxForm          = (0.843137, 0.592157, 0.388235, 1.000000) #could even fetch the theme colors...
cTransformSpace = (1.0, 0.4, 0.216, 1.0)
cBool           = (0.1, 0.1, 0.1, 1.0)
cBool3          = (0.35, 0.25, 0.18, 1.0)
cRotationOrder  = (0.0, 0.8, 0.0, 1.0)
cQuaternion     = (0.85, 0.25, 0.18, 1.0)
#
cGeometry          = (0.000000, 0.672443, 0.366253, 1.000000)
# think about making colors that are representative of the data's purpose:
   # location
   # rotation
   # scale

# OR make all of it a reference to the type of data within?

def color_equivalent(color_a, color_b):
    # because Blender's floating point numbers are not quite equal. pain.
    from .base_definitions import FLOAT_EPSILON
    for channel_a, channel_b in zip(color_a, color_b):
        if abs(channel_a-channel_b) > FLOAT_EPSILON:
            return False
    return True

def map_color_to_socket_type(socket_color):
    # let's get the socket type by color for e.g. wildcard sockets.
    # for some reason I can't use match-case here. dumb.
    if color_equivalent(socket_color, cFloat):
        return "FloatSocket"
    if color_equivalent(socket_color, cColor):
        return "ColorSetSocket"
    if color_equivalent(socket_color, cVector):
        return "VectorSocket"
    if color_equivalent(socket_color, cInt):
        return "IntSocket"
    if color_equivalent(socket_color, cDriver):
        return "DriverSocket"
    if color_equivalent(socket_color, cDriverVariable):
        return "DriverVariableSocket"
    if color_equivalent(socket_color, cFCurve):
        return "FCurveSocket"
    if color_equivalent(socket_color, cKeyframe):
        return "KeyframeSocket"
    if color_equivalent(socket_color, cEnable):
        return "BooleanSocket"
    if color_equivalent(socket_color, cDeformer):
        return "DeformerSocket"
    if color_equivalent(socket_color, cShapeKey):
        return "MorphTargetSocket"
    if color_equivalent(socket_color, cMatrix):
        return "MatrixSocket"
    if color_equivalent(socket_color, cxForm):
        return "xFormSocket"
    if color_equivalent(socket_color, cBool):
        return "BooleanSocket"
    if color_equivalent(socket_color, cBool3):
        return "BooleanThreeTupleSocket"
    return "StringSocket"


# Hybrid approach: Make same-data, similar purpose have similar colors.
from typing import List
def TellClasses() -> List[MantisSocket]:
    return [ #MantisSocket,
             #DefaultSocket,
             #InputSocket,
             MatrixSocket,
             xFormSocket,
             RelationshipSocket,
             DeformerSocket,
             GeometrySocket,
             GenericRotationSocket,
             EnableSocket,
             HideSocket,
            #  InverseKinematicsSocket,
             DriverSocket,
             DriverVariableSocket,
             FCurveSocket,
            #  LayerMaskSocket,
            #  LayerMaskInputSocket,
             BoneCollectionSocket,
             EnumArrayGetOptions,

             EnumCustomPropTypeSocket,
             CustomPropSocket,
             xFormParameterSocket,
             ParameterBoolSocket,
             ParameterIntSocket,
             ParameterFloatSocket,
             ParameterVectorSocket,
             ParameterStringSocket,

             TransformSpaceSocket,
             BooleanSocket,
             InvertedBooleanSocket,
             BooleanThreeTupleSocket,
             RotationOrderSocket,
             QuaternionSocket,
             QuaternionSocketAA,
             UnsignedIntSocket,
             IntSocket,
             StringSocket,
             CollectionDeclarationSocket,
             ColorSetDisplaySocket,
             ColorSetSocket,

             EnumMetaRigSocket,
             EnumMetaBoneSocket,
             EnumArmature,
             EnumExistingBoneSocket,
             EnumCurveSocket,
             EnumWidgetLibrarySocket,
             BoolUpdateParentNode,
            #  LabelSocket,
             IKChainLengthSocket,
             EnumInheritScale,
             EnumRotationMix,
             EnumRotationMixCopyTransforms,
             EnumMaintainVolumeStretchTo,
             EnumRotationStretchTo,
             EnumTrackAxis,
             EnumUpAxis,
             EnumFollowPathForwardAxis,
             EnumFloorAxis,
             EnumLockAxis,
             EnumLimitMode,
             EnumYScaleMode,
             EnumXZScaleMode,
             EnumTransformationMap,
             EnumTransformationRotationMode,
             EnumTransformationRotationOrder,
             EnumTransformationTranslationMixMode,
             EnumTransformationRotationMixMode,
             EnumTransformationScaleMixMode,
             EnumTransformationAxes,
             EnumBBoneHandleType,
             # Shrinkwrap
             EnumShrinkwrapTypeSocket,
             EnumShrinkwrapFaceCullSocket,
             EnumShrinkwrapProjectAxisSocket,
             EnumShrinkwrapModeSocket,
             # Geometry Attribute
             EnumGeometryAttributeDataTypeSocket,
             EnumGeometryAttributeDomainSocket,
             EnumMixModeGeometryAttribute,
             # Deformers
             EnumSkinning,
             MorphTargetSocket,
             #
             FloatSocket,
             FloatPositiveSocket,
             FloatFactorSocket,
             FloatAngleSocket,
             VectorSocket,
             VectorEulerSocket,
             VectorTranslationSocket,
             VectorScaleSocket,
             # Drivers
             EnumDriverVariableType,
             EnumDriverVariableEvaluationSpace,
             EnumDriverVariableTransformChannel,
             EnumDriverRotationMode,
             EnumDriverType,
             KeyframeSocket,
             EnumKeyframeInterpolationTypeSocket,
             EnumKeyframeBezierHandleTypeSocket,
             EnumLatticeInterpolationTypeSocket,
             EnumCorrectiveSmoothTypeSocket,
             eFCrvExtrapolationMode,
             # other enums
             EnumArmatureDisplayType,
             EnumDisplayType,
             # Math
             MathFloatOperation,
             MathVectorOperation,
             MatrixTransformOperation,
             #conditions
             EnumCompareOperation,
             # modes, options for node operations
            EnumMatrixFromCurveMode,
            EnumComposeMatrixModes,
             # Schema
             WildcardSocket,
            #  xFormArraySocket,
            #  RelationshipArraySocket,
            #  BooleanArraySocket,
            #  IntArraySocket,
            #  FloatArraySocket,
            #  BooleanThreeTupleArraySocket,
            #  VectorArraySocket,
            #  QuaternionArraySocket,
            #  MatrixArraySocket,
            #  StringArraySocket,
             ]


def Tell_bl_idnames():                                # reroute nodes
    return [cls.bl_idname for cls in TellClasses()]#+["NodeSocketColor"]

def tell_valid_bl_idnames():
    valid_classes = filter(lambda cls : cls.is_valid_interface_type, [cls for cls in TellClasses()])
    return (cls.bl_idname for cls in valid_classes)


enum_default_xForm_values =(
        ('NONE', "None", "None - fail if unconnected (RECOMMENDED)."),
        ('ARMATURE', "Generated Armature", "Generate an armature automatically. "
                     "PLEASE use this only for development and testing. "
                     "If you use this as a feature in your rigs you will be sorry."),)
    
########################################################################
#  Update Callbacks
########################################################################

def interface_socket_update(self, context):
    from .execution.overlays import fill_root_tree_overlays, parser_handle_text
    from itertools import chain
    # so what I need to do here is:
    #  - if this is the root tree, and the interface has connections, invalidate them
    #  - or if the root tree node is using an overlay, update it directly
    #  - if there are any overlay-tagged, invalidate them
    root_tree = socket_update_get_root_tree(self, context)
    if root_tree is None: return # happens on startup or if e.g. tree is executing
    parsed_tree = root_tree.parsed_tree
    if len(parsed_tree) == 0: return # nothing to do here
    # get the mContext
    # HACK HACK HACK this is so ugly
    keys = list(parsed_tree.keys())
    mContext = None; i=0
    while mContext is None:
        mantis_node = parsed_tree[ keys[i] ]
        mContext = mantis_node.mContext; i+=1
        if i > len(keys): return # no mContext found
        # should exit immediately, the first node probably has it
    if self.id_data.name == root_tree.name:
        # checc for node group inputs and recursively reset execution for their children
        for node in root_tree.nodes:
            if node.bl_idname in {'NodeGroupInput'}:
                for o in node.outputs:
                    for l in o.links:
                        # We're in the root tree, that makes this easier
                        if mantis_node := parsed_tree.get( (None, l.to_node.name) ):
                            #rebuild the tree, it's unlikely the root tree change will not require this
                            root_tree.update_tree(force=True)
                            try: # if only I had a goto in this confounded language
                                prPurple(f"Executing tree after interface change")
                                root_tree.execute_tree(context)
                            except Exception as e:
                                prRed("Automatic Tree Execution failed because of %s" % e)
                            return
            else: # The overlays in the root tree get set directly, let's handle that here, also
                for socket in chain(node.inputs, node.outputs):   
                    
                    value = None
                    if hasattr(socket, 'default_value'):
                        value = socket.default_value
                        if hasattr(socket, 'use_overlay') and socket.use_overlay:
                            value = parser_handle_text(socket.overlay_text)
                    if isinstance(value, str) and '$' in value:
                        if socket.name  == 'Schema Length': # this one has to force a new parse
                            root_tree.update_tree(force=True) # because it modifies tree topology
                            try: # if only I had a goto in this confounded language
                                prPurple(f"Executing tree after interface change")
                                root_tree.execute_tree(context)
                            except Exception as e:
                                prRed("Automatic Tree Execution failed because of %s" % e)
                            return
                        value = fill_root_tree_overlays(mContext, socket.bl_idname, value)

    # Now update the overlay-tagged nodes.
    for mantis_node_signature, socket_id in mContext.tagged_for_overlay:
        if socket_id == 'Schema Length': break # break to force update
        # We always need to parse again after changing schema length
        mantis_node = parsed_tree.get(mantis_node_signature)
        if mantis_node:
            from .utilities.utilities import get_ui_node
            if mantis_node.ui_signature is None: break # can't update it
            ui_node = get_ui_node(mantis_node.ui_signature, root_tree)
            if ui_node:
                if socket_id == 'socket': # this is an anonymous output in a simple-input node
                    ui_socket = ui_node.outputs[0]
                else:
                    if (ui_socket := ui_node.inputs.get(socket_id)) is None:
                        for socket in ui_node.inputs:
                            if socket_id == socket.identifier: break
                        else: # Failed to update it, just update the tree.
                            break
                # Now we have the ui socket
                mantis_node.ui_modify_socket(ui_socket, ui_socket.name)
    else:
        return
    # if we break from the for loop above, we failed to update the socket and have to update the tree
    root_tree.update_tree(force=True)
    try:
        prPurple(f"Executing tree after interface change")
        root_tree.execute_tree(context)
    except Exception as e:
        prRed("Automatic Tree Execution failed because of %s" % e)
    # TODO: I can update these values instead of resetting them

def socket_update(mantis_node, ui_socket, socket_name=None):
    node_updated = mantis_node.ui_modify_socket(ui_socket, socket_name)
    if not node_updated: # so that we can tag its dependencies
        mantis_node.reset_execution_recursive()
    return node_updated

GROUP_TYPES = {"MantisNodeGroup", "MantisSchemaGroup"}

def default_update(ui_socket, context, do_execute=True):
    if not context:
        context = bpy.context
    root_tree = socket_update_get_root_tree(ui_socket, context)
    if root_tree is None: return
    # if it is a Schema Node, it will fail the checks below -- but we need it to update the tree.
    from .base_definitions import SchemaUINode
    if isinstance(ui_socket.node, SchemaUINode):
        # This was causing infinite loops before checking for is_updating
        # It seems to be happening when adding/removing links that are in schema trees
        # even if they are not connected to the schema node
        # I suspect that this completely disables this feature... whatever. TODO checc this
        if ui_socket.node.is_updating: return
        updating = ui_socket.node.is_updating
        ui_socket.node.is_updating=True
        try:
            root_tree.update_tree(context, force = True)
            prPurple(f"Executing tree after socket change: {ui_socket.node.name}:{ui_socket.name}")
            root_tree.execute_tree(context)
        finally:
            ui_socket.node.is_updating=updating; return
    if hasattr(ui_socket.node, 'is_updating'):
        if ui_socket.node.is_updating: return
    # similarly, we can do an early exit for changing group sockets.
    if (ui_socket.node.bl_idname in {"MantisNodeGroup", "MantisSchemaGroup"}):
        mantis_updated=False # this kind of socket can't be updated here (yet)
        root_tree.update_tree(context, force=True)
        try:
            prPurple(f"Executing tree after socket change: {ui_socket.node.name}:{ui_socket.name}")
            root_tree.execute_tree(context)
        except Exception as e:
            prRed("Automatic Tree Execution failed because of %s" % e)
        return
    # Now we know we are dealing with a normal node
    if hasattr(ui_socket.node, "initialized"):
        if not ui_socket.node.initialized: return
    else: return
    # if the socket has survived THAT ordeal, then the context is OK.
    # first, we try to update the Mantis tree in-situ.
    # Some nodes can update their b-objects, others will have to force-update the tree
    # because we just modified the data without modifying the topology of the graph.
    # finally, try and execute it if mantis couldn't update the b_objects itself.
    from .base_definitions import array_output_types
    mantis_updated=True
    if ui_socket.node.bl_idname in array_output_types:
        mantis_updated=False
        root_tree.update_tree(context, force=True)
    elif hasattr(ui_socket, 'default_value'):
        from .utilities.utilities import tree_from_mantis_node
        # we may not have to regenerate the tree; try and update the socket
        for mantis_node in root_tree.parsed_tree.values():
            if mantis_node.ui_signature is None: continue
            if mantis_node.ui_signature[-1] == ui_socket.node.name and \
                        tree_from_mantis_node(mantis_node.ui_signature, root_tree) == ui_socket.node.id_data:
                mantis_updated = try_update_mantis_node_for_socket(mantis_node, root_tree, ui_socket) and mantis_updated
        root_tree.update_tree(context, force = (mantis_updated == False) )
    root_tree.display_update(context)
    if mantis_updated==False:
        try:
            prPurple(f"Executing tree after socket change: {ui_socket.node.name}:{ui_socket.name}")
            root_tree.execute_tree(context)
        except Exception as e:
            prRed("Automatic Tree Execution failed because of %s" % e)

def try_update_mantis_node_for_socket(mantis_node, root_tree, ui_socket):
    # check to see if the mantis node is in the same ui-tree as this ui_socket
    node_updated = True
    from .misc_nodes import SimpleInputNode
    if isinstance(mantis_node, SimpleInputNode):
        node_updated = socket_update(mantis_node, ui_socket)
        for l in mantis_node.outputs[ui_socket.name].links:
            node_updated = node_updated and socket_update(l.to_node, ui_socket, l.to_socket)
    else:
        node_updated = socket_update(mantis_node, ui_socket)
    # execute the tree if even one node didn't update
    return node_updated


def update_socket(self, context,):
    default_update(self,context)

def driver_variable_socket_update(self, context):
    default_update(self,context)

def driver_socket_update(self, context):
    default_update(self,context)

def update_mute_socket(self, context):
    self.node.mute = not self.default_value
    default_update(self,context)

def update_hide_socket(self, context):
    self.node.mute = self.default_value
    default_update(self,context)

def ik_chain_length_update_socket(self, context):
    default_update(self,context)
    # self.node.update_chain_length(context)

def update_parent_node(self, context):
    default_update(self,context)
    if hasattr(self.node, "display_update"):
        self.node.display_update(context)

def update_metarig_armature(self, context,):
    if self.search_prop:
        self.node.armature = self.search_prop.name
        self.node.inputs[1].armature = self.search_prop
    default_update(self,context)

def update_metarig_posebone(self, context,):
    self.node.pose_bone = self.default_value
    default_update(self,context)

def update_socket_external_load(self, context):
    # this is a socket update for sockets that load data from a pack
    # e.g. widget, metarig, curve, or component selector sockets
    # currently no plans to add any but widgets, but whatever
    default_update(self, context)
    self.previous_value = self.default_value # this is all I need to do lol
    items = get_widget_library_items(self, context) # feels silly to do this here
    for item in items:
        if item[0] == self.default_value:
            self.previous_index = item[-1]
            break

########################################################################
#  Interface Types
########################################################################

# Custom Interface Types give the user the ability to set properties for the interface
# we'll define a base class, and generate the individual classes from the base class
# but we'll leave the option to define a few of them directly.
from bpy.types import NodeTreeInterfaceSocket

interface_default_value_description="The default value of the socket when it is not connected."
class MantisInterfaceSocketBaseClass():
    is_array : bpy.props.BoolProperty(default =False, update=interface_socket_update,
            description="Whether the socket is an array, otherwise it is constant." ) 
    is_connection : bpy.props.BoolProperty(default =False, update=interface_socket_update,
            description="If the socket is a connection or not. Ensure this is always paired"
                        " with an input and an output." ) 
    connected_to : bpy.props.StringProperty(default="", update=interface_socket_update,
            description="The name of the socket this one is connected to." ) 
    # we are just gonna use ONE base class (it's easier)
    # so generate ALL properties and show only what is needed.
    default_string : bpy.props.StringProperty(default="", update=interface_socket_update,
            description=interface_default_value_description, ) 
    default_float : bpy.props.FloatProperty(default=0.0, update=interface_socket_update,
            description=interface_default_value_description, ) 
    default_vector : bpy.props.FloatVectorProperty( size = 3, default = (0.0, 0.0, 0.0, ),
            description=interface_default_value_description, update=interface_socket_update,) 
    default_int : bpy.props.IntProperty(default=0, update=interface_socket_update,
            description=interface_default_value_description, ) 
    default_bool : bpy.props.BoolProperty(default=False, update=interface_socket_update,
            description=interface_default_value_description, ) 
    default_bool_vector : bpy.props.BoolVectorProperty(subtype = "XYZ", update=interface_socket_update,
            description=interface_default_value_description, ) 
    default_xForm : bpy.props.EnumProperty( default = 'NONE', update = interface_socket_update,
        items=enum_default_xForm_values, description=interface_default_value_description,)

def interface_draw(self, context, layout):
    if not self.is_connection:
        layout.prop(self, "is_array", text="Is Array", toggle=True,)
    if not self.is_array and self.id_data.bl_idname == 'SchemaTree':
        layout.prop(self, "is_connection", text="Is Connection", toggle=True,)
        if False: # DISABLED for now because it will take a big change to Schema to make this work.
            if self.is_connection: # only show this if in a Schema AND set to is_connection
                layout.prop(self, "connected_to", text="Connected To", toggle=True,)

# Different classes to handle different data types. In the future, these should also
#  have settable min/max and such where appropriate
def interface_string_draw(self, context, layout):
    layout.prop(self, "default_string", text="Default Value", toggle=True,)
    interface_draw(self, context, layout)

def interface_float_draw(self, context, layout):
    layout.prop(self, "default_float", text="Default Value", toggle=True,)
    interface_draw(self, context, layout)

def interface_vector_draw(self, context, layout):
    layout.prop(self, "default_vector", text="Default Value", toggle=True,)
    interface_draw(self, context, layout)

def interface_int_draw(self, context, layout):
    layout.prop(self, "default_int", text="Default Value", toggle=True,)
    interface_draw(self, context, layout)

def interface_bool_draw(self, context, layout):
    layout.prop(self, "default_bool", text="Default Value", toggle=True,)
    interface_draw(self, context, layout)

def interface_bool_vector_draw(self, context, layout):
    layout.prop(self, "default_bool_vector", text="Default Value", toggle=True,)
    interface_draw(self, context, layout)

def interface_xform_draw(self, context, layout):
    if self.in_out == 'INPUT':
        layout.prop(self, "default_xForm", text="Default Value", toggle=True,)
    interface_draw(self, context, layout)


def generate_custom_interface_types():
    generated_classes = []
    # copied from above
    valid_classes = filter(lambda cls : cls.is_valid_interface_type, [cls for cls in TellClasses()])
    for cls in valid_classes:
        name = cls.__name__ + "Interface"
            
        my_interface_draw = interface_draw
        # set the right draw function by the value's type
        match map_color_to_socket_type(cls.color_simple): #there has to be a better way to do this
            case "BooleanSocket":
                my_interface_draw = interface_bool_draw
            case "IntSocket":
                my_interface_draw = interface_int_draw
            case "FloatSocket":
                my_interface_draw = interface_float_draw
            case "BooleanThreeTupleSocket":
                my_interface_draw = interface_bool_vector_draw
            case "VectorSocket":
                my_interface_draw = interface_vector_draw
            case "StringSocket":
                my_interface_draw = interface_string_draw
            case "xFormSocket":
                my_interface_draw = interface_xform_draw
            case _:
                my_interface_draw = interface_draw

        interface = type(
                      name,
                      (MantisInterfaceSocketBaseClass, NodeTreeInterfaceSocket,),
                      {
                          "draw"             : my_interface_draw,
                          "bl_idname"        : name,
                          "bl_socket_idname" : cls.bl_idname,
                          "socket_type"      : cls.bl_idname,
                      },
                  )
        generated_classes.append(interface)
    return generated_classes


# Was setting color like this:
# color : bpy.props.FloatVectorProperty(size = 4, default = cFCurve,)
# but this didn't work when Blender automatically generated interface classes?
# so changed it to color = cVariable
# but for color-changing sockets, if I make them, this won' work? Maybe?
#
# I actually think I was wrong about all of that lol
# TODO change it back, dingus

########################################################################
#  Sockets
########################################################################

text_only_output_types = ["NodeGroupInput", "NodeGroupOutput", "SchemaArrayInput",
                          "SchemaArrayInputGet", "SchemaArrayInputAll", "SchemaConstInput",
                          "SchemaIncomingConnection"]

def ChooseDraw(self, context, layout, node, text, icon = "NONE", use_enum=True, nice_bool=True, icon_only=False):
    invert_checkbox = False
    if hasattr(self, "invert") and self.invert == True:
        invert_checkbox=True
    # TEXT ONLY
    if self.node.bl_idname in text_only_output_types:
        layout.label(text=text)
    elif hasattr(self, "display_text") and self.display_text and self.is_linked:
            layout.label(text=self.display_text)
    else:
        # ENUM VALUES (this is a HACK, fix it later)
        if ('Enum' in self.bl_idname) and (use_enum):
            if not (self.is_output or self.is_linked):
                if self.__class__.enum_display_type == 'DROPDOWN':
                    layout.prop(self, "default_value",)
                else:
                    layout.prop_tabs_enum(self, "default_value",)
            else:
                layout.prop(text=text)
        # for OUTPUT sockets that take INPUT (confusing name!)
        elif ((hasattr(self, "default_value")) and hasattr(self, "input") and getattr(self, "input")):
            # for simple input nodes
            layout.prop(self, "default_value", text=text, toggle=nice_bool, slider=True)
        # for INPUTS that are NOT CONNECTED
        elif (hasattr(self, "default_value")) and not (self.is_output or self.is_linked):
            # DO: expose these values as parameters for this function
            #   and set them for each socket.
            if icon == 'NONE': icon_only = False
            elif icon_only == True : text = "" # "real" icon-only looks bad for strings, need to check other props types.
            layout.prop(self, "default_value", text=text, toggle=nice_bool, slider=True, icon=icon,
                        invert_checkbox=invert_checkbox)
        # CONNECTED sockets and outputs without input fields
        else:
            layout.label(text=text)

def CollectionSocketDraw(socket, context, layout, node, text):
    # create the UI objects
    indent_length = len(socket.collection_path.split('>'))
    layout.alignment = 'EXPAND'
    # label_col = layout.row()
    label_col = layout.split(factor=0.20)
    label_col.alignment = 'LEFT' # seems backwards?
    label_col.scale_x = 9.0
    x_split = label_col.split(factor=0.35)
    x_split.scale_x=2.0
    x_split.alignment = 'RIGHT'
    operator_col = layout.row()
    # operator_col = layout
    operator_col.alignment = 'RIGHT'  # seems backwards?
    operator_col.scale_x = 1.0
    # x_split = operator_col.split(factor=0.5)
    # x_split.scale_x = 0.5
    # x_split.alignment = 'RIGHT'

    # Now fill in the text and operators and such
    label_text = socket.collection_path.split('>')[-1]
    if indent_length > 1:
        label_text = '└'+label_text #┈ use this character to extend
        for indent in range(indent_length):
            if indent <= 1: continue
            indent_text = ' ▹ '
            label_text=indent_text+label_text
    op_props = x_split.operator('mantis.collection_remove')
    op_props.socket_invoked = socket.identifier
    label_col.label(text=label_text)
    op_props = operator_col.operator('mantis.collection_add_new')
    op_props.socket_invoked = socket.identifier
    # this works well enough!

class RelationshipSocket(MantisSocket):
    # Description string
    '''Relationship'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'RelationshipSocket'
    bl_label = "Relationship"
    color_simple = cRelationship
    color : bpy.props.FloatVectorProperty(default=cRelationship, size=4)
    input : bpy.props.BoolProperty(default =False,)
    is_valid_interface_type=True

class DeformerSocket(MantisSocket):
    # Description string
    '''Deformer'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'DeformerSocket'
    bl_label = "Deformer"
    is_valid_interface_type=True
    color_simple = cDeformer
    color : bpy.props.FloatVectorProperty(default=cDeformer, size=4)
    input : bpy.props.BoolProperty(default =False,)



class MatrixSocket(MantisSocket):
    '''Matrix Input Output'''
    bl_idname = 'MatrixSocket'
    bl_label = "Matrix"
    default_value : bpy.props.FloatVectorProperty(
        default = (1.0, 0.0, 0.0, 0.0,
                   0.0, 1.0, 0.0, 0.0,
                   0.0, 0.0, 1.0, 0.0,
                   0.0, 0.0, 0.0, 1.0),
        size=16,
        update = update_socket,)
    color_simple = cMatrix
    color : bpy.props.FloatVectorProperty(default=cMatrix, size=4)
    input : bpy.props.BoolProperty(default =False,)
    is_valid_interface_type=True

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text=text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

    # Utility functions to make handling the 16 numbers more bearable
    def SetValue(self, mat):
        self.default_value =  ( mat[0][0], mat[0][1], mat[0][2], mat[0][3],
                                mat[1][0], mat[1][1], mat[1][2], mat[1][3],
                                mat[2][0], mat[2][1], mat[2][2], mat[2][3],
                                mat[3][0], mat[3][1], mat[3][2], mat[3][3], )
    def TellBoneLength(self):
        return self.default_value[15]


class xFormSocket(MantisSocket):
    '''xFrom Input Output'''
    bl_idname = 'xFormSocket'
    bl_label = "xForm"
    color_simple = cxForm
    color : bpy.props.FloatVectorProperty(default=cxForm, size=4)
    input : bpy.props.BoolProperty(default =False,)
    is_valid_interface_type=True

class GeometrySocket(MantisSocket):
    '''Geometry Input Output'''
    bl_idname = 'GeometrySocket'
    bl_label = "Geometry"
    color_simple = cGeometry
    color : bpy.props.FloatVectorProperty(default=cGeometry, size=4)
    input : bpy.props.BoolProperty(default =False,)
    is_valid_interface_type=True

class GenericRotationSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'GenericRotationSocket'
    bl_label = "Rotation"
    color = (0.0,0.0,0.0,0.0)
    input : bpy.props.BoolProperty(default =False,)

###############################

class EnableSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnableSocket'
    bl_label = "Enable"
    default_value: bpy.props.BoolProperty(default=True, update = update_mute_socket,)
    color_simple = cEnable
    color : bpy.props.FloatVectorProperty(default=cEnable, size=4)
    input : bpy.props.BoolProperty(default =False,)

    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, nice_bool=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class HideSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'HideSocket'
    bl_label = "Hide"
    default_value: bpy.props.BoolProperty(default=False, update = update_hide_socket,)
    color_simple = cEnable
    color : bpy.props.FloatVectorProperty(default=cEnable, size=4)
    input : bpy.props.BoolProperty(default =False,)

    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, nice_bool=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class FCurveSocket(MantisSocket):
    '''fCurve'''
    bl_idname = 'FCurveSocket'
    bl_label = "fCurve"
    color_simple = cFCurve
    color : bpy.props.FloatVectorProperty(default=cFCurve, size=4)
    input : bpy.props.BoolProperty(default =False, update = update_socket)
    is_valid_interface_type=True
    def init(self):
        self.display_shape = 'CIRCLE_DOT'

class DriverSocket(MantisSocket):
    '''Driver'''
    bl_idname = 'DriverSocket'
    bl_label = "Driver"
    color_simple = cDriver
    color : bpy.props.FloatVectorProperty(default=cDriver, size=4)
    input : bpy.props.BoolProperty(default =False, update = update_socket)
    is_valid_interface_type=True

    def init(self):
        self.display_shape = 'CIRCLE_DOT'

class DriverVariableSocket(MantisSocket):
    '''Driver'''
    bl_idname = 'DriverVariableSocket'
    bl_label = "Driver Variable"
    color_simple = cDriverVariable
    color : bpy.props.FloatVectorProperty(default=cDriverVariable, size=4)
    input : bpy.props.BoolProperty(default =False, update = update_socket)
    is_valid_interface_type=True

    def init(self):
        self.display_shape = 'CIRCLE_DOT'

def get_transform_space(self, context):
    if "Owner" in self.name:
        return transform_spaces_bone_from
    else:
        return transform_spaces_bone_to

class TransformSpaceSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'TransformSpaceSocket'
    bl_label = "Transform Space"
    default_value: bpy.props.EnumProperty(
        name="Space Transform",
        description="Space Transform",
        items=get_transform_space,
        default=0,
        update = update_socket,)
    color_simple = cTransformSpace
    color : bpy.props.FloatVectorProperty(default=cTransformSpace, size=4)
    input : bpy.props.BoolProperty(default =False,)

class BooleanSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'BooleanSocket'
    bl_label = "Boolean"
    default_value: bpy.props.BoolProperty(update = update_socket,)
    color_simple = cBool
    color : bpy.props.FloatVectorProperty(default=cBool, size=4)
    input : bpy.props.BoolProperty(default =False,)
    is_valid_interface_type=True

class InvertedBooleanSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'InvertedBooleanSocket'
    bl_label = "Inverted Boolean"
    default_value: bpy.props.BoolProperty(update = update_socket,)
    color_simple = cBool
    color : bpy.props.FloatVectorProperty(default=cBool, size=4)
    input : bpy.props.BoolProperty(default =False,)
    invert : bpy.props.BoolProperty(default=True,)
    is_valid_interface_type=False

class BooleanThreeTupleSocket(MantisSocket):
    # Description string
    '''Custom node socket type'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'BooleanThreeTupleSocket'
    bl_label = "Boolean Vector"
    default_value: bpy.props.BoolVectorProperty(subtype = "XYZ",update = update_socket,)
    color_simple = cBool3
    color : bpy.props.FloatVectorProperty(default=cBool3, size=4)
    input : bpy.props.BoolProperty(default =False,)
    is_valid_interface_type=True

class RotationOrderSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'RotationOrderSocket'
    bl_label = "Rotation Order"
    default_value: bpy.props.EnumProperty(
        name="Rotation Order",
        description="Rotation Order",
        items=enumRotationOrder,
        default='AUTO',
        update = update_socket,)
    color_simple = cRotationOrder
    color : bpy.props.FloatVectorProperty(default=cRotationOrder, size=4)
    input : bpy.props.BoolProperty(default =False,)

class QuaternionSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'QuaternionSocket'
    bl_label = "Quaternion"
    default_value: bpy.props.FloatVectorProperty(
        subtype = "QUATERNION",
        size = 4,
        default = (1.0, 0.0, 0.0, 0.0,),
        update = update_socket,)
    color_simple = cQuaternion
    color : bpy.props.FloatVectorProperty(default=cQuaternion, size=4)
    input : bpy.props.BoolProperty(default =False,)

class QuaternionSocketAA(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'QuaternionSocketAA'
    bl_label = "Axis Angle Quaternion"
    color_simple = cQuaternion
    color : bpy.props.FloatVectorProperty(default=cQuaternion, size=4)
    input : bpy.props.BoolProperty(default =False,)
    default_value: bpy.props.FloatVectorProperty(
        subtype = "AXISANGLE",
        size = 4,
        default = (1.0, 0.0, 0.0, 0.0,),
        update = update_socket,)

class IntSocket(MantisSocketOverlayEnabled):
    '''Custom node socket type'''
    bl_idname = 'IntSocket'
    bl_label = "Integer"
    default_value: bpy.props.IntProperty(default=0, update = update_socket, soft_min=-256, soft_max=256)
    color_simple = cInt
    color : bpy.props.FloatVectorProperty(default=cInt, size=4)
    input : bpy.props.BoolProperty(default =False,)
    is_valid_interface_type=True

class UnsignedIntSocket(MantisSocketOverlayEnabled):
    '''Unsigned Integer Socket'''
    bl_idname = 'UnsignedIntSocket'
    bl_label = "Unsigned Integer"
    default_value: bpy.props.IntProperty(default=0, update = update_socket, min=0, soft_max=256, max=2**13)
    color_simple = cInt
    color : bpy.props.FloatVectorProperty(default=cInt, size=4)
    input : bpy.props.BoolProperty(default =False,)
    is_valid_interface_type=True

class StringSocket(MantisSocket):
    """Float Input socket"""
    bl_idname = 'StringSocket'
    bl_label = "String"
    default_value : bpy.props.StringProperty(default = "", update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    icon : bpy.props.StringProperty(default = "NONE",)
    input : bpy.props.BoolProperty(default =False,)
    display_text : bpy.props.StringProperty(default="")
    is_valid_interface_type=True
    # def init(self):
        # if self.node.bl_idname == 'UtilityBoneProperties':
            # self.display_shape='CIRCLE_DOT'
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, icon=self.icon, icon_only=True,)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

def collection_declaration_get_default_value(self):
    return self.collection_path

class CollectionDeclarationSocket(MantisSocket):
    """Socket for declaring a collection"""
    bl_idname = 'CollectionDeclarationSocket'
    bl_label = "Collection"
    default_value : bpy.props.StringProperty(get=collection_declaration_get_default_value)
    collection_path : bpy.props.StringProperty(default="")
    color_simple = cBoneCollection
    color : bpy.props.FloatVectorProperty(default=cBoneCollection, size=4)
    icon : bpy.props.StringProperty(default = "NONE",)
    input : bpy.props.BoolProperty(default =True,)
    display_text : bpy.props.StringProperty(default="")
    is_valid_interface_type=False
    def draw(self, context, layout, node, text):
        CollectionSocketDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple
class BoneCollectionSocket(MantisSocket):
    """Collection socket"""
    bl_idname = 'BoneCollectionSocket'
    bl_label = "Collection"
    default_value: bpy.props.StringProperty(default = "Collection", update = update_socket,)
    input : bpy.props.BoolProperty(default =False,)
    color_simple = cBoneCollection
    color : bpy.props.FloatVectorProperty(default=cBoneCollection, size=4)
    is_valid_interface_type=True

def get_bone_theme_color(socket, prop,):
    from bpy import context
    color_index=socket.color_index
    color_set = context.preferences.themes[0].bone_color_sets[color_index]
    return getattr(color_set, prop )
def get_active_color(socket):
    if socket is None:
        from bpy import context
        return context.preferences.themes[0].view_3d.bone_pose_active
    return get_bone_theme_color(socket, 'active')
def get_normal_color(socket):
    if socket is None:
        from bpy import context
        return context.preferences.themes[0].view_3d.bone_solid
    return get_bone_theme_color(socket, 'normal')
def get_select_color(socket):
    if socket is None:
        from bpy import context
        return context.preferences.themes[0].view_3d.bone_pose
    return get_bone_theme_color(socket, 'select')

def get_color_set_value(socket,):
    return   [ socket.active_color[0],
               socket.active_color[1],
               socket.active_color[2],
               socket.normal_color[0],
               socket.normal_color[1],
               socket.normal_color[2],
               socket.selected_color[0],
               socket.selected_color[1],
               socket.selected_color[2],]

class ColorSetDisplaySocket(MantisSocket):
    """Socket for displaying a bone color theme"""
    bl_idname = 'ColorSetDisplaySocket'
    bl_label = "Color Set"
    default_value : bpy.props.FloatVectorProperty(get=get_color_set_value, size=9)
    color_simple = cColor
    color : bpy.props.FloatVectorProperty(default=cColor, size=4)
    icon : bpy.props.StringProperty(default = "NONE",)
    input : bpy.props.BoolProperty(default =False,)
    display_text : bpy.props.StringProperty(default="")
    color_index : bpy.props.IntProperty(default=0)
    active_color : bpy.props.FloatVectorProperty(
        name='Active Color', size=3, subtype='COLOR_GAMMA',
        get=get_active_color )
    normal_color : bpy.props.FloatVectorProperty(
        name='Normal Color', size=3, subtype='COLOR_GAMMA',
        get=get_normal_color )
    selected_color : bpy.props.FloatVectorProperty(
        name='Selected Color', size=3, subtype='COLOR_GAMMA',
        get=get_select_color )
    is_valid_interface_type=False
    def draw(self, context, layout, node, text):
        layout.prop( text='', data=self,
                    property='active_color', )
        layout.prop( text='', data=self,
            property='normal_color',)
        layout.prop( text='', data=self,
                    property='selected_color',)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class ColorSetSocket(MantisSocket):
    """Socket for setting a bone color"""
    bl_idname = 'ColorSetSocket'
    bl_label = "Custom Color Set"
    default_value : bpy.props.FloatVectorProperty(get=get_color_set_value, size=9)
    color_simple = cColor
    color : bpy.props.FloatVectorProperty(default=cColor, size=4)
    icon : bpy.props.StringProperty(default = "NONE",)
    input : bpy.props.BoolProperty(default = True,)
    display_text : bpy.props.StringProperty(default="")
    active_color : bpy.props.FloatVectorProperty(
        name='Active Color', size=3, subtype='COLOR_GAMMA',
        default=get_active_color(None),)
    normal_color : bpy.props.FloatVectorProperty(
        name='Normal Color', size=3, subtype='COLOR_GAMMA',
        default=get_normal_color(None),)
    selected_color : bpy.props.FloatVectorProperty(
        name='Selected Color', size=3, subtype='COLOR_GAMMA',
        default=get_select_color(None),)
    is_valid_interface_type=True
    def draw(self, context, layout, node, text):
        inherit_color_socket = self.node.inputs.get("Inherit Color")
        if (self.is_output == False) and (self.is_linked == True):
            layout.label(text=self.name)
        elif self.node.bl_idname in text_only_output_types:
            layout.label(text=self.name)
        elif inherit_color_socket and inherit_color_socket.default_value == True:
            layout.label(text='Using Inherit Color.')
        else:
            layout.prop( text='Color Set', data=self,
                        property='active_color', )
            layout.prop( text='', data=self,
                property='normal_color',)
            layout.prop( text='', data=self,
                        property='selected_color',)
        if self.node.bl_idname == 'InputColorSetPallete':
            ops_props = layout.operator('mantis.color_pallete_socket_remove')
            ops_props.tree_invoked = self.node.id_data.name
            ops_props.node_invoked = self.node.name
            ops_props.socket_invoked = self.identifier

    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


eArrayGetOptions =(
        ('CAP', "Cap", "Fail if the index is out of bounds."),
        ('WRAP', "Wrap", "Wrap around to the beginning of the array once the idex goes out of bounds."),
        ('HOLD', "Hold", "Reuse the last element of the array if the index is out of bounds."),)

class EnumArrayGetOptions(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumArrayGetOptions'
    bl_label = "OoB Behaviour"
    default_value: bpy.props.EnumProperty(
        items=eArrayGetOptions,
        name="OoB Behaviour",
        description="Out-of-bounds behaviour.",
        default = 'HOLD',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)


#####################################################################################
# Parameters
#####################################################################################


eCustomPropType = (
        ('BOOL'   , "Boolean", "Boolean", 0),
        ('INT'    , "Int"    , "Integer", 1),
        ('FLOAT'  , "Float"  , "Floating Point Number", 2),
        ('VECTOR' , "Vector" , "Vector", 3),
        ('STRING' , "String" , "String", 4),
    )

class EnumCustomPropTypeSocket(MantisSocket):
    """Custom Property Type"""
    bl_idname = 'EnumCustomPropTypeSocket'
    bl_label = "Property Type"
    color_simple = cString
    default_value: bpy.props.EnumProperty(
        items=eCustomPropType,
        description="Custom Property Type",
        default = 'BOOL',
        update = update_socket,)
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

class CustomPropSocket(MantisSocket):
    '''Custom Property'''
    bl_idname = 'CustomPropSocket'
    bl_label = "Custom Property"
    color_simple = cString
    is_valid_interface_type=True
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def init(self):
        self.display_shape = 'CIRCLE_DOT'

class xFormParameterSocket(MantisSocket):
    '''xFrom Parameter'''
    bl_idname = 'xFormParameterSocket'
    bl_label = "xForm Parameter"
    color_simple = cxForm
    color : bpy.props.FloatVectorProperty(default=cxForm, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def init(self):
        self.display_shape = 'CIRCLE_DOT'

class ParameterBoolSocket(MantisSocket):
    """Boolean Parameter Socket"""
    bl_idname = 'ParameterBoolSocket'
    bl_label = "Boolean Parameter"
    color_simple = cBool
    color : bpy.props.FloatVectorProperty(default=cBool, size=4)
    input : bpy.props.BoolProperty(default =False,)
    #custom properties:
    min:bpy.props.FloatProperty(default = 0)
    max:bpy.props.FloatProperty(default = 1)
    soft_min:bpy.props.FloatProperty(default = 0)
    soft_max:bpy.props.FloatProperty(default = 1)
    description:bpy.props.StringProperty(default = "")
    default_value : bpy.props.BoolProperty(default = False, update = update_socket,)
    def init(self):
        self.display_shape = 'CIRCLE_DOT'

class ParameterIntSocket(MantisSocket):
    """Integer Parameter socket"""
    bl_idname = 'ParameterIntSocket'
    bl_label = "Integer Parameter"

    default_value : bpy.props.IntProperty(default = 0, update = update_socket,)
    color_simple = cInt
    color : bpy.props.FloatVectorProperty(default=cInt, size=4)
    input : bpy.props.BoolProperty(default =False,)
    #custom properties:
    min:bpy.props.FloatProperty(default = 0)
    max:bpy.props.FloatProperty(default = 1)
    soft_min:bpy.props.FloatProperty(default = 0)
    soft_max:bpy.props.FloatProperty(default = 1)
    description:bpy.props.StringProperty(default = "")
    def init(self):
        self.display_shape = 'CIRCLE_DOT'

class ParameterFloatSocket(MantisSocket):
    """Float Parameter socket"""
    bl_idname = 'ParameterFloatSocket'
    bl_label = "Float Parameter"
    default_value : bpy.props.FloatProperty(default = 0.0, update = update_socket,)
    color_simple = cFloat

    color : bpy.props.FloatVectorProperty(default=cFloat, size=4)
    input : bpy.props.BoolProperty(default =False,)
    #custom properties:
    min:bpy.props.FloatProperty(default = 0)
    max:bpy.props.FloatProperty(default = 1)
    soft_min:bpy.props.FloatProperty(default = 0)
    soft_max:bpy.props.FloatProperty(default = 1)
    description:bpy.props.StringProperty(default = "")
    def init(self):
        self.display_shape = 'CIRCLE_DOT'

class ParameterVectorSocket(MantisSocket):
    """Vector Parameter socket"""
    bl_idname = 'ParameterVectorSocket'
    bl_label = "Vector Parameter"
    default_value : bpy.props.FloatVectorProperty(
        default = (0.0, 0.0, 0.0),
        update = update_socket,)
    color_simple = cVector

    color : bpy.props.FloatVectorProperty(default=cVector, size=4)
    input : bpy.props.BoolProperty(default =False,)
    #custom properties:
    description:bpy.props.StringProperty(default = "")
    def init(self):
        self.display_shape = 'CIRCLE_DOT'

class ParameterStringSocket(MantisSocket):
    """String Parameter socket"""
    bl_idname = 'ParameterStringSocket'
    bl_label = "String Parameter"
    default_value : bpy.props.StringProperty(default = "", update = update_socket,)
    color_simple = cString

    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    #custom properties:
    description:bpy.props.StringProperty(default = "")
    def init(self):
        self.display_shape = 'CIRCLE_DOT'

#####################################################################################
# Additional socket types, for special cases
#####################################################################################

from bpy.props import PointerProperty, StringProperty

def poll_is_armature(self, obj):
    return obj.type == "ARMATURE"

# def poll_is_armature(self, obj):
    # return obj.type == "ARMATURE"

class EnumMetaRigSocket(MantisSocketOverlayEnabled):
    '''Custom node socket type'''
    bl_idname = 'EnumMetaRigSocket'
    bl_label = "Meta Rig"
    color_simple = cString

    search_prop:PointerProperty(type=bpy.types.Object, poll=poll_is_armature, update=update_metarig_armature)

    def get_default_value(self):
        if self.search_prop:
            return self.search_prop.name
        return ""

    def set_default_value(self, value):
        if ob:= bpy.data.objects.get(value):
            if ob.type == 'ARMATURE':
                self.search_prop=ob

    default_value  : StringProperty(name = "", get=get_default_value, set=set_default_value)
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    
    def draw(self, context, layout, node, text):
        if self.is_output:
            layout.label(text=self.name)
        elif not (self.is_linked):
            row = layout.row(align=True)
            # We'll show the property or the overlay field here
            if self.use_overlay:
                row.prop(self, "overlay_text",text=self.name)
            else:
                row.prop_search(data=self, property="search_prop", search_data=bpy.data,
                                   search_property="objects", text="", icon="OUTLINER_OB_ARMATURE",
                                   results_are_suggestions=True)
            # and the button to choose whether or not to use the overlay field
            row.prop(self, "use_overlay", text="", icon='CONSOLE', toggle=True)
        elif hasattr(self.node, "armature"):
            layout.label(text=self.node.armature)
            # TODO: we should actually use the parsed tree to query this info directly, since this socket may belong to a node group in/out
            # which doesn't have this parameter. whatever.
        else:
            layout.label(text=self.name)

    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

# I donno why but I can't just subclass the above. hmm.so this is a duplicate
class EnumArmature(MantisSocket):
    bl_idname = "EnumArmature"
    bl_label = "Armature"
    color_simple = cString

    search_prop:PointerProperty(type=bpy.types.Object, poll=poll_is_armature, update=update_metarig_armature)

    def get_default_value(self):
        if self.search_prop:
            return self.search_prop.name
        return ""

    def set_default_value(self, value):
        if ob:= bpy.data.objects.get(value):
            if ob.type == 'ARMATURE':
                self.search_prop=ob

    default_value  : StringProperty(name = "", get=get_default_value, set=set_default_value)
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    
    def draw(self, context, layout, node, text):
        if self.is_output:
            layout.label(text=self.name)
        elif not (self.is_linked):
            layout.prop_search(data=self, property="search_prop", search_data=bpy.data, search_property="objects", text="", icon="OUTLINER_OB_ARMATURE", results_are_suggestions=True)
        elif hasattr(self.node, "armature"):
            layout.label(text=self.node.armature)
            # TODO: we should actually use the parsed tree to query this info directly, since this socket may belong to a node group in/out
            # which doesn't have this parameter. whatever.
        else:
            layout.label(text=self.name)

    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

def poll_is_curve(self, obj):
    return obj.type == "CURVE"

class EnumCurveSocket(MantisSocket):
    '''Choose a curve'''
    bl_idname = 'EnumCurveSocket'
    bl_label = "Curve"
    is_valid_interface_type=True

    search_prop:PointerProperty(type=bpy.types.Object, poll=poll_is_curve, update=update_socket)

    def get_default_value(self):
        if self.search_prop:
            return self.search_prop.name
        return ""

    def set_default_value(self, value):
        if ob:= bpy.data.objects.get(value):
            if ob.type == 'CURVE':
                self.search_prop=ob

    default_value  : StringProperty(name = "", get=get_default_value, set=set_default_value)

    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    def draw(self, context, layout, node, text):
        if not (self.is_linked) and not self.is_output:
            layout.prop_search(data=self, property="search_prop", search_data=bpy.data, search_property="objects", text="", icon="CURVE_DATA", results_are_suggestions=True)
        else:
            try:
                layout.label(text=self.search_prop.name)
            except AttributeError: # TODO make this show the graph's result
                layout.label(text=self.name)



    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

def SearchPBDraw(self, context, layout, node, text, icon = "NONE", use_enum=True, nice_bool=True, icon_only=False):
    layout.prop_search(data=self, property="default_value", search_data=self.armature.data, search_property="bones", text=text, icon=icon, results_are_suggestions=True)

class EnumMetaBoneSocket(MantisSocket):
    '''Socket to Get a Bone from an object'''
    bl_idname = 'EnumMetaBoneSocket'
    bl_label = "Bone"

    # this armature property is set by the parent node.
    armature:PointerProperty(type=bpy.types.Object)
    bone:StringProperty()

    def populate_bones_list(self, context):
        # just gonna hardcode the value
        if (meta_rig := self.armature):
            retList = []; i = -1
            retList.append( ('NONE', '', '', 'NONE', i:=i+1 ) )
            for b in meta_rig.data.bones:
                retList.append( (b.name, b.name, "Bone to copy matrix from", "BONE_DATA", i:=i+1 ) )
            return(retList)
        return None

    default_value  : StringProperty(name = "", update=update_metarig_posebone)

    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    def draw(self, context, layout, node, text):
        if not (self.is_linked):
            if self.armature is None:
                layout.prop(self, "default_value", text="", icon="BONE_DATA",)
            else:
                SearchPBDraw(self, context, layout, node, text="")
        else:
            layout.label(text=self.node.pose_bone)

    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

# I don't know why but I can't subclass the above and I had to duplicate it here
class EnumExistingBoneSocket(MantisSocket): 
    '''Socket to Get a Bone from an object'''
    bl_idname = 'EnumExistingBoneSocket'
    bl_label = "Bone"
    color_simple = cString

    # this armature property is set by the parent node.
    armature:PointerProperty(type=bpy.types.Object)
    bone:StringProperty()

    def populate_bones_list(self, context):
        # just gonna hardcode the value
        if (meta_rig := self.armature):
            retList = []; i = -1
            retList.append( ('NONE', '', '', 'NONE', i:=i+1 ) )
            for b in meta_rig.data.bones:
                retList.append( (b.name, b.name, "Bone to copy matrix from", "BONE_DATA", i:=i+1 ) )
            return(retList)
        return None

    default_value  : StringProperty(name = "", update=update_metarig_posebone)

    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    def draw(self, context, layout, node, text):
        if not (self.is_linked):
            if self.armature is None:
                layout.prop(self, "default_value", text="", icon="BONE_DATA",)
            else:
                SearchPBDraw(self, context, layout, node, text="")
        else:
            layout.label(text=self.node.pose_bone)

    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


# TODO: make it so that this makes an item for "missing" widgets
# for when a widget is moved or deleted
# Make it read .blend
# make it read the current directory, too?
def get_widget_library_items(self, context):
    from .preferences import get_bl_addon_object
    bl_mantis_addon = get_bl_addon_object()
    from os import path as os_path
    prev_name = os_path.split(self.previous_value)[-1]
    default_missing_value = ('MISSING', f'MISSING: {prev_name}', self.previous_value, 'ERROR', self.previous_index)
    return_value = [default_missing_value]
    widget_names={}
    if bl_mantis_addon and bl_mantis_addon.preferences:
        widgets_path = bl_mantis_addon.preferences.WidgetsLibraryFolder
        from os import walk as os_walk
        for path_root, dirs, files, in os_walk(widgets_path):
            # TODO handle .blend files
            for file in files:
                relative_file_name = os_path.join(os_path.sep.join(dirs), file)
                if file.endswith('.obj'):
                    widget_names[relative_file_name[:-4]] = relative_file_name
    if widget_names.keys():
        return_value=[]
        # first we select the previous value if it exists
        add_missing_key=False
        add_one=0
        if self.previous_value and self.previous_value not in widget_names.values():
            add_missing_key=True # we need to add the missing key at the previous index
        sorted_keys = list(widget_names.keys())
        sorted_keys.sort()
        for i, name in enumerate(sorted_keys):
            path = widget_names[name]
            if add_missing_key and i == self.previous_index:
                add_one+=1; return_value.append(default_missing_value)
            return_value.append( (path, name, path, 'GIZMO', i+add_one) )
    return return_value

# THIS is a special socket type that finds the widgets in your widgets library (set in preferences)
class EnumWidgetLibrarySocket(MantisSocket):
    '''Choose a Wdiget'''
    bl_idname = 'EnumWidgetLibrarySocket'
    bl_label = "Widget"
    is_valid_interface_type=False
    default_value  : bpy.props.EnumProperty(
        items=get_widget_library_items,
        name="Widget",
        description="Which widget to use",
        default = 0,
        update = update_socket_external_load,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    previous_value : bpy.props.StringProperty(default="")
    previous_index : bpy.props.IntProperty(default=0)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class BoolUpdateParentNode(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'BoolUpdateParentNode'
    bl_label = "Boolean"
    default_value: bpy.props.BoolProperty(default=False, update = update_parent_node)
    color_simple = cBool
    color : bpy.props.FloatVectorProperty(default=cBool, size=4)
    input : bpy.props.BoolProperty(default =False,)

class IKChainLengthSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'IKChainLengthSocket'
    bl_label = "IK Chain Length"
    default_value: bpy.props.IntProperty(default=0, update = ik_chain_length_update_socket, min = 0, max = 255)
    color_simple = cInt

    color : bpy.props.FloatVectorProperty(default=cInt, size=4)
    input : bpy.props.BoolProperty(default =False,)

# Inherit
eInheritScale = (
        ('FULL', "Full", "Fully inherit scale", 1),
        ('AVERAGE', "Average", "todo", 2),
        ('ALIGNED', "Aligned", "todo", 3),
        ('FIX_SHEAR', "Fix Shear", "todo", 4),
        ('NONE', "None", "todo", 5),
    )
class EnumInheritScale(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumInheritScale'
    bl_label = "Inherit Scale"
    default_value: bpy.props.EnumProperty(
        items=eInheritScale,
        name="Inherit Scale",
        description="Inherit Scale",
        default = 'FULL',
        #options = set(),
        update = update_socket,)
    color_simple = cString

    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

# Copy Rotation
eRotationMix =(
        ('REPLACE', "Replace", "Fully inherit scale", 0),
        ('BEFORE', "Before", "Fully inherit scale", 1),
        ('AFTER', "After", "Fully inherit scale", 2),
        ('ADD', "Add", "Fully inherit scale", 3),
        #todo, but i don't care much
    )

# TODO HACK
# do enum_flag as mutually exclusive options here

class EnumRotationMix(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumRotationMix'
    bl_label = "Rotation Mix"
    enum_display_type='DROPDOWN'
    default_value: bpy.props.EnumProperty(
        items=eRotationMix,
        name="Rotation Mix",
        description="Rotation Mix",
        default = 'REPLACE',#{'REPLACE'},
        options = set(), # this has to be a set lol
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

eRotationMix_copytransforms =(
        ('REPLACE', "Replace (Aligned)", "Fully inherit scale"),
        ('BEFORE', "Before (Aligned)", "Fully inherit scale"),
        ('AFTER', "After (Aligned)", "Fully inherit scale"),
        ('REPLACE_SPLIT', "Replace (Split Channels)", "Fully inherit scale"),
        ('BEFORE_SPLIT', "Before (Split Channels)", "Fully inherit scale"),
        ('AFTER_SPLIT', "After (Split Channels)", "Fully inherit scale"),
        ('REPLACE_FULL', "Replace (Full)", "Fully inherit scale"),
        ('BEFORE_FULL', "Before (Full)", "Fully inherit scale"),
        ('AFTER_FULL', "After (Full)", "Fully inherit scale"),)

class EnumRotationMixCopyTransforms(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumRotationMixCopyTransforms'
    bl_label = "Rotation Mix"

    default_value: bpy.props.EnumProperty(
        items=eRotationMix_copytransforms,
        name="Rotation Mix",
        description="Rotation Mix",
        default = 'REPLACE', #{'REPLACE'},
        #options = {'ENUM_FLAG'}, # this sux
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

# STRETCH TO
eMaintainVolumeStretchTo = (('VOLUME_XZX', "XZ", "XZ", 1),
                            ('VOLUME_X', "X", "X", 2),
                            ('VOLUME_Z', "Z", "Z", 4),
                            ('NO_VOLUME', "None", "None", 8),)
class EnumMaintainVolumeStretchTo(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumMaintainVolumeStretchToSocket'
    bl_label = "Maintain Volume"

    default_value: bpy.props.EnumProperty(
        items=eMaintainVolumeStretchTo,
        name="Maintain Volume",
        description="Maintain Volume",
        default = 'VOLUME_XZX',
        #options = {'ENUM_FLAG'},
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
eRotationStretchTo = (('PLANE_X', "XZ", "XZ", 1),
                      ('PLANE_Z', "ZX", "ZX", 2),
                      ('SWING_Y', "Swing", "Swing", 4),)

class EnumRotationStretchTo(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumRotationStretchTo'
    bl_label = "Rotation"

    default_value: bpy.props.EnumProperty(
        items=eRotationStretchTo,
        name="Rotation",
        description="Rotation",
        default = 'PLANE_X',
        #options = {'ENUM_FLAG'},
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

# Track-To
eTrackAxis = (('TRACK_X', "X", "X", 1),
               ('TRACK_Y', "Y", "Y", 2),
               ('TRACK_Z', "Z", "Z", 4),
               ('TRACK_NEGATIVE_X', "-X", "-X", 8),
               ('TRACK_NEGATIVE_Y', "-Y", "-Y", 16),
               ('TRACK_NEGATIVE_Z', "-Z", "-Z", 32,))

eUpAxis = (('UP_X', "X", "X", 1),
           ('UP_Y', "Y", "Y", 2),
           ('UP_Z', "Z", "Z", 4),)
# ugly but I can't change it easily without messing up versioning

class EnumTrackAxis(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumTrackAxis'
    bl_label = "Track Axis"

    default_value: bpy.props.EnumProperty(
        items=eTrackAxis,
        name="Track Axis",
        description="Track Axis",
        default = 'TRACK_X',
        #options = {'ENUM_FLAG'},
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

class EnumUpAxis(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumUpAxis'
    bl_label = "Up Axis"

    default_value: bpy.props.EnumProperty(
        items=eUpAxis,
        name="Up Axis",
        description="Up Axis",
        default = 'UP_X',
        #options = {'ENUM_FLAG'},
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

# Follow Track Forward axis
eForwardAxis = (('FORWARD_X',        "X",  "X",  0),
                ('FORWARD_Y',        "Y",  "Y",  1),
                ('FORWARD_Z',        "Z",  "Z",  2),
                ('TRACK_NEGATIVE_X', "-X", "-X", 3),
                ('TRACK_NEGATIVE_Y', "-Y", "-Y", 4),
                ('TRACK_NEGATIVE_Z', "-Z", "-Z", 5),)

class EnumFollowPathForwardAxis(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumFollowPathForwardAxis'
    bl_label = "Forward Axis"

    default_value: bpy.props.EnumProperty(
        items=eForwardAxis,
        name="Forward Axis",
        description="Forward Axis",
        default = 'FORWARD_X',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

# Follow Track Forward axis
eFloorAxis =   (('FLOOR_X',        "X",  "X",  0),
                ('FLOOR_Y',        "Y",  "Y",  1),
                ('FLOOR_Z',        "Z",  "Z",  2),
                ('FLOOR_NEGATIVE_X', "-X", "-X", 3),
                ('FLOOR_NEGATIVE_Y', "-Y", "-Y", 4),
                ('FLOOR_NEGATIVE_Z', "-Z", "-Z", 5),)

class EnumFloorAxis(MantisSocket):
    '''Floor Constraint Axis'''
    bl_idname = 'EnumFloorAxis'
    bl_label = "Floor Axis"

    default_value: bpy.props.EnumProperty(
        items=eFloorAxis,
        name="Floor Axis",
        description="Floor Axis",
        default = 'FLOOR_X',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

# Locked Track
eLockAxis = (('LOCK_X', "X", "X", 1),
             ('LOCK_Y', "Y", "Y", 2),
             ('LOCK_Z', "Z", "Z", 4),)

class EnumLockAxis(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumLockAxis'
    bl_label = "Lock Axis"

    default_value: bpy.props.EnumProperty(
        items=eLockAxis,
        name="Lock Axis",
        description="Lock Axis",
        default = 'LOCK_X',
        #options = {'ENUM_FLAG'},
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

# Limit Distance:
eLimitMode = (('LIMITDIST_INSIDE', "Inside", "Inside",),
              ('LIMITDIST_OUTSIDE', "Outside", "Outside",),
              ('LIMITDIST_ONSURFACE', "On Surface", "On Surface",),)

class EnumLimitMode(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumLimitMode'
    bl_label = "Clamp Region"

    default_value: bpy.props.EnumProperty(
        items=eLimitMode,
        name="Clamp Region",
        description="Clamp Region",
        default = 'LIMITDIST_INSIDE',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

# Spline IK
eYScaleMode = (('NONE', "None", "Don’t scale the X and Z axes.",),
              ('FIT_CURVE', "Fit Curve", "Scale the bones to fit the entire length of the curve.",),
              ('BONE_ORIGINAL', "Bone Original", "Use the original scaling of the bones.",),)

eXZScaleMode = (('NONE', "None", "Don’t scale the X and Z axes.",),
                ('BONE_ORIGINAL', "Bone Original", "Use the original scaling of the bones.",),
                ('INVERSE_PRESERVE', "Inverse Scale", "Scale of the X and Z axes is the inverse of the Y-Scale.",),
                ('VOLUME_PRESERVE', "Volume Preservation", "Scale of the X and Z axes are adjusted to preserve the volume of the bones.",),)

class EnumYScaleMode(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumYScaleMode'
    bl_label = "Y Scale Mode"

    default_value: bpy.props.EnumProperty(
        items=eYScaleMode,
        name="Y Scale Mode",
        description="Y Scale Mode",
        default = 'FIT_CURVE',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

class EnumXZScaleMode(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumXZScaleMode'
    bl_label = "XZ Scale Mode"

    default_value: bpy.props.EnumProperty(
        items=eXZScaleMode,
        name="XZ Scale Mode",
        description="XZ Scale Mode",
        default = 'NONE',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

eMapxForm = (('LOCATION', "Location", "Location",),
             ('ROTATION', "Rotation", "Rotation",),
             ('SCALE', "Scale", "Scale",),)


eRotationMode = (('AUTO', 'Auto', 'Automattically Selected.', 0),
                 ('XYZ', "XYZ", "Euler using the XYZ rotation order", 1),
                 ('XZY', "XZY", "Euler using the XZY rotation order", 2),
                 ('ZXY', "ZXY", "Euler using the ZXY rotation order", 3),
                 ('ZYX', "ZYX", "Euler using the ZYX rotation order", 4),
                 ('YXZ', "YXZ", "Euler using the YXZ rotation order", 5),
                 ('YZX', "YZX", "Euler using the YZX rotation order", 6),
                 ('QUATERNION', "Quaternion", "Quaternion", 7),
                 ('SWING_TWIST_X', 'Swing and X Twist.', 'Decompose into a swing rotation to aim the X axis, followed by twist around it.',  8),
                 ('SWING_TWIST_Y', 'Swing and Y Twist.', 'Decompose into a swing rotation to aim the Y axis, followed by twist around it.',  9),
                 ('SWING_TWIST_Z', 'Swing and Z Twist.', 'Decompose into a swing rotation to aim the Z axis, followed by twist around it.', 10),)

enumTransformationRotationOrder = enumRotationOrder[:6]


eTranslationMix =(
        ('ADD', "Add", "", 0),
        ('REPLACE', "Replace", "", 1),
    )

eScaleMix =(
        ('MULTIPLY', "Multiply", "", 0),
        ('REPLACE', "Replace", "", 1),
    )


class EnumTransformationMap(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumTransformationMap'
    bl_label = "Map To/From"

    default_value: bpy.props.EnumProperty(
        items=eMapxForm,
        name="Map To/From",
        description="Map To/From",
        default = 'LOCATION',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

class EnumTransformationRotationMode(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumTransformationRotationMode'
    bl_label = "Map To/From"

    default_value: bpy.props.EnumProperty(
        items=eRotationMode,
        name="Rotation Mode",
        description="Rotation Mode",
        default = 'AUTO',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class EnumTransformationRotationOrder(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumTransformationRotationOrder'
    bl_label = "Map To/From"

    default_value: bpy.props.EnumProperty(
        items=enumTransformationRotationOrder,
        name="Rotation Order",
        description="Rotation Order",
        default = 'AUTO',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class EnumTransformationTranslationMixMode(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumTransformationTranslationMixMode'
    bl_label = "Mix Mode"

    default_value: bpy.props.EnumProperty(
        items=eTranslationMix,
        name="Mix Translation",
        description="Mix Translation",
        default = 'ADD',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class EnumTransformationRotationMixMode(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumTransformationRotationMixMode'
    bl_label = "Mix Mode"

    default_value: bpy.props.EnumProperty(
        items=eRotationMix,
        name="Mix Rotation",
        description="Mix Rotation",
        default = 'ADD',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class EnumTransformationScaleMixMode(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumTransformationScaleMixMode'
    bl_label = "Mix Mode"

    default_value: bpy.props.EnumProperty(
        items=eScaleMix,
        name="Mix Scale",
        description="Mix Scale",
        default = 'REPLACE',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

eAxes = (
        ('X', "X", "X", 0),
        ('Y', "Y", "Y", 1),
        ('Z', "Z", "Z", 2),
    )

class EnumTransformationAxes(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumTransformationAxes'
    bl_label = "Axes"

    default_value: bpy.props.EnumProperty(
        items=eAxes,
        # name="",
        # description="",
        default = 'X',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

#

eBBoneHandleType = (
        ('AUTO', "Automatic", "", 0),
        ('ABSOLUTE', "Absolute", "", 1),
        ('RELATIVE', "Relative", "", 2),
        ('TANGENT', "Tangent", "", 3),
    )

class EnumBBoneHandleType(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumBBoneHandleType'
    bl_label = "Axes"

    default_value: bpy.props.EnumProperty(
        items=eBBoneHandleType,
        # name="",
        # description="",
        default = 'AUTO',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

eShrinkwrapType = (
        ('NEAREST_SURFACE', "Nearest Surface Point",
                     "Shrink the location to the nearest target surface.", 0),
        ('PROJECT', "Project", "Shrink the location to the nearest target "
                     "surface along a given axis.", 1),
        ('NEAREST_VERTEX', "Nearest Vertex", "Shrink the location to the"
                     " nearest target vertex.", 2),
        ('TARGET_PROJECT', "Target Normal Project", "Shrink the location to the"
                     " nearest target surface along the interpolated vertex"
                     " normals of the target.", 3),
    )

class EnumShrinkwrapTypeSocket(MantisSocket):
    '''Shrinkwrap Type Socket'''
    bl_idname = 'EnumShrinkwrapTypeSocket'
    bl_label = "Shrinkwrap Type"
    default_value: bpy.props.EnumProperty(
        items=eShrinkwrapType,
        description="Select type of shrinkwrap algorithm for target position",
        default = 'TARGET_PROJECT',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


eShrinkwrapFaceCull = (
        ('OFF', "Off", "No Culling.", 0),
        ('FRONT', "Front", "No projection when in front of the face.", 1),
        ('BACK', "Back", "No projection when behind the face.", 2),
    )

class EnumShrinkwrapFaceCullSocket(MantisSocket):
    '''Shrinkwrap Face Cull method Socket'''
    bl_idname = 'EnumShrinkwrapFaceCullSocket'
    bl_label = "Shrinkwrap Type"
    default_value: bpy.props.EnumProperty(
        items=eShrinkwrapFaceCull,
        description="Stop vertices from projecting to a face on the target"
                    " when facing towards/away",
        default = 'OFF',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

eShrinkwrapProjectAxis = (
        ('POS_X', "+X", "", 0),
        ('POS_Y', "+Y", "", 1),
        ('POS_Z', "+Z", "", 2),
        ('NEG_X', "-X", "", 3),
        ('NEG_Y', "-Y", "", 4),
        ('NEG_Z', "-Z", "", 5), )

class EnumShrinkwrapProjectAxisSocket(MantisSocket):
    '''Shrinkwrap Projection Axis Socket'''
    bl_idname = 'EnumShrinkwrapProjectAxisSocket'
    bl_label = "Shrinkwrap Projection Axis"
    default_value: bpy.props.EnumProperty(
        items=eShrinkwrapProjectAxis,
        description="Axis constrain to",
        default = 'POS_X',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

eShrinkwrapMode = (
        ('ON_SURFACE', "On Surface", "The point is constrained to the surface"
                       " of the target object, with distance offset towards the"
                       " original point location.", 0),
        ('INSIDE', "Inside", "The point is constrained to be inside the target"
                   " object", 1),
        ('OUTSIDE', "Outside", "The point is constrained to be outside the "
                   "target object.", 2),
        ('OUTSIDE_SURFACE', "Outside Surface", "The point is constrained to the"
                            " surface of the target object, with distance"
                            " offset always to the outside, towards or away"
                            " from the original location.", 3),
        ('ABOVE_SURFACE', "Above Surface", "The point is constrained to the"
                          " surface of the target object, with distance offset "
                          "applied exactly along the target normal.", 4), )

class EnumShrinkwrapModeSocket(MantisSocket):
    '''Shrinkwrap Mode Socket'''
    bl_idname = 'EnumShrinkwrapModeSocket'
    bl_label = "Shrinkwrap Mode"
    default_value: bpy.props.EnumProperty(
        items=eShrinkwrapMode,
        description="Select how to constrain the object to the target surface",
        default = 'ON_SURFACE',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


eDataTypeMode = (
       ('VECTOR', "Vector", "Vector", 0), 
       ('QUATERNION', "Quaternion", "", 1), 
       ('FLOAT4X4', "4x4 Matrix", "", 2), )

class EnumGeometryAttributeDataTypeSocket(MantisSocket):
    '''Shrinkwrap Mode Socket'''
    bl_idname = 'EnumGeometryAttributeDataTypeSocket'
    bl_label = "Datatype"
    default_value: bpy.props.EnumProperty(
        items=eDataTypeMode,
        description="Select the data type of the attribute",
        default = 'VECTOR',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

eDomaineMode = (
    ('POINT', "Point", "Point", 0), 
    ('EDGE', "Edge", "Edge", 1), 
    ('FACE', "Face", "Face", 2), 
    ('FACE_CORNER', "Face Corner", "Face Corner", 3), 
    ('SPLINE', "Spline", "Spline", 4), 
    ('INSTANCE', "Instance", "Instance", 5), )

class EnumGeometryAttributeDomainSocket(MantisSocket):
    '''Shrinkwrap Mode Socket'''
    bl_idname = 'EnumGeometryAttributeDomainSocket'
    bl_label = "Domain"
    default_value: bpy.props.EnumProperty(
        items=eDomaineMode,
        description="Select the data type of the attribute",
        default = 'POINT',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

eMix_geometryattribute =(
        ('REPLACE', "Replace (Aligned)", "Fully inherit scale"),
        ('BEFORE_SPLIT', "Before (Split Channels)", "Fully inherit scale"),
        ('AFTER_SPLIT', "After (Split Channels)", "Fully inherit scale"),
        ('BEFORE_FULL', "Before (Full)", "Fully inherit scale"),
        ('AFTER_FULL', "After (Full)", "Fully inherit scale"),)

class EnumMixModeGeometryAttribute(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumMixModeGeometryAttribute'
    bl_label = "Rotation Mix"

    default_value: bpy.props.EnumProperty(
        items=eMix_geometryattribute,
        name="Mix Mode",
        description="Mix mode",
        default = 'REPLACE', #{'REPLACE'},
        #options = {'ENUM_FLAG'}, # this sux
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

eSkinningMethod = (('EXISTING_GROUPS', "Use Existing Groups", "Use the existing vertex groups, or create empty groups if not found.",),
                   ('AUTOMATIC_HEAT', "Automatic (Heat)", "Use Blender's heatmap automatic skinning",),
                   ('COPY_FROM_OBJECT', "Copy from object", "Copy skin weights from the selected object"),)

class EnumSkinning(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumSkinning'
    bl_label = "Skinning Method"
    default_value: bpy.props.EnumProperty(
        items=eSkinningMethod,
        name="Skinning Method",
        description="Skinning Method",
        default = 'AUTOMATIC_HEAT',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)


class MorphTargetSocket(MantisSocket):
    """Morph Target"""
    bl_idname = 'MorphTargetSocket'
    bl_label = "Morph Target"

    color_simple = cShapeKey
    color : bpy.props.FloatVectorProperty(default=cShapeKey, size=4)
    input : bpy.props.BoolProperty(default =False,)
    is_valid_interface_type=True

eDriverVariableType = (
                        ( 'SINGLE_PROP',
                          "Property",
                          "Property",
                          1),
                        ( 'LOC_DIFF',
                          "Distance",
                          "Distance",
                          2),
                       ( 'ROTATION_DIFF',
                         "Rotational Difference",
                         "Rotational Difference",
                         3),
                    #    ( 'TRANSFORMS',
                    #      "Transform Channel",
                    #      "Transform Channel",
                    #      4),
                      )

class EnumDriverVariableType(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumDriverVariableType'
    bl_label = "Variable Type"

    default_value: bpy.props.EnumProperty(
        items = eDriverVariableType,
        name = "Variable Type",
        description = "Variable Type",
        default = 'SINGLE_PROP',
        update = driver_variable_socket_update,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


eDriverVariableEvaluationSpace = (
                        ( 'WORLD_SPACE',
                          "World",
                          "World",
                          1),

                        ( 'TRANSFORM_SPACE',
                          "Transform",
                          "Transform",
                          2),
                        ( 'LOCAL_SPACE',
                          "Local",
                          "Local",
                          3),
                      )

class EnumDriverVariableEvaluationSpace(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumDriverVariableEvaluationSpace'
    bl_label = "Evaluation Space"

    default_value: bpy.props.EnumProperty(
        items = eDriverVariableEvaluationSpace,
        name = "Evaluation Space",
        description = "Evaluation Space",
        default = 'WORLD_SPACE',
        update = driver_variable_socket_update,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

eDriverVariableTransformChannel = (
                ("LOC_X", "X Location", "The X-coordinate of an object's location.", 1),
                ("LOC_Y", "Y Location", "The Y-coordinate of an object's location.", 2),
                ("LOC_Z", "Z Location", "The Z-coordinate of an object's location.", 3),
                ("ROT_X", "X Rotation", "Rotation X-axis.", 4),
                ("ROT_Y", "Y Rotation", "Rotation Y-axis.", 5),
                ("ROT_Z", "Z Rotation", "Rotation Z-axis.", 6),
                ("ROT_W", "W Rotation", "Rotation W-axis.", 7),
                ("SCALE_X", "X Scale", "The X-scale of an object's scale.", 8),
                ("SCALE_Y", "Y Scale", "The Y-scale of an object's scale.", 9),
                ("SCALE_Z", "Z Scale", "The Z-scale of an object's scale.", 10),
                ("SCALE_AVG", "Average Scale", "The scale factor of an object's scale.", 11),
                )

class EnumDriverVariableTransformChannel(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumDriverVariableTransformChannel'
    bl_label = "Transform Channel"

    default_value: bpy.props.EnumProperty(
        items = eDriverVariableTransformChannel,
        name = "Transform Channel",
        description = "Transform Channel",
        default = 'LOC_X',
        update = driver_variable_socket_update,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class EnumDriverRotationMode(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumDriverRotationMode'
    bl_label  = "Rotaton Mode"

    default_value: bpy.props.EnumProperty(
        items = eRotationMode,
        name = "Rotation Mode",
        description = "Rotation Mode",
        default = 'AUTO',
        update = driver_variable_socket_update,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple
#


eDriverType = (('AVERAGE', 'Average', 'Average', 0),
               ('SUM', "Sum", "Sum", 1),
               ('SCRIPTED', "Scripted", "Scripted Expression", 2),
               ('MIN', "Min", "Minimum", 3),
               ('MAX', "Max", "Maximum", 4),)

class EnumDriverType(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumDriverType'
    bl_label  = "Driver Type"

    default_value: bpy.props.EnumProperty(
        items = eDriverType,
        name = "Driver Type",
        description = "Driver Type",
        default = 'AVERAGE',
        update = driver_socket_update,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


# Keyframe

# Enum for kf handle type
# enum for interpolation type
# eventually gonna make it to the fancy stuff

class FloatSocket(MantisSocketOverlayEnabled):
    """Float Input socket"""
    bl_idname = 'FloatSocket'
    bl_label = "Float"
    is_valid_interface_type=True
    default_value : bpy.props.FloatProperty(default = 0.0, update = update_socket,)
    color_simple = cFloat
    color : bpy.props.FloatVectorProperty(default=cFloat, size=4)
    input : bpy.props.BoolProperty(default =False,)

class FloatPositiveSocket(MantisSocketOverlayEnabled):
    """Float Input socket"""
    bl_idname = 'FloatPositiveSocket'
    bl_label = "Float (Positive)"
    is_valid_interface_type=True
    default_value : bpy.props.FloatProperty(default = 0.0, min=0, update = update_socket,)
    color_simple = cFloat
    color : bpy.props.FloatVectorProperty(default=cFloat, size=4)
    input : bpy.props.BoolProperty(default =False,)

class FloatFactorSocket(MantisSocketOverlayEnabled):
    '''xFrom Input Output'''
    bl_idname = 'FloatFactorSocket'
    bl_label = "Float (Factor)"
    is_valid_interface_type=True
    default_value : bpy.props.FloatProperty(
        default = 0.0,
        min = 0.0,
        max=1.0,
        update = update_socket,
        subtype='FACTOR',)
    color_simple = cFloat
    color : bpy.props.FloatVectorProperty(default=cFloat, size=4)
    input : bpy.props.BoolProperty(default =False,)

class FloatAngleSocket(MantisSocketOverlayEnabled):
    '''xFrom Input Output'''
    bl_idname = 'FloatAngleSocket'
    bl_label = "Float (Angle)"
    is_valid_interface_type=True
    default_value : bpy.props.FloatProperty(
        default = 0.0,
        min = -180,
        max=180,
        update = update_socket,
        subtype='ANGLE',)
    color_simple = cFloat
    color : bpy.props.FloatVectorProperty(default=cFloat, size=4)
    input : bpy.props.BoolProperty(default =False,)

class VectorSocket(MantisSocket):
    """Vector Input socket"""
    bl_idname = 'VectorSocket'
    bl_label = "Vector"
    is_valid_interface_type=True
    default_value : bpy.props.FloatVectorProperty(
        default = (0.0, 0.0, 0.0),
        update = update_socket,)
    color_simple = cVector
    color : bpy.props.FloatVectorProperty(default=cVector, size=4)
    input : bpy.props.BoolProperty(default =False,)

class VectorEulerSocket(MantisSocket):
    """Vector Input socket"""
    bl_idname = 'VectorEulerSocket'
    bl_label = "Euler"
    is_valid_interface_type=True
    default_value : bpy.props.FloatVectorProperty(
        default = (0.0, 0.0, 0.0),
        update = update_socket,
        subtype='EULER',)
    color_simple = cVector
    color : bpy.props.FloatVectorProperty(default=cVector, size=4)
    input : bpy.props.BoolProperty(default =False,)

class VectorTranslationSocket(MantisSocket):
    """Vector Input socket"""
    bl_idname = 'VectorTranslationSocket'
    bl_label = "Vector (Translation)"

    default_value : bpy.props.FloatVectorProperty(
        default = (0.0, 0.0, 0.0),
        update = update_socket,
        subtype='TRANSLATION',)
    color_simple = cVector
    color : bpy.props.FloatVectorProperty(default=cVector, size=4)
    input : bpy.props.BoolProperty(default =False,)

class VectorScaleSocket(MantisSocket):
    """Vector Input socket"""
    bl_idname = 'VectorScaleSocket'
    bl_label = "Vector (Scale)"

    default_value : bpy.props.FloatVectorProperty(
        default = (1.0, 1.0, 1.0),
        update = update_socket,
        subtype='XYZ',)
    color_simple = cVector
    color : bpy.props.FloatVectorProperty(default=cVector, size=4)
    input : bpy.props.BoolProperty(default =False,)

class KeyframeSocket(MantisSocket):
    '''Keyframe'''
    bl_idname = 'KeyframeSocket'
    bl_label = "Keyframe"
    is_valid_interface_type=True
    color_simple = cKeyframe
    color : bpy.props.FloatVectorProperty(default=cKeyframe, size=4)
    input : bpy.props.BoolProperty(default =False, update = update_socket)
    def init(self):
        self.display_shape = 'CIRCLE_DOT'

EnumKeyframeInterpolationType = (('CONSTANT', 'Stepped', 'Stepped'),
                                 ('LINEAR', "Linear", "Linear"),
                                 ('BEZIER', "Bezier", "Bezier"),)


class EnumKeyframeInterpolationTypeSocket(MantisSocket):
    '''Keyframe Interpolation Type'''
    bl_idname = 'EnumKeyframeInterpolationTypeSocket'
    bl_label = "Keyframe Interpolation Type"

    default_value :bpy.props.EnumProperty(
        name="",
        description="Interpolation",
        items=EnumKeyframeInterpolationType,
        default='LINEAR',
        update = update_socket,)

    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False, update = update_socket)


EnumKeyframeBezierHandleType = (('FREE', 'Free', 'Completely independent manually set handle.'),
                                ('ALIGNED', "Aligned", "Manually set handle with rotation locked together with its pair."),
                                ('VECTOR', "Vector", "Automatic handles that create straight lines."),
                                ('AUTO', "Automatic", "Automatic handles that create smooth curves."),
                                ('AUTO_CLAMPED', "Auto Clamped", "Automatic handles that create smooth curves which only change direction at keyframes."),)

class EnumKeyframeBezierHandleTypeSocket(MantisSocket):
    '''Keyframe Bezier Handle Type'''
    bl_idname = 'EnumKeyframeBezierHandleTypeSocket'
    bl_label = "Keyframe Bezier Handle Type"
    default_value :bpy.props.EnumProperty(
        name="",
        description="Handle Type",
        items=EnumKeyframeBezierHandleType,
        default='AUTO_CLAMPED',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False, update = update_socket)


enumExtrapolationMode = (('CONSTANT', 'Constant', 'Constant'),
                         ('LINEAR', "Linear", "Linear"),)

class eFCrvExtrapolationMode(MantisSocket):
    '''FCurve Extrapolation Mode'''
    bl_idname = 'eFCrvExtrapolationMode'
    bl_label = "Extrapolation Mode"

    default_value :bpy.props.EnumProperty(
        name="",
        description="Handle Type",
        items=enumExtrapolationMode,
        default='CONSTANT',
        update = update_socket,)

    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False, update = update_socket)

EnumLatticeInterpolationType = (('KEY_LINEAR',   'Linear', 'Linear Interpolation.'),
                                ('KEY_CARDINAL', "Cardinal", "Cardinal Interpolation."),
                                ('KEY_CATMULL_ROM', "Catmull Rom", "Catmull Rom Interpolation."),
                                ('KEY_BSPLINE', "B-Spline", "B Spline Interpolation."),)


class EnumLatticeInterpolationTypeSocket(MantisSocket):
    '''Lattice Interpolation Type'''
    bl_idname = 'EnumLatticeInterpolationTypeSocket'
    bl_label = "Lattice Interpolation Type"

    default_value :bpy.props.EnumProperty(
        name="",
        description="Interpolation Type",
        items=EnumLatticeInterpolationType,
        default='KEY_BSPLINE',
        update = update_socket,)

    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False, update = update_socket)

EnumCorrectiveSmoothType = (('SIMPLE',   'Simple', 'Use the average of adjacent edge-vertices.'),
                            ('LENGTH_WEIGHTED', "Length Weight", "Use the average of adjacent"
                                                      "edge-vertices weighted by their length."),)
class EnumCorrectiveSmoothTypeSocket(MantisSocket):
    '''Lattice Interpolation Type'''
    bl_idname = 'EnumCorrectiveSmoothTypeSocket'
    bl_label = "Lattice Interpolation Type"

    default_value :bpy.props.EnumProperty(
        name="",
        description="Interpolation Type",
        items=EnumCorrectiveSmoothType,
        default='SIMPLE',
        update = update_socket,)

    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False, update = update_socket)

enumArmatureDisplayType =( ('OCTAHEDRAL', "Octahedral", "Octahedral"),
                           ('STICK', "Stick", "Stick"),
                           ('BBONE', "BBone", "BBone"),
                           ('ENVELOPE', "Envelope", "Envelope"),
                           ('WIRE', "Wire", "Wire"),)

class EnumArmatureDisplayType(MantisSocket):
    """Float Math Operation"""
    bl_idname = 'EnumArmatureDisplayType'
    bl_label = "Operation"
    default_value :bpy.props.EnumProperty(
        name="",
        description="Display Type",
        items=enumArmatureDisplayType,
        default='OCTAHEDRAL',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

enumDisplayType =(('ARMATURE_DEFINED', 'Auto', 'Auto'),
                  ('OCTAHEDRAL', "Octahedral", "Octahedral"),
                  ('STICK', "Stick", "Stick"),
                  ('BBONE', "BBone", "BBone"),
                  ('ENVELOPE', "Envelope", "Envelope"),
                  ('WIRE', "Wire", "Wire"),)

class EnumDisplayType(MantisSocket):
    """Float Math Operation"""
    bl_idname = 'EnumDisplayType'
    bl_label = "Operation"
    default_value :bpy.props.EnumProperty(
        name="",
        description="Display Type",
        items=enumDisplayType,
        default='ARMATURE_DEFINED',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text, use_enum=False)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

enumFloatOperations = (('ADD', 'Add', 'Add'),
                      ('SUBTRACT', "Subtract", "Subtract"),
                      ('MULTIPLY', "Multiply", "Multiply"),
                      ('DIVIDE', "Divide", "Divide"),
                      ('POWER', "Power", "Power"),
                      ('FLOOR_DIVIDE', "Floor Divide", "Floor Divide"),
                      ('MODULUS', "Modulus", "Modulus"),
                      ('ABSOLUTE', "Absolute", "Absolute Value"),
                      ('MAXIMUM', "Maximum", "Maximum"),
                      ('MINIMUM', "Minimum", "Minimum"),
                      ('GREATER THAN', "Greater Than", "Greater Than"),
                      ('LESS THAN', "Less Than", "Less Than"),
                      ('ARCTAN2', "atan2", "2-argument arctan function"),
                      ('FLOOR', "Floor", "the nearest integer lower than input A"),
                      ('CEIL', "Ceiling", "the next integer higher than input A"),
                      ('ROUND', "Round", "Round to the nearest integer"),)

class MathFloatOperation(MantisSocket):
    """Float Math Operation"""
    bl_idname = 'MathFloatOperation'
    bl_label = "Operation"
    default_value :bpy.props.EnumProperty(
        name="",
        description="Operation",
        items=enumFloatOperations,
        default='MULTIPLY',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)


enumVectorOperations = (('ADD', 'Add', 'Add (Component-wise)'),
                        ('SUBTRACT', "Subtract", "Subtract (Component-wise)"),
                        ('MULTIPLY', "Multiply", "Multiply (Component-wise)"),
                        ('SCALE', "Scale", "Scales vector by input float or average magnitude of input vector's components."),
                        ('DIVIDE', "Divide", "Divide (Component-wise)"),
                        ('POWER', "Power", "Power (Component-wise)"),
                        ('LENGTH', "Length", "Length"),
                        ('CROSS', "Cross Product", "Cross product of A X B"),
                        ('NORMALIZE', "Normalize", "Returns a normalized vector."),
                        ('DOT', "Dot Product", "Dot product of A . B"),
                        ('LINEAR_INTERP', "Linear Interpolation", "Linear Interpolation between vectors A and B by factor"))



class MathVectorOperation(MantisSocket):
    """Vector Math Operation"""
    bl_idname = 'MathVectorOperation'
    bl_label = "Operation"
    default_value :bpy.props.EnumProperty(
        name="",
        description="Operation",
        items=enumVectorOperations,
        default='MULTIPLY',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)


enumMatrixTransform  = (('TRANSLATE', 'Translate', 'Translate'),
                        ('ROTATE_AXIS_ANGLE', "Rotate (Axis-angle)", "Rotates a number of radians around an axis"),
                        # ('ROTATE_EULER', "Rotate (Euler)", "Euler Rotation"),
                        # ('ROTATE_QUATERNION', "Rotate (Quaternion)", "Quaternion Rotation"),
                        ('SCALE', "Scale", "Scale"),)



class MatrixTransformOperation(MantisSocket):
    """Matrix Transform Operation"""
    bl_idname = 'MatrixTransformOperation'
    bl_label = "Operation"
    default_value :bpy.props.EnumProperty(
        name="",
        description="Operation",
        items=enumMatrixTransform,
        default='TRANSLATE',
        update = update_socket,)
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

enumIntOperations =  (('ADD', 'Add', 'Add'),
                      ('SUBTRACT', "Subtract", "Subtract"),
                      ('MULTIPLY', "Multiply", "Multiply"),
                      ('FLOOR_DIVIDE', "Floor Divide", "Floor Divide"),
                      ('POWER', "Power", "Power"),
                      ('MODULUS', "Modulus", "Modulus"),
                      ('ABSOLUTE', "Absolute", "Absolute Value"),
                      ('MAXIMUM', "Maximum", "Maximum"),
                      ('MINIMUM', "Minimum", "Minimum"),
                      ('GREATER THAN', "Greater Than", "Greater Than"),
                      ('LESS THAN', "Less Than", "Less Than"),)

class MathIntOperation(MantisSocket):
    """Int Math Operation"""
    bl_idname = 'MathIntOperation'
    bl_label = "Operation"

    default_value :bpy.props.EnumProperty(
        name="",
        description="Operation",
        items=enumIntOperations,
        default='MULTIPLY',
        update = update_socket,)

    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

enumCompareOperations =  (('EQUAL', "Equal", "Equal"),
                          ('NOT_EQUAL', "Not Equal", "Not Equal"),
                          ('GREATER_THAN', "Greater Than", "Greater Than"),
                          ('GREATER_THAN_EQUAL', "Greater Than or Equal", "Greater Than or Equal"),
                          ('LESS_THAN', "Less Than", "Less Than"),
                          ('LESS_THAN_EQUAL', "Equal or Less Than", "Equal or Less Than"),)

class EnumCompareOperation(MantisSocket):
    """Compare Operation"""
    bl_idname = 'EnumCompareOperation'
    bl_label = "Comparison"
    default_value :bpy.props.EnumProperty(
        name="",
        description="Comparison",
        items=enumCompareOperations,
        default='EQUAL',
        update = update_socket,)
    enum_display_type = 'DROPDOWN'
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

class EnumMatrixFromCurveMode(MantisSocket):
    """Matrix From Curve Mode"""
    bl_idname = 'EnumMatrixFromCurveMode'
    bl_label = "Mode"
    enum_display_type='DROPDOWN'
    default_value :bpy.props.EnumProperty(
        name="",
        description="Mode",
        items=eMatrixFromCurveModes,
        default='DIVISIONS',
        update = update_socket,)

    color_simple = cString
    enum_display_type = 'DROPDOWN'
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

class EnumComposeMatrixModes(MantisSocket):
    """Compose Matrix Mode"""
    bl_idname = 'EnumComposeMatrixModes'
    bl_label = "Mode"
    enum_display_type='DROPDOWN'
    default_value :bpy.props.EnumProperty(
        name="",
        description="Mode",
        items=eMatrixComposeModes,
        default='BASIS',
        update = update_socket,)

    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)

class WildcardSocket(MantisSocket):
    """Some kind of node socket lol I donno"""
    bl_idname = 'WildcardSocket'
    bl_label = ""

    color_simple = (0.0,0.0,0.0,0.0)
    color : bpy.props.FloatVectorProperty(default=(0.0,0.0,0.0,0.0), size=4)
    input : bpy.props.BoolProperty(default =False,)
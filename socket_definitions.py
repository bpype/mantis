import bpy
from bpy.types import NodeSocket, NodeSocketStandard

# Classes which do not have default_value
# needed to detect when there is an error updating dynamic nodes
no_default_value= [
            'MantisSocket',
            'RelationshipSocket',
            'DeformerSocket',
            'xFormSocket',
            'GeometrySocket',
            'GenericRotationSocket',
            'FCurveSocket',
            'DriverSocket',
            'DriverVariableSocket',
            'xFormParameterSocket',
            'MorphTargetSocket',
            'KeyframeSocket',
            'WildcardSocket',
]
# the sockets that do not have this field do not transfer data.
# instead, it is the link itself which is meaningful.

class MantisSocket(NodeSocket):
    is_valid_interface_type=False
    

from .utilities import (prRed, prGreen, prPurple, prWhite,
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
             
             xFormParameterSocket,
             ParameterBoolSocket,
             ParameterIntSocket,
             ParameterFloatSocket,
             ParameterVectorSocket,
             ParameterStringSocket,
             
             TransformSpaceSocket,
             BooleanSocket,
             BooleanThreeTupleSocket,
             RotationOrderSocket,
             QuaternionSocket,
             QuaternionSocketAA,
             UnsignedIntSocket,
             IntSocket,
             StringSocket,

             EnumMetaRigSocket,
             EnumMetaBoneSocket,
             EnumCurveSocket,
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
             eFCrvExtrapolationMode,
             
             # Math
             MathFloatOperation,
             MathVectorOperation,
             MatrixTransformOperation,
             #conditions
             EnumCompareOperation,
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

# Was setting color like this:
# color : bpy.props.FloatVectorProperty(size = 4, default = cFCurve,)
# but this didn't work when Blender automatically generated interface classes?
# so changed it to color = cVariable
# but for color-changing sockets, if I make them, this won' work? Maybe?
#
# I actually think I was wrong about all of that lol
# TODO change it back, dingus

########################################################################
#  Update Callbacks
########################################################################


def socket_update(mantis_node, ui_socket, socket_name=None):
    node_updated = mantis_node.ui_modify_socket(ui_socket, socket_name)
    if not node_updated: # so that we can tag its dependencies
        mantis_node.reset_execution_recursive()
    return node_updated

def default_update(ui_socket, context, do_execute=True):
    context = bpy.context
    if not context.space_data:
        return
    if not hasattr(context.space_data, "path"):
        return
    try:
        node_tree = context.space_data.path[0].node_tree
    except IndexError: # not in the UI, for example, in a script instead.
        return
    if node_tree.is_executing or node_tree.is_exporting or not node_tree.do_live_update:
        return
    if hasattr(ui_socket.node, "initialized"):
        if not ui_socket.node.initialized: return
    elif hasattr(ui_socket.node, 'is_updating'):
        if ui_socket.node.is_updating: return
    else: return
    # if the socket has survived THAT ordeal, then the context is OK.
    # first, we try to update the Mantis tree in-situ.
    # Some nodes can update their b-objects, others will have to force-update the tree
    # because we just modified the data without modifying the topology of the graph.
    # finally, try and execute it if mantis couldn't update the b_objects itself.
    mantis_updated=True
    if (ui_socket.node.bl_idname in ["MantisNodeGroup", "MantisSchemaGroup"]):
        mantis_updated=False # this kind of socket can't be updated here (yet)
        node_tree.update_tree(context, force=True)
    elif hasattr(ui_socket, 'default_value'):
        # we may not have to regenerate the tree; try and update the socket
        from .utilities import tree_from_nc
        for mantis_node in node_tree.parsed_tree.values():
            if mantis_node.node_type in ['DUMMY', 'DUMMY_SCHEMA']:
                continue
            # check to see if the mantis node is in the same ui-tree as this ui_socket
            if mantis_node.ui_signature[-1] == ui_socket.node.name and \
                        tree_from_nc(mantis_node.ui_signature, node_tree) == ui_socket.node.id_data:
                from .misc_nodes import SimpleInputNode
                if isinstance(mantis_node, SimpleInputNode):
                    node_updated = socket_update(mantis_node, ui_socket)
                    for l in mantis_node.outputs[ui_socket.name].links:
                        print (l.to_node, l.to_socket)
                        node_updated = node_updated and socket_update(l.to_node, ui_socket, l.to_socket)
                        print (node_updated)
                else:
                    node_updated = socket_update(mantis_node, ui_socket)
                # execute the tree if even one node didn't update
                mantis_updated = node_updated and mantis_updated
        node_tree.update_tree(context)
    node_tree.display_update(context)
    if mantis_updated==False:
        try:
            prPurple(f"Executing tree after socket change: {ui_socket.node.name}:{ui_socket.name}")
            node_tree.execute_tree(context)
        except Exception as e:
            prRed("Automatic Tree Execution failed because of %s" % e)


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
        self.node.inputs["Meta-Bone"].search_prop = self.search_prop
    default_update(self,context)

def update_metarig_posebone(self, context,):
    self.node.pose_bone = self.default_value
    default_update(self,context)



########################################################################
#  Sockets
########################################################################


def ChooseDraw(self, context, layout, node, text, icon = "NONE", use_enum=True, nice_bool=True, icon_only=False):
    # return
    # TEXT ONLY
    if self.node.bl_idname in ["NodeGroupInput", "NodeGroupOutput"]:
        layout.label(text=text)
    elif hasattr(self, "display_text") and self.display_text and self.is_linked:
            layout.label(text=self.display_text)
    else:
        # ENUM VALUES (this is a HACK, fix it later)
        if ('Enum' in self.bl_idname) and (use_enum):
            if not (self.is_output or self.is_linked):
                layout.prop_tabs_enum(self, "default_value",)
            else:
                layout.label(text=text)
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
            layout.prop(self, "default_value", text=text, toggle=nice_bool, slider=True, icon=icon,)
        # CONNECTED sockets and outputs without input fields
        else:
            layout.label(text=text)

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple



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
    def TellValue(self):
        from mathutils import Matrix
        v = self.default_value
        return Matrix( ( ( v[ 0], v[ 1], v[ 2], v[ 3],),
                         ( v[ 4], v[ 5], v[ 6], v[ 7],),
                         ( v[ 8], v[ 9], v[10], v[11],),
                         ( v[12], v[13], v[14], v[15]), ) )
                         #NOTE, we're not using the last row
                         # so we're gonna use it to store data
                         # unused, unused, unused, bone_length
                         # but we're not going to make it
                         # available except by accessor functions
    # would like to make this stuff easier to deal with tho
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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class GeometrySocket(MantisSocket):
    '''Geometry Input Output'''
    bl_idname = 'GeometrySocket'
    bl_label = "Geometry"
    color_simple = cGeometry
    color : bpy.props.FloatVectorProperty(default=cGeometry, size=4)
    input : bpy.props.BoolProperty(default =False,)
    is_valid_interface_type=True
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class GenericRotationSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'GenericRotationSocket'
    bl_label = "Rotation"
    color = (0.0,0.0,0.0,0.0)
    input : bpy.props.BoolProperty(default =False,)
    


    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple



# transform_spaces
# transform_spaces_bone_object
# transform_spaces_object

# def get_transform_space_enum(self, context):
    # pass

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
    
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class BooleanSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'BooleanSocket'
    bl_label = "Boolean"
    default_value: bpy.props.BoolProperty(update = update_socket,)
    color_simple = cBool
    color : bpy.props.FloatVectorProperty(default=cBool, size=4)
    input : bpy.props.BoolProperty(default =False,)
    is_valid_interface_type=True
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple
    def TellValue(self):
        return (self.default_value[0], self.default_value[1], self.default_value[2])

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
    
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class IntSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'IntSocket'
    bl_label = "Integer"
    default_value: bpy.props.IntProperty(default=0, update = update_socket, soft_min=-256, soft_max=256)
    color_simple = cInt
    color : bpy.props.FloatVectorProperty(default=cInt, size=4)
    input : bpy.props.BoolProperty(default =False,)
    is_valid_interface_type=True
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class UnsignedIntSocket(MantisSocket):
    '''Unsigned Integer Socket'''
    bl_idname = 'UnsignedIntSocket'
    bl_label = "Unsigned Integer"
    default_value: bpy.props.IntProperty(default=0, update = update_socket, min=0, soft_max=256, max=2**13)
    color_simple = cInt
    color : bpy.props.FloatVectorProperty(default=cInt, size=4)
    input : bpy.props.BoolProperty(default =False,)
    is_valid_interface_type=True
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class StringSocket(bpy.types.NodeSocketString, MantisSocket):
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

class BoneCollectionSocket(MantisSocket):
    """Bone Collection socket"""
    bl_idname = 'BoneCollectionSocket'
    bl_label = "Bone Collection"
    default_value: bpy.props.StringProperty(default = "Collection", update = update_socket,)
    input : bpy.props.BoolProperty(default =False,)
    color_simple = cBoneCollection
    color : bpy.props.FloatVectorProperty(default=cBoneCollection, size=4)
    
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
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
    
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

#####################################################################################
# Parameters
#####################################################################################



class xFormParameterSocket(MantisSocket):
    '''xFrom Parameter'''
    bl_idname = 'xFormParameterSocket'
    bl_label = "sForm Parameter"
    color_simple = cxForm
    color : bpy.props.FloatVectorProperty(default=cxForm, size=4)
    input : bpy.props.BoolProperty(default =False,)
    
    
    def init(self):
        self.display_shape = 'CIRCLE_DOT'
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple
# what is this one again?


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
        # if True:
            # print (self.is_property_set("default_value"))
            # ui_data = self.id_properties_ui("default_value")
            # ui_data.update(
                # description=self.description,
                # default=0,) # for now
            # ui_data.update(
                # min = self.min,
                # max = self.max,
                # soft_min = self.soft_min,
                # soft_max = self.soft_max,)
                        
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple
        
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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple
        
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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple
        
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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


#####################################################################################
# Additional socket types, for special cases
#####################################################################################

from bpy.props import PointerProperty, StringProperty

def poll_is_armature(self, obj):
    return obj.type == "ARMATURE"
    
# def poll_is_armature(self, obj):
    # return obj.type == "ARMATURE"

class EnumMetaRigSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumMetaRigSocket'
    bl_label = "Meta Rig"
    
    
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
    
    color_simple = cString
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
    layout.prop_search(data=self, property="default_value", search_data=self.search_prop.data, search_property="bones", text=text, icon=icon, results_are_suggestions=True)
    
class EnumMetaBoneSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumMetaBoneSocket'
    bl_label = "Meta Bone"
    
    
    search_prop:PointerProperty(type=bpy.types.Object)
    bone:StringProperty()
    
    def populate_bones_list(self, context):
        # just gonna hardcode the value
        if (meta_rig := self.search_prop):
            retList = []
            armatures = []
            i = -1
            retList.append( ('NONE', '', '', 'NONE', i:=i+1 ) )
            for b in meta_rig.data.bones:
                retList.append( (b.name, b.name, "Bone to copy matrix from", "BONE_DATA", i:=i+1 ) )
            return(retList)
        return None

    # default_value : bpy.props.EnumProperty(
                 # items = populate_bones_list,
                 # name = "Meta Rig")
                 
    # def get_default_value(self):
    #     return self.search_prop.name
    
    default_value  : StringProperty(name = "", update=update_metarig_posebone)
                 
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    def draw(self, context, layout, node, text):
        if not (self.is_linked):
            if self.search_prop is None:
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
    
    
    
    
    


class BoolUpdateParentNode(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'BoolUpdateParentNode'
    bl_label = "Boolean"
    default_value: bpy.props.BoolProperty(default=False, update = update_parent_node)
    color_simple = cBool
    color : bpy.props.FloatVectorProperty(default=cBool, size=4)
    input : bpy.props.BoolProperty(default =False,)
    
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class IKChainLengthSocket(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'IKChainLengthSocket'
    bl_label = "IK Chain Length"
    default_value: bpy.props.IntProperty(default=0, update = ik_chain_length_update_socket, min = 0, max = 255)
    color_simple = cInt
    
    color : bpy.props.FloatVectorProperty(default=cInt, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

# Copy Rotation

eRotationMix =(
        ('REPLACE', "Replace", "Fully inherit scale", 0),
        ('BEFORE', "Before", "Fully inherit scale", 1),
        ('AFTER', "After", "Fully inherit scale", 2),
        ('ADD', "Add", "Fully inherit scale", 3),
        #todo, but i don't care much
    )
    
# TODO HACK
# I am trying to figure out how to do enum_flag as
#  mutually exclusive options
# but! I don't think it's possible
# I just like the UI for it :P
    
class EnumRotationMix(MantisSocket):
    '''Custom node socket type'''
    bl_idname = 'EnumRotationMix'
    bl_label = "Rotation Mix"
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
    
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


class MorphTargetSocket(MantisSocket):
    """Morph Target"""
    bl_idname = 'MorphTargetSocket'
    bl_label = "Morph Target"
    
    color_simple = cShapeKey
    color : bpy.props.FloatVectorProperty(default=cShapeKey, size=4)
    input : bpy.props.BoolProperty(default =False,)
    is_valid_interface_type=True
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple




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


class FloatSocket(bpy.types.NodeSocketFloat, MantisSocket):
    """Float Input socket"""
    bl_idname = 'FloatSocket'
    bl_label = "Float"
    is_valid_interface_type=True
    default_value : bpy.props.FloatProperty(default = 0.0, update = update_socket,)
    color_simple = cFloat
    color : bpy.props.FloatVectorProperty(default=cFloat, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple
        
class FloatPositiveSocket(bpy.types.NodeSocketFloat, MantisSocket):
    """Float Input socket"""
    bl_idname = 'FloatPositiveSocket'
    bl_label = "Float (Positive)"
    is_valid_interface_type=True
    default_value : bpy.props.FloatProperty(default = 0.0, min=0, update = update_socket,)
    color_simple = cFloat
    color : bpy.props.FloatVectorProperty(default=cFloat, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class FloatFactorSocket(bpy.types.NodeSocketFloatFactor, MantisSocket):
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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class FloatAngleSocket(bpy.types.NodeSocketFloatAngle, MantisSocket):
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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class VectorSocket(bpy.types.NodeSocketVectorEuler, MantisSocket):
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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class VectorEulerSocket(bpy.types.NodeSocketVectorEuler, MantisSocket):
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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class VectorTranslationSocket(bpy.types.NodeSocketVectorTranslation, MantisSocket):
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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class VectorScaleSocket(bpy.types.NodeSocketVectorXYZ, MantisSocket):
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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple







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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple




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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple



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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
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
                      ('ARCTAN2', "atan2", "2-argument arctan function"),)

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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple



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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple




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
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


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
    
    color_simple = cString
    color : bpy.props.FloatVectorProperty(default=cString, size=4)
    input : bpy.props.BoolProperty(default =False,)
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple

class WildcardSocket(MantisSocket):
    """Some kind of node socket lol I donno"""
    bl_idname = 'WildcardSocket'
    bl_label = ""
    
    color_simple = (0.0,0.0,0.0,0.0)
    color : bpy.props.FloatVectorProperty(default=(0.0,0.0,0.0,0.0), size=4)
    input : bpy.props.BoolProperty(default =False,)
        
    def draw(self, context, layout, node, text):
        ChooseDraw(self, context, layout, node, text)
    def draw_color(self, context, node):
        return self.color
    @classmethod
    def draw_color_simple(self):
        return self.color_simple


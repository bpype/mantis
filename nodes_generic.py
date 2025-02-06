import bpy
from bpy.types import Node
from .base_definitions import MantisNode


from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

def TellClasses():
    return [ InputFloatNode,
             InputIntNode,
             InputVectorNode,
             InputBooleanNode,
             InputBooleanThreeTupleNode,
             InputRotationOrderNode,
             InputTransformSpaceNode,
             InputStringNode,
             InputQuaternionNode,
             InputQuaternionNodeAA,
             InputMatrixNode,
             InputLayerMaskNode,
             # InputGeometryNode,
             InputExistingGeometryObjectNode,
             InputExistingGeometryDataNode,
             
            #  ComposeMatrixNode,
             MetaRigMatrixNode,
             UtilityMatrixFromCurve,
             UtilityPointFromCurve,
             UtilityMatricesFromCurve,
            #  ScaleBoneLengthNode,
             UtilityMetaRigNode,
             UtilityBonePropertiesNode,
             UtilityDriverVariableNode,
             UtilityFCurveNode,
             UtilityDriverNode,
             UtilitySwitchNode,
             UtilityKeyframe,
             UtilityCombineThreeBoolNode,
             UtilityCombineVectorNode,
             UtilityCatStringsNode,
             UtilityGetBoneLength,
             UtilityPointFromBoneMatrix,
             UtilitySetBoneLength,
             UtilityMatrixSetLocation,
             UtilityMatrixGetLocation,
             UtilityMatrixFromXForm,
             UtilityAxesFromMatrix,
             UtilityBoneMatrixHeadTailFlip,
             UtilityMatrixTransform,
             UtilityTransformationMatrix,
             UtilitySetBoneMatrixTail,

             UtilityIntToString,
             UtilityArrayGet,
             #
             UtilityCompare,
             UtilityChoose,
             # for testing
             UtilityPrint,
            ]


def default_traverse(self,socket):
    return None


class InputFloatNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputFloatNode'
    bl_label = "Float"
    bl_icon = 'NODE'
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.outputs.new('FloatSocket', "Float Input").input = True
        self.initialized = True

class InputIntNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputIntNode'
    bl_label = "Integer"
    bl_icon = 'NODE'
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.outputs.new('IntSocket', "Integer").input = True
        self.initialized = True
    
class InputVectorNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputVectorNode'
    bl_label = "Vector"
    bl_icon = 'NODE'
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.outputs.new('VectorSocket', "").input = True
        self.initialized = True

class InputBooleanNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputBooleanNode'
    bl_label = "Boolean"
    bl_icon = 'NODE'
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.outputs.new('BooleanSocket', "").input = True
        self.initialized = True

class InputBooleanThreeTupleNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputBooleanThreeTupleNode'
    bl_label = "Boolean Vector"
    bl_icon = 'NODE'
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.outputs.new('BooleanThreeTupleSocket', "")
        self.initialized = True

class InputRotationOrderNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputRotationOrderNode'
    bl_label = "Rotation Order"
    bl_icon = 'NODE'
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.outputs.new('RotationOrderSocket', "").input = True
        self.initialized = True

class InputTransformSpaceNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputTransformSpaceNode'
    bl_label = "Transform Space"
    bl_icon = 'NODE'
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.outputs.new('TransformSpaceSocket', "").input = True
        self.initialized = True

class InputStringNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputStringNode'
    bl_label = "String"
    bl_icon = 'NODE'
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.outputs.new('StringSocket', "").input = True
        self.initialized = True

class InputQuaternionNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputQuaternionNode'
    bl_label = "Quaternion"
    bl_icon = 'NODE'
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.outputs.new('QuaternionSocket', "").input = True
        self.initialized = True

class InputQuaternionNodeAA(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputQuaternionNodeAA'
    bl_label = "Axis Angle"
    bl_icon = 'NODE'
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.outputs.new('QuaternionSocketAA', "").input = True
        self.initialized = True


class InputMatrixNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputMatrixNode'
    bl_label = "Matrix"
    bl_icon = 'NODE'
    first_row  : bpy.props.FloatVectorProperty(name="", size=4, default = (1.0, 0.0, 0.0, 0.0,))
    second_row : bpy.props.FloatVectorProperty(name="", size=4, default = (0.0, 1.0, 0.0, 0.0,))
    third_row  : bpy.props.FloatVectorProperty(name="", size=4, default = (0.0, 0.0, 1.0, 0.0,))
    fourth_row : bpy.props.FloatVectorProperty(name="", size=4, default = (0.0, 0.0, 0.0, 1.0,))
    initialized : bpy.props.BoolProperty(default = False)

    def set_matrix(self):
        return (self.first_row[ 0], self.first_row[ 1], self.first_row[ 2], self.first_row[ 3],
                self.second_row[0], self.second_row[1], self.second_row[2], self.second_row[3],
                self.third_row[ 0], self.third_row[ 1], self.third_row[ 2], self.third_row[ 3],
                self.fourth_row[0], self.fourth_row[1], self.fourth_row[2], self.fourth_row[3],)

    def init(self, context):
        self.outputs.new('MatrixSocket', "Matrix")
        self.initialized = True
        
    def update_node(self, context):
        self.outputs["Matrix"].default_value = self.set_matrix()

    def draw_buttons(self, context, layout):
        # return
        layout.prop(self, "first_row")
        layout.prop(self, "second_row")
        layout.prop(self, "third_row")
        layout.prop(self, "fourth_row")

    def update(self):
        mat_sock = self.outputs[0]
        mat_sock.default_value = self.set_matrix()

class ScaleBoneLengthNode(Node, MantisNode):
    '''Scale Bone Length'''
    bl_idname = 'ScaleBoneLength'
    bl_label = "Scale Bone Length"
    bl_icon = 'NODE'
    initialized : bpy.props.BoolProperty(default = False)

    # === Optional Functions ===
    def init(self, context):
        self.inputs.new('MatrixSocket', "In Matrix")
        self.inputs.new('FloatSocket', "Factor")
        self.outputs.new('MatrixSocket', "Out Matrix")
        self.initialized = True



class MetaRigMatrixNode(Node, MantisNode):
    # Identical to the above, except
    '''A node representing a bone's matrix'''
    bl_idname = 'MetaRigMatrixNode'
    bl_label = "Matrix"
    bl_icon = 'NODE'
    first_row  : bpy.props.FloatVectorProperty(name="", size=4, default = (1.0, 0.0, 0.0, 0.0,))
    second_row : bpy.props.FloatVectorProperty(name="", size=4, default = (0.0, 1.0, 0.0, 0.0,))
    third_row  : bpy.props.FloatVectorProperty(name="", size=4, default = (0.0, 0.0, 1.0, 0.0,))
    fourth_row : bpy.props.FloatVectorProperty(name="", size=4, default = (0.0, 0.0, 0.0, 1.0,))
    initialized : bpy.props.BoolProperty(default = False)

    def set_matrix(self):
        return (self.first_row[ 0], self.first_row[ 1], self.first_row[ 2], self.first_row[ 3],
                self.second_row[0], self.second_row[1], self.second_row[2], self.second_row[3],
                self.third_row[ 0], self.third_row[ 1], self.third_row[ 2], self.third_row[ 3],
                self.fourth_row[0], self.fourth_row[1], self.fourth_row[2], self.fourth_row[3],)

    def init(self, context):
        self.outputs.new('MatrixSocket', "Matrix")
        self.initialized = True
    
    def traverse(self, context):
        from mathutils import Matrix
        v = self.outputs[0].default_value
        # print( Matrix( ( ( v[ 0], v[ 1], v[ 2], v[ 3],),
        #                  ( v[ 4], v[ 5], v[ 6], v[ 7],),
        #                  ( v[ 8], v[ 9], v[10], v[11],),
        #                  ( v[12], v[13], v[14], v[15],), ) ) )
        return None
    
    def update_node(self, context):
        self.outputs["Matrix"].default_value = self.set_matrix()

    def update(self):
        mat_sock = self.outputs[0]
        mat_sock.default_value = self.set_matrix()


class UtilityMatrixFromCurve(Node, MantisNode):
    """Gets a matrix from a curve."""
    bl_idname = "UtilityMatrixFromCurve"
    bl_label = "Matrix from Curve"
    bl_icon = "NODE"
    
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        curv = self.inputs.new("EnumCurveSocket", "Curve")
        curv.icon = "OUTLINER_OB_CURVE"
        self.inputs.new('IntSocket', 'Total Divisions')
        self.inputs.new('IntSocket', 'Matrix Index')
        self.outputs.new("MatrixSocket", "Matrix")
        self.initialized = True


class UtilityPointFromCurve(Node, MantisNode):
    """Gets a point from a curve."""
    bl_idname = "UtilityPointFromCurve"
    bl_label = "Point from Curve"
    bl_icon = "NODE"
    
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        curv = self.inputs.new("EnumCurveSocket", "Curve")
        curv.icon = "OUTLINER_OB_CURVE"
        self.inputs.new('FloatFactorSocket', 'Factor')
        self.outputs.new("VectorSocket", "Point")
        self.initialized = True

class UtilityMatricesFromCurve(Node, MantisNode):
    """Gets a matrix from a curve."""
    bl_idname = "UtilityMatricesFromCurve"
    bl_label = "Matrices from Curve"
    bl_icon = "NODE"
    
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        curv = self.inputs.new("EnumCurveSocket", "Curve")
        curv.icon = "OUTLINER_OB_CURVE"
        self.inputs.new('IntSocket', 'Total Divisions')
        o = self.outputs.new("MatrixSocket", "Matrices")
        o.display_shape = 'SQUARE_DOT'
        self.initialized = True

class UtilityMetaRigNode(Node, MantisNode):
    """Gets a matrix from a meta-rig bone."""
    bl_idname = "UtilityMetaRig"
    bl_label = "Meta-Rig"
    bl_icon = "NODE"
    
    armature:bpy.props.StringProperty()
    pose_bone:bpy.props.StringProperty()
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        armt = self.inputs.new("EnumMetaRigSocket", "Meta-Armature")
        bone = self.inputs.new("EnumMetaBoneSocket", "Meta-Bone")
        armt.icon = "OUTLINER_OB_ARMATURE"
        bone.icon = "BONE_DATA"
        bone.hide=True
        self.outputs.new("MatrixSocket", "Matrix")
        self.initialized = True
    
    def display_update(self, parsed_tree, context):
        from .base_definitions import get_signature_from_edited_tree
        nc = parsed_tree.get(get_signature_from_edited_tree(self, context))
        if nc:
            self.armature= nc.evaluate_input("Meta-Armature")
            self.pose_bone= nc.evaluate_input("Meta-Bone")
        if not self.armature:
            self.inputs["Meta-Bone"].hide=True
        else:
            self.inputs["Meta-Bone"].hide=False
        if self.inputs["Meta-Armature"].is_linked:
            self.inputs["Meta-Armature"].search_prop = None
        if self.inputs["Meta-Bone"].is_linked:
            self.inputs["Meta-Bone"].search_prop = None

class UtilityBonePropertiesNode(Node, MantisNode):
    """Provides as sockets strings identifying bone transform properties."""
    bl_idname = "UtilityBoneProperties"
    bl_label = "Bone Properties"
    bl_icon = "NODE"
    #bl_width_default = 250
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.outputs.new("ParameterStringSocket", "matrix")
        self.outputs.new("ParameterStringSocket", "matrix_local")
        self.outputs.new("ParameterStringSocket", "matrix_basis")
        self.outputs.new("ParameterStringSocket", "head")
        self.outputs.new("ParameterStringSocket", "tail")
        self.outputs.new("ParameterStringSocket", "length")
        self.outputs.new("ParameterStringSocket", "rotation")
        self.outputs.new("ParameterStringSocket", "location")
        self.outputs.new("ParameterStringSocket", "scale")
        self.initialized = True
        
        for o in self.outputs:
            o.text_only = True

class UtilityDriverVariableNode(Node, MantisNode):
    """Creates a variable for use in a driver."""
    bl_idname = "UtilityDriverVariable"
    bl_label = "Driver Variable"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    
    def init(self, context):
        self.inputs.new("EnumDriverVariableType", "Variable Type")                 # 0
        self.inputs.new("ParameterStringSocket", "Property")                       # 1
        self.inputs.new("IntSocket", "Property Index")                             # 2
        self.inputs.new("EnumDriverVariableEvaluationSpace", "Evaluation Space")   # 3
        self.inputs.new("EnumDriverRotationMode", "Rotation Mode")                 # 4
        self.inputs.new("xFormSocket", "xForm 1")                                  # 5
        self.inputs.new("xFormSocket", "xForm 2")                                  # 6
        self.outputs.new("DriverVariableSocket", "Driver Variable")
        self.inputs[3].hide = True
        self.initialized = True
    
    def display_update(self, parsed_tree, context):
        from .base_definitions import get_signature_from_edited_tree
        if self.inputs["Variable Type"].is_linked:
            if context.space_data:
                node_tree = context.space_data.path[0].node_tree
                nc = parsed_tree.get(get_signature_from_edited_tree(self, context))
                if nc:
                    driver_type = nc.evaluate_input("Variable Type")
        else:
            driver_type = self.inputs[0].default_value
        if driver_type == 'SINGLE_PROP':
            self.inputs[1].hide = False
            self.inputs[2].hide = False
            self.inputs[3].hide = False
            self.inputs[4].hide = False
            self.inputs[5].hide = False
            self.inputs[6].hide = True
        elif driver_type == 'LOC_DIFF':
            self.inputs[1].hide = True
            self.inputs[2].hide = True
            self.inputs[3].hide = True
            self.inputs[4].hide = True
            self.inputs[5].hide = False
            self.inputs[6].hide = False
        elif driver_type == 'ROTATION_DIFF':
            self.inputs[1].hide = True
            self.inputs[2].hide = True
            self.inputs[3].hide = True
            self.inputs[4].hide = False
            self.inputs[5].hide = False
            self.inputs[6].hide = False
        elif driver_type == 'TRANSFORMS':
            self.inputs[1].hide = True
            self.inputs[2].hide = True
            self.inputs[3].hide = False
            self.inputs[4].hide = False
            self.inputs[5].hide = False
            self.inputs[6].hide = True
    

# TODO: make a way to edit the fCurve directly.
# I had a working version of this in the past, but it required doing sinful things like
# keeping track of the RAM address of the window.
class UtilityFCurveNode(Node, MantisNode):
    """Creates an fCurve for use with a driver."""
    bl_idname = "UtilityFCurve"
    bl_label = "fCurve"
    bl_icon = "NODE"
    
    use_kf_nodes   : bpy.props.BoolProperty(default=True)
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.outputs.new("FCurveSocket", "fCurve")
        self.initialized = True
            
    def draw_buttons(self, context, layout):
        layout.operator( 'mantis.fcurve_node_add_kf' )
        if (len(self.inputs) > 0):
            layout.operator( 'mantis.fcurve_node_remove_kf' )


class UtilityDriverNode(Node, MantisNode):
    """Represents a Driver relationship"""
    bl_idname = "UtilityDriver"
    bl_label = "Driver"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("EnumDriverType", "Driver Type")
        self.inputs.new("FCurveSocket", "fCurve")
        self.inputs.new("StringSocket", "Expression")
        self.outputs.new("DriverSocket", "Driver")
        self.initialized = True
        
    def display_update(self, parsed_tree, context):
        if not self.inputs["Driver Type"].is_linked:
            dType = self.inputs["Driver Type"].default_value
        from .base_definitions import get_signature_from_edited_tree
        nc = parsed_tree.get(get_signature_from_edited_tree(self, context))
        if nc:
            dType = nc.evaluate_input("Driver Type")
        if dType == 'SCRIPTED':
            self.inputs["Expression"].hide = False
        else:
            self.inputs["Expression"].hide = True
    
    def draw_buttons(self, context, layout):
        # return
        layout.operator( 'mantis.driver_node_add_variable' )
        if (len(self.inputs) > 3):
            layout.operator( 'mantis.driver_node_remove_variable' )

class UtilitySwitchNode(Node, MantisNode):
    """Represents a switch relationship between one driver property and one or more driven properties."""
    bl_idname = "UtilitySwitch"
    bl_label = "Switch"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        # self.inputs.new("xFormSocket", "xForm")
        self.inputs.new("ParameterStringSocket", "Parameter")
        self.inputs.new("IntSocket", "Parameter Index")
        self.inputs.new("BooleanSocket", "Invert Switch")
        self.outputs.new("DriverSocket", "Driver")
        self.initialized = True

class UtilityCombineThreeBoolNode(Node, MantisNode):
    """Combines three booleans into a three-bool."""
    bl_idname = "UtilityCombineThreeBool"
    bl_label = "CombineThreeBool"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("BooleanSocket", "X")
        self.inputs.new("BooleanSocket", "Y")
        self.inputs.new("BooleanSocket", "Z")
        self.outputs.new("BooleanThreeTupleSocket", "Three-Bool")
        # this node should eventually just be a Combine Boolean Three-Tuple node
        # and the "Driver" output will need to be figured out some other way
        self.initialized = True
class UtilityCombineVectorNode(Node, MantisNode):
    """Combines three floats into a vector."""
    bl_idname = "UtilityCombineVector"
    bl_label = "CombineVector"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("FloatSocket", "X")
        self.inputs.new("FloatSocket", "Y")
        self.inputs.new("FloatSocket", "Z")
        self.outputs.new("VectorSocket", "Vector")
        # this node should eventually just be a Combine Boolean Three-Tuple node
        # and the "Driver" output will need to be figured out some other way
        self.initialized = True
        
class UtilityCatStringsNode(Node, MantisNode):
    """Adds a suffix to a string"""
    bl_idname = "UtilityCatStrings"
    bl_label = "Concatenate Strings"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("StringSocket", "String_1")
        self.inputs.new("StringSocket", "String_2")
        self.outputs.new("StringSocket", "OutputString")
        self.initialized = True
    
class InputLayerMaskNode(Node, MantisNode):
    """Represents a layer mask for a bone."""
    bl_idname = "InputLayerMaskNode"
    bl_label = "Layer Mask"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.outputs.new("LayerMaskInputSocket", "Layer Mask")
        self.initialized = True

class InputExistingGeometryObjectNode(Node, MantisNode):
    """Represents an existing geometry object from within the scene."""
    bl_idname = "InputExistingGeometryObject"
    bl_label = "Existing Object"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    # We want Mantis to import widgets and stuff, so we hold a reference to the object
    object_reference : bpy.props.PointerProperty(type=bpy.types.Object,) 
    
    def init(self, context):
        self.inputs.new("StringSocket", "Name")
        self.outputs.new("xFormSocket", "Object")
        self.initialized = True
    
    def display_update(self, parsed_tree, context):
        from .base_definitions import get_signature_from_edited_tree
        nc = parsed_tree.get(get_signature_from_edited_tree(self, context))
        if nc: # this is done here so I don't have to define yet another custom socket.
            self.object_reference = bpy.data.objects.get(nc.evaluate_input("Name"))
    
# TODO: maybe I should hold a data reference here, too.
#       but it is complicated by the fact that Mantis does not distinguish b/tw geo types
class InputExistingGeometryDataNode(Node, MantisNode):
    """Represents a mesh or curve datablock from the scene."""
    bl_idname = "InputExistingGeometryData"
    bl_label = "Existing Geometry"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("StringSocket", "Name")
        self.outputs.new("GeometrySocket", "Geometry")
        self.initialized = True

class UtilityGetBoneLength(Node, MantisNode):
    """Returns the length of the bone from its matrix."""
    bl_idname = "UtilityGetBoneLength"
    bl_label = "Get Bone Length"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("MatrixSocket", "Bone Matrix")
        self.outputs.new("FloatSocket", "Bone Length")
        self.initialized = True

# TODO: make it work with BBones!
class UtilityPointFromBoneMatrix(Node, MantisNode):
    """Returns a point representing the location along a bone, given a matrix representing that bone's shape."""
    bl_idname = "UtilityPointFromBoneMatrix"
    bl_label = "Point from Bone Matrix"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("MatrixSocket", "Bone Matrix")
        self.inputs.new("FloatFactorSocket", "Head/Tail")
        self.outputs.new("VectorSocket", "Point")
        self.initialized = True
class UtilitySetBoneLength(Node, MantisNode):
    """Sets the length of a bone matrix."""
    bl_idname = "UtilitySetBoneLength"
    bl_label = "Set Bone Matrix Length"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("MatrixSocket", "Bone Matrix")
        self.inputs.new("FloatSocket", "Length")
        self.outputs.new("MatrixSocket", "Bone Matrix")
        self.initialized = True

# TODO: more keyframe types should be supported in the future.
# Some of the code that can do this is commented out here until I can implement it properly.
class UtilityKeyframe(Node, MantisNode):
    """A keyframe for a FCurve"""
    bl_idname = "UtilityKeyframe"
    bl_label = "KeyFrame"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        # x and y
        # output is keyframe
        # self.inputs.new("EnumKeyframeInterpolationTypeSocket", "Interpolation")
        # self.inputs.new("EnumKeyframeBezierHandleType", "Left Handle Type")
        # self.inputs.new("EnumKeyframeBezierHandleType", "Right Handle Type")

        # self.inputs.new("FloatSocket", "Left Handle Distance")
        # self.inputs.new("FloatSocket", "Left Handle Value")
        # self.inputs.new("FloatSocket", "Right Handle Frame")
        # self.inputs.new("FloatSocket", "Right Handle Value")

        self.inputs.new("FloatSocket", "Frame")
        self.inputs.new("FloatSocket", "Value")
        self.outputs.new("KeyframeSocket", "Keyframe")
        # there will eventually be inputs for e.g. key type, key handles, etc.
        # right now I am gonna hardcode LINEAR keyframes so I don't have to deal with anything else
        # TODO TODO TODO

    # def display_update(self, parsed_tree, context):
    #     if context.space_data:
    #         nc = parsed_tree.get(get_signature_from_edited_tree(self, context))
    #         if nc.evaluate_input("Interpolation") in ["CONSTANT", "LINEAR"]:
    #             for inp in self.inputs[1:6]:
    #                 inp.hide = True
    #         else:
    #             if nc.evaluate_input("Left Handle Type") in ["FREE", "ALIGNED"]:

    #             for inp in self.inputs[1:6]:
    #                 inp.hide = False
        self.initialized = True


class UtilityBoneMatrixHeadTailFlip(Node, MantisNode):
    """Flips a bone matrix so that the head is where the tail was and visa versa."""
    bl_idname = "UtilityBoneMatrixHeadTailFlip"
    bl_label = "Flip Head/Tail"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("MatrixSocket", "Bone Matrix")
        self.outputs.new("MatrixSocket", "Bone Matrix")
        self.initialized = True

class UtilityMatrixTransform(Node, MantisNode):
    """Transforms a matrix by another."""
    bl_idname = "UtilityMatrixTransform"
    bl_label = "Matrix Transform"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("MatrixSocket", "Matrix 1")
        self.inputs.new("MatrixSocket", "Matrix 2")
        self.outputs.new("MatrixSocket", "Out Matrix")
        self.initialized = True

class UtilityMatrixSetLocation(Node, MantisNode):
    """Sets a matrix's location."""
    bl_idname = "UtilityMatrixSetLocation"
    bl_label = "Set Matrix Location"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("MatrixSocket", "Matrix")
        self.inputs.new("VectorSocket", "Location")
        self.outputs.new("MatrixSocket", "Matrix")
        self.initialized = True

class UtilityMatrixGetLocation(Node, MantisNode):
    """Gets a matrix's location."""
    bl_idname = "UtilityMatrixGetLocation"
    bl_label = "Get Matrix Location"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("MatrixSocket", "Matrix")
        self.outputs.new("VectorSocket", "Location")
        self.initialized = True

class UtilityTransformationMatrix(Node, MantisNode):
    """Constructs a matrix representing a transformation"""
    bl_idname = "UtilityTransformationMatrix"
    bl_label = "Transformation Matrix"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        # first input is a transformation type - translation, rotation, or scale
        #                         rotation is an especially annoying feature because it can take multiple types
        #   so Euler, axis/angle, quaternion, matrix...
        #   for now I am only going to implement axis-angle
        # it should get an axis and a magnitude
        # self.inputs.new("MatrixSocket", "Bone Matrix")
        
        self.inputs.new("MatrixTransformOperation", "Operation")
        self.inputs.new("VectorSocket", "Vector")
        self.inputs.new("FloatSocket", "W")
        self.outputs.new("MatrixSocket", "Matrix")
        self.initialized = True


    def display_update(self, parsed_tree, context):
        from .base_definitions import get_signature_from_edited_tree
        operation = self.inputs['Operation'].default_value
        if self.inputs['Operation'].is_linked:
            if context.space_data:
                nc = parsed_tree.get(get_signature_from_edited_tree(self, context))
                operation = nc.evaluate_input("Operation")
        if operation in ["ROTATE_AXIS_ANGLE", "SCALE"]:
            self.inputs["Vector"].hide = False
            self.inputs["W"].hide = False
        if operation in ["TRANSLATE"]:
            self.inputs["Vector"].hide = False
            self.inputs["W"].hide = True
            

# Blender calculates bone roll this way...
# https://projects.blender.org/blender/blender/src/commit/dd209221675ac7b62ce47b7ea42f15cbe34a6035/source/blender/editors/armature/armature_edit.cc#L281
# but this looks like it will be harder to re-implement than to re-use. Unfortunately, it doesn't apply directly to a matrix so I have to call a method
# in the edit bone.
# So instead, we need to avoid calculating the roll for now.
# but I want to make that its own node and add roll-recalc to this node, too.

class UtilitySetBoneMatrixTail(Node, MantisNode):
    """Constructs a matrix representing a transformation"""
    bl_idname = "UtilitySetBoneMatrixTail"
    bl_label = "Set Bone Matrix Tail"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("MatrixSocket", "Matrix")
        self.inputs.new("VectorSocket", "Tail Location")
        self.outputs.new("MatrixSocket", "Result")
        self.initialized = True


class UtilityMatrixFromXForm(Node, MantisNode):
    """Returns the matrix of the given xForm node."""
    bl_idname = "UtilityMatrixFromXForm"
    bl_label = "Matrix of xForm"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("xFormSocket", "xForm")
        self.outputs.new("MatrixSocket", "Matrix")
        self.initialized = True

class UtilityAxesFromMatrix(Node, MantisNode):
    """Returns the axes of the matrix."""
    bl_idname = "UtilityAxesFromMatrix"
    bl_label = "Axes of Matrix"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("MatrixSocket", "Matrix")
        self.outputs.new("VectorSocket", "X Axis")
        self.outputs.new("VectorSocket", "Y Axis")
        self.outputs.new("VectorSocket", "Z Axis")
        self.initialized = True

class UtilityIntToString(Node, MantisNode):
    """Converts a number to a string"""
    bl_idname = "UtilityIntToString"
    bl_label = "Number String"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        
        self.inputs.new("IntSocket", "Number")
        self.inputs.new("IntSocket", "Zero Padding")
        self.outputs.new("StringSocket", "String")
        self.initialized = True


class UtilityArrayGet(Node, MantisNode):
    """Gets a value from an array at a specified index."""
    bl_idname = "UtilityArrayGet"
    bl_label  = "Array Get"
    bl_icon   = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new('EnumArrayGetOptions', 'OoB Behaviour')
        self.inputs.new("IntSocket", "Index")
        s = self.inputs.new("WildcardSocket", "Array", use_multi_input=True)
        s.display_shape = 'SQUARE_DOT'
        self.outputs.new("WildcardSocket", "Output")
        self.initialized = True
    
    def update(self):
        wildcard_color = (0.0,0.0,0.0,0.0)
        if self.inputs['Array'].is_linked == False:
            self.inputs['Array'].color = wildcard_color
            self.outputs['Output'].color = wildcard_color

    def insert_link(self, link):
        prGreen(link.from_node.name, link.from_socket.identifier, link.to_node.name, link.to_socket.identifier)
        if link.to_socket.identifier == self.inputs['Array'].identifier:
            from_socket = link.from_socket
            print (from_socket.color)
            if hasattr(from_socket, "color"):
                self.inputs['Array'].color = from_socket.color
                self.outputs['Output'].color = from_socket.color


class UtilityCompare(Node, MantisNode):
    """Compares two inputs and produces a boolean output"""
    bl_idname = "UtilityCompare"
    bl_label = "Compare"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("WildcardSocket", "A")
        self.inputs.new("WildcardSocket", "B")
        self.outputs.new("BooleanSocket", "Result")
        self.initialized = True
    
    def update(self):
        wildcard_color = (0.0,0.0,0.0,0.0)
        if self.inputs['A'].is_linked == False:
            self.inputs['A'].color = wildcard_color
        if self.inputs['B'].is_linked == False:
            self.inputs['B'].color = wildcard_color

    def insert_link(self, link):
        if link.to_socket.identifier == self.inputs['A'].identifier:
            self.inputs['A'].color = link.from_socket.color_simple
            if hasattr(link.from_socket, "color"):
                self.inputs['A'].color = link.from_socket.color
        if link.to_socket.identifier == self.inputs['B'].identifier:
            self.inputs['B'].color = link.from_socket.color_simple
            if hasattr(link.from_socket, "color"):
                self.inputs['B'].color = link.from_socket.color

class UtilityChoose(Node, MantisNode):
    """Chooses an output"""
    bl_idname = "UtilityChoose"
    bl_label = "Choose"
    bl_icon = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        
        self.inputs.new("BooleanSocket", "Condition")
        self.inputs.new("WildcardSocket", "A")
        self.inputs.new("WildcardSocket", "B")
        self.outputs.new("WildcardSocket", "Result")
        self.initialized = True
    
    def update(self):
        wildcard_color = (0.0,0.0,0.0,0.0)
        if self.inputs['A'].is_linked == False:
            self.inputs['A'].color = wildcard_color
            self.outputs['Result'].color = (1.0,0.0,0.0,0.0) # red for Error
        if self.inputs['B'].is_linked == False:
            self.inputs['B'].color = wildcard_color
            self.outputs['Result'].color = (1.0,0.0,0.0,0.0)
        # if both inputs are the same color, then use that color for the result
        if self.inputs['A'].is_linked and self.inputs['A'].color == self.inputs['B'].color:
            self.outputs['Result'].color = self.inputs['A'].color
        #
        if ((self.inputs['A'].is_linked and self.inputs['B'].is_linked) and
            (self.inputs['A'].links[0].from_socket.bl_idname != self.inputs['B'].links[0].from_socket.bl_idname)):
            self.inputs['A'].color = (1.0,0.0,0.0,0.0)
            self.inputs['B'].color = (1.0,0.0,0.0,0.0)
            self.outputs['Result'].color = (1.0,0.0,0.0,0.0)

    def insert_link(self, link):
        if link.to_socket.identifier == self.inputs['A'].identifier:
            self.inputs['A'].color = from_socket.color_simple
            if hasattr(from_socket, "color"):
                self.inputs['A'].color = from_socket.color
        if link.to_socket.identifier == self.inputs['B'].identifier:
            self.inputs['B'].color = from_socket.color_simple
            if hasattr(from_socket, "color"):
                self.inputs['B'].color = from_socket.color




class UtilityPrint(Node, MantisNode):
    """A utility used to print arbitrary values."""
    bl_idname = "UtilityPrint"
    bl_label  = "Print"
    bl_icon   = "NODE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new("WildcardSocket", "Input")
        self.initialized = True
    

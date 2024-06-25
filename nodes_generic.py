import bpy
from bpy.types import Node
from .base_definitions import MantisNode

def TellClasses():
    return [ InputFloatNode,
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
            #  ScaleBoneLengthNode,
             UtilityMetaRigNode,
             UtilityBonePropertiesNode,
             UtilityDriverVariableNode,
             UtilityFCurveNode,
             UtilityDriverNode,
             UtilitySwitchNode,
             UtilityCombineThreeBoolNode,
             UtilityCombineVectorNode,
             UtilityCatStringsNode,
            ]


def default_traverse(self,socket):
    return None


class InputFloatNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputFloatNode'
    bl_label = "Float"
    bl_icon = 'NODE'

    def init(self, context):
        self.outputs.new('FloatSocket', "Float Input").input = True
    
class InputVectorNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputVectorNode'
    bl_label = "Vector"
    bl_icon = 'NODE'

    def init(self, context):
        self.outputs.new('VectorSocket', "").input = True

class InputBooleanNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputBooleanNode'
    bl_label = "Boolean"
    bl_icon = 'NODE'

    def init(self, context):
        self.outputs.new('BooleanSocket', "").input = True

class InputBooleanThreeTupleNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputBooleanThreeTupleNode'
    bl_label = "Boolean Vector"
    bl_icon = 'NODE'

    def init(self, context):
        self.outputs.new('BooleanThreeTupleSocket', "")

class InputRotationOrderNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputRotationOrderNode'
    bl_label = "Rotation Order"
    bl_icon = 'NODE'

    def init(self, context):
        self.outputs.new('RotationOrderSocket', "").input = True

class InputTransformSpaceNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputTransformSpaceNode'
    bl_label = "Transform Space"
    bl_icon = 'NODE'

    def init(self, context):
        self.outputs.new('TransformSpaceSocket', "").input = True

class InputStringNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputStringNode'
    bl_label = "String"
    bl_icon = 'NODE'

    def init(self, context):
        self.outputs.new('StringSocket', "").input = True

class InputQuaternionNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputQuaternionNode'
    bl_label = "Quaternion"
    bl_icon = 'NODE'

    def init(self, context):
        self.outputs.new('QuaternionSocket', "").input = True

class InputQuaternionNodeAA(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputQuaternionNodeAA'
    bl_label = "Axis Angle"
    bl_icon = 'NODE'

    def init(self, context):
        self.outputs.new('QuaternionSocketAA', "").input = True


class InputMatrixNode(Node, MantisNode):
    '''A node representing inheritance'''
    bl_idname = 'InputMatrixNode'
    bl_label = "Matrix"
    bl_icon = 'NODE'
    first_row  : bpy.props.FloatVectorProperty(name="", size=4, default = (1.0, 0.0, 0.0, 0.0,))
    second_row : bpy.props.FloatVectorProperty(name="", size=4, default = (0.0, 1.0, 0.0, 0.0,))
    third_row  : bpy.props.FloatVectorProperty(name="", size=4, default = (0.0, 0.0, 1.0, 0.0,))
    fourth_row : bpy.props.FloatVectorProperty(name="", size=4, default = (0.0, 0.0, 0.0, 1.0,))

    def set_matrix(self):
        return (self.first_row[ 0], self.first_row[ 1], self.first_row[ 2], self.first_row[ 3],
                self.second_row[0], self.second_row[1], self.second_row[2], self.second_row[3],
                self.third_row[ 0], self.third_row[ 1], self.third_row[ 2], self.third_row[ 3],
                self.fourth_row[0], self.fourth_row[1], self.fourth_row[2], self.fourth_row[3],)

    def init(self, context):
        self.outputs.new('MatrixSocket', "Matrix")
        
    def update_node(self, context):
        self.outputs["Matrix"].default_value = self.set_matrix()

    def draw_buttons(self, context, layout):
        layout.prop(self, "first_row")
        layout.prop(self, "second_row")
        layout.prop(self, "third_row")
        layout.prop(self, "fourth_row")

    def update(self):
        mat_sock = self.outputs[0]
        mat_sock.default_value = self.set_matrix()

# TODO: reimplement the nodes beneath here

# from .utilities import QuerySocket, to_mathutils_value
# class ComposeMatrixNode(Node, MantisNode):
#     '''A utility node for composing a matrix'''
#     bl_idname = 'ComposeMatrixNode'
#     bl_label = "Compose Matrix"
#     bl_icon = 'NODE'

#     def init(self, context):
#         self.inputs.new('VectorTranslationSocket', "Translation")
#         self.inputs.new('GenericRotationSocket', "Rotation")
#         self.inputs.new('VectorScaleSocket', "Scale")
#         self.outputs.new('MatrixSocket', "Matrix")

#     def update_node(self, context = None):
#         from mathutils import Matrix, Euler, Quaternion, Vector
#         mat_sock = self.outputs[0]
#         rotation = Matrix.Identity(4)
#         scale = Matrix.Identity(4)
#         translation = Matrix.Identity(4)

#         sock = QuerySocket(self.inputs["Rotation"])[0]
#         val = to_mathutils_value(sock)
#         if (val):
#             if (isinstance(val, Vector)):
#                 val = Euler((val[0], val[1], val[2]), 'XYZ')
#             rotation = val.to_matrix().to_4x4()
#         sock = QuerySocket(self.inputs["Scale"])[0]
#         val = to_mathutils_value(sock)
#         if (val):
#             if (isinstance(val, Vector)):
#                 scale = Matrix.Scale(val[0],4,(1.0,0.0,0.0)) @ Matrix.Scale(val[1],4,(0.0,1.0,0.0)) @ Matrix.Scale(val[2],4,(0.0,0.0,1.0))
#         sock = QuerySocket(self.inputs["Translation"])[0]
#         val = to_mathutils_value(sock)
#         if (val):
#             if (isinstance(val, Vector)):
#                 translation = Matrix.Translation((val))
        
#         mat = translation @ rotation @ scale
#         mat_sock.default_value = ( mat[0][0], mat[0][1], mat[0][2], mat[0][3],
#                                    mat[1][0], mat[1][1], mat[1][2], mat[1][3],
#                                    mat[2][0], mat[2][1], mat[2][2], mat[2][3],
#                                    mat[3][0], mat[3][1], mat[3][2], mat[3][3], )


class ScaleBoneLengthNode(Node, MantisNode):
    '''Scale Bone Length'''
    bl_idname = 'ScaleBoneLength'
    bl_label = "Scale Bone Length"
    bl_icon = 'NODE'

    # === Optional Functions ===
    def init(self, context):
        self.inputs.new('MatrixSocket', "In Matrix")
        self.inputs.new('FloatSocket', "Factor")
        self.outputs.new('MatrixSocket', "Out Matrix")



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

    def set_matrix(self):
        return (self.first_row[ 0], self.first_row[ 1], self.first_row[ 2], self.first_row[ 3],
                self.second_row[0], self.second_row[1], self.second_row[2], self.second_row[3],
                self.third_row[ 0], self.third_row[ 1], self.third_row[ 2], self.third_row[ 3],
                self.fourth_row[0], self.fourth_row[1], self.fourth_row[2], self.fourth_row[3],)

    def init(self, context):
        self.outputs.new('MatrixSocket', "Matrix")
    
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



class UtilityMetaRigNode(Node, MantisNode):
    """Gets a matrix from a meta-rig bone."""
    bl_idname = "UtilityMetaRig"
    bl_label = "Meta-Rig"
    bl_icon = "NODE"
    
    armature:bpy.props.StringProperty()
    pose_bone:bpy.props.StringProperty()
    
    def init(self, context):
        armt = self.inputs.new("EnumMetaRigSocket", "Meta-Armature")
        bone = self.inputs.new("EnumMetaBoneSocket", "Meta-Bone")
        armt.icon = "OUTLINER_OB_ARMATURE"
        bone.icon = "BONE_DATA"
        bone.hide=True
        self.outputs.new("MatrixSocket", "Matrix")
    
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

class UtilityBonePropertiesNode(Node, MantisNode):
    """Provides as sockets strings identifying bone transform properties."""
    bl_idname = "UtilityBoneProperties"
    bl_label = "Bone Properties"
    bl_icon = "NODE"
    #bl_width_default = 250
    
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
        
        for o in self.outputs:
            o.text_only = True

class UtilityDriverVariableNode(Node, MantisNode):
    """Creates a variable for use in a driver."""
    bl_idname = "UtilityDriverVariable"
    bl_label = "Driver Variable"
    bl_icon = "NODE"
    
    
    def init(self, context):
        self.inputs.new("EnumDriverVariableType", "Variable Type")
        self.inputs.new("ParameterStringSocket", "Property")
        self.inputs.new("IntSocket", "Property Index")
        self.inputs.new("EnumDriverVariableEvaluationSpace", "Evaluation Space")
        self.inputs.new("EnumDriverRotationMode", "Rotation Mode")
        self.inputs.new("xFormSocket", "xForm 1")
        self.inputs.new("xFormSocket", "xForm 2")
        self.outputs.new("DriverVariableSocket", "Driver Variable")
        
    def update_on_socket_change(self, context):
        self.update()
    
    def display_update(self, parsed_tree, context):
        from .base_definitions import get_signature_from_edited_tree
        if context.space_data:
            node_tree = context.space_data.path[0].node_tree
            nc = parsed_tree.get(get_signature_from_edited_tree(self, context))
            if nc:
                driver_type = nc.evaluate_input("Variable Type")
                if driver_type == 'SINGLE_PROP':
                    self.inputs[0].hide = False
                    self.inputs[1].hide = False
                    self.inputs[2].hide = False
                    self.inputs[3].hide = False
                    self.inputs[4].hide = False
                    self.inputs[5].hide = False
                    self.inputs[6].hide = True
                elif driver_type == 'LOC_DIFF':
                    self.inputs[0].hide = False
                    self.inputs[1].hide = True
                    self.inputs[2].hide = True
                    self.inputs[3].hide = True
                    self.inputs[4].hide = True
                    self.inputs[5].hide = False
                    self.inputs[6].hide = False
                elif driver_type == 'ROTATION_DIFF':
                    self.inputs[0].hide = False
                    self.inputs[1].hide = True
                    self.inputs[2].hide = True
                    self.inputs[3].hide = True
                    self.inputs[4].hide = False
                    self.inputs[5].hide = False
                    self.inputs[6].hide = False
    

class UtilityFCurveNode(Node, MantisNode):
    """Creates an fCurve for use with a driver."""
    bl_idname = "UtilityFCurve"
    bl_label = "fCurve"
    bl_icon = "NODE"
    
    use_kf_nodes   : bpy.props.BoolProperty(default=False)
    fake_fcurve_ob : bpy.props.PointerProperty(type=bpy.types.Object)
    
    def init(self, context):
        self.outputs.new("FCurveSocket", "fCurve")
        if not self.fake_fcurve_ob:
            ob = bpy.data.objects.new("fake_ob_"+self.name, None)
            self.fake_fcurve_ob = ob
            ob.animation_data_create()
            ob.animation_data.action = bpy.data.actions.new('fake_action_'+self.name)
            fc = ob.animation_data.action.fcurves.new('location', index=0, action_group='location')
            fc.keyframe_points.add(2)
            kf0 = fc.keyframe_points[0]; kf0.co_ui = (0, 0)
            kf1 = fc.keyframe_points[1]; kf1.co_ui = (1, 1)
            #
            kf0.interpolation = 'BEZIER'
            kf0.handle_left_type  = 'AUTO_CLAMPED'
            kf0.handle_right_type = 'AUTO_CLAMPED'
            kf1.interpolation = 'BEZIER'
            kf1.handle_left_type  = 'AUTO_CLAMPED'
            kf1.handle_right_type = 'AUTO_CLAMPED'
            #
            
    def draw_buttons(self, context, layout):
        if self.use_kf_nodes:
            layout.prop(self, "use_kf_nodes",  text="[ Use fCurve data ]", toggle=True, invert_checkbox=True)
            layout.operator( 'mantis.fcurve_node_add_kf' )
            if (len(self.inputs) > 0):
                layout.operator( 'mantis.fcurve_node_remove_kf' )
        else:
            layout.prop(self, "use_kf_nodes",  text="[ Use Keyframe Nodes ]", toggle=True)
            layout.operator('mantis.edit_fcurve_node')
        
            
    
    # THE DIFFICULT part is getting it to show up in the graph editor
    # TRY:
    #       a modal operator that opens the Graph Editor
    #       and then finishes when it is closed
    #       it would reveal the object holding the fCurve before
    #       showing the Graph Editor
    #       And hide it after closing it.
    #
        
        
        
        

class UtilityDriverNode(Node, MantisNode):
    """Represents a Driver relationship"""
    bl_idname = "UtilityDriver"
    bl_label = "Driver"
    bl_icon = "NODE"
    
    def init(self, context):
        self.inputs.new("EnumDriverType", "Driver Type")
        self.inputs.new("FCurveSocket", "fCurve")
        self.inputs.new("StringSocket", "Expression")
        self.outputs.new("DriverSocket", "Driver")
        
    def update(self):
        return
        context = bpy.context
        try:
            tree = context.space_data.path[0].node_tree
            proceed = True
        except AttributeError:
            proceed = False
        if proceed:
            from .f_nodegraph import (GetDownstreamXFormNodes, get_node_container)
            if (node_container := get_node_container(self, context)[0]):
                dType = node_container.evaluate_input("Driver Type")
            else:
                dType = self.inputs[0].default_value
            
            if dType == 'SCRIPTED':
                self.inputs["Expression"].hide = False
            else:
                self.inputs["Expression"].hide = True
    
    def draw_buttons(self, context, layout):
        layout.operator( 'mantis.driver_node_add_variable' )
        if (len(self.inputs) > 2):
            layout.operator( 'mantis.driver_node_remove_variable' )

class UtilitySwitchNode(Node, MantisNode):
    """Represents a switch relationship between one driver property and one or more driven properties."""
    bl_idname = "UtilitySwitch"
    bl_label = "Switch"
    bl_icon = "NODE"
    
    def init(self, context):
        self.inputs.new("xFormSocket", "xForm")
        self.inputs.new("ParameterStringSocket", "Parameter")
        self.inputs.new("IntSocket", "Parameter Index")
        self.inputs.new("BooleanSocket", "Invert Switch")
        self.outputs.new("DriverSocket", "Driver")

class UtilityCombineThreeBoolNode(Node, MantisNode):
    """Combines three booleans into a three-bool."""
    bl_idname = "UtilityCombineThreeBool"
    bl_label = "CombineThreeBool"
    bl_icon = "NODE"
    
    def init(self, context):
        self.inputs.new("BooleanSocket", "X")
        self.inputs.new("BooleanSocket", "Y")
        self.inputs.new("BooleanSocket", "Z")
        self.outputs.new("BooleanThreeTupleSocket", "Three-Bool")
        # this node should eventually just be a Combine Boolean Three-Tuple node
        # and the "Driver" output will need to be figured out some other way
class UtilityCombineVectorNode(Node, MantisNode):
    """Combines three floats into a vector."""
    bl_idname = "UtilityCombineVector"
    bl_label = "CombineVector"
    bl_icon = "NODE"
    
    def init(self, context):
        self.inputs.new("FloatSocket", "X")
        self.inputs.new("FloatSocket", "Y")
        self.inputs.new("FloatSocket", "Z")
        self.outputs.new("VectorSocket", "Vector")
        # this node should eventually just be a Combine Boolean Three-Tuple node
        # and the "Driver" output will need to be figured out some other way
        
class UtilityCatStringsNode(Node, MantisNode):
    """Adds a suffix to a string"""
    bl_idname = "UtilityCatStrings"
    bl_label = "Concatenate Strings"
    bl_icon = "NODE"
    
    def init(self, context):
        self.inputs.new("StringSocket", "String_1")
        self.inputs.new("StringSocket", "String_2")
        self.outputs.new("StringSocket", "OutputString")
    
class InputLayerMaskNode(Node, MantisNode):
    """Represents a layer mask for a bone."""
    bl_idname = "InputLayerMaskNode"
    bl_label = "Layer Mask"
    bl_icon = "NODE"
    
    def init(self, context):
        self.outputs.new("LayerMaskInputSocket", "Layer Mask")

class InputExistingGeometryObjectNode(Node, MantisNode):
    """Represents an existing geometry object from within the scene."""
    bl_idname = "InputExistingGeometryObject"
    bl_label = "Existing Object"
    bl_icon = "NODE"
    
    def init(self, context):
        self.inputs.new("StringSocket", "Name")
        self.outputs.new("xFormSocket", "Object")

class InputExistingGeometryDataNode(Node, MantisNode):
    """Represents a mesh or curve datablock from the scene."""
    bl_idname = "InputExistingGeometryData"
    bl_label = "Existing Geometry"
    bl_icon = "NODE"
    
    def init(self, context):
        self.inputs.new("StringSocket", "Name")
        self.outputs.new("GeometrySocket", "Geometry")

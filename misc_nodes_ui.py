import bpy
from bpy.types import Node
from .base_definitions import MantisUINode, get_signature_from_edited_tree
from .misc_nodes_socket_templates import *

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
             InputMatrixNode,
             InputThemeBoneColorSets,
             InputColorSetPallete,
             # InputGeometryNode,
             InputWidget,
             InputExistingGeometryObjectNode,
             InputExistingGeometryDataNode,
             UtilityCustomProperty,
             UtilityDeclareCollections,
             UtilityCollectionJoin,
             UtilityCollectionHierarchy,
             UtilityGeometryOfXForm,
             UtilityNameOfXForm,
            #  ComposeMatrixNode,
             UtilityPointFromCurve,
             UtilityMatrixFromCurve,
             UtilityMatricesFromCurve,
             UtilityNumberOfCurveSegments,
             UtilityNumberOfSplines,
             UtilityMatrixFromCurveSegment,
             UtilityGetCurvePoint,
             UtilityGetNearestFactorOnCurve,
             UtilityKDChoosePoint,
             UtilityKDChooseXForm,
             UtilityMetaRigNode,
             UtilityBonePropertiesNode,
             UtilityDriverVariableNode,
             UtilityFCurveNode,
             UtilityDriverNode,
             UtilitySwitchNode,
             UtilityKeyframe,
             UtilityCombineThreeBoolNode,
             UtilityCombineVectorNode,
             UtilitySeparateVector,
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
             UtilityMatrixInvert,
             UtilityMatrixCompose,
             UtilityMatrixAlignRoll,
             UtilityTransformationMatrix,
             UtilitySetBoneMatrixTail,

             UtilityIntToString,
             UtilityArrayGet,
             UtilityArrayLength,
             #
             UtilityCompare,
             UtilityChoose,
             # for testing
             UtilityPrint,
            ]


def default_traverse(self,socket):
    return None

def socket_data_from_collection_paths(root_data, root_name, path, socket_data):
    # so we need to 'push' the socket names and their paths in order
    # socket_data is a list of tuples of ( name, path, )
    for key, value in root_data.items():
        path.append(key)
        socket_data.append( (key, path))
        if hasattr(value , 'items'):
            socket_data = socket_data_from_collection_paths(value, key, path.copy(), socket_data)
        path.pop()
    return socket_data

class InputFloatNode(Node, MantisUINode):
    '''A node representing inheritance'''
    bl_idname = 'InputFloatNode'
    bl_label = "Float"
    mantis_node_class_name=bl_idname[:-4]

    def init(self, context):
        self.init_sockets(InputFloatSockets)
        self.initialized = True

class InputIntNode(Node, MantisUINode):
    '''A node representing inheritance'''
    bl_idname = 'InputIntNode'
    bl_label = "Integer"
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(InputIntSockets)
        self.initialized = True
    
class InputVectorNode(Node, MantisUINode):
    '''A node representing inheritance'''
    bl_idname = 'InputVectorNode'
    bl_label = "Vector"
    mantis_node_class_name=bl_idname[:-4]

    def init(self, context):
        self.init_sockets(InputVectorSockets)
        self.initialized = True

class InputBooleanNode(Node, MantisUINode):
    '''A node representing inheritance'''
    bl_idname = 'InputBooleanNode'
    bl_label = "Boolean"
    mantis_node_class_name=bl_idname[:-4]

    def init(self, context):
        self.init_sockets(InputBooleanSockets)
        self.initialized = True

class InputBooleanThreeTupleNode(Node, MantisUINode):
    '''A node representing inheritance'''
    bl_idname = 'InputBooleanThreeTupleNode'
    bl_label = "Boolean Vector"
    mantis_node_class_name=bl_idname[:-4]

    def init(self, context):
        self.init_sockets(InputBooleanThreeTupleSockets)
        self.initialized = True

class InputRotationOrderNode(Node, MantisUINode):
    '''A node representing inheritance'''
    bl_idname = 'InputRotationOrderNode'
    bl_label = "Rotation Order"
    mantis_node_class_name=bl_idname[:-4]

    def init(self, context):
        self.init_sockets(InputRotationOrderSockets)
        self.initialized = True

class InputTransformSpaceNode(Node, MantisUINode):
    '''A node representing inheritance'''
    bl_idname = 'InputTransformSpaceNode'
    bl_label = "Transform Space"
    mantis_node_class_name=bl_idname[:-4]

    def init(self, context):
        self.init_sockets(InputTransformSpaceSockets)
        self.initialized = True

class InputStringNode(Node, MantisUINode):
    '''A node representing inheritance'''
    bl_idname = 'InputStringNode'
    bl_label = "String"
    mantis_node_class_name=bl_idname[:-4]

    def init(self, context):
        self.init_sockets(InputStringSockets)
        self.initialized = True

class InputMatrixNode(Node, MantisUINode):
    '''A node representing inheritance'''
    bl_idname = 'InputMatrixNode'
    bl_label = "Matrix"
    first_row  : bpy.props.FloatVectorProperty(name="", size=4, default = (1.0, 0.0, 0.0, 0.0,))
    second_row : bpy.props.FloatVectorProperty(name="", size=4, default = (0.0, 1.0, 0.0, 0.0,))
    third_row  : bpy.props.FloatVectorProperty(name="", size=4, default = (0.0, 0.0, 1.0, 0.0,))
    fourth_row : bpy.props.FloatVectorProperty(name="", size=4, default = (0.0, 0.0, 0.0, 1.0,))
    mantis_node_class_name=bl_idname[:-4]

    def init(self, context):
        self.init_sockets(InputMatrixSockets)
        self.initialized = True

    def set_matrix(self):
        return (self.first_row[ 0], self.first_row[ 1], self.first_row[ 2], self.first_row[ 3],
                self.second_row[0], self.second_row[1], self.second_row[2], self.second_row[3],
                self.third_row[ 0], self.third_row[ 1], self.third_row[ 2], self.third_row[ 3],
                self.fourth_row[0], self.fourth_row[1], self.fourth_row[2], self.fourth_row[3],)

    def draw_buttons(self, context, layout):
        # return
        layout.prop(self, "first_row")
        layout.prop(self, "second_row")
        layout.prop(self, "third_row")
        layout.prop(self, "fourth_row")

    def update(self):
        mat_sock = self.outputs[0]
        mat_sock.default_value = self.set_matrix()

class InputThemeBoneColorSets(Node, MantisUINode):
    """Displays the theme's colors."""
    bl_idname = "InputThemeBoneColorSets"
    bl_label = "Theme Colors"
    bl_width_min=280
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        for i in range(20):
            s = self.outputs.new("ColorSetDisplaySocket", f"Color {str(i).zfill(2)}")
            s.color_index=i
        self.initialized = True

class InputColorSetPallete(Node, MantisUINode):
    """Displays the theme's colors."""
    bl_idname = "InputColorSetPallete"
    bl_label = "Color Pallete"
    bl_width_min=280
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.initialized = True
    
    def draw_buttons(self, context, layout):
        ops_props = layout.operator('mantis.color_pallete_socket_add')
        ops_props.tree_invoked = self.id_data.name
        ops_props.node_invoked = self.name

class UtilityMatrixFromCurve(Node, MantisUINode):
    """Gets a matrix from a curve."""
    bl_idname = "UtilityMatrixFromCurve"
    bl_label = "Matrix from Curve"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(MatrixFromCurveSockets)
        self.initialized = True

class UtilityPointFromCurve(Node, MantisUINode):
    """Gets a point from a curve."""
    bl_idname = "UtilityPointFromCurve"
    bl_label = "Point from Curve"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(PointFromCurveSockets)
        self.initialized = True

class UtilityNumberOfCurveSegments(Node, MantisUINode):
    """Tells the number of segments in a curve."""
    bl_idname = "UtilityNumberOfCurveSegments"
    bl_label = "Number of Curve Segments"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(NumberOfCurveSegmentsSockets)
        self.initialized = True
    
class UtilityNumberOfSplines(Node, MantisUINode):
    """Tells the number of splines in a curve."""
    bl_idname = "UtilityNumberOfSplines"
    bl_label = "Number of Splines"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(NumberOfSplinesSockets)
        self.initialized = True

class UtilityMatrixFromCurveSegment(Node, MantisUINode):
    """Gets a matrix from a curve segment."""
    bl_idname = "UtilityMatrixFromCurveSegment"
    bl_label = "Matrix from Curve Segment"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(MatrixFromCurveSegmentSockets)
        self.initialized = True

class UtilityGetCurvePoint(Node, MantisUINode):
    bl_idname = 'UtilityGetCurvePoint'
    bl_label = "Control Point from Curve"
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(GetCurvePointSockets)
        self.initialized = True

    def display_update(self, parsed_tree, context):
        self.outputs["Point"].hide=False
        self.outputs["Left Handle"].hide=True
        self.outputs["Right Handle"].hide=True
        spline_index = self.inputs['Spline Index'].default_value
        index = self.inputs['Index'].default_value
        curve = self.inputs['Curve'].default_value
        if self.inputs['Spline Index'].is_linked or self.inputs['Index'].is_linked \
            or self.inputs['Curve'].is_linked:
            mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
            spline_index = mantis_node.evaluate_input("Spline Index")
            index = mantis_node.evaluate_input("Index")
            curve = mantis_node.evaluate_input("Curve")
        if curve := bpy.data.objects.get(curve):
            if curve.type != "CURVE":
                self.outputs["Point"].hide=True
            spline = curve.data.splines[spline_index]
            if spline.type == 'BEZIER':
                self.outputs["Left Handle"].hide=False
                self.outputs["Right Handle"].hide=False
    
class UtilityMatricesFromCurve(Node, MantisUINode):
    """Gets a matrix from a curve."""
    bl_idname = "UtilityMatricesFromCurve"
    bl_label = "Matrices from Curve"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(MatricesFromCurveSockets)
        self.initialized = True

def display_update_choose_nearest(self, parsed_tree, context):
    number_of_points = self.inputs['Number to Find'].default_value
    if self.inputs["Number to Find"].is_linked:
        mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
        number_of_points = mantis_node.evaluate_input("Number to Find")
    elif number_of_points == 0:
        self.inputs['Number to Find'].default_value=1
    if number_of_points > 1:
        # then we need to make it an array out
        self.outputs.display_shape = 'SQUARE_DOT'
    else:
        self.outputs.display_shape = 'CIRCLE'

class UtilityGetNearestFactorOnCurve(Node, MantisUINode):
    bl_idname = 'UtilityGetNearestFactorOnCurve'
    bl_label = "Get Factor on Curve at Point"
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(GetNearestFactorOnCurveSockets)
        self.initialized = True

class UtilityKDChoosePoint(Node, MantisUINode):
    """Chooses the nearest point with a KD Tree."""
    bl_idname = "UtilityKDChoosePoint"
    bl_label = "Choose Nearest Point"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(KDChoosePointSockets)
        self.initialized = True
    
    def display_update(self, parsed_tree, context):
        display_update_choose_nearest(self, parsed_tree, context)

class UtilityKDChooseXForm(Node, MantisUINode):
    """Chooses the nearest xForm with a KD Tree."""
    bl_idname = "UtilityKDChooseXForm"
    bl_label = "Choose Nearest xForm"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(KDChooseXFormSockets)
        self.initialized = True
    
    def display_update(self, parsed_tree, context):
        display_update_choose_nearest(self, parsed_tree, context)

class UtilityMetaRigNode(Node, MantisUINode):
    """Gets a matrix from a meta-rig bone."""
    bl_idname = "UtilityMetaRig"
    bl_label = "Meta-Rig"
    armature:bpy.props.StringProperty()
    pose_bone:bpy.props.StringProperty()
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(MetaRigSockets)
        self.initialized = True
    
    def display_update(self, parsed_tree, context):
        mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
        if mantis_node:
            self.armature= mantis_node.evaluate_input("Meta-Armature")
            self.pose_bone= mantis_node.evaluate_input("Meta-Bone")
        if not self.armature:
            self.inputs["Meta-Bone"].hide=True
        else:
            self.inputs["Meta-Bone"].hide=False
        if self.inputs["Meta-Armature"].is_linked:
            self.inputs["Meta-Armature"].search_prop = None
        if self.inputs["Meta-Bone"].is_linked:
            self.inputs["Meta-Bone"].search_prop = None

class UtilityBonePropertiesNode(Node, MantisUINode):
    """Provides as sockets strings identifying bone transform properties."""
    bl_idname = "UtilityBoneProperties"
    bl_label = "Bone Properties"
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(BonePropertiesSockets)
        self.initialized = True
        

class UtilityDriverVariableNode(Node, MantisUINode):
    """Creates a variable for use in a driver."""
    bl_idname = "UtilityDriverVariable"
    bl_label = "Driver Variable"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(DriverVariableSockets)
        self.initialized = True
    
    def display_update(self, parsed_tree, context):
        if self.inputs["Variable Type"].is_linked:
            if context.space_data:
                node_tree = context.space_data.path[0].node_tree
                mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
                if mantis_node:
                    driver_type = mantis_node.evaluate_input("Variable Type")
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
class UtilityFCurveNode(Node, MantisUINode):
    """Creates an fCurve for use with a driver."""
    bl_idname = "UtilityFCurve"
    bl_label = "fCurve"
    
    use_kf_nodes   : bpy.props.BoolProperty(default=True)
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(FCurveSockets)
        self.initialized = True
            
    def draw_buttons(self, context, layout):
        layout.operator( 'mantis.fcurve_node_add_kf' )
        if (len(self.inputs) > 1):
            layout.operator( 'mantis.fcurve_node_remove_kf' )


class UtilityDriverNode(Node, MantisUINode):
    """Represents a Driver relationship"""
    bl_idname = "UtilityDriver"
    bl_label = "Driver"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(DriverSockets)
        self.initialized = True
        
    def display_update(self, parsed_tree, context):
        if not self.inputs["Driver Type"].is_linked:
            dType = self.inputs["Driver Type"].default_value
        mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
        if mantis_node:
            dType = mantis_node.evaluate_input("Driver Type")
        if dType == 'SCRIPTED':
            self.inputs["Expression"].hide = False
        else:
            self.inputs["Expression"].hide = True
    
    def draw_buttons(self, context, layout):
        # return
        layout.operator( 'mantis.driver_node_add_variable' )
        if (len(self.inputs) > 3):
            layout.operator( 'mantis.driver_node_remove_variable' )

class UtilitySwitchNode(Node, MantisUINode):
    """Represents a switch relationship between one driver property and one or more driven properties."""
    bl_idname = "UtilitySwitch"
    bl_label = "Switch"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(SwitchSockets)
        self.initialized = True

class UtilityCombineThreeBoolNode(Node, MantisUINode):
    """Combines three booleans into a three-bool."""
    bl_idname = "UtilityCombineThreeBool"
    bl_label = "CombineThreeBool"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(CombineThreeBoolSockets)
        self.initialized = True

class UtilityCombineVectorNode(Node, MantisUINode):
    """Combines three floats into a vector."""
    bl_idname = "UtilityCombineVector"
    bl_label = "CombineVector"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(CombineVectorSockets)
        
class UtilitySeparateVector(Node, MantisUINode):
    """Separates a vector into three floats"""
    bl_idname = "UtilitySeparateVector"
    bl_label = "Separate Vector"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(SeparateVectorSockets)
        self.initialized = True
        
class UtilityCatStringsNode(Node, MantisUINode):
    """Combines multiple strings into one."""
    bl_idname = "UtilityCatStrings"
    bl_label = "Join Strings"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(CatStringsSockets)
        self.initialized = True

    def draw_label(self): # this will prefer a user-set label, or return the evaluated name
        if self.label:
            return self.label
        if self.outputs['OutputString'].display_text:
            return self.outputs['OutputString'].display_text
        return self.name
        
    def display_update(self, parsed_tree, context):
        if context.space_data:
            mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
            self.inputs['String_1'].display_text = ""
            self.inputs['String_2'].display_text = ""
            self.outputs['OutputString'].display_text = ""
            if mantis_node:
                try:
                    self.inputs['String_1'].display_text = a = mantis_node.evaluate_input("String_1")
                    self.inputs['String_2'].display_text = b = mantis_node.evaluate_input("String_2")
                    # cat the strings here, since the node may not have run yet.
                    self.outputs['OutputString'].display_text = a+b
                except KeyError:
                    return # the tree isn't ready yet.
                

class InputWidget(Node, MantisUINode):
    """Fetches a Widget from the Widget Library."""
    bl_idname = "InputWidget"
    bl_label = "Widget"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(InputWidgetSockets)
        self.initialized = True
    
class InputExistingGeometryObjectNode(Node, MantisUINode):
    """Represents an existing geometry object from within the scene."""
    bl_idname = "InputExistingGeometryObject"
    bl_label = "Existing Object"
    mantis_node_class_name=bl_idname
    # We want Mantis to import widgets and stuff, so we hold a reference to the object
    object_reference : bpy.props.PointerProperty(type=bpy.types.Object,) 
    
    def init(self, context):
        self.init_sockets(InputExistingGeometryObjectSockets)
        self.initialized = True
    
    def display_update(self, parsed_tree, context):
        mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
        if mantis_node: # this is done here so I don't have to define yet another custom socket.
            self.object_reference = bpy.data.objects.get(mantis_node.evaluate_input("Name"))
    
# TODO: maybe I should hold a data reference here, too.
#       but it is complicated by the fact that Mantis does not distinguish b/tw geo types
class InputExistingGeometryDataNode(Node, MantisUINode):
    """Represents a mesh or curve datablock from the scene."""
    bl_idname = "InputExistingGeometryData"
    bl_label = "Existing Geometry"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(InputExistingGeometrySockets)
        self.initialized = True

class UtilityCustomProperty(Node, MantisUINode):
    """A declaration of a custom property."""
    bl_idname = "UtilityCustomProperty"
    bl_label  = "Custom Property"
    bl_icon   = "NODE"
    mantis_node_class_name=bl_idname
    def init(self, context):
        self.init_sockets(UtilityCustomPropertySockets)
        self.initialized = True
    
    def display_update(self, parsed_tree, context):
        mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
        prop_type = self.inputs['Type'].default_value
        if mantis_node: # this is done here so I don't have to define yet another custom socket.
            prop_type = mantis_node.evaluate_input("Type")
        visible_categories = ['general']
        match prop_type:
            case 'STRING': visible_categories.append('string')
            case 'BOOL': visible_categories.append('bool')
            case 'INT': visible_categories.append('int')
            case 'FLOAT': visible_categories.append('float')
            case 'VECTOR': visible_categories.append('vector')
        for i, socket_template in enumerate(UtilityCustomPropertySockets):
            if socket_template.is_input == False: continue
            if socket_template.category in visible_categories:
                self.inputs[i].hide = False
            else:
                self.inputs[i].hide = True
        if prop_type == "VECTOR":
            for i in range (4): # keep the min/max open
                self.inputs[i+3].hide=False
    
    def draw_label(self): # this will prefer a user-set label, or return the evaluated name
        if self.label:
            return self.label
        if self.inputs['Name'].display_text:
            return self.inputs['Name'].display_text
        return self.name

class UtilityDeclareCollections(Node, MantisUINode):
    """A utility used to declare bone collections."""
    bl_idname = "UtilityDeclareCollections"
    bl_label  = "Collections"
    bl_icon   = "NODE"
    bl_width_min = 320
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname
    # Here is the layout of the data:
    # nested dicts of key:dict ( key = name, dict = children)
    # the 'leaf nodes' are empty dicts
    # we'll store it as a JSON string in order to make it a bpy.props 
    # and still have the ability to use it as a dict and save it
    # TODO: check and see if these strings have a character limit
    collection_declarations : bpy.props.StringProperty(default="")

    def update_interface(self):
        from .utilities import get_socket_maps, do_relink
        # we need to do dynamic stuff here like with interfaces
        socket_map_out = get_socket_maps(self)[1]
        self.outputs.clear()
        current_data = self.read_declarations_from_json()
        socket_data = socket_data_from_collection_paths(current_data, self.name, [], [])
        for item in socket_data:
            full_path_name = '>'.join(item[1]+[item[0]])
            s = self.outputs.new('CollectionDeclarationSocket', name=item[0],identifier=full_path_name )
            s.collection_path = full_path_name
        for s in self.outputs:
            if s.identifier in socket_map_out.keys():
                do_relink(self, s, socket_map_out, 'OUTPUT')
        
    def init(self, context):
        self.initialized = True
        if self.collection_declarations == "":
            self.push_declarations_to_json({})
    
    def push_declarations_to_json(self, dict):
        import json
        j_str = json.dumps(dict)
        self.collection_declarations = j_str

    def read_declarations_from_json(self):
        import json
        j_data = json.loads(self.collection_declarations)
        return j_data
    
    def draw_buttons(self, context, layout):
        op_props = layout.operator('mantis.collection_add_new')
        op_props.socket_invoked = '' # this isn't reset between invocations
        # so we have to make sure to unset it when running it from the node

class UtilityCollectionJoin(Node, MantisUINode):
    """A utility used to join bone collection declarations."""
    bl_idname = "UtilityCollectionJoin"
    bl_label  = "Join Collection Declarations"
    bl_icon   = "NODE"
    mantis_node_class_name=bl_idname
    def init(self, context):
        self.init_sockets(CollectionJoinSockets)
        self.initialized = True

class UtilityCollectionHierarchy(Node, MantisUINode):
    """A utility used to declare bone collection hierarchies."""
    bl_idname = "UtilityCollectionHierarchy"
    bl_label  = "Collection Child Declaration"
    bl_icon   = "NODE"
    mantis_node_class_name=bl_idname
    def init(self, context):
        self.init_sockets(CollectionHierarchySockets)
        self.initialized = True
        
class UtilityGeometryOfXForm(Node, MantisUINode):
    """Retrieves a mesh or curve datablock from an xForm."""
    bl_idname = "UtilityGeometryOfXForm"
    bl_label = "Geometry of xForm"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(GeometryOfXFormSockets)
        self.initialized = True


class UtilityNameOfXForm(Node, MantisUINode):
    """Retrieves the name of a xForm."""
    bl_idname = "UtilityNameOfXForm"
    bl_label = "Name of xForm"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(NameOfXFormSockets)
        self.initialized = True

class UtilityGetBoneLength(Node, MantisUINode):
    """Returns the length of the bone from its matrix."""
    bl_idname = "UtilityGetBoneLength"
    bl_label = "Get Bone Length"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(GetBoneLengthSockets)
        self.initialized = True

# TODO: make it work with BBones!
class UtilityPointFromBoneMatrix(Node, MantisUINode):
    """Returns a point representing the location along a bone, given a matrix representing that bone's shape."""
    bl_idname = "UtilityPointFromBoneMatrix"
    bl_label = "Point from Bone Matrix"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(PointFromBoneMatrixSockets)
        self.initialized = True

class UtilitySetBoneLength(Node, MantisUINode):
    """Sets the length of a bone matrix."""
    bl_idname = "UtilitySetBoneLength"
    bl_label = "Set Bone Matrix Length"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(SetBoneLengthSockets)
        self.initialized = True

# TODO: more keyframe types should be supported in the future.
# Some of the code that can do this is commented out here until I can implement it properly.
class UtilityKeyframe(Node, MantisUINode):
    """A keyframe for a FCurve"""
    bl_idname = "UtilityKeyframe"
    bl_label = "KeyFrame"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(KeyframeSockets)
        self.initialized = True

    # TODO: I'll implement this when I finish adding the extra features to the Keyframe node
    # def display_update(self, parsed_tree, context):
    #     if context.space_data:
    #         mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
    #         if mantis_node.evaluate_input("Interpolation") in ["CONSTANT", "LINEAR"]:
    #             for inp in self.inputs[1:6]:
    #                 inp.hide = True
    #         else:
    #             if mantis_node.evaluate_input("Left Handle Type") in ["FREE", "ALIGNED"]:

    #             for inp in self.inputs[1:6]:
    #                 inp.hide = False


class UtilityBoneMatrixHeadTailFlip(Node, MantisUINode):
    """Flips a bone matrix so that the head is where the tail was and visa versa."""
    bl_idname = "UtilityBoneMatrixHeadTailFlip"
    bl_label = "Flip Head/Tail"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(BoneMatrixHeadTailFlipSockets)
        self.initialized = True

class UtilityMatrixTransform(Node, MantisUINode):
    """Transforms a matrix by another."""
    bl_idname = "UtilityMatrixTransform"
    bl_label = "Multiply Matrices"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(MatrixTransformSockets)
        self.initialized = True

class UtilityMatrixInvert(Node, MantisUINode):
    """Inverts an invertable matrix, otherwise throws an error."""
    bl_idname = "UtilityMatrixInvert"
    bl_label = "Invert Matrix"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(MatrixInvertSockets)
        self.initialized = True

class UtilityMatrixCompose(Node, MantisUINode):
    """Inverts an invertable matrix, otherwise throws an error."""
    bl_idname = "UtilityMatrixCompose"
    bl_label = "Compose Matrix"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(MatrixComposeSockets)
        self.initialized = True

class UtilityMatrixAlignRoll(Node, MantisUINode):
    """Aligns the Z axis of a matrix to point in a direction."""
    bl_idname = "UtilityMatrixAlignRoll"
    bl_label = "Align Matrix Roll"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(MatrixAlignRollSockets)
        self.initialized = True

class UtilityMatrixSetLocation(Node, MantisUINode):
    """Sets a matrix's location."""
    bl_idname = "UtilityMatrixSetLocation"
    bl_label = "Set Matrix Location"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(MatrixSetLocationSockets)
        self.initialized = True

class UtilityMatrixGetLocation(Node, MantisUINode):
    """Gets a matrix's location."""
    bl_idname = "UtilityMatrixGetLocation"
    bl_label = "Get Matrix Location"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(MatrixGetLocationSockets)
        self.initialized = True

class UtilityTransformationMatrix(Node, MantisUINode):
    """Constructs a matrix representing a transformation"""
    bl_idname = "UtilityTransformationMatrix"
    bl_label = "Transformation Matrix"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        # first input is a transformation type - translation, rotation, or scale
        #                         rotation is an especially annoying feature because it can take multiple types
        #   so Euler, axis/angle, quaternion, matrix...
        #   for now I am only going to implement axis-angle
        self.init_sockets(TransformationMatrixSockets)
        self.initialized = True

    def display_update(self, parsed_tree, context):
        operation = self.inputs['Operation'].default_value
        if self.inputs['Operation'].is_linked:
            if context.space_data:
                mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
                operation = mantis_node.evaluate_input("Operation")
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

class UtilitySetBoneMatrixTail(Node, MantisUINode):
    """Constructs a matrix representing a transformation"""
    bl_idname = "UtilitySetBoneMatrixTail"
    bl_label = "Set Bone Matrix Tail"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(SetBoneMatrixTailSockets)
        self.initialized = True


class UtilityMatrixFromXForm(Node, MantisUINode):
    """Returns the matrix of the given xForm node."""
    bl_idname = "UtilityMatrixFromXForm"
    bl_label = "Matrix of xForm"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(MatrixFromXFormSockets)
        self.initialized = True

class UtilityAxesFromMatrix(Node, MantisUINode):
    """Returns the axes of the matrix."""
    bl_idname = "UtilityAxesFromMatrix"
    bl_label = "Axes of Matrix"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(AxesFromMatrixSockets)
        self.initialized = True

class UtilityIntToString(Node, MantisUINode):
    """Converts a number to a string"""
    bl_idname = "UtilityIntToString"
    bl_label = "Number String"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(IntToStringSockets)
        self.initialized = True


class UtilityArrayGet(Node, MantisUINode):
    """Gets a value from an array at a specified index."""
    bl_idname = "UtilityArrayGet"
    bl_label  = "Array Get"
    bl_icon   = "NODE"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(ArrayGetSockets)
        self.initialized = True
    
    def update(self):
        wildcard_color = (0.0,0.0,0.0,0.0)
        if self.inputs['Array'].is_linked == False:
            self.inputs['Array'].color = wildcard_color
            self.outputs['Output'].color = wildcard_color

    def insert_link(self, link):
        super().insert_link(link)
        if link.to_socket.identifier == self.inputs['Array'].identifier:
            from_socket = link.from_socket
            if hasattr(from_socket, "color"):
                self.inputs['Array'].color = from_socket.color
                self.outputs['Output'].color = from_socket.color

class UtilityArrayLength(Node, MantisUINode):
    """Gets The length of an array."""
    bl_idname = "UtilityArrayLength"
    bl_label  = "Array Length"
    bl_icon   = "NODE"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        s = self.init_sockets(UtilityArrayLengthSockets)
        self.initialized = True
    
    def update(self):
        wildcard_color = (0.0,0.0,0.0,0.0)
        if self.inputs['Array'].is_linked == False:
            self.inputs['Array'].color = wildcard_color

    def insert_link(self, link):
        super().insert_link(link)
        if link.to_socket.identifier == self.inputs['Array'].identifier:
            from_socket = link.from_socket
            if hasattr(from_socket, "color"):
                self.inputs['Array'].color = from_socket.color


class UtilityCompare(Node, MantisUINode):
    """Compares two inputs and produces a boolean output"""
    bl_idname = "UtilityCompare"
    bl_label = "Compare"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(CompareSockets)
        self.initialized = True
    
    def update(self):
        wildcard_color = (0.0,0.0,0.0,0.0)
        if self.inputs['A'].is_linked == False:
            self.inputs['A'].color = wildcard_color
        if self.inputs['B'].is_linked == False:
            self.inputs['B'].color = wildcard_color

    def insert_link(self, link):
        super().insert_link(link)
        if link.to_socket.identifier == self.inputs['A'].identifier:
            self.inputs['A'].color = link.from_socket.color_simple
            if hasattr(link.from_socket, "color"):
                self.inputs['A'].color = link.from_socket.color
        if link.to_socket.identifier == self.inputs['B'].identifier:
            self.inputs['B'].color = link.from_socket.color_simple
            if hasattr(link.from_socket, "color"):
                self.inputs['B'].color = link.from_socket.color

class UtilityChoose(Node, MantisUINode):
    """Chooses an output"""
    bl_idname = "UtilityChoose"
    bl_label = "Choose"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(ChooseSockets)
        self.initialized = True
    
    def display_update(self, parsed_tree, context):
        wildcard_color = (0.0,0.0,0.0,0.0)
        if not self.inputs['A'].is_linked:
            self.inputs['A'].color = wildcard_color
        if not self.inputs['B'].is_linked:
            self.inputs['B'].color = wildcard_color
        self.outputs['Result'].color = wildcard_color
        # if both inputs are the same color, then use that color for the result
        if self.inputs['Condition'].is_linked:
            from .base_definitions import get_signature_from_edited_tree
            mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
            if mantis_node:
                condition = mantis_node.evaluate_input('Condition')
        else:
            condition = self.inputs['Condition'].default_value
        if condition == True:
            self.outputs['Result'].color = self.inputs['B'].color
        else:
            self.outputs['Result'].color = self.inputs['A'].color

    def insert_link(self, link):
        super().insert_link(link)
        if link.to_socket.identifier == self.inputs['A'].identifier:
            self.inputs['A'].color = link.from_socket.color_simple
            if hasattr(link.from_socket, "color"):
                self.inputs['A'].color = link.from_socket.color
        if link.to_socket.identifier == self.inputs['B'].identifier:
            self.inputs['B'].color = link.from_socket.color_simple
            if hasattr(link.from_socket, "color"):
                self.inputs['B'].color = link.from_socket.color


class UtilityPrint(Node, MantisUINode):
    """A utility used to print arbitrary values."""
    bl_idname = "UtilityPrint"
    bl_label  = "Print"
    bl_icon   = "NODE"
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(PrintSockets)
        self.initialized = True

# Set up the class property that ties the UI classes to the Mantis classes.
for cls in TellClasses():
    cls.mantis_node_library='.misc_nodes'
    cls.set_mantis_class()
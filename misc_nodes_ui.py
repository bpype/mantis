import bpy
from bpy.types import Node
from .base_definitions import MantisMiscNode, get_signature_from_edited_tree
from .misc_nodes_socket_templates import *

from .utilities.utilities import (prRed, prGreen, prPurple, prWhite,
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

#################################################
# Base Classes for the Misc Nodes
#################################################

class SimpleInputNode(MantisMiscNode):
    def init(self, context):
        super().init(context)
        for s in self.outputs:
            s.input=True # give it the property that makes it draw correctly

class InputFloatNode(Node, SimpleInputNode):
    '''A node representing inheritance'''
    bl_idname = 'InputFloatNode'
    bl_label = "Float"
    mantis_node_class_name=bl_idname[:-4]
    socket_templates=InputFloatSockets

class InputIntNode(Node, SimpleInputNode):
    '''A node representing inheritance'''
    bl_idname = 'InputIntNode'
    bl_label = "Integer"
    mantis_node_class_name=bl_idname
    socket_templates=InputIntSockets
    
class InputVectorNode(Node, SimpleInputNode):
    '''A node representing inheritance'''
    bl_idname = 'InputVectorNode'
    bl_label = "Vector"
    mantis_node_class_name=bl_idname[:-4]
    socket_templates=InputVectorSockets

class InputBooleanNode(Node, SimpleInputNode):
    '''A node representing inheritance'''
    bl_idname = 'InputBooleanNode'
    bl_label = "Boolean"
    mantis_node_class_name=bl_idname[:-4]
    socket_templates=InputBooleanSockets

class InputBooleanThreeTupleNode(Node, SimpleInputNode):
    '''A node representing inheritance'''
    bl_idname = 'InputBooleanThreeTupleNode'
    bl_label = "Boolean Vector"
    mantis_node_class_name=bl_idname[:-4]
    socket_templates=InputBooleanThreeTupleSockets

class InputRotationOrderNode(Node, SimpleInputNode):
    '''A node representing inheritance'''
    bl_idname = 'InputRotationOrderNode'
    bl_label = "Rotation Order"
    mantis_node_class_name=bl_idname[:-4]
    socket_templates=InputRotationOrderSockets

class InputTransformSpaceNode(Node, SimpleInputNode):
    '''A node representing inheritance'''
    bl_idname = 'InputTransformSpaceNode'
    bl_label = "Transform Space"
    mantis_node_class_name=bl_idname[:-4]
    socket_templates=InputTransformSpaceSockets

class InputStringNode(Node, SimpleInputNode):
    '''A node representing inheritance'''
    bl_idname = 'InputStringNode'
    bl_label = "String"
    mantis_node_class_name=bl_idname[:-4]
    socket_templates=InputStringSockets

class InputMatrixNode(Node, SimpleInputNode):
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

class InputThemeBoneColorSets(Node, MantisMiscNode):
    """Displays the theme's colors."""
    bl_idname = "InputThemeBoneColorSets"
    bl_label = "Theme Colors"
    bl_width_min=280
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        for i in range(20):
            s = self.outputs.new("ColorSetDisplaySocket", f"Color {str(i).zfill(2)}")
            s.color_index=i
        self.initialized = True

class InputColorSetPallete(Node, MantisMiscNode):
    """Displays the theme's colors."""
    bl_idname = "InputColorSetPallete"
    bl_label = "Color Pallete"
    bl_width_min=280
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.initialized = True
    
    def draw_buttons(self, context, layout):
        ops_props = layout.operator('mantis.color_pallete_socket_add')
        ops_props.tree_invoked = self.id_data.name
        ops_props.node_invoked = self.name

class UtilityMatrixFromCurve(Node, MantisMiscNode):
    """Gets a matrix from a curve."""
    bl_idname = "UtilityMatrixFromCurve"
    bl_label = "Matrix from Curve"
    mantis_node_class_name=bl_idname
    socket_templates=MatrixFromCurveSockets

    def display_update(self, parsed_tree, context):
        # first we'll checc if the mode is connected to a noodle, should be rare
        mode = 'DIVISIONS'
        if self.inputs['Mode'].is_linked:
            if mantis_node := parsed_tree.get(get_signature_from_edited_tree(self, context)):
                mode = mantis_node.evaluate_input("Mode")
        else: # We can use it directly, this is a little faster.
            mode = self.inputs['Mode'].default_value
        # We just hide/show based on the selected mode.
        for template in self.__class__.socket_templates:
            if mode == 'DIVISIONS' and template.category == 'factor':
                self.inputs[template.name].hide=True
            if mode == 'DIVISIONS' and template.category == 'divisions':
                self.inputs[template.name].hide=False
            elif mode == 'FACTOR' and template.category == 'divisions':
                self.inputs[template.name].hide=True
            elif mode == 'FACTOR' and template.category == 'factor':
                self.inputs[template.name].hide=False

class UtilityPointFromCurve(Node, MantisUINode):
    """Gets a point from a curve."""
    bl_idname = "UtilityPointFromCurve"
    bl_label = "Point from Curve"
    mantis_node_class_name=bl_idname
    socket_templates=PointFromCurveSockets

class UtilityNumberOfCurveSegments(Node, MantisMiscNode):
    """Tells the number of segments in a curve."""
    bl_idname = "UtilityNumberOfCurveSegments"
    bl_label = "Number of Curve Segments"
    mantis_node_class_name=bl_idname
    socket_templates=NumberOfCurveSegmentsSockets
    
class UtilityNumberOfSplines(Node, MantisMiscNode):
    """Tells the number of splines in a curve."""
    bl_idname = "UtilityNumberOfSplines"
    bl_label = "Number of Splines"
    mantis_node_class_name=bl_idname
    socket_templates=NumberOfSplinesSockets

class UtilityMatrixFromCurveSegment(Node, MantisMiscNode):
    """Gets a matrix from a curve segment."""
    bl_idname = "UtilityMatrixFromCurveSegment"
    bl_label = "Matrix from Curve Segment"
    mantis_node_class_name=bl_idname
    socket_templates=MatrixFromCurveSegmentSockets

class UtilityGetCurvePoint(Node, MantisMiscNode):
    bl_idname = 'UtilityGetCurvePoint'
    bl_label = "Control Point from Curve"
    mantis_node_class_name=bl_idname
    socket_templates=GetCurvePointSockets

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
    
class UtilityMatricesFromCurve(Node, MantisMiscNode):
    """Gets a matrix from a curve."""
    bl_idname = "UtilityMatricesFromCurve"
    bl_label = "Matrices from Curve"
    mantis_node_class_name=bl_idname
    socket_templates=MatricesFromCurveSockets

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

class UtilityGetNearestFactorOnCurve(Node, MantisMiscNode):
    bl_idname = 'UtilityGetNearestFactorOnCurve'
    bl_label = "Get Factor on Curve at Point"
    mantis_node_class_name=bl_idname
    socket_templates=GetNearestFactorOnCurveSockets

class UtilityKDChoosePoint(Node, MantisMiscNode):
    """Chooses the nearest point with a KD Tree."""
    bl_idname = "UtilityKDChoosePoint"
    bl_label = "Choose Nearest Point"
    mantis_node_class_name=bl_idname
    socket_templates=KDChoosePointSockets
    
    def display_update(self, parsed_tree, context):
        display_update_choose_nearest(self, parsed_tree, context)

class UtilityKDChooseXForm(Node, MantisMiscNode):
    """Chooses the nearest xForm with a KD Tree."""
    bl_idname = "UtilityKDChooseXForm"
    bl_label = "Choose Nearest xForm"
    mantis_node_class_name=bl_idname
    socket_templates=KDChooseXFormSockets
    
    def display_update(self, parsed_tree, context):
        display_update_choose_nearest(self, parsed_tree, context)

class UtilityMetaRigNode(Node, MantisMiscNode):
    """Gets a matrix from a meta-rig bone."""
    bl_idname = "UtilityMetaRig"
    bl_label = "Meta-Rig"
    armature:bpy.props.StringProperty()
    pose_bone:bpy.props.StringProperty()
    mantis_node_class_name=bl_idname
    socket_templates=MetaRigSockets
    
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

class UtilityBonePropertiesNode(Node, MantisMiscNode):
    """Provides as sockets strings identifying bone transform properties."""
    bl_idname = "UtilityBoneProperties"
    bl_label = "Bone Properties"
    mantis_node_class_name=bl_idname
    socket_templates=BonePropertiesSockets
        

class UtilityDriverVariableNode(Node, MantisMiscNode):
    """Creates a variable for use in a driver."""
    bl_idname = "UtilityDriverVariable"
    bl_label = "Driver Variable"
    mantis_node_class_name=bl_idname
    socket_templates=DriverVariableSockets

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
class UtilityFCurveNode(Node, MantisMiscNode):
    """Creates an fCurve for use with a driver."""
    bl_idname = "UtilityFCurve"
    bl_label = "fCurve"
    mantis_node_class_name=bl_idname
    socket_templates=FCurveSockets
    use_kf_nodes   : bpy.props.BoolProperty(default=True)

class UtilityDriverNode(Node, MantisMiscNode):
    """Represents a Driver relationship"""
    bl_idname = "UtilityDriver"
    bl_label = "Driver"
    mantis_node_class_name=bl_idname
    socket_templates=DriverSockets
    
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

class UtilitySwitchNode(Node, MantisMiscNode):
    """Represents a switch relationship between one driver property and one or more driven properties."""
    bl_idname = "UtilitySwitch"
    bl_label = "Switch"
    mantis_node_class_name=bl_idname
    socket_templates=SwitchSockets

class UtilityCombineThreeBoolNode(Node, MantisMiscNode):
    """Combines three booleans into a three-bool."""
    bl_idname = "UtilityCombineThreeBool"
    bl_label = "CombineThreeBool"
    mantis_node_class_name=bl_idname
    socket_templates=CombineThreeBoolSockets

class UtilityCombineVectorNode(Node, MantisMiscNode):
    """Combines three floats into a vector."""
    bl_idname = "UtilityCombineVector"
    bl_label = "CombineVector"
    mantis_node_class_name=bl_idname
    socket_templates=CombineVectorSockets
        
class UtilitySeparateVector(Node, MantisMiscNode):
    """Separates a vector into three floats"""
    bl_idname = "UtilitySeparateVector"
    bl_label = "Separate Vector"
    mantis_node_class_name=bl_idname
    socket_templates=SeparateVectorSockets
        
class UtilityCatStringsNode(Node, MantisMiscNode):
    """Combines multiple strings into one."""
    bl_idname = "UtilityCatStrings"
    bl_label = "Join Strings"
    mantis_node_class_name=bl_idname
    socket_templates=CatStringsSockets

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
                

class InputWidget(Node, MantisMiscNode):
    """Fetches a Widget from the Widget Library."""
    bl_idname = "InputWidget"
    bl_label = "Widget"
    mantis_node_class_name=bl_idname
    socket_templates=InputWidgetSockets
    
class InputExistingGeometryObjectNode(Node, MantisMiscNode):
    """Represents an existing geometry object from within the scene."""
    bl_idname = "InputExistingGeometryObject"
    bl_label = "Existing Object"
    mantis_node_class_name=bl_idname
    # We want Mantis to import widgets and stuff, so we hold a reference to the object
    object_reference : bpy.props.PointerProperty(type=bpy.types.Object,)
    socket_templates=InputExistingGeometryObjectSockets
    
    def display_update(self, parsed_tree, context):
        mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
        if mantis_node: # this is done here so I don't have to define yet another custom socket.
            self.object_reference = bpy.data.objects.get(mantis_node.evaluate_input("Name"))
    
# TODO: maybe I should hold a data reference here, too.
#       but it is complicated by the fact that Mantis does not distinguish b/tw geo types
class InputExistingGeometryDataNode(Node, MantisMiscNode):
    """Represents a mesh or curve datablock from the scene."""
    bl_idname = "InputExistingGeometryData"
    bl_label = "Existing Geometry"
    mantis_node_class_name=bl_idname
    socket_templates=InputExistingGeometrySockets

class UtilityCustomProperty(Node, MantisMiscNode):
    """A declaration of a custom property."""
    bl_idname = "UtilityCustomProperty"
    bl_label  = "Custom Property"
    bl_icon   = "NODE"
    mantis_node_class_name=bl_idname
    socket_templates=UtilityCustomPropertySockets
    
    def display_update(self, parsed_tree, context):
        prop_type = self.inputs['Type'].default_value
        if context: # I need to be able to call this without context in versioing.
            if mantis_node := parsed_tree.get(get_signature_from_edited_tree(self, context)):
                # this is done here so I don't have to define yet another custom socket.
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

class UtilityDeclareCollections(Node, MantisMiscNode):
    """A utility used to declare bone collections."""
    bl_idname = "UtilityDeclareCollections"
    bl_label  = "Collections"
    bl_icon   = "NODE"
    bl_width_min = 320
    mantis_node_class_name=bl_idname
    # Here is the layout of the data:
    # nested dicts of key:dict ( key = name, dict = children)
    # the 'leaf nodes' are empty dicts
    # we'll store it as a JSON string in order to make it a bpy.props 
    # and still have the ability to use it as a dict and save it
    # TODO: check and see if these strings have a character limit
    collection_declarations : bpy.props.StringProperty(default="")

    def update_interface(self):
        from .utilities.utilities import get_socket_maps, do_relink
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

class UtilityCollectionJoin(Node, MantisMiscNode):
    """A utility used to join bone collection declarations."""
    bl_idname = "UtilityCollectionJoin"
    bl_label  = "Join Collection Declarations"
    bl_icon   = "NODE"
    mantis_node_class_name=bl_idname
    socket_templates=CollectionJoinSockets

class UtilityCollectionHierarchy(Node, MantisMiscNode):
    """A utility used to declare bone collection hierarchies."""
    bl_idname = "UtilityCollectionHierarchy"
    bl_label  = "Collection Child Declaration"
    bl_icon   = "NODE"
    mantis_node_class_name=bl_idname
    socket_templates=CollectionHierarchySockets
        
class UtilityGeometryOfXForm(Node, MantisMiscNode):
    """Retrieves a mesh or curve datablock from an xForm."""
    bl_idname = "UtilityGeometryOfXForm"
    bl_label = "Geometry of xForm"
    mantis_node_class_name=bl_idname
    socket_templates=GeometryOfXFormSockets

class UtilityNameOfXForm(Node, MantisMiscNode):
    """Retrieves the name of a xForm."""
    bl_idname = "UtilityNameOfXForm"
    bl_label = "Name of xForm"
    mantis_node_class_name=bl_idname
    socket_templates=NameOfXFormSockets

class UtilityGetBoneLength(Node, MantisMiscNode):
    """Returns the length of the bone from its matrix."""
    bl_idname = "UtilityGetBoneLength"
    bl_label = "Get Bone Length"
    mantis_node_class_name=bl_idname
    socket_templates=GetBoneLengthSockets

# TODO: make it work with BBones!
class UtilityPointFromBoneMatrix(Node, MantisMiscNode):
    """Returns a point representing the location along a bone, given a matrix representing that bone's shape."""
    bl_idname = "UtilityPointFromBoneMatrix"
    bl_label = "Point from Bone Matrix"
    mantis_node_class_name=bl_idname
    socket_templates=PointFromBoneMatrixSockets

class UtilitySetBoneLength(Node, MantisMiscNode):
    """Sets the length of a bone matrix."""
    bl_idname = "UtilitySetBoneLength"
    bl_label = "Set Bone Matrix Length"
    mantis_node_class_name=bl_idname
    socket_templates=SetBoneLengthSockets

# TODO: more keyframe types should be supported in the future.
# Some of the code that can do this is commented out here until I can implement it properly.
class UtilityKeyframe(Node, MantisMiscNode):
    """A keyframe for a FCurve"""
    bl_idname = "UtilityKeyframe"
    bl_label = "KeyFrame"
    mantis_node_class_name=bl_idname
    socket_templates=KeyframeSockets

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


class UtilityBoneMatrixHeadTailFlip(Node, MantisMiscNode):
    """Flips a bone matrix so that the head is where the tail was and visa versa."""
    bl_idname = "UtilityBoneMatrixHeadTailFlip"
    bl_label = "Flip Head/Tail"
    mantis_node_class_name=bl_idname
    socket_templates=BoneMatrixHeadTailFlipSockets

class UtilityMatrixTransform(Node, MantisMiscNode):
    """Transforms a matrix by another."""
    bl_idname = "UtilityMatrixTransform"
    bl_label = "Multiply Matrices"
    mantis_node_class_name=bl_idname
    socket_templates=MatrixTransformSockets

class UtilityMatrixInvert(Node, MantisMiscNode):
    """Inverts an invertable matrix, otherwise throws an error."""
    bl_idname = "UtilityMatrixInvert"
    bl_label = "Invert Matrix"
    mantis_node_class_name=bl_idname
    socket_templates=MatrixInvertSockets

class UtilityMatrixCompose(Node, MantisMiscNode):
    """Inverts an invertable matrix, otherwise throws an error."""
    bl_idname = "UtilityMatrixCompose"
    bl_label = "Compose Matrix"
    mantis_node_class_name=bl_idname
    socket_templates=MatrixComposeSockets

class UtilityMatrixAlignRoll(Node, MantisMiscNode):
    """Aligns the Z axis of a matrix to point in a direction."""
    bl_idname = "UtilityMatrixAlignRoll"
    bl_label = "Align Matrix Roll"
    mantis_node_class_name=bl_idname
    socket_templates=MatrixAlignRollSockets

class UtilityMatrixSetLocation(Node, MantisMiscNode):
    """Sets a matrix's location."""
    bl_idname = "UtilityMatrixSetLocation"
    bl_label = "Set Matrix Location"
    mantis_node_class_name=bl_idname
    socket_templates=MatrixSetLocationSockets

class UtilityMatrixGetLocation(Node, MantisMiscNode):
    """Gets a matrix's location."""
    bl_idname = "UtilityMatrixGetLocation"
    bl_label = "Get Matrix Location"
    mantis_node_class_name=bl_idname
    socket_templates=MatrixGetLocationSockets

class UtilityTransformationMatrix(Node, MantisMiscNode):
    """Constructs a matrix representing a transformation"""
    bl_idname = "UtilityTransformationMatrix"
    bl_label = "Transformation Matrix"
    mantis_node_class_name=bl_idname
    socket_templates=TransformationMatrixSockets

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

class UtilitySetBoneMatrixTail(Node, MantisMiscNode):
    """Constructs a matrix representing a transformation"""
    bl_idname = "UtilitySetBoneMatrixTail"
    bl_label = "Set Bone Matrix Tail"
    mantis_node_class_name=bl_idname
    socket_templates=SetBoneMatrixTailSockets

class UtilityMatrixFromXForm(Node, MantisMiscNode):
    """Returns the matrix of the given xForm node."""
    bl_idname = "UtilityMatrixFromXForm"
    bl_label = "Matrix of xForm"
    mantis_node_class_name=bl_idname
    socket_templates=MatrixFromXFormSockets

class UtilityAxesFromMatrix(Node, MantisMiscNode):
    """Returns the axes of the matrix."""
    bl_idname = "UtilityAxesFromMatrix"
    bl_label = "Axes of Matrix"
    mantis_node_class_name=bl_idname
    socket_templates=AxesFromMatrixSockets

class UtilityIntToString(Node, MantisMiscNode):
    """Converts a number to a string"""
    bl_idname = "UtilityIntToString"
    bl_label = "Number String"
    mantis_node_class_name=bl_idname
    socket_templates=IntToStringSockets

class UtilityArrayGet(Node, MantisMiscNode):
    """Gets a value from an array at a specified index."""
    bl_idname = "UtilityArrayGet"
    bl_label  = "Array Get"
    bl_icon   = "NODE"
    mantis_node_class_name=bl_idname
    socket_templates=ArrayGetSockets
    
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

class UtilityArrayLength(Node, MantisMiscNode):
    """Gets The length of an array."""
    bl_idname = "UtilityArrayLength"
    bl_label  = "Array Length"
    bl_icon   = "NODE"
    mantis_node_class_name=bl_idname
    socket_templates=UtilityArrayLengthSockets
    
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


class UtilityCompare(Node, MantisMiscNode):
    """Compares two inputs and produces a boolean output"""
    bl_idname = "UtilityCompare"
    bl_label = "Compare"
    mantis_node_class_name=bl_idname
    socket_templates=CompareSockets
    
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

class UtilityChoose(Node, MantisMiscNode):
    """Chooses an output"""
    bl_idname = "UtilityChoose"
    bl_label = "Choose"
    mantis_node_class_name=bl_idname
    socket_templates=ChooseSockets
    
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


class UtilityPrint(Node, MantisMiscNode):
    """A utility used to print arbitrary values."""
    bl_idname = "UtilityPrint"
    bl_label  = "Print"
    bl_icon   = "NODE"
    mantis_node_class_name=bl_idname
    socket_templates=PrintSockets
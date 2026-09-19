from .mantis_dataclasses import MantisSocketTemplate as ST
from dataclasses import replace

# reused templates
SplineIndexTemplate = ST(name="Spline Index",
        bl_idname='UnsignedIntSocket', is_input=True, default_value=0,)
FactorTemplate = ST(name="Factor", bl_idname='FloatFactorSocket', is_input=True,)
MatrixOutput = ST( name="Matrix", is_input=False, bl_idname='MatrixSocket', )
MatricesOutTemplate = replace(MatrixOutput, name='Matrices', use_multi_input=True)
StringOutput = ST( name="String", is_input=False, bl_idname='StringSocket', )
MatrixInput = replace(MatrixOutput, is_input=True)
VectorOutput = ST(name="Vector", bl_idname="VectorSocket", is_input=False)
VectorInput = replace(VectorOutput, is_input = True)

# input classes
InputFloatSockets = [
    FloatInput := ST(name='Float Input',
        bl_idname='FloatSocket', is_input=False),
]
InputIntSockets = [
    IntInput := ST(name='Integer',
        bl_idname='IntSocket', is_input=False),
]
InputVectorSockets = [
    replace(VectorOutput, name='',),
]
InputBooleanSockets = [
    BoolInput := ST(name='',
        bl_idname='BooleanSocket', is_input=False),
]
InputBooleanThreeTupleSockets = [
    BoolThreeTupleInput := ST(name='',
        bl_idname='BooleanThreeTupleSocket', is_input=False),
]
InputRotationOrderSockets = [
    RotationOrderInput := ST(name='',
        bl_idname='RotationOrderSocket', is_input=False),
]
InputTransformSpaceSockets = [
    TransformSpaceInput := ST(name='',
        bl_idname='TransformSpaceSocket', is_input=False),
]
InputStringSockets = [
    StringInput := ST(name='', bl_idname='StringSocket',
        is_input=False),
]
InputMatrixSockets = [
    MatrixOutput
]

MatrixFromCurveSockets=[
    CurveTemplate := ST(name="Curve", bl_idname='EnumCurveSocket', 
        is_input=True,),
    SplineIndexTemplate,
    TotalDivisionsTemplate := ST(name="Total Divisions",
        bl_idname='UnsignedIntSocket', is_input=True, default_value=0,),
    MatrixIndexTemplate := ST(name="Matrix Index",
        bl_idname='UnsignedIntSocket', is_input=True, default_value=0,),
    MatrixOutput,
]

MatricesFromCurveSockets=MatrixFromCurveSockets.copy()
MatricesFromCurveSockets[4] = MatricesOutTemplate
MatricesFromCurveSockets.pop(3)

MatrixFromCurveSegmentSockets=[
    CurveTemplate,
    SplineIndexTemplate,
    SegmentIndexTemplate := replace(SplineIndexTemplate, name="Segment Index"),
    MatrixOutput,
]

PointFromCurveSockets=[
    CurveTemplate,
    SplineIndexTemplate,
    FactorTemplate,
    PointOutTemplate := ST(name="Point", bl_idname="VectorSocket",
        is_input=False, )
]

NumberOfCurveSegmentsSockets = [
    CurveTemplate,
    SplineIndexTemplate,
    NumberOfSegments := ST(name='Number of Segments',
        bl_idname='UnsignedIntSocket', is_input=False),
]

GetCurvePointSockets=[
    CurveTemplate,
    SplineIndexTemplate,
    IndexTemplate := ST(name="Index",
        bl_idname='UnsignedIntSocket', is_input=True, default_value=0,),
    OutputPointTemplate := ST(name="Point",
        bl_idname='VectorSocket', is_input=False,),
    OutputLeftHandleTemplate := ST(name="Left Handle",
        bl_idname='VectorSocket', is_input=False, hide=True),
    OutputRightHandleTemplate := ST(name="Right Handle",
        bl_idname='VectorSocket', is_input=False, hide=True),
]

GetNearestFactorOnCurveSockets=[
    CurveTemplate,
    SplineIndexTemplate,
    ReferencePointTemplate := ST(name="Reference Point",
        bl_idname='VectorSocket', is_input=True,),
    OutputFactorTemplate := ST(name="Factor",
        bl_idname='FloatSocket', is_input=False,),
]

KDChoosePointSockets = [
    ReferencePointTemplate,
    PointsArray := ST(name="Points", bl_idname="VectorSocket",
        use_multi_input=True,  is_input=True),
    NumberToFind := ST(name='Number to Find',
        bl_idname = "UnsignedIntSocket", default_value=1,  is_input=True),
    ResultPoint :=ST(name='Result Point', bl_idname="VectorSocket",
        is_input=False, ),
    ResultIndex :=ST(name='Result Index',
        bl_idname="UnsignedIntSocket", is_input=False, ),
    ResultDistance :=ST(name='Result Distance',
        bl_idname="FloatSocket", is_input=False, ),
]

KDChooseXFormSockets = [
    ReferencePointTemplate,
    xFormsArray := ST(name="xForm Nodes", bl_idname="xFormSocket",
        use_multi_input=True, is_input=True,),
    GetPointHeadTail := ST(name="Get Point Head/Tail",
        bl_idname = "FloatFactorSocket",  is_input=True,),
    NumberToFind,
    ResultxForm := ST(name='Result xForm', bl_idname='xFormSocket', is_input=False),
    ResultIndex,
    ResultDistance,
]

MetaRigSockets = [
    MetaArmature := ST(name='Meta-Armature', bl_idname="EnumMetaRigSocket",
        is_input = True, ),
    MetaBone := ST(name='Meta-Bone', bl_idname="EnumMetaBoneSocket",
        is_input = True, hide=True ),
    MatrixOutput,
]

BonePropertiesSockets = [
    replace( StringOutput, name='matrix'),
    replace( StringOutput, name='matrix_local'),
    replace( StringOutput, name='matrix_basis'),
    replace( StringOutput, name='head'),
    replace( StringOutput, name='tail'),
    replace( StringOutput, name='length'),
    replace( StringOutput, name='rotation'),
    replace( StringOutput, name='location'),
    replace( StringOutput, name='scale'),
]

DriverVariableSockets = [
    VariableType := ST(name='Variable Type', bl_idname="EnumDriverVariableType", is_input=True),
    Property := ST(name='Property', bl_idname="ParameterStringSocket", is_input=True),
    PropertyIndex := ST(name='Property Index', bl_idname="IntSocket", is_input=True),
    EvaluationSpace := ST(name='Evaluation Space', bl_idname="EnumDriverVariableEvaluationSpace", is_input=True,
        hide = True,),
    RotationMode := ST(name='Rotation Mode', bl_idname="EnumDriverRotationMode", is_input=True),
    xForm1 := ST(name='xForm 1', bl_idname="xFormSocket", is_input=True),
    xForm2 := ST(name='xForm 2', bl_idname="xFormSocket", is_input=True),
    DriverVariable := ST(name='Driver Variable', bl_idname="DriverVariableSocket", is_input=False),
]

FCurveSockets = [
    ExtrapolationMode := ST( name="Extrapolation Mode",
        bl_idname="eFCrvExtrapolationMode", is_input=True),
    fCurveOutput := ST(name="fCurve", bl_idname="FCurveSocket", is_input=False),
]

DriverSockets = [
    DriverType := ST(name="Driver Type", bl_idname="EnumDriverType", is_input=True),
    FCurve := ST(name="fCurve", bl_idname="FCurveSocket", is_input=True),
    Expression := ST(name="Expression", bl_idname="StringSocket", is_input=True),
    DriverOutput := ST(name="Driver", bl_idname="DriverSocket", is_input=False),
]

SwitchSockets = [
    Parameter := ST(name="Parameter", bl_idname="ParameterStringSocket", is_input=True),
    ParameterIndex := ST(name="Parameter Index", bl_idname="IntSocket", is_input=True),
    InvertSwitch := ST(name="Invert Switch", bl_idname="BooleanSocket", is_input=True),
    DriverOutput,
]

CombineThreeBoolSockets = [
    AxisX := ST(name="X", bl_idname="BooleanSocket", is_input=True),
    AxisY := replace(AxisX, name='Y'),
    AxisZ := replace(AxisX, name='Z'),
    ThreeBoolOutput := ST(name="Three-Bool", bl_idname="BooleanThreeTupleSocket", is_input=False),
]

CombineThreeBoolSockets = [
    AxisX := ST(name="X", bl_idname="BooleanSocket", is_input=True),
    AxisY := replace(AxisX, name='Y'),
    AxisZ := replace(AxisX, name='Z'),
    ThreeBoolOutput := ST(name="Three-Bool", bl_idname="BooleanThreeTupleSocket", is_input=False),
]

CombineVectorSockets = [
    AxisX := replace(AxisX, bl_idname="FloatSocket", name='X'),
    AxisY := replace(AxisY, bl_idname="FloatSocket", name='Y'),
    AxisZ := replace(AxisZ, bl_idname="FloatSocket", name='Z'),
    VectorOutput := ST(name="Vector", bl_idname="VectorSocket", is_input=False),
]

SeparateVectorSockets = [
    Vector := ST(name="Vector", bl_idname="VectorSocket", is_input=True),
    AxisXOutput := replace(AxisX, bl_idname="FloatSocket", is_input=False),
    AxisYOutput := replace(AxisXOutput, name='Y'),
    AxisZOutput := replace(AxisXOutput, name='Z'),
]

CatStringsSockets = [
    String_1 := ST(name="String_1", bl_idname="StringSocket", is_input=True),
    String_2 := replace(String_1, name="String_2"),
    OutputString := ST(name="OutputString", bl_idname="StringSocket", is_input=False),
]

InputWidgetSockets = [
    WidgetName := ST(name='Name', is_input=True,
        bl_idname="EnumWidgetLibrarySocket",),
    Scale := ST(name='Scale', is_input=True,
        bl_idname="VectorScaleSocket", default_value=(1.0, 1.0, 1.0)),
    FlipAxes := ST(name='Flip Axes', is_input=True,
        bl_idname="BooleanThreeTupleSocket",),
    xFormOutput := ST(name='Widget',
        bl_idname='xFormSocket', is_input=False),
]

InputExistingGeometryObjectSockets = [
    Name := ST(name="Name", bl_idname="StringSocket", is_input=True),
    ObjectOutput := ST(name="Object", bl_idname="xFormSocket", is_input=False),
]

InputExistingGeometrySockets = [
    Name,
    GeometryOutput := ST(name="Geometry", bl_idname="GeometrySocket", is_input=False),
]

UtilityCustomPropertySockets = [
    Name := ST(name='Name', is_input=True,
        bl_idname="StringSocket", category='general'),
    
    CustomPropType := ST(name='Type', is_input=True,
        bl_idname="EnumCustomPropTypeSocket", category='general'),
    # Subtype - add this later

    # float properties
    DefaultFloatValue := ST(name='Default (Float)', is_input=True,
        bl_idname="FloatSocket",  category='float'),
    Min := ST(name='Min (Float)', is_input=True,
        bl_idname="FloatSocket", category='float'),
    Max := ST(name='Max (Float)', is_input=True,
        bl_idname="FloatSocket", category='float'),
    SoftMin := ST(name='Soft Min (Float)', is_input=True,
        bl_idname="FloatSocket", category='float'),
    SoftMax := ST(name='Soft Max (Float)', is_input=True,
        bl_idname="FloatSocket", category='float'),
    
    # bool properties
    DefaultVectorValue := ST(name='Default (Bool)', is_input=True,
        bl_idname="BooleanSocket", hide=True, category='bool'),
    # int properties
    DefaultIntValue := ST(name='Default (Int)', is_input=True,
        bl_idname="IntSocket", hide=True, category='int'),
    IntMin := ST(name='Min (Int)', is_input=True,
        bl_idname="IntSocket", hide=True, category='int'),
    IntMax := ST(name='Max (Int)', is_input=True,
        bl_idname="IntSocket", hide=True, category='int'),
    IntSoftMin := ST(name='Soft Min (Int)', is_input=True,
        bl_idname="IntSocket", hide=True, category='int'),
    IntSoftMax := ST(name='Soft Max (Int)', is_input=True,
        bl_idname="IntSocket", hide=True, category='int'),
    # vector properties
    DefaultVectorValue := ST(name='Default (Vector)', is_input=True,
        bl_idname="VectorSocket", hide=True, category='vector'),
    # String Properties
    DefaultStringValue := ST(name='Default (String)', is_input=True,
        bl_idname="StringSocket", hide=True, category='string'),
    # general:
    Description := ST(name='Description', is_input=True,
        bl_idname="StringSocket", category='general'),
    PropertyDeclaration := ST(name='Custom Property',
        is_input=False, bl_idname="CustomPropSocket", category='general'),
]

CollectionJoinSockets = [
    JoinCollections := ST(name='Collections', is_input=True,
        bl_idname="BoneCollectionSocket", display_shape='SQUARE_DOT',
        use_multi_input=True,),
    CollectionDeclarationOutput := ST(name='Collection',
        bl_idname="BoneCollectionSocket", is_input=False,)
]

CollectionHierarchySockets = [
    ParentCollection := ST(name='Parent Collection', is_input=True,
        bl_idname="BoneCollectionSocket",),
    ChildCollection := ST(name='Child Collection', is_input=True,
        bl_idname="BoneCollectionSocket",),
    CollectionDeclarationOutput,
]

GeometryOfXFormSockets = [
    xForm := ST(name="xForm", bl_idname="xFormSocket", is_input=True),
    GeometryOutput,
]

NameOfXFormSockets = [
    xForm,
    replace(Name, is_input=False),
]

GetBoneLengthSockets = [
    BoneMatrix := ST(name="Bone Matrix", bl_idname="MatrixSocket", is_input=True),
    BoneLength := ST(name="Bone Length", bl_idname="FloatSocket", is_input=False),
]

PointFromBoneMatrixSockets = [
    replace(MatrixInput, name = "Bone Matrix",),
    HeadTail := ST(name="Head/Tail", bl_idname = "FloatFactorSocket", is_input=True) ,
    replace(VectorOutput, name="Point"),
]

SetBoneLengthSockets = [
    replace(MatrixInput, name = "Bone Matrix"),
    Length := ST(name="Length", bl_idname = "FloatSocket", is_input=True) ,
    replace(MatrixOutput, name = "Bone Matrix"),
]

# there will eventually be inputs for e.g. key type, key handles, etc.
# right now I am gonna hardcode LINEAR keyframes so I don't have to deal with anything else
# TODO TODO TODO
KeyframeSockets = [
    # Interpolation := ST(name="Interpolation", bl_idname="EnumKeyframeInterpolationTypeSocket", is_input=True),
    # LeftHandleType := ST(name="Left Handle Type", bl_idname="EnumKeyframeBezierHandleType", is_input=True),
    # RightHandleType := ST(name="Right Handle Type", bl_idname="EnumKeyframeBezierHandleType", is_input=True),
    # LeftHandleDistance := ST(name="Left Handle Distance", bl_idname="FloatSocket", is_input=True),
    # LeftHandleValue := ST(name="Left Handle Value", bl_idname="FloatSocket", is_input=True),
    # RightHandleFrame := ST(name="Right Handle Frame", bl_idname="FloatSocket", is_input=True),
    # RightHandleValue := ST(name="Right Handle Value", bl_idname="FloatSocket", is_input=True),
    Frame := ST(name="Frame", bl_idname="FloatSocket", is_input=True),
    Value := ST(name="Value", bl_idname="FloatSocket", is_input=True),
    Keyframe := ST(name="Keyframe", bl_idname="KeyframeSocket", is_input=False),
]

BoneMatrixHeadTailFlipSockets = [
    replace(MatrixInput, name = "Bone Matrix",),
    replace(MatrixOutput, name = "Bone Matrix"),
]

MatrixTransformSockets = [
    Matrix1Template := ST( name="Matrix 1", is_input=True,
        bl_idname='MatrixSocket', ),
    Matrix2Template := replace(Matrix1Template, name = "Matrix 2"),
    replace(MatrixOutput, name = "Out Matrix"),
]

MatrixInvertSockets=[
    Matrix1Template,
    MatrixOutput,
]

MatrixComposeSockets=[
    XBasisVector := ST(
    name="X Basis Vector", is_input=True,  bl_idname='VectorSocket', 
        default_value = (1.0, 0.0, 0.0) ),
    YBasisVector := replace(XBasisVector, name="Y Basis Vector",
        default_value = (0.0, 1.0, 0.0) ),
    ZBasisVector := replace(XBasisVector, name="Z Basis Vector",
        default_value = (0.0, 0.0, 1.0) ),
    Translation := replace(XBasisVector, name="Translation"),
    MatrixOutput,
]

MatrixAlignRollSockets = [
    MatrixInTemplate := replace(Matrix1Template, name="Matrix"),
    AlignVector := ST(name="Alignment Vector", is_input=True,
       bl_idname='VectorSocket', default_value=(0.0,-1.0,0.0)),
    MatrixOutput,
]

MatrixSetLocationSockets = [
    MatrixInput,
    replace(VectorInput, name="Location"),
    MatrixOutput,
]

MatrixGetLocationSockets = [
    MatrixInput,
    replace(VectorInput, is_input=False, name="Location"),
]

TransformationMatrixSockets = [
    MatrixTransformOperation := ST(name="Operation",
        bl_idname="MatrixTransformOperation", is_input=True),
    Vector,
    AxisW := replace(AxisX, name="W"),
    MatrixOutput,
]

SetBoneMatrixTailSockets = [
    MatrixInput,
    replace(VectorInput, name="Tail Location"),
    replace(MatrixOutput, name = "Result"),
]

MatrixFromXFormSockets = [
    xForm,
    MatrixOutput,
]

AxesFromMatrixSockets = [
    MatrixInput,
    replace(VectorOutput, name='X Axis',),
    replace(VectorOutput, name='Y Axis',),
    replace(VectorOutput, name='Z Axis',),
]

IntToStringSockets = [
    Number := ST(name = 'Number', bl_idname = 'IntSocket',
        is_input = True),
    Number := ST(name = 'Zero Padding', bl_idname = 'IntSocket',
        is_input = True),
    StringOutput,
]

ArrayGetSockets = [
    OoBBehaviour := ST(name="OoB Behaviour", bl_idname="EnumArrayGetOptions",
        is_input=True),
    Index := ST(name="Index", bl_idname="IntSocket", is_input=True),
    Array := ST(name="Array", bl_idname="WildcardSocket", is_input=True,
        use_multi_input=True, display_shape='SQUARE_DOT'),
    WildcardOutput := ST(name="Output", bl_idname="WildcardSocket", is_input=False),
]

UtilityArrayLengthSockets = [
    Array,
    replace(NumberOfSegments, name="Length"),
]

CompareSockets = [
    ComparisonOperation := ST( name='Comparison',
            is_input=True, bl_idname="EnumCompareOperation",
            default_value="EQUAL",),
    WildcardATemplate := ST(
        name="A", is_input=True,  bl_idname='WildcardSocket', ),
    WildcardBTemplate := replace(WildcardATemplate, name="B"),
    CompareOutputTemplate := ST(
        name="Result", is_input=False, bl_idname="BooleanSocket",),
]

ChooseSockets = [
    Condition := ST(name="Condition", bl_idname="BooleanSocket", is_input=True),
    ChooseA := ST(name="A", bl_idname="WildcardSocket", is_input=True),
    ChooseB := ST(name="B", bl_idname="WildcardSocket", is_input=True),
    replace(WildcardOutput, name='Result'),
]

PrintSockets = [
    replace(ChooseA, name='Input'),
]

NumberOfSplinesSockets=[
    CurveTemplate,
    NumberOfSplinesOut := ST(name="Number of Splines",
        bl_idname='UnsignedIntSocket', is_input=False),
]

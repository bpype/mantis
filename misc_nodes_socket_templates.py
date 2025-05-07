from .base_definitions import MantisSocketTemplate as SockTemplate
from dataclasses import replace

SplineIndexTemplate = SockTemplate(name="Spline Index",
        bl_idname='UnsignedIntSocket', is_input=True, default_value=0,)

MatrixFromCurveSockets=[
    CurveTemplate := SockTemplate(name="Curve", bl_idname='EnumCurveSocket', 
        is_input=True,),
    SplineIndexTemplate,
    TotalDivisionsTemplate := SockTemplate(name="Total Divisions",
        bl_idname='UnsignedIntSocket', is_input=True, default_value=0,),
    MatrixIndexTemplate := SockTemplate(name="Matrix Index",
        bl_idname='UnsignedIntSocket', is_input=True, default_value=0,),
    MatrixOutTemplate := SockTemplate(
        name="Matrix", is_input=False,  bl_idname='MatrixSocket', ),
]

MatricesOutTemplate = replace(MatrixOutTemplate,
        name='Matrices', use_multi_input=True)
MatricesFromCurveSockets=MatrixFromCurveSockets.copy()
MatricesFromCurveSockets[4] = MatricesOutTemplate
MatricesFromCurveSockets.pop(3)

MatrixFromCurveSegmentSockets=[
    CurveTemplate,
    SplineIndexTemplate,
    SegmentIndexTemplate := replace(SplineIndexTemplate, name="Segment Index"),
    MatrixOutTemplate,
]

PointFromCurveSockets=[
    CurveTemplate,
    SplineIndexTemplate,
    FactorTemplate := SockTemplate(name="Factor", bl_idname='FloatFactorSocket', 
        is_input=True,),
    PointOutTemplate := SockTemplate(name="Point", bl_idname="VectorSocket",
        is_input=False, )
]

GetCurvePointSockets=[
    CurveTemplate,
    SplineIndexTemplate,
    IndexTemplate := SockTemplate(name="Index",
        bl_idname='UnsignedIntSocket', is_input=True, default_value=0,),
    OutputPointTemplate := SockTemplate(name="Point",
        bl_idname='VectorSocket', is_input=False,),
    OutputLeftHandleTemplate := SockTemplate(name="Left Handle",
        bl_idname='VectorSocket', is_input=False, hide=True),
    OutputRightHandleTemplate := SockTemplate(name="Right Handle",
        bl_idname='VectorSocket', is_input=False, hide=True),
]

GetNearestFactorOnCurveSockets=[
    CurveTemplate,
    SplineIndexTemplate,
    ReferencePointTemplate := SockTemplate(name="Reference Point",
        bl_idname='VectorSocket', is_input=True,),
    OutputFactorTemplate := SockTemplate(name="Factor",
        bl_idname='FloatSocket', is_input=False,),
]

MatrixInvertSockets=[
    Matrix1Template := SockTemplate(
    name="Matrix 1", is_input=True,  bl_idname='MatrixSocket', ),
    MatrixOutTemplate,
]

MatrixComposeSockets=[
    XBasisVector := SockTemplate(
    name="X Basis Vector", is_input=True,  bl_idname='VectorSocket', 
        default_value = (1.0, 0.0, 0.0) ),
    YBasisVector := replace(XBasisVector, name="Y Basis Vector",
        default_value = (0.0, 1.0, 0.0) ),
    ZBasisVector := replace(XBasisVector, name="Z Basis Vector",
        default_value = (0.0, 0.0, 1.0) ),
    Translation := replace(XBasisVector, name="Translation"),
    MatrixOutTemplate,
]

MatrixAlignRollSockets=[
    MatrixInTemplate := replace(Matrix1Template, name="Matrix"),
    AlignVector := SockTemplate(name="Alignment Vector", is_input=True,
       bl_idname='VectorSocket', default_value=(0.0,-1.0,0.0)),
    MatrixOutTemplate,
]

CompareSockets = [
    ComparisonOperation := SockTemplate( name='Comparison',
            is_input=True, bl_idname="EnumCompareOperation",
            default_value="EQUAL",),
    WildcardATemplate := SockTemplate(
        name="A", is_input=True,  bl_idname='WildcardSocket', ),
    WildcardBTemplate := replace(WildcardATemplate, name="B"),
    CompareOutputTemplate := SockTemplate(
        name="Result", is_input=False, bl_idname="BooleanSocket",),
]

NumberOfSplinesSockets=[
    CurveTemplate,
    NumberOfSplinesOut := SockTemplate(name="Number of Splines",
        bl_idname='UnsignedIntSocket', is_input=False),
]

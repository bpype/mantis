from .base_definitions import MantisSocketTemplate as SockTemplate
from dataclasses import replace

GetCurvePointSockets=[
    CurveTemplate := SockTemplate(name="Curve", bl_idname='EnumCurveSocket', 
        is_input=True,),
    SplineIndexTemplate := SockTemplate(name="Spline Index",
        bl_idname='UnsignedIntSocket', is_input=True, default_value=0,),
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
    MatrixOutTemplate := SockTemplate(
    name="Matrix", is_input=False,  bl_idname='MatrixSocket', ),
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
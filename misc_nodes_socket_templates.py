from .base_definitions import MantisSocketTemplate as SockTemplate

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

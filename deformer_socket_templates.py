from .base_definitions import MantisSocketTemplate as SockTemplate
from dataclasses import replace

from .misc_nodes_socket_templates import SplineIndexTemplate


Target = SockTemplate(name="Target", bl_idname='xFormSocket',
        is_input=True,
    )

HookSockets= [
    DeformerInput := SockTemplate(name="Deformer", bl_idname='DeformerSocket',
        is_input=True,),
    HookTarget := replace(Target, name="Hook Target"),
    replace(SplineIndexTemplate,),
    CurvePointIndex := SockTemplate(name="Point Index", bl_idname='UnsignedIntSocket',
        is_input=True, default_value=0 ),
    Influence := SockTemplate(name="Influence", bl_idname='FloatFactorSocket',
        is_input=True, default_value=1.0, blender_property='strength'),
    HookDrivesRadius := SockTemplate(name="Affect Curve Radius", bl_idname='BooleanSocket',
        is_input=True, default_value=True,),
    HookAutoBezier := SockTemplate(name="Auto-Bezier", bl_idname='BooleanSocket',
        is_input=True, default_value=True,),
    DeformerOutput := SockTemplate(name="Deformer", bl_idname='DeformerSocket',
        is_input=False,), 
]
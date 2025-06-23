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

SurfaceDeformSockets= [
    DeformerInput := SockTemplate(name="Deformer", bl_idname='DeformerSocket',
        is_input=True,),
    SurfaceDeformTarget := replace(Target, name="Target",),
    replace(SplineIndexTemplate,),
    Falloff := SockTemplate(name="Falloff", bl_idname='FloatSocket',
        is_input=True, default_value=4.0, blender_property="falloff", ),
    Strength := replace(Influence, name="Strength", bl_idname='FloatSocket',
        is_input=True, default_value=1.0, blender_property='strength'),
    VertexGroup := SockTemplate(name="Vertex Group", bl_idname='StringSocket',
        is_input=True, default_value="", blender_property="vertex_group"),
    InvertVertexGroup := SockTemplate(name="Invert Vertex Group", bl_idname='BooleanSocket',
        is_input=True, default_value=False, blender_property="invert_vertex_group"),
    SparseBind := SockTemplate(name="Sparse Bind", bl_idname='BooleanSocket',
        is_input=True, default_value=False, blender_property="use_sparse_bind"),
    DeformerOutput := SockTemplate(name="Deformer", bl_idname='DeformerSocket',
        is_input=False,), 
]
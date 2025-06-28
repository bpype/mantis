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
    DeformerInput,
    SurfaceDeformTarget := replace(Target, name="Target",),
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
    DeformerOutput,
]

MeshDeformSockets= [
    DeformerInput := SockTemplate(name="Deformer", bl_idname='DeformerSocket',
        is_input=True,),
    MeshDeformTarget := replace(Target, name="Object",),
    VertexGroup,
    InvertVertexGroup,
    MeshDeformPrecision := SockTemplate(name="Precision", bl_idname='UnsignedIntSocket',
        is_input=True, default_value=4, blender_property="precision"),
    DynamicBind := SockTemplate(name="Dynamic Bind", bl_idname='BooleanSocket',
        is_input=True, default_value=False, blender_property="use_dynamic_bind"),
    DeformerOutput, 
]

LatticeDeformSockets = [
    DeformerInput := SockTemplate(name="Deformer", bl_idname='DeformerSocket',
        is_input=True,),
    LatticeDeformTarget := replace(Target, name="Object",),
    VertexGroup,
    InvertVertexGroup,
    Strength := replace(Strength, bl_idname='FloatFactorSocket',),
    DeformerOutput,
]

SmoothDeformSockets = [
    DeformerInput,
    Factor := replace(Influence, name="Factor", bl_idname='FloatSocket',
                        default_value=1.0, blender_property='factor'),
    iterations := SockTemplate(name='Iterations', bl_idname="UnsignedIntSocket",
            is_input=True, default_value=5, blender_property='iterations'),
    # SmoothType :=SockTemplate(name="Length Weighted Smoothing", bl_idname="BooleanSocket",
    #         is_input=True, default_value=False, ),
            # TODO: should be possible to drive this property by an int...
    OnlySmooth := SockTemplate(name="Only Smooth", bl_idname="BooleanSocket",
            is_input=True, default_value=True, blender_property="use_only_smooth"),
    PinBoundary := SockTemplate(name="Pin Boundary", bl_idname="BooleanSocket",
            is_input=True, default_value=False, blender_property="use_pin_boundary"),
    VertexGroup,
    InvertVertexGroup,
    DeformerOutput,
]

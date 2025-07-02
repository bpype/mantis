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
    SparseBind := SockTemplate(name="Sparse Bind", bl_idname='BooleanSocket',
        is_input=True, default_value=False, blender_property="use_sparse_bind"),
    VertexGroup := SockTemplate(name="Vertex Group", bl_idname='StringSocket',
        is_input=True, default_value="", blender_property="vertex_group"),
    InvertVertexGroup := SockTemplate(name="Invert Vertex Group", bl_idname='BooleanSocket',
        is_input=True, default_value=False, blender_property="invert_vertex_group"),
    EnableViewportTemplate := SockTemplate(
        name="Enable in Viewport", is_input=True,  bl_idname='EnableSocket',
        default_value=True, blender_property='show_viewport'),
    EnableRenderTemplate := SockTemplate(
        name="Enable in Render", is_input=True,  bl_idname='BooleanSocket',
        default_value=True, blender_property='show_render'),
    DeformerOutput,
]

MeshDeformSockets= [
    DeformerInput := SockTemplate(name="Deformer", bl_idname='DeformerSocket',
        is_input=True,),
    MeshDeformTarget := replace(Target, name="Object",),
    MeshDeformPrecision := SockTemplate(name="Precision", bl_idname='UnsignedIntSocket',
        is_input=True, default_value=4, blender_property="precision"),
    DynamicBind := SockTemplate(name="Dynamic Bind", bl_idname='BooleanSocket',
        is_input=True, default_value=False, blender_property="use_dynamic_bind"),
    VertexGroup,
    InvertVertexGroup,
    EnableViewportTemplate,
    EnableRenderTemplate,
    DeformerOutput, 
]

LatticeDeformSockets = [
    DeformerInput := SockTemplate(name="Deformer", bl_idname='DeformerSocket',
        is_input=True,),
    LatticeDeformTarget := replace(Target, name="Object",),
    Strength := replace(Strength, bl_idname='FloatFactorSocket',),
    VertexGroup,
    InvertVertexGroup,
    EnableViewportTemplate,
    EnableRenderTemplate,
    DeformerOutput,
]

SmoothDeformSockets = [
    DeformerInput,
    Factor := replace(Influence, name="Factor", bl_idname='FloatSocket',
                        default_value=0.5, blender_property='factor'),
    iterations := SockTemplate(name='Iterations', bl_idname="UnsignedIntSocket",
            is_input=True, default_value=4, blender_property='iterations'),
    SmoothType :=SockTemplate(name="Smoothing Type", bl_idname="EnumCorrectiveSmoothTypeSocket", 
              is_input=True, blender_property="smooth_type" ),
    PinBoundary := SockTemplate(name="Pin Boundary", bl_idname="BooleanSocket",
            is_input=True, default_value=False, blender_property="use_pin_boundary"),
    OnlySmooth := SockTemplate(name="Use Corrective Smooth", bl_idname="InvertedBooleanSocket",
            is_input=True, default_value=True, blender_property="use_only_smooth"),
    DeltaMushScale := SockTemplate(name="Corrective Smooth Scale", bl_idname="FloatSocket",
            is_input=True, default_value=1.0, blender_property="scale", category='corrective_smooth' ),
    VertexGroup,
    InvertVertexGroup,
    EnableViewportTemplate,
    EnableRenderTemplate,
    DeformerOutput,
]

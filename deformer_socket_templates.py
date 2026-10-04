from .mantis_dataclasses import MantisSocketTemplate as ST
from dataclasses import replace

from .misc_nodes_socket_templates import SplineIndexTemplate


Target = ST(name="Target", bl_idname='xFormSocket',
        is_input=True,
    )

DeformArmatureSockets = [ 
    ArmatureObject := replace(Target, name="Armature Object"),
    BlendVertexGroup := ST(name="Blend Vertex Group", bl_idname="StringSocket", is_input=True,
                           blender_property='vertex_group'),
    InvertBlendVertexGroup := ST(name="Invert Vertex Group", bl_idname="BooleanSocket", is_input=True,
                           blender_property='invert_vertex_group'),
    # QuatBlendVertexGroup := ST(name="Preserve Volume Vertex Group", bl_idname="StringSocket", is_input=True)
    # ^ TODO figure out the right UX for automatic dual-quat blending
    PreserveVolume := ST(name="Preserve Volume", bl_idname="BooleanSocket", is_input=True,
                           blender_property='use_deform_preserve_volume'),
    # ^ TODO: make the above controlled by a vertex group instead.
    # might just set this below to auto (I don't evern understand it)
    UseMultiModifier := ST(name="Use Multi Modifier", bl_idname="BooleanSocket", is_input=True,
                           blender_property='use_multi_modifier'),
    UseEnvelopes := ST(name="Use Envelopes", bl_idname="BooleanSocket", is_input=True, default_value=False,
                           blender_property='use_bone_envelopes'),
    UseVertexGroups := ST(name="Use Vertex Groups", bl_idname="BooleanSocket", is_input=True, default_value=True,
                           blender_property='use_vertex_groups'),
    DeformerInput := ST(name="Deformer", bl_idname="DeformerSocket", is_input=True),
    CopySkinWeightsFrom := ST(name="Copy Skin Weights From", bl_idname="xFormSocket", is_input=True, hide=True),
    SkinningMethod := ST(name="Skinning Method", bl_idname="EnumSkinning", is_input=True),
    DeformerOutput := ST(name="Deformer", bl_idname="DeformerSocket", is_input=False),

]

HookSockets= [
    DeformerInput,
    HookTarget := replace(Target, name="Hook Target"),
    replace(SplineIndexTemplate,),
    CurvePointIndex := ST(name="Point Index", bl_idname='UnsignedIntSocket',
        is_input=True, default_value=0 ),
    Influence := ST(name="Influence", bl_idname='FloatFactorSocket',
        is_input=True, default_value=1.0, blender_property='strength'),
    HookDrivesRadius := ST(name="Affect Curve Radius", bl_idname='BooleanSocket',
        is_input=True, default_value=True,),
    HookAutoBezier := ST(name="Auto-Bezier", bl_idname='BooleanSocket',
        is_input=True, default_value=True,),
    DeformerOutput, 
]

#NOTE that this guy is a dynamic node so this is only its initial state.
MorphTargetDeformSockets = [
    DeformerInput,
    UseShapeKey := ST(name="Use Shape Key", bl_idname="BooleanSocket", is_input=True),
    UseOffset := ST(name="Use Offset", bl_idname="BooleanSocket", is_input=True, default_value=True),
    Extend := ST(name="", bl_idname="WildcardSocket", is_input=True, identifier="__extend__", ui_only=True),
    DeformerOutput,
]


MorphTargetSockets = [
    RelativeTo := ST(name="Relative to", bl_idname="xFormSocket", is_input=True),
    Object := ST(name="Object", bl_idname="xFormSocket", is_input=True),
    VertexGroup := ST(name="Vertex Group", bl_idname="StringSocket", is_input=True),
    MorphTarget := ST(name="Morph Target", bl_idname="MorphTargetSocket", is_input=False),
]

SurfaceDeformSockets= [
    DeformerInput,
    SurfaceDeformTarget := replace(Target, name="Target",),
    Falloff := ST(name="Falloff", bl_idname='FloatSocket',
        is_input=True, default_value=4.0, blender_property="falloff", ),
    Strength := replace(Influence, name="Strength", bl_idname='FloatSocket',
        is_input=True, default_value=1.0, blender_property='strength'),
    SparseBind := ST(name="Sparse Bind", bl_idname='BooleanSocket',
        is_input=True, default_value=False, blender_property="use_sparse_bind"),
    VertexGroup := ST(name="Vertex Group", bl_idname='StringSocket',
        is_input=True, default_value="", blender_property="vertex_group"),
    InvertVertexGroup := ST(name="Invert Vertex Group", bl_idname='BooleanSocket',
        is_input=True, default_value=False, blender_property="invert_vertex_group"),
    EnableViewportTemplate := ST(
        name="Enable in Viewport", is_input=True,  bl_idname='EnableSocket',
        default_value=True, blender_property='show_viewport'),
    EnableRenderTemplate := ST(
        name="Enable in Render", is_input=True,  bl_idname='BooleanSocket',
        default_value=True, blender_property='show_render'),
    DeformerOutput,
]

MeshDeformSockets= [
    DeformerInput := ST(name="Deformer", bl_idname='DeformerSocket',
        is_input=True,),
    MeshDeformTarget := replace(Target, name="Object",),
    MeshDeformPrecision := ST(name="Precision", bl_idname='UnsignedIntSocket',
        is_input=True, default_value=4, blender_property="precision"),
    DynamicBind := ST(name="Dynamic Bind", bl_idname='BooleanSocket',
        is_input=True, default_value=False, blender_property="use_dynamic_bind"),
    VertexGroup,
    InvertVertexGroup,
    EnableViewportTemplate,
    EnableRenderTemplate,
    DeformerOutput, 
]

LatticeDeformSockets = [
    DeformerInput := ST(name="Deformer", bl_idname='DeformerSocket',
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
    iterations := ST(name='Iterations', bl_idname="UnsignedIntSocket",
            is_input=True, default_value=4, blender_property='iterations'),
    SmoothType :=ST(name="Smoothing Type", bl_idname="EnumCorrectiveSmoothTypeSocket", 
              is_input=True, blender_property="smooth_type" ),
    PinBoundary := ST(name="Pin Boundary", bl_idname="BooleanSocket",
            is_input=True, default_value=False, blender_property="use_pin_boundary"),
    OnlySmooth := ST(name="Use Corrective Smooth", bl_idname="InvertedBooleanSocket",
            is_input=True, default_value=True, blender_property="use_only_smooth"),
    DeltaMushScale := ST(name="Corrective Smooth Scale", bl_idname="FloatSocket",
            is_input=True, default_value=1.0, blender_property="scale", category='corrective_smooth' ),
    VertexGroup,
    InvertVertexGroup,
    EnableViewportTemplate,
    EnableRenderTemplate,
    DeformerOutput,
]

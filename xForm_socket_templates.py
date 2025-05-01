from .base_definitions import MantisSocketTemplate as SockTemplate
from .misc_nodes_socket_templates import SplineIndexTemplate
from dataclasses import replace

xFormArmatureSockets=[
    NameTemplate := SockTemplate(
        name="Name", is_input=True,  bl_idname='StringSocket',
            default_value='Armature', blender_property='name' ),
    RotationOrderTemplate := SockTemplate(
        name="Rotation Order", is_input=True,  bl_idname='RotationOrderSocket',
            default_value='XYZ', blender_property='rotation_mode' ),
    ObjectMatrixTemplate := SockTemplate(
        name="Matrix", is_input=True,  bl_idname='MatrixSocket',
            blender_property='matrix_world' ),
    RelationshipInSocket := SockTemplate(
        name="Relationship", is_input=True,  bl_idname='RelationshipSocket', ),
    xFormOutTemplate := SockTemplate(
        name="xForm Out", is_input=False,  bl_idname='xFormSocket', ),
]

xFormGeometryObjectSockets=[
    replace(NameTemplate, default_value='Object'),
    GeometryTemplate := SockTemplate(
        name="Geometry", is_input=True,  bl_idname='GeometrySocket', ),
    ObjectMatrixTemplate,
    RelationshipInSocket,
    DeformerInTemplate := SockTemplate(name="Deformer", is_input=True,
                                       bl_idname='DeformerSocket', ),
    HideTemplate := SockTemplate(name="Hide in Viewport",
        is_input=True, bl_idname='HideSocket', default_value=False,
        blender_property='hide_viewport' ),
    HideRenderTemplate := SockTemplate(name="Hide in Render",
        is_input=True, bl_idname='BooleanSocket', default_value=False,
        blender_property='hide_render' ),
    xFormOutTemplate,
]

xFormGeometryObjectInstanceSockets=[
    replace(NameTemplate, default_value='Object Instance'),
    SourcexFormTemplate := SockTemplate(
        name="Source Object", is_input=True,  bl_idname='xFormSocket', ),
    AsInstanceTemplate := SockTemplate( name="As Instance", is_input=True,
                            bl_idname='BooleanSocket', default_value=True,),
    ObjectMatrixTemplate,
    RelationshipInSocket,
    DeformerInTemplate,
    HideTemplate,
    HideRenderTemplate,
    xFormOutTemplate,
]

xFormCurvePinSockets = [
    replace(NameTemplate, default_value='Curve Pin'),
    ParentCurveTemplate := SockTemplate(
        name="Parent Curve", is_input=True,  bl_idname='xFormSocket', ),
    SplineIndexTemplate,
    FactorTemplate := SockTemplate(
        name="Curve Pin Factor", is_input=True,  bl_idname='FloatFactorSocket',
        default_value=0.0, blender_property='offset_factor' ),
    ForwardAxisTemplate := SockTemplate(
        name="Forward Axis", is_input=True,  bl_idname='EnumFollowPathForwardAxis',
        default_value="FORWARD_Y", blender_property='forward_axis' ),
    UpAxisTemplate := SockTemplate(
        name="Up Axis", is_input=True,  bl_idname='EnumUpAxis',
        default_value="UP_Z", blender_property='up_axis' ),
    CurvePinDisplaySize := SockTemplate(
        name="Display Size", is_input=True,  bl_idname='FloatPositiveSocket',
        default_value=0.05, blender_property='empty_display_size'),
    xFormOutTemplate,
]

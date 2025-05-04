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
    RelationshipInTemplate := SockTemplate(
        name="Relationship", is_input=True,  bl_idname='RelationshipSocket', ),
    xFormOutTemplate := SockTemplate(
        name="xForm Out", is_input=False,  bl_idname='xFormSocket', ),
]

xFormGeometryObjectSockets=[
    replace(NameTemplate, default_value='Object'),
    GeometryTemplate := SockTemplate(
        name="Geometry", is_input=True,  bl_idname='GeometrySocket', ),
    ObjectMatrixTemplate,
    RelationshipInTemplate,
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
    RelationshipInTemplate,
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

# and bones! this one is a bit much...
from math import pi
xFormBoneSockets = [
    replace(NameTemplate, default_value='Bone', category='always_show'),
    replace(RotationOrderTemplate, category='always_show'),
    BoneMatrixTemplate := replace(ObjectMatrixTemplate,
            blender_property='matrix', category='always_show'),
    replace(RelationshipInTemplate, category='always_show'),
    # IK
    IKStretch := SockTemplate(
        name="IK Stretch", is_input=True,  bl_idname='FloatFactorSocket',
        default_value=0, blender_property='ik_stretch', category='IK'),
    IKLock := SockTemplate(
        name="Lock IK", is_input=True,  bl_idname='BooleanThreeTupleSocket',
        default_value=(False, False, False), category='IK',
        blender_property=('lock_ik_x', 'lock_ik_y', 'lock_ik_z'),),
    IKStiffness := SockTemplate(
        name="IK Stiffness", is_input=True,  bl_idname='BooleanThreeTupleSocket',
        default_value=(0, 0, 0), category='IK',
        blender_property=('ik_stiffness_x', 'ik_stiffness_y', 'ik_stiffness_z')),
    IKLimit := SockTemplate(
        name="Limit IK", is_input=True,  bl_idname='BooleanThreeTupleSocket',
        default_value=(False, False, False), category='IK',
        blender_property=('use_ik_limit_x', 'use_ik_limit_y', 'use_ik_limit_z')),
    IKXMin := SockTemplate(
        name="X Min", is_input=True,  bl_idname='NodeSocketFloatAngle',
        default_value=-pi, blender_property='ik_min_x', category='IK'),
    IKXMax := replace(IKXMin, name="X Max", default_value=pi,
                      blender_property='ik_max_x'),
    IKYMax := replace(IKXMin, name="Y Min", blender_property='ik_min_y'),
    IKYMax := replace(IKXMax, name="Y Max", blender_property='ik_max_y'),
    IKZMax := replace(IKXMin, name="Z Min", blender_property='ik_min_z'),
    IKZMax := replace(IKXMax, name="Z Max", blender_property='ik_max_z'),
    # Visual Stuff
    BoneCollectionTemplate := SockTemplate(name="Bone Collection", is_input=True,
            bl_idname='BoneCollectionSocket', category='Display'),
    CustomObjectTemplate := replace(SourcexFormTemplate, name='Custom Object',
                                    category='Display'),
    OverrideXFormTemplate := replace(SourcexFormTemplate,
                    name='Custom Object xForm Override', category='Display'),
    CustomObjectScaleToBoneTemplate := replace(HideRenderTemplate,
            name='Custom Object Scale to Bone Length', category='Display',
            blender_property='use_custom_shape_bone_size',
            default_value=True,),
    CustomObjectWireframeTemplate := replace(HideRenderTemplate,
            name='Custom Object Wireframe', category='Display',
            blender_property='show_wire', default_value=True,),
    CustomObjectScaleTemplate := SockTemplate(name="Custom Object Scale",
            is_input=True, bl_idname='VectorScaleSocket',
            category='Display', default_value=(1.0,1.0,1.0),),
    CustomObjectScaleTemplate := SockTemplate(name="Custom Object Translation",
            is_input=True, bl_idname='VectorSocket',
            category='Display', default_value=(0.0,0.0,0.0),),
    CustomObjectScaleTemplate := SockTemplate(name="Custom Object Rotation",
            is_input=True, bl_idname='VectorEulerSocket',
            category='Display', default_value=(0.0,0.0,0.0),),
    # Deform Stuff
    BoneDeformTemplate := replace(HideRenderTemplate, name='Deform',
        category='Deform', blender_property='use_deform', default_value=False,),
    EnvelopeDistanceTemplate := SockTemplate( name='Envelope Distance',
            bl_idname='FloatPositiveSocket', category='Deform',
            blender_property='envelope_distance', default_value=0,),
    EnvelopeWeightTemplate := replace(EnvelopeDistanceTemplate,
            name='Envelope Weight', bl_idname = 'FloatFactorSocket',
            blender_property='envelope_weight', default_value=1.0,),
    EnvelopeWeightTemplate := replace(EnvelopeDistanceTemplate,
            name='Envelope Multiply', bl_idname = 'BooleanSocket',
            blender_property='use_envelope_multiply', default_value=False,),
    EnvelopeWeightTemplate := replace(EnvelopeDistanceTemplate,
        name='Envelope Head Radius', blender_property='head_radius', default_value=0.0,),
    EnvelopeWeightTemplate := replace(EnvelopeDistanceTemplate,
        name='Envelope Tail Radius', blender_property='tail_radius', default_value=0.0,),
    # BBone Stuff
    BBoneSegmentsTemplate := SockTemplate(name="BBone Segments", is_input=True,
        bl_idname='UnsignedIntSocket', category = 'bbone',
        blender_property='bbone_segments', default_value=1 ),
    BBoneXSizeTemplate := replace(BBoneSegmentsTemplate, name='BBone X Size',
        bl_idname='FloatSocket', blender_property='bbone_x', default_value=0.0025, ),
    BBoneYSizeTemplate := replace(BBoneXSizeTemplate, name='BBone Z Size',
        blender_property='bbone_y', ),
    BBoneHQDeformation := replace(BBoneSegmentsTemplate, name='BBone HQ Deformation',
        bl_idname='BooleanSocket', blender_property='', default_value=None ),
    BBoneXCurveInTemplate := replace( BBoneXSizeTemplate, name="BBone X Curve-In",
        bl_idname='FloatSocket', blender_property='bbone_curveinx', default_value=0.0, ),
    BBoneZCurveInTemplate := replace(BBoneXCurveInTemplate, name="BBone Z Curve-In",
        blender_property='bbone_curveinz', ),
    BBoneXCurveOutTemplate := replace(BBoneXCurveInTemplate, name="BBone X Curve-Out",
        blender_property='bbone_curveoutx', ),
    BBoneZCurveOutTemplate := replace(BBoneXCurveInTemplate, name="BBone Z Curve-Out",
        blender_property='bbone_curveoutz', ),  # I'm tired of assigning variables, not gonna bother anymore lol
                                                # it's just a conincidence that a lot of these are also unimplemented
    replace(BBoneXCurveInTemplate, name="BBone Roll-In", blender_property='bbone_rollin', ), # CURRENTLY UNIMPLEMENTED
    replace(BBoneXCurveInTemplate, name="BBone Roll-Out", blender_property='bbone_rollout', ), # CURRENTLY UNIMPLEMENTED
    replace(BBoneXCurveInTemplate, name="BBone Inherit End Roll",
            bl_idname='BooleanSocket',), # CURRENTLY UNIMPLEMENTED
    replace(BBoneXCurveInTemplate, name="BBone Scale-In",
            bl_idname='VectorSocket',), # CURRENTLY DOESN'T WORK
    replace(BBoneXCurveInTemplate, name="BBone Scale-Out",
            bl_idname='VectorSocket',), # CURRENTLY DOESN'T WORK
    replace(BBoneXCurveInTemplate, name="BBone Ease-In",), # CURRENTLY DOESN'T WORK
    replace(BBoneXCurveInTemplate, name="BBone Ease-Out",), # CURRENTLY DOESN'T WORK
    replace(BBoneXCurveInTemplate, name="BBone Easing",
            bl_idname='BooleanSocket',), # CURRENTLY DOESN'T WORK
    replace(BBoneXCurveInTemplate, name="BBone Start Handle Type",
            bl_idname="EnumBBoneHandleType",
            blender_property='bbone_handle_type_start',),
    replace(BBoneXCurveInTemplate, name="BBone Custom Start Handle",
            bl_idname="StringSocket",
            blender_property='bbone_custom_handle_start',),
    replace(BBoneXCurveInTemplate, name="BBone Start Handle Scale",
            bl_idname="BooleanThreeTupleSocket",
            blender_property='bbone_handle_use_scale_start',),
    replace(BBoneXCurveInTemplate, name="BBone Start Handle Ease",
            bl_idname='BooleanSocket',),# CURRENTLY DOESN'T WORK),
    replace(BBoneXCurveInTemplate, name="BBone End Handle Type",
            bl_idname="EnumBBoneHandleType",
            blender_property='bbone_handle_type_end',),
    replace(BBoneXCurveInTemplate, name="BBone Custom End Handle",
            bl_idname="StringSocket",
            blender_property='bbone_custom_handle_end',),
    replace(BBoneXCurveInTemplate, name="BBone End Handle Scale",
            bl_idname="BooleanThreeTupleSocket",
            blender_property='bbone_handle_use_scale_end',),
    replace(BBoneXCurveInTemplate, name="BBone End Handle Ease",
            bl_idname='BooleanSocket',),# CURRENTLY DOESN'T WORK),
    # locks
    LockLocationTemplate := SockTemplate(name="Lock Location",
        is_input=True, bl_idname='BooleanThreeTupleSocket', category = 'lock',
        blender_property='lock_location', default_value=[True, True, True] ),
    LockRotationTemplate := replace(LockLocationTemplate, name="Lock Rotation",
        blender_property='lock_rotation',),
    LockRotationTemplate := replace(LockLocationTemplate, name="Lock Scale",
        blender_property='lock_scale',),
    # hide
    replace(HideTemplate, name='Hide', category='always_show',
            blender_property='hide', default_value=False,)
]
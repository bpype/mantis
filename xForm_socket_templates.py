from .mantis_dataclasses import MantisSocketTemplate as SockTemplate
from .misc_nodes_socket_templates import SplineIndexTemplate
from dataclasses import replace
from bpy.app import version as bpy_version

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
    ArmatureDisplayType := SockTemplate(name='Display Type', category='Display',
        default_value='OCTAHEDRAL', blender_property='display_type',
        min_bpy_version=(4,5,0), bl_idname='EnumArmatureDisplayType',  is_input=True,),
    CustomPropsTemplate := SockTemplate(
        name="Custom Properties", is_input=True,  bl_idname='CustomPropSocket',
            use_multi_input=True, is_animatable=False, ),
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
    CustomPropsTemplate,
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
    CustomPropsTemplate,
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
    CustomPropsTemplate,
    xFormOutTemplate,
]

xFormGetBoneSockets = [
    ParentArmatureTemplate := SockTemplate(
        name="Parent Armature", is_input=True,  bl_idname='EnumArmature', ),
    ExistingBoneNameTemplate := replace(NameTemplate, name='Bone',
        default_value='', bl_idname="EnumExistingBoneSocket"),
    xFormOutTemplate,
]


# Some (especially BBone) properties are good to treat differently
#  based on bone/posebone or value/driver
# I'll use these lists to make decisions about that sort of thing
attributes_shared_by_bone_and_pose_bone = [
    "bbone_curveinx",
    "bbone_curveinz",
    "bbone_curveoutx",
    "bbone_curveoutz",
    "bbone_custom_handle_end",
    "bbone_custom_handle_start",
    "bbone_easein",
    "bbone_easeout",
    "bbone_rollin",
    "bbone_rollout",
    "bbone_scalein",
    "bbone_scaleout",
]

# these need to be 1 in edit mode and 0 in pose mode, by default. Pain.
need_different_defaults = [
    ("bbone_easein", 1, 0 ),
    ("bbone_easeout", 1, 0),
]


# VERSIONING for Bone
bone_hide_prop_group='bone'
if bpy_version >= (5,0,0):
    bone_hide_prop_group='pose_bone'
bone_hide_template = replace(HideTemplate, name='Hide', category='always_show',
                            blender_property='hide', default_value=False,
                            prop_owner_group = bone_hide_prop_group)

bbone_template = SockTemplate( name="<BBone Template>",
        default_value = 0.0, blender_property=None, is_input=True,
        bl_idname='FloatSocket', prop_owner_group='bone',)

# And there is some serious confusing stuff regarding BBones so I'll explain...
# Blender has duplicated properties for Bone and Pose Bone
# When there is a driver, you usually want the Pose Bone to hold it
# but when there isn't you probably want it on the Bone since it isn't animated


# Version-dependent for Blender

BoneDisplayType = SockTemplate(name='Display Type', category='Display',
    default_value='ARMATURE_DEFINED', blender_property='display_type',
    min_bpy_version=(4,5,0), bl_idname='EnumDisplayType',
    prop_owner_group='bone', is_input=True,)
# 5.0 needed for these
UseTransformAtCustomShape = SockTemplate(name="Affect Gizmo", category='Display',
    default_value=False, blender_property='use_transform_at_custom_shape', is_input=True,
    min_bpy_version=(5,0,0), bl_idname='BooleanSocket', prop_owner_group='pose_bone',)
UseTransformAroundCustomShape = SockTemplate(name="Use as Pivot", category='Display',
    default_value=False, blender_property='use_transform_around_custom_shape', is_input=True,
    min_bpy_version=(5,0,0), bl_idname='BooleanSocket', prop_owner_group='pose_bone',)



# and bones! this one is a bit much...
from math import pi
xFormBoneSockets = [
    replace(NameTemplate, default_value='Bone', category='always_show',
            is_animatable=False,),
    replace(RotationOrderTemplate, category='always_show',),
    BoneMatrixTemplate := replace(ObjectMatrixTemplate, is_animatable=False,
            blender_property='matrix', category='always_show',),
    replace(RelationshipInTemplate, category='always_show', is_animatable=False,),
    # IK
    IKStretch := SockTemplate(
        name="IK Stretch", is_input=True,  bl_idname='FloatFactorSocket',
        default_value=0, blender_property='ik_stretch', category='IK',
        prop_owner_group='pose_bone',),
    IKLock := SockTemplate(
        name="Lock IK", is_input=True,  bl_idname='BooleanThreeTupleSocket',
        default_value=(False, False, False), category='IK',
        blender_property=('lock_ik_x', 'lock_ik_y', 'lock_ik_z'),
        prop_owner_group='pose_bone', ),
    IKStiffness := SockTemplate(
        name="IK Stiffness", is_input=True,  bl_idname='VectorSocket',
        default_value=(False, False, False), category='IK',
        blender_property=('ik_stiffness_x', 'ik_stiffness_y', 'ik_stiffness_z'),
        prop_owner_group='pose_bone', ),
    IKLimit := SockTemplate(
        name="Limit IK", is_input=True,  bl_idname='BooleanThreeTupleSocket',
        default_value=(False, False, False), category='IK',
        blender_property=('use_ik_limit_x', 'use_ik_limit_y', 'use_ik_limit_z'),
        prop_owner_group='pose_bone', ),
    IKXMin := SockTemplate(
        name="X Min", is_input=True,  bl_idname='NodeSocketFloatAngle',
        default_value=-pi, blender_property='ik_min_x', category='IK',
        prop_owner_group='pose_bone', ),
    IKXMax := replace(IKXMin, name="X Max", default_value=pi,
                      blender_property='ik_max_x',),
    IKYMax := replace(IKXMin, name="Y Min", blender_property='ik_min_y'),
    IKYMax := replace(IKXMax, name="Y Max", blender_property='ik_max_y'),
    IKZMax := replace(IKXMin, name="Z Min", blender_property='ik_min_z'),
    IKZMax := replace(IKXMax, name="Z Max", blender_property='ik_max_z'),
    # Visual Stuff
    BoneCollectionTemplate := SockTemplate(name="Bone Collection", is_input=True,
            bl_idname='BoneCollectionSocket', category='Display', use_multi_input=True,
            is_animatable=False,),
    CustomObjectTemplate := replace(SourcexFormTemplate, name='Custom Object',
        category='Display', is_animatable=False,),
    OverrideXFormTemplate := replace(SourcexFormTemplate, is_animatable=False,
        name='Custom Object xForm Override', category='Display',),
    CustomObjectScaleToBoneTemplate := replace(HideRenderTemplate,
        name='Custom Object Scale to Bone Length', category='Display',
        blender_property='use_custom_shape_bone_size',
        default_value=True, prop_owner_group='pose_bone', ),
    UseTransformAtCustomShape, # requires Blender >= 5.0 to use
    UseTransformAroundCustomShape, # requires Blender >= 5.0 to use
    CustomObjectWireWidth := SockTemplate(name='Custom Object Wire Width',
        category='Display', default_value=1.0, blender_property='custom_shape_wire_width',
        bl_idname='FloatPositiveSocket', prop_owner_group='pose_bone', is_input=True,),
    BoneDisplayType, # requires Blender >= 4.5.0 to use
    CustomObjectWireframeTemplate := replace(HideRenderTemplate,
            name='Custom Object Wireframe', category='Display',
            blender_property='show_wire', default_value=True,
            prop_owner_group='bone', ),
    CustomObjectScaleTemplate := SockTemplate(name="Custom Object Scale",
            is_input=True, bl_idname='VectorScaleSocket',
            category='Display', default_value=(1.0,1.0,1.0),
            blender_property = 'custom_shape_scale_xyz',
            prop_owner_group='pose_bone', ),
    CustomObjectTranslationTemplate := SockTemplate(name="Custom Object Translation",
            is_input=True, bl_idname='VectorSocket',
            category='Display', default_value=(0.0,0.0,0.0),
            blender_property = 'custom_shape_translation',
            prop_owner_group='pose_bone', ),
    CustomObjectRotationTemplate := SockTemplate(name="Custom Object Rotation",
            is_input=True, bl_idname='VectorEulerSocket',
            category='Display', default_value=(0.0,0.0,0.0),
            blender_property = 'custom_shape_rotation_euler',
            prop_owner_group='pose_bone', ),
    CustomColor := SockTemplate(name="Color",
            is_input=True, bl_idname='ColorSetSocket',
            category='Display', is_animatable=False,),
    InheritColor := SockTemplate(name="Inherit Color",
            is_input=True, bl_idname='BooleanSocket', is_animatable=False,
            category='Display', default_value=True, prop_owner_group='pose_bone', ),
    # Deform Stuff
    BoneDeformTemplate := replace(HideRenderTemplate, name='Deform',
        category='Deform', blender_property='use_deform', default_value=False,
        prop_owner_group='edit_bone', is_animatable=False,),
    EnvelopeDistanceTemplate := SockTemplate( name='Envelope Distance',
        bl_idname='FloatPositiveSocket', category='Deform',
        blender_property='envelope_distance', default_value=0,
        is_input=True, prop_owner_group='edit_bone', is_animatable=False,),
    EnvelopeWeightTemplate := replace(EnvelopeDistanceTemplate,
        name='Envelope Weight', bl_idname = 'FloatFactorSocket',
        blender_property='envelope_weight', default_value=1.0,
        prop_owner_group='edit_bone', is_animatable=False,),
    EnvelopeMultiplyTemplate := replace(EnvelopeDistanceTemplate,
        name='Envelope Multiply', bl_idname = 'BooleanSocket',
        blender_property='use_envelope_multiply', default_value=False,
        prop_owner_group='edit_bone', is_animatable=False,),
    EnvelopeHeadRadiusTemplate := replace(EnvelopeDistanceTemplate,
        name='Envelope Head Radius', blender_property='head_radius', default_value=0.0,),
    EnvelopeTailRadiusTemplate := replace(EnvelopeDistanceTemplate,
        name='Envelope Tail Radius', blender_property='tail_radius', default_value=0.0,),
    # BBone Stuff
    BBoneSegmentsTemplate := SockTemplate(name="BBone Segments", is_input=True,
        bl_idname='UnsignedIntSocket', category = 'bbone',
        blender_property='bbone_segments', default_value=1,
        prop_owner_group='bone', ),
    BBoneXSizeTemplate := replace(BBoneSegmentsTemplate, name='BBone X Size',
        bl_idname='FloatSocket', blender_property='bbone_x', default_value=0.0025,
        prop_owner_group='bone',),
    BBoneZSizeTemplate := replace(BBoneXSizeTemplate, name='BBone Z Size',
        blender_property='bbone_z', ),
    BBoneHQDeformation := replace(BBoneSegmentsTemplate, name='BBone HQ Deformation',
        bl_idname='BooleanSocket', blender_property='', default_value=None, is_animatable=False, ),
    BBoneXCurveInTemplate := replace( BBoneXSizeTemplate, name="BBone X Curve-In",
        bl_idname='FloatSocket', blender_property='bbone_curveinx', default_value=0.0,
        prop_owner_group='bone',),
    BBoneZCurveInTemplate := replace(BBoneXCurveInTemplate, name="BBone Z Curve-In",
        blender_property='bbone_curveinz', prop_owner_group='bone', ),
    BBoneXCurveOutTemplate := replace(BBoneXCurveInTemplate, name="BBone X Curve-Out",
                                      default_value=0.0,
        blender_property='bbone_curveoutx', prop_owner_group='bone', ),
    BBoneZCurveOutTemplate := replace(BBoneXCurveInTemplate, name="BBone Z Curve-Out",
        blender_property='bbone_curveoutz', prop_owner_group='bone', ), 
    replace(bbone_template, name="BBone Roll-In",
            default_value = 0.0,
            blender_property='bbone_rollin',),
    replace(bbone_template, name="BBone Roll-Out", blender_property='bbone_rollout', ),
    replace(bbone_template, name="BBone Inherit End Roll",
            bl_idname='BooleanSocket', default_value=False,
            blender_property = 'use_endroll_as_inroll',
            is_animatable=False, prop_owner_group='bone',),
    replace(bbone_template, name="BBone Scale-In",
            bl_idname='VectorSocket', default_value=(1.0,1.0,1.0),
            blender_property = 'bbone_scalein'),
    replace(bbone_template, name="BBone Scale-Out",
            bl_idname='VectorSocket', default_value=(1.0,1.0,1.0),
            blender_property = 'bbone_scaleout'),
    replace(bbone_template, name="BBone Ease-In",
            blender_property = 'bbone_easein'),
    replace(bbone_template, name="BBone Ease-Out",
            blender_property = 'bbone_easeout'),
    replace(bbone_template, name="BBone Easing",
            bl_idname='BooleanSocket', default_value=False,
            blender_property='use_scale_easing',  prop_owner_group='bone',),
    replace(bbone_template, name="BBone Start Handle Type",
            bl_idname="EnumBBoneHandleType",
            blender_property='bbone_handle_type_start', default_value=None,
            prop_owner_group='bone', is_animatable=False,),
    replace(bbone_template, name="BBone Custom Start Handle",
            bl_idname="StringSocket",
            blender_property=None, # not handled by this system
            default_value=None, is_animatable=False,),
    replace(bbone_template, name="BBone Start Handle Scale",
            bl_idname="BooleanThreeTupleSocket",
            default_value = (False, False, False),
            blender_property='bbone_handle_use_scale_start',
            prop_owner_group='bone', ),
    replace(bbone_template, name="BBone Start Handle Ease",
            bl_idname='BooleanSocket', default_value=False,
            blender_property = 'bbone_handle_use_ease_start',
            prop_owner_group='bone',),
    replace(bbone_template, name="BBone End Handle Type",
            bl_idname="EnumBBoneHandleType",
            blender_property='bbone_handle_type_end', default_value=None,
            prop_owner_group='bone', is_animatable=False,),
    replace(bbone_template, name="BBone Custom End Handle",
            bl_idname="StringSocket",
            blender_property=None, # not handled by this system
            default_value=None, is_animatable=False,),
    replace(bbone_template, name="BBone End Handle Scale",
            bl_idname="BooleanThreeTupleSocket",
            default_value= (False, False, False),
            blender_property='bbone_handle_use_scale_end',
            prop_owner_group='bone',),
    replace(bbone_template, name="BBone End Handle Ease",
            bl_idname='BooleanSocket', default_value=False,
            blender_property = 'bbone_handle_use_ease_end',
            prop_owner_group='bone',),
    # locks
    LockLocationTemplate := SockTemplate(name="Lock Location",
        is_input=True, bl_idname='BooleanThreeTupleSocket', category = 'lock',
        blender_property='lock_location', default_value=[True, True, True],
        prop_owner_group='pose_bone', ),
    LockRotationTemplate := replace(LockLocationTemplate, name="Lock Rotation",
        blender_property='lock_rotation',),
    LockRotationTemplate := replace(LockLocationTemplate, name="Lock Scale",
        blender_property='lock_scale',),
    # hide
    bone_hide_template,
    CustomPropsTemplate,
    # Output
    xFormOutTemplate,
]

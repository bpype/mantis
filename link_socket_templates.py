from .base_definitions import MantisSocketTemplate as SockTemplate
from bpy import app

from .misc_nodes_socket_templates import SplineIndexTemplate
# Socket Templates we will reuse:
# inputs:
InputRelationshipTemplate : SockTemplate = SockTemplate(
    name="Input Relationship", is_input=True,  bl_idname='RelationshipSocket', )
TargetTemplate : SockTemplate = SockTemplate(
    name="Target", is_input=True,  bl_idname='xFormSocket', )
Head_Tail_Template : SockTemplate = SockTemplate(
    name="Head/Tail", is_input=True,  bl_idname='FloatFactorSocket',
    default_value=0.0, blender_property='head_tail' )
UseBBoneTemplate : SockTemplate = SockTemplate(
    name="UseBBone", is_input=True,  bl_idname='BooleanSocket',
    default_value=False, blender_property='use_bbone_shape' )
AxeSockTemplate : SockTemplate = SockTemplate(
    name="Axes", is_input=True,  bl_idname='BooleanThreeTupleSocket',
    default_value=[True, True, True], blender_property=['use_x', 'use_y', 'use_z'])
AxesInvertTemplate : SockTemplate = SockTemplate(
    name="Invert", is_input=True,  bl_idname='BooleanThreeTupleSocket',
    default_value=[False, False, False], blender_property=['invert_x', 'invert_y', 'invert_z'])
TargetSpaceTemplate : SockTemplate = SockTemplate(
    name="Target Space", is_input=True,  bl_idname='TransformSpaceSocket',
    default_value="WORLD", blender_property='target_space' )
OwnerSpaceTemplate : SockTemplate = SockTemplate(
    name="Owner Space", is_input=True,  bl_idname='TransformSpaceSocket',
    default_value="WORLD", blender_property='owner_space' )
InfluenceTemplate : SockTemplate = SockTemplate(
    name="Influence", is_input=True,  bl_idname='FloatFactorSocket',
    default_value=1.0, blender_property='influence')
EnableTemplate : SockTemplate = SockTemplate(
    name="Enable", is_input=True,  bl_idname='EnableSocket',
    default_value=True, blender_property='mute')
OffsetTemplate : SockTemplate = SockTemplate(
    name="Offset", bl_idname='BooleanSocket', is_input=True,
    default_value=False, blender_property='use_offset')
# Limit Constraints follow a pattern and can use this generator
LimitTemplateGenerator = lambda name_stub, axis : SockTemplate(
    name=name_stub+axis.upper(), is_input=True,  bl_idname='BooleanSocket' if "Use" in name_stub else "FloatSocket",
    default_value=False, blender_property=name_stub.lower().replace(' ', '_')+axis.lower())
LimitAxesSocketTemplates = [] # could generate these with loops, but this is easier to understand
LimitAxesSocketTemplates.append(UseMaxXTemplate := LimitTemplateGenerator("Use Max ", "X"))
LimitAxesSocketTemplates.append(MaxXTemplate    := LimitTemplateGenerator("Max ", "X"))
LimitAxesSocketTemplates.append(UseMaxYTemplate := LimitTemplateGenerator("Use Max ", "Y"))
LimitAxesSocketTemplates.append(MaxYTemplate    := LimitTemplateGenerator("Max ", "Y"))
LimitAxesSocketTemplates.append(UseMaxZTemplate := LimitTemplateGenerator("Use Max ", "Z"))
LimitAxesSocketTemplates.append(MaxZTemplate    := LimitTemplateGenerator("Max ", "Z"))
LimitAxesSocketTemplates.append(UseMinXTemplate := LimitTemplateGenerator("Use Min ", "X"))
LimitAxesSocketTemplates.append(MinXTemplate    := LimitTemplateGenerator("Min ", "X"))
LimitAxesSocketTemplates.append(UseMinYTemplate := LimitTemplateGenerator("Use Min ", "Y"))
LimitAxesSocketTemplates.append(MinYTemplate    := LimitTemplateGenerator("Min ", "Y"))
LimitAxesSocketTemplates.append(UseMinZTemplate := LimitTemplateGenerator("Use Min ", "Z"))
LimitAxesSocketTemplates.append(MinZTemplate    := LimitTemplateGenerator("Min ", "Z"))
LimitRotationSocketTemplates = [
    UseXTemplate := LimitTemplateGenerator("Use ", "X"),
    MaxXTemplate,
    MinXTemplate,
    UseYTemplate := LimitTemplateGenerator("Use ", "Y"),
    MaxYTemplate,
    MinYTemplate,
    UseZTemplate := LimitTemplateGenerator("Use ", "Z"),
    MaxZTemplate,
    MinZTemplate,
]
# annoyingly these are a little different than the pattern:
UseXTemplate.blender_property='use_limit_x'
UseYTemplate.blender_property='use_limit_y'
UseZTemplate.blender_property='use_limit_z'
AffectTransformTemplate : SockTemplate = SockTemplate(
    name="Affect Transform", bl_idname='BooleanSocket', is_input=True,
    default_value=False, blender_property='use_transform_limit')

# Tracking
TrackAxisTemplate= SockTemplate(name="Track Axis", bl_idname="EnumTrackAxis",
            is_input=True, default_value='TRACK_Y', blender_property='track_axis')

# outputs:
OutputRelationshipTemplate : SockTemplate = SockTemplate(
    name="Output Relationship", is_input=False,  bl_idname='RelationshipSocket', )


LinkInheritSockets = [              
    SockTemplate(name="Inherit Rotation", is_input=True,
                 bl_idname='BooleanSocket',       default_value=True,),
    SockTemplate(name="Inherit Scale",    is_input=True,
                 bl_idname='EnumInheritScale',    default_value="FULL",),
    SockTemplate(name="Connected",        is_input=True,
                 bl_idname='BooleanSocket',       default_value=False,),
    SockTemplate(name="Parent",           is_input=True,   bl_idname='xFormSocket',),
    SockTemplate(name="Inheritance",      is_input=False,  bl_idname='RelationshipSocket',),
]


LinkCopyLocationSockets = [
    InputRelationshipTemplate,
    Head_Tail_Template,
    UseBBoneTemplate,
    AxeSockTemplate,
    AxesInvertTemplate,
    TargetSpaceTemplate,
    OwnerSpaceTemplate,
    OffsetTemplate,
    InfluenceTemplate,
    TargetTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]
    
LinkCopyRotationSockets = [
    InputRelationshipTemplate,
    SockTemplate(name='RotationOrder', bl_idname='RotationOrderSocket', is_input=True,
                         default_value='AUTO', blender_property='euler_order'),
    SockTemplate(name='Rotation Mix',  bl_idname='EnumRotationMix', is_input=True,
                         default_value='REPLACE', blender_property='mix_mode'),
    AxeSockTemplate,
    AxesInvertTemplate,
    TargetSpaceTemplate,
    OwnerSpaceTemplate,
    InfluenceTemplate,
    TargetTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

LinkCopyScaleSockets = [
    InputRelationshipTemplate,
    OffsetTemplate,
    SockTemplate(name='Average', bl_idname = 'BooleanSocket', is_input=True,
                         default_value=False, blender_property='use_make_uniform'),
    SockTemplate(name='Additive', bl_idname = 'BooleanSocket', is_input=True,
                         default_value=False, blender_property='use_add'),
    AxeSockTemplate,
    SockTemplate(name='Power', bl_idname = 'FloatFactorSocket', is_input=True,
                         default_value=1.0, blender_property='power'),
    TargetSpaceTemplate,
    OwnerSpaceTemplate,
    InfluenceTemplate,
    TargetTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

LinkCopyTransformsSockets = [
    InputRelationshipTemplate,
    Head_Tail_Template,
    UseBBoneTemplate,
    SockTemplate(name='Mix', bl_idname = 'EnumRotationMixCopyTransforms', is_input=True,
                         default_value="REPLACE", blender_property='mix_mode'),
    TargetSpaceTemplate,
    OwnerSpaceTemplate,
    InfluenceTemplate,
    TargetTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

TransformationMinMaxTemplateGenerator = lambda name, bprop  : SockTemplate(
    name=name, is_input=True,
    bl_idname='EnumTransformationAxes' if "Source" in name else "FloatSocket",
    default_value='X' if "Source" in name else 1.0,
    blender_property=bprop)
    
LinkTransformationSockets = [
    InputRelationshipTemplate,
    TargetTemplate,
    OwnerSpaceTemplate,
    TargetSpaceTemplate,
    SockTemplate(name="Extrapolate", is_input=True, bl_idname='BooleanSocket',
                default_value=False, blender_property='use_motion_extrapolate'),
    SockTemplate(name="Map From", is_input=True, bl_idname='EnumTransformationMap',
                default_value="LOCATION", blender_property='map_from'),
    SockTemplate(name="Rotation Mode", is_input=True, bl_idname='EnumTransformationRotationMode',
                default_value="AUTO", blender_property='from_rotation_mode', hide=True),
    TransformationMinMaxTemplateGenerator("X Min From", "from_min_x"),
    TransformationMinMaxTemplateGenerator("X Max From", "from_max_x"),
    TransformationMinMaxTemplateGenerator("Y Min From", "from_min_y"),
    TransformationMinMaxTemplateGenerator("Y Max From", "from_max_y"),
    TransformationMinMaxTemplateGenerator("Z Min From", "from_min_z"),
    TransformationMinMaxTemplateGenerator("Z Max From", "from_max_z"),
    SockTemplate(name="Map To", is_input=True, bl_idname='EnumTransformationMap',
                default_value="LOCATION", blender_property='map_to'),
    SockTemplate(name="Rotation Order", is_input=True, bl_idname='EnumTransformationRotationOrder',
                default_value="AUTO", blender_property='to_euler_order', hide=True),
    TransformationMinMaxTemplateGenerator("X Source Axis", "map_to_x_from"),
    TransformationMinMaxTemplateGenerator("X Min To", "to_min_x"),
    TransformationMinMaxTemplateGenerator("X Max To", "to_max_x"),
    TransformationMinMaxTemplateGenerator("Y Source Axis", "map_to_y_from"),
    TransformationMinMaxTemplateGenerator("Y Min To", "to_min_y"),
    TransformationMinMaxTemplateGenerator("Y Max To", "to_max_y"),
    TransformationMinMaxTemplateGenerator("Z Source Axis", "map_to_z_from"),
    TransformationMinMaxTemplateGenerator("Z Min To", "to_min_z"),
    TransformationMinMaxTemplateGenerator("Z Max To", "to_max_z"),
    SockTemplate(name="Mix Mode (Translation)", is_input=True,
                 bl_idname='EnumTransformationTranslationMixMode',
                default_value="REPLACE", blender_property='mix_mode',),
    SockTemplate(name="Mix Mode (Rotation)", is_input=True,
                 bl_idname='EnumTransformationRotationMixMode',
                default_value="ADD", blender_property='mix_mode_rot',  hide=True),
    SockTemplate(name="Mix Mode (Scale)", is_input=True,
                 bl_idname='EnumTransformationScaleMixMode',
                default_value="REPLACE", blender_property='mix_mode_scale',  hide=True),
    InfluenceTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

LinkLimitLocationScaleSockets = [
    InputRelationshipTemplate,
    *LimitAxesSocketTemplates, # we generated these ahead of time in a list
    AffectTransformTemplate,
    OwnerSpaceTemplate,
    InfluenceTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

LinkLimitRotationSockets = [
    InputRelationshipTemplate,
    *LimitRotationSocketTemplates, # we generated these ahead of time in a list
    AffectTransformTemplate,
    OwnerSpaceTemplate,
    InfluenceTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

LinkLimitLocationScaleSockets = [
    InputRelationshipTemplate,
    *LimitAxesSocketTemplates, # we generated these ahead of time in a list
    AffectTransformTemplate,
    OwnerSpaceTemplate,
    InfluenceTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]
LinkLimitDistanceSockets = [
    InputRelationshipTemplate,
    Head_Tail_Template,
    UseBBoneTemplate,
    SockTemplate(name="Distance", bl_idname='FloatSocket', is_input=True,
                 default_value=0.0, blender_property='distance'),
    SockTemplate(name="Clamp Region", bl_idname="EnumLimitMode", is_input=True,
                 default_value='LIMITDIST_INSIDE', blender_property='limit_mode'),
    AffectTransformTemplate,
    OwnerSpaceTemplate,
    TargetSpaceTemplate,
    InfluenceTemplate,
    TargetTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

LinkStretchToSockets = [
    InputRelationshipTemplate,
    Head_Tail_Template,
    UseBBoneTemplate,
    SockTemplate(name="Original Length", bl_idname='FloatSocket', is_input=True,
                 default_value=0.0, blender_property='rest_length'),
    SockTemplate(name="Volume Variation", bl_idname='FloatSocket', is_input=True,
                 default_value=1.0, blender_property='bulge'),
    SockTemplate(name="Use Volume Min", bl_idname='BoolUpdateParentNode', is_input=True,
                 default_value=False, blender_property='use_bulge_min'),
    SockTemplate(name="Volume Min", bl_idname='FloatSocket', is_input=True,
                 default_value=1.0, blender_property='bulge_min'),
    SockTemplate(name="Use Volume Max", bl_idname='BoolUpdateParentNode', is_input=True,
                 default_value=False, blender_property='use_bulge_max'),
    SockTemplate(name="Volume Max", bl_idname='FloatSocket', is_input=True,
                 default_value=1.0, blender_property='bulge_max'),
    SockTemplate(name="Smooth", bl_idname='FloatFactorSocket', is_input=True,
                 default_value=0.0, blender_property='bulge_smooth'),
    SockTemplate(name="Maintain Volume", bl_idname='EnumMaintainVolumeStretchToSocket', is_input=True,
                 default_value="VOLUME_XZX", blender_property='volume'),
    SockTemplate(name="Rotation", bl_idname='EnumRotationStretchTo', is_input=True,
                 default_value="SWING_Y", blender_property='keep_axis'),
    InfluenceTemplate,
    TargetTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

LinkDampedTrackSockets =[
    InputRelationshipTemplate,
    Head_Tail_Template,
    UseBBoneTemplate,
    TrackAxisTemplate,
    InfluenceTemplate,
    TargetTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

LinkLockedTrackSockets =[
    InputRelationshipTemplate,
    Head_Tail_Template,
    UseBBoneTemplate,
    TrackAxisTemplate,
    SockTemplate(name="Lock Axis", bl_idname="EnumLockAxis", is_input=True,
                 default_value="LOCK_Z", blender_property='lock_axis'),
    InfluenceTemplate,
    TargetTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

# NOTE: I am setting different default values here than Blender in order to remain
#       consistent with the track constraints tracking the bone to the target.
LinkTrackToSockets = [
    InputRelationshipTemplate,
    Head_Tail_Template,
    UseBBoneTemplate,
    TrackAxisTemplate,
    SockTemplate(name="Up Axis", bl_idname="EnumUpAxis", is_input=True,
                 default_value="UP_Z", blender_property='up_axis'),
    SockTemplate(name="Use Target Z", bl_idname="BooleanSocket", is_input=True,
                 default_value=False, blender_property='use_target_z'),
    TargetSpaceTemplate,
    OwnerSpaceTemplate,
    InfluenceTemplate,
    TargetTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

# relationships & misc.
LinkInheritConstraintSockets = [
    InputRelationshipTemplate,
    SockTemplate(name="Location", bl_idname='BooleanThreeTupleSocket',
                  is_input=True, default_value=[True, True, True],
                 blender_property=['use_location_x', 'use_location_y', 'use_location_z']),
    SockTemplate(name="Rotation", bl_idname='BooleanThreeTupleSocket',
                  is_input=True, default_value=[True, True, True],
                 blender_property=['use_rotation_x', 'use_rotation_y', 'use_rotation_z']),
    SockTemplate(name="Scale", bl_idname='BooleanThreeTupleSocket',
                  is_input=True, default_value=[True, True, True],
                 blender_property=['use_scale_x', 'use_scale_y', 'use_scale_z']),
    InfluenceTemplate,
    TargetTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

LinkInverseKinematicsSockets = [
    InputRelationshipTemplate,
    TargetTemplate,
    SockTemplate(name="Pole Target", is_input=True,  bl_idname='xFormSocket', ),
    ChainLengthTemplate := SockTemplate(name="Chain Length",
                 bl_idname="IntSocket", is_input=True,
                 default_value=0, blender_property='chain_count'),
    SockTemplate(name="Use Tail", bl_idname="BooleanSocket", is_input=True,
                 default_value=True, blender_property='use_tail'),
    SockTemplate(name="Stretch", bl_idname="BooleanSocket", is_input=True,
                 default_value=True, blender_property='use_stretch'),
    SockTemplate(name="Position", bl_idname="FloatFactorSocket", is_input=True,
                 default_value=1.0, blender_property='weight'),
    SockTemplate(name="Rotation", bl_idname="FloatFactorSocket", is_input=True,
                 default_value=0.0, blender_property='orient_weight'),
    InfluenceTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

LinkDrivenParameterSockets = [
    InputRelationshipTemplate,
    SockTemplate(name="Value", bl_idname="FloatSocket", is_input=True,
                 default_value=-0.0,),
    SockTemplate(name="Parameter", bl_idname="ParameterStringSocket", is_input=True,
                 default_value="",),
    SockTemplate(name="Index", bl_idname="IntSocket", is_input=True,
                 default_value=0,),
    OutputRelationshipTemplate,
]
  
LinkArmatureSockets=[
    InputRelationshipTemplate,
    SockTemplate(name="Preserve Volume", bl_idname='BooleanSocket', is_input=True,
                 default_value=False, blender_property='use_deform_preserve_volume'),
    SockTemplate(name="Use Envelopes", bl_idname='BooleanSocket', is_input=True,
                 default_value=False, blender_property='use_bone_envelopes'),
    SockTemplate(name="Use Current Location", bl_idname='BooleanSocket', is_input=True,
                 default_value=False, blender_property='use_current_location'),
    InfluenceTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

LinkSplineIKSockets = [
    InputRelationshipTemplate,
    TargetTemplate,
    SplineIndexTemplate,
    ChainLengthTemplate,
    SockTemplate(name="Even Divisions", bl_idname="BooleanSocket", is_input=True,
                 default_value=False, blender_property='use_even_divisions'),
    SockTemplate(name="Chain Offset", bl_idname="BooleanSocket", is_input=True,
                 default_value=False, blender_property='use_chain_offset'),
    SockTemplate(name="Use Curve Radius", bl_idname="BooleanSocket", is_input=True,
                 default_value=True, blender_property='use_curve_radius'),
    SockTemplate(name="Y Scale Mode", bl_idname="EnumYScaleMode", is_input=True,
                 default_value="FIT_CURVE", blender_property='y_scale_mode'),
    SockTemplate(name="XZ Scale Mode", bl_idname="EnumXZScaleMode", is_input=True,
                 default_value="NONE", blender_property='xz_scale_mode'),
    #IMPORTANT NOTE: This socket is removed in 4.5
    SockTemplate(name="Use Original Scale", bl_idname="BooleanSocket", is_input=True,
                 default_value=False, blender_property='use_original_scale'),
    InfluenceTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

LinkFloorSockets = [
    InputRelationshipTemplate,
    TargetTemplate,
    FloorOffsetTemplate := SockTemplate(name="Offset", bl_idname="BooleanSocket",
            is_input=True, default_value=False, blender_property='offset'),
    FloorAxisTemplate := SockTemplate(name='Min/Max', bl_idname='EnumFloorAxis',
            is_input = True, default_value="FLOOR_X", blender_property="floor_location"),
    FloorUseRotation := SockTemplate(name="Rotation", bl_idname='BooleanSocket',
            is_input=True, default_value=False, blender_property='use_rotation',),
    TargetSpaceTemplate,
    OwnerSpaceTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

# Remove this socket because of Blender changes.
if (app.version >= (4, 5, 0)):
    LinkSplineIKSockets.pop(9)
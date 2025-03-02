import bpy
from bpy.types import NodeTree, Node, NodeSocket
from .base_definitions import MantisNode, LinkNode, GraphError
from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

from .base_definitions import get_signature_from_edited_tree

def TellClasses():
    return [ LinkInheritNode,
             LinkInverseKinematics,
             LinkCopyLocationNode,
             LinkCopyRotationNode,
             LinkCopyScaleNode,
             LinkInheritConstraintNode,
             LinkCopyTransformNode,
             LinkStretchToNode,
             LinkDampedTrackNode,
             LinkLockedTrackNode,
             LinkTrackToNode,
             LinkLimitLocationNode,
             LinkLimitScaleNode,
             LinkLimitRotationNode,
             LinkLimitDistanceNode,
             LinkDrivenParameterNode,
             LinkArmatureNode,
             LinkSplineIKNode,
             LinkTransformationNode,
           ]

def default_traverse(self, socket):
        if (socket == self.outputs["Output Relationship"]):
            return self.inputs["Input Relationship"]
        if (socket == self.inputs["Input Relationship"]):
            return self.outputs["Output Relationship"]
        return None


from mathutils import Color # these colors were sampled from Blender's UI
# TODO: maybe read the relevant colors from the Theme
linkColor = Color((0.028034, 0.093164, 0.070379)).from_scene_linear_to_srgb()
inheritColor = Color((0.083213, 0.131242, 0.116497)).from_scene_linear_to_srgb()
trackingColor = Color((0.033114, 0.049013, 0.131248)).from_scene_linear_to_srgb()
ikColor = Color((0.131117, 0.131248, 0.006971)).from_scene_linear_to_srgb()
driverColor = Color((0.043782, 0.014745, 0.131248,)).from_scene_linear_to_srgb()


class LinkInheritNode(Node, LinkNode):
    '''A node representing inheritance'''
    # cuss, messed this up
    bl_idname = 'linkInherit' # l should be L
    # need to fix this
    bl_label = "Inherit"
    bl_icon = 'CONSTRAINT_BONE'
    initialized : bpy.props.BoolProperty(default = False)
    
    
    # bone_prev : bpy.props.BoolProperty(default=False)
    # bone_next : bpy.props.BoolProperty(default=False)

    def init(self, context):
        r = self.inputs.new('BooleanSocket', "Inherit Rotation")
        s = self.inputs.new('EnumInheritScale', "Inherit Scale")
        c = self.inputs.new('BooleanSocket', "Connected")
        i = self.outputs.new('RelationshipSocket', "Inheritance")
        p = self.inputs.new('xFormSocket', "Parent")
        # set default values...
        self.initialized = True
        # color
        self.use_custom_color = True
        self.color = inheritColor

    def traverse(self, socket):
        if (socket == self.outputs["Inheritance"]):
            return self.inputs["Parent"]
        if (socket == self.inputs["Parent"]):
            return self.outputs["Inheritance"]
        return None
    
    def display_update(self, parsed_tree, context):
        node_tree = context.space_data.path[0].node_tree
        nc = parsed_tree.get(get_signature_from_edited_tree(self, context))
        if nc:
            bone_prev, bone_next = False, False
            if (inp := nc.inputs["Parent"]).is_connected:
                if  from_node := inp.links[0].from_node:
                    if from_node.__class__.__name__ in ["xFormBone"]:
                        bone_prev=True
            bone_next=True
            try:
                xForm = nc.GetxForm()
                if xForm.__class__.__name__ not in "xFormBone":
                    
                    bone_next=False
            except GraphError:

                bone_next=False
            # print(bone_prev, bone_next )
            if bone_next and bone_prev:
                self.inputs["Inherit Rotation"].hide = False
                self.inputs["Inherit Scale"].hide    = False
                self.inputs["Connected"].hide       = False
            else:
                self.inputs["Inherit Rotation"].hide = True
                self.inputs["Inherit Scale"].hide    = True
                self.inputs["Connected"].hide        = True
            # the node_groups on the way here ought to be active if there
            #  is no funny business going on.
    

# DO: make another node for ITASC IK, eh?
class LinkInverseKinematics(Node, LinkNode):
    '''A node representing inverse kinematics'''
    bl_idname = 'LinkInverseKinematics'
    bl_label = "Inverse Kinematics"
    bl_icon = 'CON_KINEMATIC'
    initialized : bpy.props.BoolProperty(default = False)
    

    def init(self, context):
        self.inputs.new('RelationshipSocket', "Input Relationship")
        self.inputs.new ('xFormSocket', "Target")
        self.inputs.new ('xFormSocket', "Pole Target")
        self.inputs.new ('IKChainLengthSocket', "Chain Length")
        self.inputs.new ('BooleanSocket', "Use Tail")
        self.inputs.new ('BooleanSocket', "Stretch")
        self.inputs.new ('FloatFactorSocket', "Position")
        self.inputs.new ('FloatFactorSocket', "Rotation")
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('EnableSocket', "Enable")
        
        #Well, it turns out that this has to be a constraint like
        # everything else, because of course, there can be more than one.
        
        #self.outputs.new('RelationshipSocket', "Inheritance")
        self.outputs.new('RelationshipSocket', "Output Relationship")

        self.initialized = True
        # color
        self.use_custom_color = True
        self.color = ikColor


class LinkCopyLocationNode(Node, LinkNode):
    '''A node representing Copy Location'''
    bl_idname = 'LinkCopyLocation'
    bl_label = "Copy Location"
    bl_icon = 'CON_LOCLIKE'
    
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.inputs.new ('RelationshipSocket', "Input Relationship")
        self.inputs.new ('FloatFactorSocket', "Head/Tail")
        self.inputs.new ('BooleanSocket', "UseBBone")
        self.inputs.new ('BooleanThreeTupleSocket', "Axes")
        self.inputs.new ('BooleanThreeTupleSocket', "Invert")
        self.inputs.new ('TransformSpaceSocket', "Target Space")
        self.inputs.new ('TransformSpaceSocket', "Owner Space")
        self.inputs.new ('BooleanSocket', "Offset")
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('xFormSocket', "Target")
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new('RelationshipSocket', "Output Relationship")
        # color
        self.use_custom_color = True
        self.color = linkColor
        self.initialized = True

        
class LinkCopyRotationNode(Node, LinkNode):
    '''A node representing Copy Rotation'''
    bl_idname = 'LinkCopyRotation'
    bl_label = "Copy Rotation"
    bl_icon = 'CON_ROTLIKE'
    
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.inputs.new ('RelationshipSocket', "Input Relationship")
        self.inputs.new ('RotationOrderSocket', "RotationOrder")
        self.inputs.new ('EnumRotationMix', "Rotation Mix")
        self.inputs.new ('BooleanThreeTupleSocket', "Axes")
        self.inputs.new ('BooleanThreeTupleSocket', "Invert")
        self.inputs.new ('TransformSpaceSocket', "Target Space")
        self.inputs.new ('TransformSpaceSocket', "Owner Space")
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('xFormSocket', "Target")
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new('RelationshipSocket', "Output Relationship")
        # color
        self.use_custom_color = True
        self.color = linkColor
        self.initialized = True


        
class LinkCopyScaleNode(Node, LinkNode):
    '''A node representing Copy Scale'''
    bl_idname = 'LinkCopyScale'
    bl_label = "Copy Scale"
    bl_icon = 'CON_SIZELIKE'
    
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.inputs.new ('RelationshipSocket', "Input Relationship")
        self.inputs.new ('BooleanSocket', "Offset")
        self.inputs.new ('BooleanSocket', "Average")
        self.inputs.new ('BooleanThreeTupleSocket', "Axes")
        #self.inputs.new ('BooleanThreeTupleSocket', "Invert")
        # dingus, this one doesn't have inverts
        self.inputs.new ('TransformSpaceSocket', "Target Space")
        self.inputs.new ('TransformSpaceSocket', "Owner Space")
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('xFormSocket', "Target")
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new('RelationshipSocket', "Output Relationship")
        # color
        self.use_custom_color = True
        self.color = linkColor
        self.initialized = True


        
class LinkInheritConstraintNode(Node, LinkNode):
    # === Basics ===
    # Description string
    '''A node representing a parent constraint'''
    bl_idname = 'LinkInheritConstraint'
    bl_label = "Inherit (constraint)"
    bl_icon = 'CON_CHILDOF'
    
    initialized : bpy.props.BoolProperty(default = False)

    # === Optional Functions ===
    def init(self, context):
        self.inputs.new ('RelationshipSocket', "Input Relationship")
        self.inputs.new ('BooleanThreeTupleSocket', "Location")
        self.inputs.new ('BooleanThreeTupleSocket', "Rotation")
        self.inputs.new ('BooleanThreeTupleSocket', "Scale")
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('xFormSocket', "Target")
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new('RelationshipSocket', "Output Relationship")
        # color
        self.use_custom_color = True
        self.color = inheritColor
        self.initialized = True


        
class LinkCopyTransformNode(Node, LinkNode):
    # === Basics ===
    # Description string
    '''A node representing Copy Transform'''
    bl_idname = 'LinkCopyTransforms'
    bl_label = "Copy Transform"
    bl_icon = 'CON_TRANSLIKE'
    
    initialized : bpy.props.BoolProperty(default = False)


    # === Optional Functions ===
    def init(self, context):
        self.inputs.new ('RelationshipSocket', "Input Relationship")
        self.inputs.new ('FloatFactorSocket', "Head/Tail")
        self.inputs.new ('BooleanSocket', "UseBBone")
        self.inputs.new ('EnumRotationMixCopyTransforms', "Mix")
        self.inputs.new ('TransformSpaceSocket', "Target Space")
        self.inputs.new ('TransformSpaceSocket', "Owner Space")
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('xFormSocket', "Target")
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new('RelationshipSocket', "Output Relationship")
        # color
        self.use_custom_color = True
        self.color = linkColor
        self.initialized = True


        
class LinkStretchToNode(Node, LinkNode):
    '''A node representing Stretch-To'''
    bl_idname = 'LinkStretchTo'
    bl_label = "Stretch To"
    bl_icon = 'CON_STRETCHTO'
    
    initialized : bpy.props.BoolProperty(default = False)
    def init(self, context):
        self.inputs.new ('RelationshipSocket', "Input Relationship")
        self.inputs.new ('FloatFactorSocket', "Head/Tail")
        self.inputs.new ('BooleanSocket', "UseBBone")
        self.inputs.new ('FloatSocket', "Original Length")
        self.inputs.new ('FloatSocket', "Volume Variation")
        self.inputs.new ('BoolUpdateParentNode', "Use Volume Min")
        self.inputs.new ('FloatSocket', "Volume Min")
        self.inputs.new ('BoolUpdateParentNode', "Use Volume Max")
        self.inputs.new ('FloatSocket', "Volume Max")
        self.inputs.new ('FloatFactorSocket', "Smooth")
        self.inputs.new ('EnumMaintainVolumeStretchToSocket', "Maintain Volume")
        self.inputs.new ('EnumRotationStretchTo', "Rotation")
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('xFormSocket', "Target")
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new('RelationshipSocket', "Output Relationship")

        self.initialized = True
        # color
        self.use_custom_color = True
        self.color = trackingColor


        
class LinkDampedTrackNode(Node, LinkNode):
    '''A node representing Stretch-To'''
    bl_idname = 'LinkDampedTrack'
    bl_label = "Damped Track"
    bl_icon = 'CON_TRACKTO'
    
    initialized : bpy.props.BoolProperty(default = False)
    def init(self, context):
        self.inputs.new ('RelationshipSocket', "Input Relationship")
        self.inputs.new ('FloatFactorSocket', "Head/Tail")
        self.inputs.new ('BooleanSocket', "UseBBone")
        self.inputs.new ('EnumTrackAxis', "Track Axis")
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('xFormSocket', "Target")
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new('RelationshipSocket', "Output Relationship")

        self.initialized = True
        # color
        self.use_custom_color = True
        self.color = trackingColor


        
class LinkLockedTrackNode(Node, LinkNode):
    '''A node representing Stretch-To'''
    bl_idname = 'LinkLockedTrack'
    bl_label = "Locked Track"
    bl_icon = 'CON_LOCKTRACK'
    
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.inputs.new ('RelationshipSocket', "Input Relationship")
        self.inputs.new ('FloatFactorSocket', "Head/Tail")
        self.inputs.new ('BooleanSocket', "UseBBone")
        self.inputs.new ('EnumTrackAxis', "Track Axis")
        self.inputs.new ('EnumLockAxis', "Lock Axis")
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('xFormSocket', "Target")
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new('RelationshipSocket', "Output Relationship")

        self.initialized = True
        # color
        self.use_custom_color = True
        self.color = trackingColor


        
class LinkTrackToNode(Node, LinkNode):
    '''A node representing Stretch-To'''
    bl_idname = 'LinkTrackTo'
    bl_label = "Track To"
    bl_icon = 'CON_TRACKTO'
    
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.inputs.new ('RelationshipSocket', "Input Relationship")
        self.inputs.new ('FloatFactorSocket', "Head/Tail")
        self.inputs.new ('BooleanSocket', "UseBBone")
        self.inputs.new ('EnumTrackAxis', "Track Axis")
        self.inputs.new ('EnumUpAxis', "Up Axis")
        self.inputs.new ('BooleanSocket', "Use Target Z")
        self.inputs.new ('TransformSpaceSocket', "Target Space")
        self.inputs.new ('TransformSpaceSocket', "Owner Space")
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('xFormSocket', "Target")
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new('RelationshipSocket', "Output Relationship")

        self.initialized = True
        # color
        self.use_custom_color = True
        self.color = trackingColor


        
class LinkLimitLocationNode(Node, LinkNode):
    '''A node representing Limit Location'''
    bl_idname = 'LinkLimitLocation'
    bl_label = "Limit Location"
    bl_icon = 'CON_LOCLIMIT'
    
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.inputs.new ('RelationshipSocket', "Input Relationship")
        self.inputs.new ('BoolUpdateParentNode', "Use Max X")
        self.inputs.new ('FloatSocket', "Max X")
        self.inputs.new ('BoolUpdateParentNode', "Use Min X")
        self.inputs.new ('FloatSocket', "Min X")
        self.inputs.new ('BoolUpdateParentNode', "Use Max Y")
        self.inputs.new ('FloatSocket', "Max Y")
        self.inputs.new ('BoolUpdateParentNode', "Use Min Y")
        self.inputs.new ('FloatSocket', "Min Y")
        self.inputs.new ('BoolUpdateParentNode', "Use Max Z")
        self.inputs.new ('FloatSocket', "Max Z")
        self.inputs.new ('BoolUpdateParentNode', "Use Min Z")
        self.inputs.new ('FloatSocket', "Min Z")
        self.inputs.new ('BooleanSocket', "Affect Transform")
        self.inputs.new ('TransformSpaceSocket', "Owner Space")
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new('RelationshipSocket', "Output Relationship")
        self.initialized = True
        # color
        self.use_custom_color = True
        self.color = linkColor


            
class LinkLimitScaleNode(Node, LinkNode):
    '''A node representing Limit Scale'''
    bl_idname = 'LinkLimitScale'
    bl_label = "Limit Scale"
    bl_icon = 'CON_SIZELIMIT'
    
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.inputs.new ('RelationshipSocket', "Input Relationship")
        self.inputs.new ('BoolUpdateParentNode', "Use Max X")
        self.inputs.new ('FloatSocket', "Max X")
        self.inputs.new ('BoolUpdateParentNode', "Use Min X")
        self.inputs.new ('FloatSocket', "Min X")
        self.inputs.new ('BoolUpdateParentNode', "Use Max Y")
        self.inputs.new ('FloatSocket', "Max Y")
        self.inputs.new ('BoolUpdateParentNode', "Use Min Y")
        self.inputs.new ('FloatSocket', "Min Y")
        self.inputs.new ('BoolUpdateParentNode', "Use Max Z")
        self.inputs.new ('FloatSocket', "Max Z")
        self.inputs.new ('BoolUpdateParentNode', "Use Min Z")
        self.inputs.new ('FloatSocket', "Min Z")
        self.inputs.new ('BooleanSocket', "Affect Transform")
        self.inputs.new ('TransformSpaceSocket', "Owner Space")
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new('RelationshipSocket', "Output Relationship")
        self.initialized = True
        # color
        self.use_custom_color = True
        self.color = linkColor


            
class LinkLimitRotationNode(Node, LinkNode):
    # === Basics ===
    # Description string
    '''A node representing Limit Rotation'''
    bl_idname = 'LinkLimitRotation'
    bl_label = "Limit Rotation"
    bl_icon = 'CON_ROTLIMIT'
    
    initialized : bpy.props.BoolProperty(default = False)

    # === Optional Functions ===
    def init(self, context):
        self.inputs.new ('RelationshipSocket', "Input Relationship")
        self.inputs.new ('BoolUpdateParentNode', "Use X")
        self.inputs.new ('FloatAngleSocket', "Min X")
        self.inputs.new ('FloatAngleSocket', "Max X")
        self.inputs.new ('BoolUpdateParentNode', "Use Y")
        self.inputs.new ('FloatAngleSocket', "Min Y")
        self.inputs.new ('FloatAngleSocket', "Max Y")
        self.inputs.new ('BoolUpdateParentNode', "Use Z")
        self.inputs.new ('FloatAngleSocket', "Min Z")
        self.inputs.new ('FloatAngleSocket', "Max Z")
        self.inputs.new ('BooleanSocket', "Affect Transform")
        self.inputs.new ('TransformSpaceSocket', "Owner Space")
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new('RelationshipSocket', "Output Relationship")
        self.initialized = True
        # color
        self.use_custom_color = True
        self.color = linkColor


        
class LinkLimitDistanceNode(Node, LinkNode):
    '''A node representing Limit Distance'''
    bl_idname = 'LinkLimitDistance'
    bl_label = "Limit Distance"
    bl_icon = 'CON_DISTLIMIT'
    
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.inputs.new ('RelationshipSocket', "Input Relationship")
        self.inputs.new ('FloatFactorSocket', "Head/Tail")
        self.inputs.new ('BooleanSocket', "UseBBone")
        self.inputs.new ('FloatSocket', "Distance")
        self.inputs.new ('EnumLimitMode', "Clamp Region")
        self.inputs.new ('BooleanSocket', "Affect Transform")
        self.inputs.new ('TransformSpaceSocket', "Owner Space")
        self.inputs.new ('TransformSpaceSocket', "Target Space")
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('xFormSocket', "Target")
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new('RelationshipSocket', "Output Relationship")
        # color
        self.use_custom_color = True
        self.color = linkColor
        self.initialized = True

        
        
class LinkTransformationNode(Node, LinkNode):
    '''A node representing Transformation (Constraint)'''
    bl_idname = 'LinkTransformation'
    bl_label = "Transformation"
    bl_icon = 'CON_TRANSFORM'
    
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        hide_me = []
        self.inputs.new ('RelationshipSocket', "Input Relationship")
        self.inputs.new ('xFormSocket', "Target")
        self.inputs.new ('TransformSpaceSocket', "Owner Space")
        self.inputs.new ('TransformSpaceSocket', "Target Space")
        self.inputs.new ('BooleanSocket', "Extrapolate")
        self.inputs.new ('EnumTransformationMap', "Map From")
        hide_me.append( self.inputs.new ('EnumTransformationRotationMode', "Rotation Mode"))
        self.inputs.new ('FloatSocket', "X Min From")
        self.inputs.new ('FloatSocket', "X Max From")
        self.inputs.new ('FloatSocket', "Y Min From")
        self.inputs.new ('FloatSocket', "Y Max From")
        self.inputs.new ('FloatSocket', "Z Min From")
        self.inputs.new ('FloatSocket', "Z Max From")
        self.inputs.new ('EnumTransformationMap', "Map To")
        hide_me.append( self.inputs.new ('EnumTransformationRotationOrder', "Rotation Order"))
        self.inputs.new ('EnumTransformationAxes', "X Source Axis")
        self.inputs.new ('FloatSocket', "X Min To")
        self.inputs.new ('FloatSocket', "X Max To")
        self.inputs.new ('EnumTransformationAxes', "Y Source Axis")
        self.inputs.new ('FloatSocket', "Y Min To")
        self.inputs.new ('FloatSocket', "Y Max To")
        self.inputs.new ('EnumTransformationAxes', "Z Source Axis")
        self.inputs.new ('FloatSocket', "Z Min To")
        self.inputs.new ('FloatSocket', "Z Max To")
        self.inputs.new ('EnumTransformationTranslationMixMode', "Mix Mode (Translation)")
        hide_me.append( self.inputs.new ('EnumTransformationRotationMixMode', "Mix Mode (Rotation)"))
        hide_me.append( self.inputs.new ('EnumTransformationScaleMixMode', "Mix Mode (Scale)"))
        self.inputs.new ('FloatFactorSocket', "Influence")
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new('RelationshipSocket', "Output Relationship")
        
        for s in hide_me:
            s.hide = True
        # color
        self.use_custom_color = True
        self.color = linkColor
        self.initialized = True

    
    
    def display_update(self, parsed_tree, context):
        node_tree = context.space_data.path[0].node_tree
        nc = parsed_tree.get(get_signature_from_edited_tree(self, context))
        if nc:
            if nc.evaluate_input("Map From") == "ROTATION":
                self.inputs["Rotation Mode"].hide=False
            else:
                self.inputs["Rotation Mode"].hide=True
            if   nc.evaluate_input("Map To") == "TRANSLATION":
                    self.inputs["Rotation Order"].hide=True
                    self.inputs["Mix Mode (Translation)"].hide=False
                    self.inputs["Mix Mode (Rotation)"].hide=True
                    self.inputs["Mix Mode (Scale)"].hide=True
            elif nc.evaluate_input("Map To") == "ROTATION":
                    self.inputs["Rotation Order"].hide=False
                    self.inputs["Mix Mode (Translation)"].hide=True
                    self.inputs["Mix Mode (Rotation)"].hide=False
                    self.inputs["Mix Mode (Scale)"].hide=True
            elif nc.evaluate_input("Map To") == "SCALE":
                    self.inputs["Rotation Order"].hide=True
                    self.inputs["Mix Mode (Translation)"].hide=True
                    self.inputs["Mix Mode (Rotation)"].hide=True
                    self.inputs["Mix Mode (Scale)"].hide=False



class LinkArmatureNode(Node, LinkNode):
    """A node representing Blender's Armature Constraint"""
    bl_idname = "LinkArmature"
    bl_label = "Armature (Constraint)"
    bl_icon = "CON_ARMATURE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new ("RelationshipSocket", "Input Relationship")
        self.inputs.new("BooleanSocket", "Preserve Volume")
        self.inputs.new("BooleanSocket", "Use Envelopes")
        self.inputs.new("BooleanSocket", "Use Current Location")
        self.inputs.new("FloatFactorSocket", "Influence")
        self.inputs.new ('EnableSocket', "Enable")
        self.outputs.new("RelationshipSocket", "Output Relationship")
        # color
        self.use_custom_color = True
        self.color = inheritColor
        self.initialized = True


    def traverse(self, socket):
        return default_traverse(self,socket)
    
    def draw_buttons(self, context, layout):
        # return
        layout.operator( 'mantis.link_armature_node_add_target' )
        if (len(self.inputs) > 6):
            layout.operator( 'mantis.link_armature_node_remove_target' )
        else:
            layout.label(text="")

class LinkSplineIKNode(Node, LinkNode):
    """"A node representing Spline IK"""
    bl_idname = "LinkSplineIK"
    bl_label = "Spline IK"
    bl_icon = "CON_SPLINEIK"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new ("RelationshipSocket", "Input Relationship")
        self.inputs.new("xFormSocket", "Target")
        self.inputs.new("IntSocket", "Chain Length")
        self.inputs.new("BooleanSocket", "Even Divisions")
        self.inputs.new("BooleanSocket", "Chain Offset")
        self.inputs.new("BooleanSocket", "Use Curve Radius")
        self.inputs.new("EnumYScaleMode", "Y Scale Mode")
        self.inputs.new("EnumXZScaleMode", "XZ Scale Mode")
        self.inputs.new("BooleanSocket", "Use Original Scale")
        self.inputs.new("FloatFactorSocket", "Influence")
        self.outputs.new("RelationshipSocket", "Output Relationship")
        # color
        self.use_custom_color = True
        self.color = ikColor
        self.initialized = True

    def traverse(self, socket):
        return default_traverse(self,socket)
        
        
# DRIVERS!!

class LinkDrivenParameterNode(Node, LinkNode):
    """Represents a driven parameter in the downstream xForm node."""
    bl_idname = "LinkDrivenParameter"
    bl_label = "Driven Parameter"
    bl_icon = "CONSTRAINT_BONE"
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.inputs.new ( "RelationshipSocket", "Input Relationship" )
        self.inputs.new ( "FloatSocket", "Value" )
        self.inputs.new ( "ParameterStringSocket", "Parameter" )
        self.inputs.new ( "IntSocket", "Index" )
        self.inputs.new ('EnableSocket', "Enable")
        #
        self.outputs.new( "RelationshipSocket", "Output Relationship" )
        self.initialized = True
        
    def traverse(self, socket):
        return default_traverse(self,socket)
        # color
        self.use_custom_color = True
        self.color = driverColor


import bpy
from bpy.types import NodeTree, Node, NodeSocket
from .base_definitions import LinkNode, GraphError
from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

from .base_definitions import get_signature_from_edited_tree
from .link_socket_templates import *

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
    mantis_node_class_name="LinkInherit"
    
    def init(self, context):
        self.init_sockets(LinkInheritSockets)
        self.initialized = True
        self.use_custom_color = True
        self.color = inheritColor
    
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
                self.inputs["Inherit Rotation"].hide = True or self.inputs["Inherit Rotation"].is_connected
                self.inputs["Inherit Scale"].hide    = True or self.inputs["Inherit Scale"].is_connected
                self.inputs["Connected"].hide        = True or self.inputs["Connected"].is_connected
            # the node_groups on the way here ought to be active if there
            #  is no funny business going on.
    

# DO: make another node for ITASC IK, eh?
class LinkInverseKinematics(Node, LinkNode):
    '''A node representing inverse kinematics'''
    bl_idname = 'LinkInverseKinematics'
    bl_label = "Inverse Kinematics"
    bl_icon = 'CON_KINEMATIC'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(LinkInverseKinematicsSockets)
        self.initialized = True
        self.use_custom_color = True
        self.color = ikColor


class LinkCopyLocationNode(Node, LinkNode):
    '''A node representing Copy Location'''
    bl_idname = 'LinkCopyLocation'
    bl_label = "Copy Location"
    bl_icon = 'CON_LOCLIKE'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(LinkCopyLocationSockets)
        self.use_custom_color = True
        self.color = linkColor
        self.initialized = True

        
class LinkCopyRotationNode(Node, LinkNode):
    '''A node representing Copy Rotation'''
    bl_idname = 'LinkCopyRotation'
    bl_label = "Copy Rotation"
    bl_icon = 'CON_ROTLIKE'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(LinkCopyRotationSockets)
        self.use_custom_color = True
        self.color = linkColor
        self.initialized = True


        
class LinkCopyScaleNode(Node, LinkNode):
    '''A node representing Copy Scale'''
    bl_idname = 'LinkCopyScale'
    bl_label = "Copy Scale"
    bl_icon = 'CON_SIZELIKE'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(LinkCopyScaleSockets)
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
    mantis_node_class_name=bl_idname

    # === Optional Functions ===
    def init(self, context):
        self.init_sockets(LinkInheritConstraintSockets)
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
    mantis_node_class_name=bl_idname

    # === Optional Functions ===
    def init(self, context):
        self.init_sockets(LinkCopyTransformsSockets)
        self.use_custom_color = True
        self.color = linkColor
        self.initialized = True


        
class LinkStretchToNode(Node, LinkNode):
    '''A node representing Stretch-To'''
    bl_idname = 'LinkStretchTo'
    bl_label = "Stretch To"
    bl_icon = 'CON_STRETCHTO'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(LinkStretchToSockets)
        self.initialized = True
        self.use_custom_color = True
        self.color = trackingColor

class LinkDampedTrackNode(Node, LinkNode):
    '''A node representing Stretch-To'''
    bl_idname = 'LinkDampedTrack'
    bl_label = "Damped Track"
    bl_icon = 'CON_TRACKTO'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(LinkDampedTrackSockets)
        self.initialized = True
        self.use_custom_color = True
        self.color = trackingColor
        
class LinkLockedTrackNode(Node, LinkNode):
    '''A node representing Stretch-To'''
    bl_idname = 'LinkLockedTrack'
    bl_label = "Locked Track"
    bl_icon = 'CON_LOCKTRACK'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(LinkLockedTrackSockets)
        self.initialized = True
        self.use_custom_color = True
        self.color = trackingColor
        
class LinkTrackToNode(Node, LinkNode):
    '''A node representing Stretch-To'''
    bl_idname = 'LinkTrackTo'
    bl_label = "Track To"
    bl_icon = 'CON_TRACKTO'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(LinkTrackToSockets)
        self.initialized = True
        self.use_custom_color = True
        self.color = trackingColor

class LinkLimitLocationNode(Node, LinkNode):
    '''A node representing Limit Location'''
    bl_idname = 'LinkLimitLocation'
    bl_label = "Limit Location"
    bl_icon = 'CON_LOCLIMIT'
    mantis_node_class_name=bl_idname
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.init_sockets(LinkLimitLocationScaleSockets)
        self.initialized = True
        self.use_custom_color = True
        self.color = linkColor

class LinkLimitScaleNode(Node, LinkNode):
    '''A node representing Limit Scale'''
    bl_idname = 'LinkLimitScale'
    bl_label = "Limit Scale"
    bl_icon = 'CON_SIZELIMIT'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(LinkLimitLocationScaleSockets)
        self.initialized = True
        self.use_custom_color = True
        self.color = linkColor
 
class LinkLimitRotationNode(Node, LinkNode):
    '''A node representing Limit Rotation'''
    bl_idname = 'LinkLimitRotation'
    bl_label = "Limit Rotation"
    bl_icon = 'CON_ROTLIMIT'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(LinkLimitRotationSockets)
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
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(LinkLimitDistanceSockets)
        self.use_custom_color = True
        self.color = linkColor
        self.initialized = True


class LinkTransformationNode(Node, LinkNode):
    '''A node representing Transformation (Constraint)'''
    bl_idname = 'LinkTransformation'
    bl_label = "Transformation"
    bl_icon = 'CON_TRANSFORM'
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname

    def init(self, context):
        self.init_sockets(LinkTransformationSockets)
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
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(LinkArmatureSockets)
        self.use_custom_color = True
        self.color = inheritColor
        self.initialized = True
    
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
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(LinkSplineIKSockets)
        self.use_custom_color = True
        self.color = ikColor
        self.initialized = True
        
# DRIVERS!!

class LinkDrivenParameterNode(Node, LinkNode):
    """Represents a driven parameter in the downstream xForm node."""
    bl_idname = "LinkDrivenParameter"
    bl_label = "Driven Parameter"
    bl_icon = "CONSTRAINT_BONE"
    initialized : bpy.props.BoolProperty(default = False)
    mantis_node_class_name=bl_idname
    
    def init(self, context):
        self.init_sockets(LinkDrivenParameterSockets)
        self.use_custom_color = True
        self.color = linkColor
        self.initialized = True

# Set up the class property that ties the UI classes to the Mantis classes.
for cls in TellClasses():
    cls.set_mantis_class()

import bpy
from bpy.types import NodeTree, Node, NodeSocket
from .base_definitions import LinkNode, GraphError
from .utilities.utilities import (prRed, prGreen, prPurple, prWhite,
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
             LinkFloorNode,
             LinkShrinkWrapNode,
             LinkGeometryAttribute,
             LinkTransformationNode,
           ]

from mathutils import Color # these colors were sampled from Blender's UI
# TODO: maybe read the relevant colors from the Theme
linkTransformColor = Color((0.028034, 0.093164, 0.070379)).from_scene_linear_to_srgb()
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
    mantis_node_class_name="LinkInherit"
    socket_templates = LinkInheritSockets
    category_color=inheritColor

    def display_update(self, parsed_tree, context):
        node_tree = context.space_data.path[0].node_tree
        mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
        if mantis_node:
            bone_prev, bone_next = False, False
            if (inp := mantis_node.inputs["Parent"]).is_connected:
                if  from_node := inp.links[0].from_node:
                    if from_node.__class__.__name__ in ["xFormBone"]:
                        bone_prev=True
            bone_next=True
            try:
                xForm = mantis_node.GetxForm()
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
    mantis_node_class_name=bl_idname
    category_color=linkTransformColor
    socket_templates = LinkInverseKinematicsSockets

class LinkCopyLocationNode(Node, LinkNode):
    '''A node representing Copy Location'''
    bl_idname = 'LinkCopyLocation'
    bl_label = "Copy Location"
    bl_icon = 'CON_LOCLIKE'
    mantis_node_class_name=bl_idname
    category_color=linkTransformColor
    socket_templates = LinkCopyLocationSockets

class LinkCopyRotationNode(Node, LinkNode):
    '''A node representing Copy Rotation'''
    bl_idname = 'LinkCopyRotation'
    bl_label = "Copy Rotation"
    bl_icon = 'CON_ROTLIKE'
    mantis_node_class_name=bl_idname
    category_color=linkTransformColor
    socket_templates = LinkCopyRotationSockets

class LinkCopyScaleNode(Node, LinkNode):
    '''A node representing Copy Scale'''
    bl_idname = 'LinkCopyScale'
    bl_label = "Copy Scale"
    bl_icon = 'CON_SIZELIKE'
    mantis_node_class_name=bl_idname
    category_color=linkTransformColor
    socket_templates = LinkCopyScaleSockets

class LinkInheritConstraintNode(Node, LinkNode):
    '''A node representing a parent constraint'''
    bl_idname = 'LinkInheritConstraint'
    bl_label = "Inherit (constraint)"
    bl_icon = 'CON_CHILDOF'
    mantis_node_class_name=bl_idname
    category_color=inheritColor
    socket_templates = LinkInheritConstraintSockets

class LinkCopyTransformNode(Node, LinkNode):
    '''A node representing Copy Transform'''
    bl_idname = 'LinkCopyTransforms'
    bl_label = "Copy Transform"
    bl_icon = 'CON_TRANSLIKE'
    mantis_node_class_name=bl_idname
    category_color=linkTransformColor
    socket_templates = LinkCopyTransformsSockets

class LinkStretchToNode(Node, LinkNode):
    '''A node representing Stretch-To'''
    bl_idname = 'LinkStretchTo'
    bl_label = "Stretch To"
    bl_icon = 'CON_STRETCHTO'
    mantis_node_class_name=bl_idname
    category_color=trackingColor
    socket_templates = LinkStretchToSockets

class LinkDampedTrackNode(Node, LinkNode):
    '''A node representing Stretch-To'''
    bl_idname = 'LinkDampedTrack'
    bl_label = "Damped Track"
    bl_icon = 'CON_TRACKTO'
    mantis_node_class_name=bl_idname
    category_color=trackingColor
    socket_templates = LinkDampedTrackSockets

class LinkLockedTrackNode(Node, LinkNode):
    '''A node representing Stretch-To'''
    bl_idname = 'LinkLockedTrack'
    bl_label = "Locked Track"
    bl_icon = 'CON_LOCKTRACK'
    mantis_node_class_name=bl_idname
    category_color=trackingColor
    socket_templates = LinkLockedTrackSockets

class LinkTrackToNode(Node, LinkNode):
    '''A node representing Stretch-To'''
    bl_idname = 'LinkTrackTo'
    bl_label = "Track To"
    bl_icon = 'CON_TRACKTO'
    mantis_node_class_name=bl_idname
    category_color=trackingColor
    socket_templates = LinkTrackToSockets

class LinkLimitLocationNode(Node, LinkNode):
    '''A node representing Limit Location'''
    bl_idname = 'LinkLimitLocation'
    bl_label = "Limit Location"
    bl_icon = 'CON_LOCLIMIT'
    mantis_node_class_name=bl_idname
    category_color=linkTransformColor
    socket_templates = LinkLimitLocationSockets

class LinkLimitScaleNode(Node, LinkNode):
    '''A node representing Limit Scale'''
    bl_idname = 'LinkLimitScale'
    bl_label = "Limit Scale"
    bl_icon = 'CON_SIZELIMIT'
    mantis_node_class_name=bl_idname
    category_color=linkTransformColor
    socket_templates = LinkLimitScaleSockets

class LinkLimitRotationNode(Node, LinkNode):
    '''A node representing Limit Rotation'''
    bl_idname = 'LinkLimitRotation'
    bl_label = "Limit Rotation"
    bl_icon = 'CON_ROTLIMIT'
    mantis_node_class_name=bl_idname
    category_color=linkTransformColor
    socket_templates = LinkLimitRotationSockets

class LinkLimitDistanceNode(Node, LinkNode):
    '''A node representing Limit Distance'''
    bl_idname = 'LinkLimitDistance'
    bl_label = "Limit Distance"
    bl_icon = 'CON_DISTLIMIT'
    mantis_node_class_name=bl_idname
    category_color=linkTransformColor
    socket_templates = LinkLimitDistanceSockets

class LinkTransformationNode(Node, LinkNode):
    '''A node representing Transformation (Constraint)'''
    bl_idname = 'LinkTransformation'
    bl_label = "Transformation"
    bl_icon = 'CON_TRANSFORM'
    mantis_node_class_name=bl_idname
    category_color=linkTransformColor
    socket_templates = LinkTransformationSockets

    def display_update(self, parsed_tree, context):
        node_tree = context.space_data.path[0].node_tree
        mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
        if mantis_node:
            if mantis_node.evaluate_input("Map From") == "ROTATION":
                self.inputs["Rotation Mode"].hide=False
            else:
                self.inputs["Rotation Mode"].hide=True
            if   mantis_node.evaluate_input("Map To") == "TRANSLATION":
                    self.inputs["Rotation Order"].hide=True
                    self.inputs["Mix Mode (Translation)"].hide=False
                    self.inputs["Mix Mode (Rotation)"].hide=True
                    self.inputs["Mix Mode (Scale)"].hide=True
            elif mantis_node.evaluate_input("Map To") == "ROTATION":
                    self.inputs["Rotation Order"].hide=False
                    self.inputs["Mix Mode (Translation)"].hide=True
                    self.inputs["Mix Mode (Rotation)"].hide=False
                    self.inputs["Mix Mode (Scale)"].hide=True
            elif mantis_node.evaluate_input("Map To") == "SCALE":
                    self.inputs["Rotation Order"].hide=True
                    self.inputs["Mix Mode (Translation)"].hide=True
                    self.inputs["Mix Mode (Rotation)"].hide=True
                    self.inputs["Mix Mode (Scale)"].hide=False

class LinkArmatureNode(Node, LinkNode):
    """A node representing Blender's Armature Constraint"""
    bl_idname = "LinkArmature"
    bl_label = "Armature (Constraint)"
    bl_icon = "CON_ARMATURE"
    mantis_node_class_name=bl_idname
    category_color=inheritColor
    socket_templates = LinkArmatureSockets

class LinkSplineIKNode(Node, LinkNode):
    """"A node representing Spline IK"""
    bl_idname = "LinkSplineIK"
    bl_label = "Spline IK"
    bl_icon = "CON_SPLINEIK"
    mantis_node_class_name=bl_idname
    category_color=ikColor
    socket_templates = LinkSplineIKSockets

class LinkFloorNode(Node, LinkNode):
    """A node representing Blender's Floor Constraint"""
    bl_idname = "LinkFloor"
    bl_label = "Floor"
    bl_icon = "CON_FLOOR"
    mantis_node_class_name=bl_idname
    category_color=linkTransformColor
    socket_templates = LinkFloorSockets

class LinkShrinkWrapNode(Node, LinkNode):
    """A node representing Blender's Shrinkwrap Constraint"""
    bl_idname = "LinkShrinkWrap"
    bl_label = "Shrinkwrap"
    bl_icon = "CON_SHRINKWRAP"
    mantis_node_class_name=bl_idname
    category_color=trackingColor
    socket_templates = LinkShrinkWrapSockets

    def display_update(self, parsed_tree, context):
        # vast majority of the time user doesn't link this.
        shrink_type = self.inputs['Mode'].default_value
        if self.inputs['Mode'].is_linked:# 1% or less of cases
            node_tree = context.space_data.path[0].node_tree
            mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
            shrink_is_project = False
            if mantis_node:
                shrink_type = mantis_node.evaluate_input("Mode")
        if shrink_type != "PROJECT":
            self.inputs['Project Axis'].hide=True
            self.inputs['Space'].hide=True
            self.inputs['Project Distance'].hide=True
            self.inputs['Project Opposite'].hide=True
            self.inputs['Face Cull'].hide=True
            self.inputs['Invert Cull'].hide=True
        else:
            for inp in self.inputs:
                inp.hide=False
        if shrink_type == 'NEAREST_VERTEX':
            self.inputs['Snap Mode'].hide=True
            self.inputs['Align to Normal'].hide=True
            self.inputs['Align Normal Axis'].hide=True
        else:
            self.inputs['Snap Mode'].hide=False
            self.inputs['Align to Normal'].hide=False
            self.inputs['Align Normal Axis'].hide=False
        # TODO: this stuff should be handled by input tags
        # once I get that working.

class LinkGeometryAttribute(Node, LinkNode):
    """A node representing Blender's Geometry Attribute Constraint"""
    bl_idname = "LinkGeometryAttribute"
    bl_label = "Geometry Attribute"
    if bpy.app.version >= (5,0,0):
        bl_icon = "CON_GEOMETRYATTRIBUTE"
    else:
        bl_icon = "ERROR"
    mantis_node_class_name=bl_idname
    category_color=linkTransformColor
    socket_templates = LinkGeometryAttributeSockets
    
    def draw_label(self):
        if bpy.app.version < (5,0,0):
            return "ERROR: ONLY SUPPORTED IN Blender 5.0 OR NEWER"
        elif self.label: 
            return self.label
        return self.bl_label
    
    def update(self):
        if bpy.app.version < (5,0,0):
            self.color = Color((1.0, 0.15, 0.15,)).from_scene_linear_to_srgb()
        elif self.color != linkTransformColor:
            self.color = linkTransformColor

    def display_update(self, parsed_tree, context):
        if bpy.app.version < (5,0,0):
            return
        data_type = self.inputs['Data Type'].default_value
        if self.inputs['Data Type'].is_linked:
            node_tree = context.space_data.path[0].node_tree
            mantis_node = parsed_tree.get(get_signature_from_edited_tree(self, context))
            if mantis_node: data_type = mantis_node.evaluate_input("Data Type")
        not_matrix_mode = (data_type != 'FLOAT4X4')
        self.inputs['Enabled Location'].hide=not_matrix_mode
        self.inputs['Enabled Rotation'].hide=not_matrix_mode
        self.inputs['Enabled Scale'].hide=not_matrix_mode

# DRIVERS!!
class LinkDrivenParameterNode(Node, LinkNode):
    """Represents a driven parameter in the downstream xForm node."""
    bl_idname = "LinkDrivenParameter"
    bl_label = "Driven Parameter"
    bl_icon = "CONSTRAINT_BONE"
    mantis_node_class_name=bl_idname
    category_color=linkTransformColor
    socket_templates = LinkDrivenParameterSockets

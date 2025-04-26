from .node_container_common import *
from bpy.types import Bone, NodeTree
from .base_definitions import MantisNode, GraphError, FLOAT_EPSILON
from .link_socket_templates import *

def TellClasses():
    return [
             # special
             LinkInherit,
             # copy
             LinkCopyLocation,
             LinkCopyRotation,
             LinkCopyScale,
             LinkCopyTransforms,
             LinkTransformation,
             # limit
             LinkLimitLocation,
             LinkLimitRotation,
             LinkLimitScale,
             LinkLimitDistance,
             # tracking
             LinkStretchTo,
             LinkDampedTrack,
             LinkLockedTrack,
             LinkTrackTo,
             #misc
             LinkInheritConstraint,
             LinkArmature,
             # IK
             LinkInverseKinematics,
             LinkSplineIK,
             # Drivers
             LinkDrivenParameter,
            ]

# set the name if it is available, otherwise just use the constraint's nice name
set_constraint_name = lambda nc : nc.evaluate_input("Name") if nc.evaluate_input("Name") else nc.__class__.__name__


class MantisLinkNode(MantisNode):
    def __init__(self, signature : tuple,
                 base_tree : NodeTree,
                 socket_templates : list[SockTemplate]=[]):
        super().__init__(signature, base_tree, socket_templates)
        self.node_type = 'LINK'
        self.prepared = True
        self.bObject=[]

    def evaluate_input(self, input_name, index=0):
        # should catch 'Target', 'Pole Target' and ArmatureConstraint targets, too
        if ('Target' in input_name) and input_name not in  ["Target Space", "Use Target Z"]:
            socket = self.inputs.get(input_name)
            if socket.is_linked:
                return socket.links[0].from_node
            return None
            
        else:
            return super().evaluate_input(input_name)
    
    def gen_property_socket_map(self) -> dict:
        props_sockets = super().gen_property_socket_map()
        if (os := self.inputs.get("Owner Space")) and os.is_connected and os.links[0].from_node.node_type == 'XFORM':
            del props_sockets['owner_space']
        if ts := self.inputs.get("Target_Space") and ts.is_connected and ts.links[0].from_node.node_type == 'XFORM':
            del props_sockets['target_space']
        return props_sockets
    
    def set_custom_space(self):
        c = self.bObject
        if (os := self.inputs.get("Owner Space")) and os.is_connected and os.links[0].from_node.node_type == 'XFORM':
            c.owner_space='CUSTOM'
            xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Owner Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        if ts := self.inputs.get("Target_Space") and ts.is_connected and ts.links[0].from_node.node_type == 'XFORM':
            c.owner_space='CUSTOM'
            xf = self.inputs["Target_Space Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Target_Space Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
    
    def GetxForm(nc, output_name="Output Relationship"):
        break_condition= lambda node : node.node_type=='XFORM'
        xforms = trace_line_up_branching(nc, output_name, break_condition)
        return_me=[]
        for xf in xforms:
            if xf.node_type != 'XFORM':
                continue
            if xf in return_me:
                continue
            return_me.append(xf)
        return return_me
    
    def bFinalize(self, bContext=None):
        finish_drivers(self)

#*#-------------------------------#++#-------------------------------#*#
# L I N K   N O D E S
#*#-------------------------------#++#-------------------------------#*#


class LinkInherit(MantisLinkNode):
    '''A node representing inheritance'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkInheritSockets)
        self.init_parameters()
        self.set_traverse([('Parent', 'Inheritance')])
        self.executed = True
    
    def GetxForm(self):
        # I think this is only run in display update.
        trace = trace_single_line_up(self, "Inheritance")
        for node in trace[0]:
            if (node.node_type == 'XFORM'):
                return node
        raise GraphError("%s is not connected to a downstream xForm" % self)

class LinkCopyLocation(MantisLinkNode):
    '''A node representing Copy Location'''
    
    def __init__(self, signature : tuple,
                 base_tree : NodeTree,):
        super().__init__(signature, base_tree, LinkCopyLocationSockets)
        additional_parameters = { "Name":None }
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            c = xf.bGetObject().constraints.new('COPY_LOCATION')
            self.get_target_and_subtarget(c)
            print(wrapGreen("Creating ")+wrapWhite("Copy Location")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            self.set_custom_space()
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)
        self.executed = True
        
class LinkCopyRotation(MantisLinkNode):
    '''A node representing Copy Rotation'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkCopyRotationSockets)
        additional_parameters = { "Name":None }
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            c = xf.bGetObject().constraints.new('COPY_ROTATION')
            self.get_target_and_subtarget(c)
            print(wrapGreen("Creating ")+wrapWhite("Copy Rotation")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            
            rotation_order = self.evaluate_input("RotationOrder")
            if ((rotation_order == 'QUATERNION') or (rotation_order == 'AXIS_ANGLE')):
                c.euler_order = 'AUTO'
            else:
                try:
                    c.euler_order = rotation_order
                except TypeError: # it's a driver or incorrect
                    c.euler_order = 'AUTO'
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            self.set_custom_space()
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)
        self.executed = True
        
class LinkCopyScale(MantisLinkNode):
    '''A node representing Copy Scale'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkCopyScaleSockets)
        additional_parameters = { "Name":None }
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            c = xf.bGetObject().constraints.new('COPY_SCALE')
            self.get_target_and_subtarget(c)
            print(wrapGreen("Creating ")+wrapWhite("Copy Scale")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            if self.inputs["Owner Space"].is_connected and self.inputs["Owner Space"].links[0].from_node.node_type == 'XFORM':
                c.owner_space='CUSTOM'
                xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
                if isinstance(xf, Bone):
                    c.space_object=self.inputs["Owner Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
                else:
                    c.space_object=xf
            if self.inputs["Target Space"].is_connected and self.inputs["Target Space"].links[0].from_node.node_type == 'XFORM':
                c.target_space='CUSTOM'
                xf = self.inputs["Target Space"].links[0].from_node.bGetObject(mode="OBJECT")
                if isinstance(xf, Bone):
                    c.space_object=self.inputs["Owner Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
                else:
                    c.space_object=xf
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)   
        self.executed = True 
            

class LinkCopyTransforms(MantisLinkNode):
    '''A node representing Copy Transfoms'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkCopyTransformsSockets)
        additional_parameters = { "Name":None }
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            c = xf.bGetObject().constraints.new('COPY_TRANSFORMS')
            self.get_target_and_subtarget(c)
            print(wrapGreen("Creating ")+wrapWhite("Copy Transforms")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            self.set_custom_space()
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)  
        self.executed = True

class LinkTransformation(MantisLinkNode):
    '''A node representing Copy Transfoms'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkTransformationSockets)
        self.init_parameters(additional_parameters={"Name":None })
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            c = xf.bGetObject().constraints.new('TRANSFORM')
            self.get_target_and_subtarget(c)
            print(wrapGreen("Creating ")+wrapWhite("Transformation")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            self.set_custom_space()
            props_sockets = self.gen_property_socket_map()
            # we have to fix the blender-property for scale/rotation
            # because Blender stores these separately.
            # I do not care that this code is ugly.
            from_replace, to_replace = '', ''
            if self.evaluate_input("Map From") == 'ROTATION':
                from_replace='_rot'
            elif self.evaluate_input("Map From") == 'SCALE':
                from_replace='_scale'
            if self.evaluate_input("Map To") == 'ROTATION':
                to_replace='_rot'
            elif self.evaluate_input("Map To") == 'SCALE':
                to_replace='_scale'
            if from_replace:
                for axis in ['x', 'y', 'z']:
                    stub='from_min_'+axis
                    props_sockets[stub+from_replace]=props_sockets[stub]
                    del props_sockets[stub]
                    stub='from_max_'+axis
                    props_sockets[stub+from_replace]=props_sockets[stub]
                    del props_sockets[stub]
            if to_replace:
                for axis in ['x', 'y', 'z']:
                    stub='to_min_'+axis
                    props_sockets[stub+to_replace]=props_sockets[stub]
                    del props_sockets[stub]
                    stub='to_max_'+axis
                    props_sockets[stub+to_replace]=props_sockets[stub]
                    del props_sockets[stub]
            evaluate_sockets(self, c, props_sockets)  
        self.executed = True

class LinkLimitLocation(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkLimitLocationScaleSockets)
        self.init_parameters(additional_parameters={ "Name":None })
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            c = xf.bGetObject().constraints.new('LIMIT_LOCATION')
            print(wrapGreen("Creating ")+wrapWhite("Limit Location")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            self.set_custom_space()
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)
        self.executed = True
        
class LinkLimitRotation(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkLimitRotationSockets)
        self.init_parameters(additional_parameters={ "Name":None })
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            c = xf.bGetObject().constraints.new('LIMIT_ROTATION')
            print(wrapGreen("Creating ")+wrapWhite("Limit Rotation")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            self.set_custom_space()
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)
        self.executed = True

class LinkLimitScale(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkLimitLocationScaleSockets)
        self.init_parameters(additional_parameters={ "Name":None })
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            c = xf.bGetObject().constraints.new('LIMIT_SCALE')
            print(wrapGreen("Creating ")+wrapWhite("Limit Scale")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            self.set_custom_space()
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)
        self.executed = True
 
class LinkLimitDistance(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkLimitDistanceSockets)
        self.init_parameters(additional_parameters={ "Name":None })
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            print(wrapGreen("Creating ")+wrapWhite("Limit Distance")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            c = xf.bGetObject().constraints.new('LIMIT_DISTANCE')
            self.get_target_and_subtarget(c)
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            self.set_custom_space()
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)
        self.executed = True

# Tracking

class LinkStretchTo(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkStretchToSockets)
        self.init_parameters(additional_parameters={ "Name":None })
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            print(wrapGreen("Creating ")+wrapWhite("Stretch-To")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            c = xf.bGetObject().constraints.new('STRETCH_TO')
            self.get_target_and_subtarget(c)
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)
            
            if (self.evaluate_input("Original Length") == 0):
                # this is meant to be set automatically.
                c.rest_length = xf.bGetObject().bone.length
        self.executed = True

class LinkDampedTrack(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkDampedTrackSockets)
        self.init_parameters(additional_parameters={ "Name":None })
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            print(wrapGreen("Creating ")+wrapWhite("Damped Track")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            c = xf.bGetObject().constraints.new('DAMPED_TRACK')
            self.get_target_and_subtarget(c)
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)
        self.executed = True

class LinkLockedTrack(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree,LinkLockedTrackSockets)
        self.init_parameters(additional_parameters={"Name":None })
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            print(wrapGreen("Creating ")+wrapWhite("Locked Track")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            c = xf.bGetObject().constraints.new('LOCKED_TRACK')
            self.get_target_and_subtarget(c)
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)
        self.executed = True

class LinkTrackTo(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkTrackToSockets)
        self.init_parameters(additional_parameters={"Name":None })
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            print(wrapGreen("Creating ")+wrapWhite("Track-To")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            c = xf.bGetObject().constraints.new('TRACK_TO')
            self.get_target_and_subtarget(c)
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)
        self.executed = True


class LinkInheritConstraint(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkInheritConstraintSockets)
        self.init_parameters(additional_parameters={"Name":None })
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            print(wrapGreen("Creating ")+wrapWhite("Child-Of")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            c = xf.bGetObject().constraints.new('CHILD_OF')
            self.get_target_and_subtarget(c)
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)
            c.set_inverse_pending
            self.executed = True

class LinkInverseKinematics(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkInverseKinematicsSockets)
        self.init_parameters(additional_parameters={"Name":None })
        self.set_traverse([("Input Relationship", "Output Relationship")])
    
    def get_base_ik_bone(self, ik_bone):
        chain_length : int = (self.evaluate_input("Chain Length"))
        if not isinstance(chain_length, (int, float)):
            raise GraphError(f"Chain Length must be an integer number in {self}::Chain Length")
        if chain_length == 0:
            chain_length = int("inf")
        
        base_ik_bone = ik_bone; i=1
        while (i<chain_length) and (base_ik_bone.parent):
            base_ik_bone=base_ik_bone.parent; i+=1
        return base_ik_bone
    
    # We need to do the calculation in a "full circle", meaning the pole_angle
    # can go over pi or less than -pi - but the actuall constraint value must
    # be clamped in that range.
    # so we simply wrap the value.
    # not very efficient but it's OK
    def set_pole_angle(self, constraint, angle: float) -> None:
        from math import pi
        from .utilities import wrap
        constraint.pole_angle = wrap(-pi, pi, angle)
    
    def calc_pole_angle_pre(self, c, ik_bone):
        """
            This function gets us most of the way to a correct IK pole angle. Unfortunately,
            due to the unpredictable nature of the iterative IK calculation, I can't figure
            out an exact solution. So we do a bisect search in calc_pole_angle_post().
        """
        # TODO: instead of these checks, convert all to armature local space. But this is tedious.
        if not c.target:
            raise GraphError(f"IK Constraint {self} must have target.")
        elif c.target.type != "ARMATURE":
            raise NotImplementedError(f"Currently, IK Constraint Target for {self} must be a bone within the same armature.")
        if c.pole_target.type != "ARMATURE":
            raise NotImplementedError(f"Currently, IK Constraint Pole Target for {self} must be a bone within the same armature.")

        ik_handle = c.target.pose.bones[c.subtarget]
        if ik_handle.id_data != ik_bone.id_data:
            raise NotImplementedError(f"Currently, IK Constraint Target for {self} must be a bone within the same armature.")
        ik_pole = c.pole_target.pose.bones[c.pole_subtarget]
        if ik_pole.id_data != ik_bone.id_data:
            raise NotImplementedError(f"Currently,IK Constraint Pole Target for {self} must be a bone within the same armature.")
        
        base_ik_bone = self.get_base_ik_bone(ik_bone)
        
        start_effector = base_ik_bone.bone.head_local
        end_effector = ik_handle.bone.head_local
        pole_location = ik_pole.bone.head_local

        # this is the X-Axis of the bone's rest-pose, added to its bone
        knee_location = base_ik_bone.bone.matrix_local.col[0].xyz+start_effector
        ik_axis = (end_effector-start_effector).normalized()
        from .utilities import project_point_to_plane
        pole_planar_projection = project_point_to_plane(pole_location, start_effector, ik_axis)
        # this planar projection is necessary because the IK axis is different than the base_bone's y axis
        planar_projection = project_point_to_plane(knee_location, start_effector, ik_axis)

        knee_direction =(planar_projection       -  start_effector).normalized()
        pole_direction =(pole_planar_projection  -  start_effector).normalized()

        return knee_direction.angle(pole_direction)

    def calc_pole_angle_post(self, c, ik_bone, context):
        """
            This function should give us a completely accurate result for IK.
        """
        from time import time
        start_time=time()
        def signed_angle(vector_u, vector_v, normal):
            # it seems that this fails if the vectors are exactly aligned under certain circumstances.
            angle = vector_u.angle(vector_v, 0.0) # So we use a fallback of 0
            # Normal specifies orientation
            if angle != 0 and vector_u.cross(vector_v).angle(normal) < 1:
                angle = -angle
            return angle
        
        # we have already checked for valid data.
        ik_handle = c.target.pose.bones[c.subtarget]
        base_ik_bone = self.get_base_ik_bone(ik_bone)
        start_effector = base_ik_bone.bone.head_local
        angle = c.pole_angle

        dg = context.view_layer.depsgraph
        dg.update()

        ik_axis = (ik_handle.bone.head_local-start_effector).normalized()
        center_point = start_effector +(ik_axis*base_ik_bone.bone.length)
        knee_direction = base_ik_bone.bone.tail_local - center_point
        current_knee_direction = base_ik_bone.tail-center_point

        error=signed_angle(current_knee_direction, knee_direction, ik_axis)
        if error == 0:
            prGreen("No Fine-tuning needed."); return
        
        # Flip it if needed
        dot_before=current_knee_direction.dot(knee_direction)
        if dot_before < 0 and angle!=0: # then it is not aligned and we should check the inverse
            angle = -angle; c.pole_angle=angle
            dg.update()
            current_knee_direction = base_ik_bone.tail-center_point
            dot_after=current_knee_direction.dot(knee_direction)
            if dot_after < dot_before: # they are somehow less aligned
                prPurple("Mantis has gone down an unexpected code path. Please report this as a bug.")
                angle = -angle; self.set_pole_angle(c, angle)
                dg.update()

        # now we can do a bisect search to find the best value.
        error_threshhold = FLOAT_EPSILON
        max_iterations=600
        error=signed_angle(current_knee_direction, knee_direction, ik_axis)
        if error == 0:
            prGreen("No Fine-tuning needed."); return
        angle+=error
        alt_angle = angle+(error*-2) # should be very near the center when flipped here
        # we still need to bisect search because the relationship of pole_angle <==> error is somewhat unpredictable
        upper_bounds = alt_angle if alt_angle > angle else angle
        lower_bounds = alt_angle if alt_angle < angle else angle
        i, error_identical = 0, 0

        while ( True ):
            if (i>=max_iterations):
                prOrange(f"IK Pole Angle Set reached max iterations of {i-error_identical} in {time()-start_time} seconds")
                break
            if (abs(error)<error_threshhold) or (upper_bounds<=lower_bounds) or (error_identical > 3):
                prPurple(f"IK Pole Angle Set converged after {i-error_identical} iterations with error={error} in {time()-start_time} seconds")
                break
            # get the center-point betweeen the bounds
            try_angle = lower_bounds + (upper_bounds-lower_bounds)/2
            self.set_pole_angle(c, try_angle); dg.update()
            prev_error = error
            error = signed_angle((base_ik_bone.tail-center_point), knee_direction, ik_axis)
            error_identical+= int(error == prev_error)
            if error>0: upper_bounds=try_angle
            if error<0: lower_bounds=try_angle
            i+=1

    def bExecute(self, context):
        prepare_parameters(self)
        for xf in self.GetxForm():
            print(wrapGreen("Creating ")+wrapOrange("Inverse Kinematics")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            ik_bone = xf.bGetObject()
            c = xf.bGetObject().constraints.new('IK')
            self.get_target_and_subtarget(c)
            self.get_target_and_subtarget(c, input_name = 'Pole Target')
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            
            self.bObject.append(c)
            c.chain_count = 1 # so that, if there are errors, this doesn't print
            #  a whole bunch of circular dependency crap from having infinite chain length
            if (c.pole_target):
                self.set_pole_angle(c, self.calc_pole_angle_pre(c, ik_bone))

            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)
            c.use_location   = self.evaluate_input("Position") > 0
            c.use_rotation   = self.evaluate_input("Rotation") > 0
        self.executed = True

    def bFinalize(self, bContext = None):
        # adding a test here
        if bContext:
            for i, constraint in enumerate(self.bObject):
                ik_bone = self.GetxForm()[i].bGetObject(mode='POSE')
                if constraint.pole_target:
                    prWhite(f"Fine-tuning IK Pole Angle for {self}")
                    # make sure to enable it first
                    enabled_before = constraint.mute
                    constraint.mute = False
                    self.calc_pole_angle_post(constraint, ik_bone, bContext)
                    constraint.mute = enabled_before
        super().bFinalize(bContext)
        

def ik_report_error(pb, context, do_print=False):
    dg = context.view_layer.depsgraph
    dg.update()
    loc1, rot_quaternion1, scl1 = pb.matrix.decompose()
    loc2, rot_quaternion2, scl2 = pb.bone.matrix_local.decompose()
    location_error=(loc1-loc2).length
    rotation_error = rot_quaternion1.rotation_difference(rot_quaternion2).angle
    scale_error = (scl1-scl2).length
    if location_error < FLOAT_EPSILON: location_error = 0
    if abs(rotation_error) < FLOAT_EPSILON: rotation_error = 0
    if scale_error < FLOAT_EPSILON: scale_error = 0
    if do_print:
        print (f"IK Location Error: {location_error}")
        print (f"IK Rotation Error: {rotation_error}")
        print (f"IK Scale Error   : {scale_error}")
    return (location_error, rotation_error, scale_error) 

# This is kinda a weird design decision?
class LinkDrivenParameter(MantisLinkNode):
    '''A node representing an armature object'''
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkDrivenParameterSockets)
        self.init_parameters(additional_parameters={ "Name":None })
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, bContext = None,):
        prepare_parameters(self)
        prGreen("Executing Driven Parameter node")
        prop = self.evaluate_input("Parameter")
        index = self.evaluate_input("Index")
        value = self.evaluate_input("Value")
        for xf in self.GetxForm():
            ob = xf.bGetObject(mode="POSE")
            # IMPORTANT: this node only works on pose bone attributes.
            self.bObject.append(ob)
            length=1
            if hasattr(ob, prop):
                try:
                    length = len(getattr(ob, prop))
                except TypeError:
                    pass
                except AttributeError:
                    pass
            else:
                raise AttributeError(f"Cannot Set value {prop} on object because it does not exist.")
            def_value = 0.0
            if length>1:
                def_value=[0.0]*length
                self.parameters["Value"] = tuple( 0.0 if i != index else value for i in range(length))

            props_sockets = {
                prop: ("Value", def_value)
            }
            evaluate_sockets(self, ob, props_sockets)

        self.executed = True

    def bFinalize(self, bContext = None):
        driver = self.evaluate_input("Value")
        try:
            for i, val in enumerate(self.parameters["Value"]):
                from .drivers import MantisDriver
                if isinstance(val, MantisDriver):
                    driver["ind"] = i
                    val = driver
        except AttributeError:
            self.parameters["Value"] = driver
        except TypeError:
            self.parameters["Value"] = driver
        super().bFinalize(bContext)
    
class LinkArmature(MantisLinkNode):
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree,):
        super().__init__(signature, base_tree, LinkArmatureSockets)
        self.init_parameters(additional_parameters={"Name":None })
        self.set_traverse([("Input Relationship", "Output Relationship")])
        setup_custom_props(self) # <-- this takes care of the runtime-added sockets

    def bExecute(self, bContext = None,):
        prepare_parameters(self)
        for xf in self.GetxForm():
            print(wrapGreen("Creating ")+wrapOrange("Armature")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            c = xf.bGetObject().constraints.new('ARMATURE')
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            # get number of targets
            num_targets = len( list(self.inputs.values())[6:] )//2
            
            props_sockets = self.gen_property_socket_map()
            targets_weights = {}
            for i in range(num_targets):
                target = c.targets.new()
                target_input_name = list(self.inputs.keys())[i*2+6  ]
                weight_input_name = list(self.inputs.keys())[i*2+6+1]
                self.get_target_and_subtarget(target, target_input_name)
                weight_value=self.evaluate_input(weight_input_name)
                if not isinstance(weight_value, float):
                    weight_value=0
                targets_weights[i]=weight_value
                props_sockets["targets[%d].weight" % i] = (weight_input_name, 0)
                # targets_weights.append({"weight":(weight_input_name, 0)})
            evaluate_sockets(self, c, props_sockets)
            for target, value in targets_weights.items():
                c.targets[target].weight=value
        self.executed = True

class LinkSplineIK(MantisLinkNode):
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkSplineIKSockets)
        self.init_parameters(additional_parameters={"Name":None })
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def bExecute(self, bContext = None,):
        prepare_parameters(self)
        if not self.inputs['Target'].is_linked:
            raise GraphError(f"ERROR: {self} is not connected to a target curve.")
        for xf in self.GetxForm():
            print(wrapGreen("Creating ")+wrapOrange("Spline-IK")+
                wrapGreen(" Constraint for bone: ") +
                wrapOrange(xf.bGetObject().name))
            c = xf.bGetObject().constraints.new('SPLINE_IK')
            # set the spline - we need to get the right one 
            spline_index = self.evaluate_input("Spline Index")
            from .utilities import get_extracted_spline_object
            proto_curve = self.inputs['Target'].links[0].from_node.bGetObject()
            curve = get_extracted_spline_object(proto_curve, spline_index, self.mContext)
            # link it to the view layer
            if (curve.name not in bContext.view_layer.active_layer_collection.collection.objects):
                bContext.view_layer.active_layer_collection.collection.objects.link(curve)
            c.target=curve
            if constraint_name := self.evaluate_input("Name"):
                c.name = constraint_name
            self.bObject.append(c)
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, c, props_sockets)
        self.executed = True
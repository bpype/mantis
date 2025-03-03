from .node_container_common import *
from bpy.types import Bone
from .base_definitions import MantisNode, NodeSocket, GraphError

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

class MantisLinkNode(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        self.node_type = 'LINK'
        self.prepared = True

    def evaluate_input(self, input_name, index=0):
        # should catch 'Target', 'Pole Target' and ArmatureConstraint targets, too
        if ('Target' in input_name) and input_name not in  ["Target Space", "Use Target Z"]:
            socket = self.inputs.get(input_name)
            if socket.is_linked:
                return socket.links[0].from_node
            return None
            
        else:
            return super().evaluate_input(input_name)

# set the name if it is available, otherwise just use the constraint's nice name
set_constraint_name = lambda nc : nc.evaluate_input("Name") if nc.evaluate_input("Name") else nc.__class__.__name__


#*#-------------------------------#++#-------------------------------#*#
# L I N K   N O D E S
#*#-------------------------------#++#-------------------------------#*#

def GetxForm(nc):
    trace = trace_single_line_up(nc, "Output Relationship")
    for node in trace[0]:
        if (node.node_type == 'XFORM'):
            return node
    raise GraphError("%s is not connected to a downstream xForm" % nc)

class LinkInherit(MantisLinkNode):
    '''A node representing inheritance'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = ["Parent", "Inherit Rotation", "Inherit Scale", "Connected"]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Inheritance"])
        self.init_parameters()
        self.set_traverse([('Parent', 'Inheritance')])
        self.executed = True
    
    def GetxForm(self): # DUPLICATED, TODO fix this
        # I think this is only run in display update.
        trace = trace_single_line_up(self, "Inheritance")
        for node in trace[0]:
            if (node.node_type == 'XFORM'):
                return node
        raise GraphError("%s is not connected to a downstream xForm" % self)
    
    
        


class LinkCopyLocation(MantisLinkNode):
    '''A node representing Copy Location'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship",
            "Head/Tail",
            "UseBBone",
            "Axes",
            "Invert",
            "Target Space",
            "Owner Space",
            "Offset",
            "Influence",
            "Target",
            "Enable",
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
    
    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        c = self.GetxForm().bGetObject().constraints.new('COPY_LOCATION')
        get_target_and_subtarget(self, c)
        print(wrapGreen("Creating ")+wrapWhite("Copy Location")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        custom_space_owner, custom_space_target = False, False
        if self.inputs["Owner Space"].is_connected and self.inputs["Owner Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_owner=True
            c.owner_space='CUSTOM'
            xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Owner Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        if self.inputs["Target Space"].is_connected and self.inputs["Target Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_target=True
            c.target_space='CUSTOM'
            xf = self.inputs["Target Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Target Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        props_sockets = {
        'use_offset'       : ("Offset", False),
        'head_tail'       : ("Head/Tail", 0),
        'use_bbone_shape' : ("UseBBone", False),
        'invert_x'        : ( ("Invert", 0), False),
        'invert_y'        : ( ("Invert", 1), False),
        'invert_z'        : ( ("Invert", 2), False),
        'use_x'           : ( ("Axes", 0), False),
        'use_y'           : ( ("Axes", 1), False),
        'use_z'           : ( ("Axes", 2), False),
        'owner_space'     : ("Owner Space",  'WORLD'),
        'target_space'    : ("Target Space", 'WORLD'),
        'influence'       : ("Influence", 1),
        'mute'            : ("Enable", True),
        }
        if custom_space_owner: del props_sockets['owner_space']
        if custom_space_target: del props_sockets['target_space']
        #
        evaluate_sockets(self, c, props_sockets)
        self.executed = True
        
    def bFinalize(self, bContext = None):
        finish_drivers(self)
    
        
        

class LinkCopyRotation(MantisLinkNode):
    '''A node representing Copy Rotation'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship",
            "RotationOrder",
            "Rotation Mix",
            "Axes",
            "Invert",
            "Target Space",
            "Owner Space",
            "Influence",
            "Target",
            "Enable",
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
        

    
    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        c = self.GetxForm().bGetObject().constraints.new('COPY_ROTATION')
        get_target_and_subtarget(self, c)
        print(wrapGreen("Creating ")+wrapWhite("Copy Rotation")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        
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
        self.bObject = c
        custom_space_owner, custom_space_target = False, False
        if self.inputs["Owner Space"].is_connected and self.inputs["Owner Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_owner=True
            c.owner_space='CUSTOM'
            xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Owner Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        if self.inputs["Target Space"].is_connected and self.inputs["Target Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_target=True
            c.target_space='CUSTOM'
            xf = self.inputs["Target Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Target Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        props_sockets = {
        'euler_order' : ("RotationOrder", 'AUTO'),
        'mix_mode'       : ("Rotation Mix", 'REPLACE'),
        'invert_x'       : ( ("Invert", 0), False),
        'invert_y'       : ( ("Invert", 1), False),
        'invert_z'       : ( ("Invert", 2), False),
        'use_x'          : ( ("Axes", 0), False),
        'use_y'          : ( ("Axes", 1), False),
        'use_z'          : ( ("Axes", 2), False),
        'owner_space'    : ("Owner Space",  'WORLD'),
        'target_space'   : ("Target Space", 'WORLD'),
        'influence'      : ("Influence", 1),
        'mute'            : ("Enable", True),
        }
        if custom_space_owner: del props_sockets['owner_space']
        if custom_space_target: del props_sockets['target_space']
        #
        evaluate_sockets(self, c, props_sockets)
        self.executed = True
            
    def bFinalize(self, bContext = None):
        finish_drivers(self)
    
        
        
class LinkCopyScale(MantisLinkNode):
    '''A node representing Copy Scale'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship",
            "Offset",
            "Average",
            "Additive",
            "Axes",
            "Target Space",
            "Owner Space",
            "Influence",
            "Target",
            "Enable",
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
    
    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        c = self.GetxForm().bGetObject().constraints.new('COPY_SCALE')
        get_target_and_subtarget(self, c)
        print(wrapGreen("Creating ")+wrapWhite("Copy Scale")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        custom_space_owner, custom_space_target = False, False
        if self.inputs["Owner Space"].is_connected and self.inputs["Owner Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_owner=True
            c.owner_space='CUSTOM'
            xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Owner Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        if self.inputs["Target Space"].is_connected and self.inputs["Target Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_target=True
            c.target_space='CUSTOM'
            xf = self.inputs["Target Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Owner Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        props_sockets = {
        'use_offset'       : ("Offset", False),
        'use_make_uniform' : ("Average", False),
        'owner_space'      : ("Owner Space",  'WORLD'),
        'target_space'     : ("Target Space", 'WORLD'),
        'use_x'            : ( ("Axes", 0), False),
        'use_y'            : ( ("Axes", 1), False),
        'use_z'            : ( ("Axes", 2), False),
        'influence'        : ("Influence", 1),
        'mute'             : ("Enable", True),
        }
        if custom_space_owner: del props_sockets['owner_space']
        if custom_space_target: del props_sockets['target_space']
        #
        evaluate_sockets(self, c, props_sockets)   
        self.executed = True 
            
    def bFinalize(self, bContext = None):
        finish_drivers(self)
    
        

class LinkCopyTransforms(MantisLinkNode):
    '''A node representing Copy Transfoms'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship",
            "Head/Tail",
            "UseBBone",
            "Additive",
            "Mix",
            "Target Space",
            "Owner Space",
            "Influence",
            "Target",
            "Enable",
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        c = self.GetxForm().bGetObject().constraints.new('COPY_TRANSFORMS')
        get_target_and_subtarget(self, c)
        print(wrapGreen("Creating ")+wrapWhite("Copy Transforms")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        custom_space_owner, custom_space_target = False, False
        if self.inputs["Owner Space"].is_connected and self.inputs["Owner Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_owner=True
            c.owner_space='CUSTOM'
            xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Owner Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        if self.inputs["Target Space"].is_connected and self.inputs["Target Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_target=True
            c.target_space='CUSTOM'
            xf = self.inputs["Target Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Target Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        props_sockets = {
        'head_tail'       : ("Head/Tail", 0),
        'use_bbone_shape' : ("UseBBone", False),
        'mix_mode'        : ("Mix", 'REPLACE'),
        'owner_space'     : ("Owner Space",  'WORLD'),
        'target_space'    : ("Target Space", 'WORLD'),
        'influence'       : ("Influence", 1),
        'mute'            :  ("Enable", False)
        }
        if custom_space_owner: del props_sockets['owner_space']
        if custom_space_target: del props_sockets['target_space']
        #
        evaluate_sockets(self, c, props_sockets)  
        self.executed = True

    def bFinalize(self, bContext = None):
        finish_drivers(self)
    
        


transformation_props_sockets = {
            'use_motion_extrapolate' : ("Extrapolate", False),
            'map_from'               : ("Map From", 'LOCATION'),
            'from_rotation_mode'     : ("Rotation Mode", 'AUTO'),
            'from_min_x'             : ("X Min From", 0.0),
            'from_max_x'             : ("X Max From", 0.0),
            'from_min_y'             : ("Y Min From", 0.0),
            'from_max_y'             : ("Y Max From", 0.0),
            'from_min_z'             : ("Z Min From", 0.0),
            'from_max_z'             : ("Z Max From", 0.0),
            'from_min_x_rot'         : ("X Min From", 0.0),
            'from_max_x_rot'         : ("X Max From", 0.0),
            'from_min_y_rot'         : ("Y Min From", 0.0),
            'from_max_y_rot'         : ("Y Max From", 0.0),
            'from_min_z_rot'         : ("Z Min From", 0.0),
            'from_max_z_rot'         : ("Z Max From", 0.0),
            'from_min_x_scale'       : ("X Min From", 0.0),
            'from_max_x_scale'       : ("X Max From", 0.0),
            'from_min_y_scale'       : ("Y Min From", 0.0),
            'from_max_y_scale'       : ("Y Max From", 0.0),
            'from_min_z_scale'       : ("Z Min From", 0.0),
            'from_max_z_scale'       : ("Z Max From", 0.0),
            'map_to'                 : ("Map To", "LOCATION"),
            'map_to_x_from'          : ("X Source Axis", "X"),
            'map_to_y_from'          : ("Y Source Axis", "Y"),
            'map_to_z_from'          : ("Z Source Axis", "Z"),
            'to_min_x'               : ("X Min To", 0.0),
            'to_max_x'               : ("X Max To", 0.0),
            'to_min_y'               : ("Y Min To", 0.0),
            'to_max_y'               : ("Y Max To", 0.0),
            'to_min_z'               : ("Z Min To", 0.0),
            'to_max_z'               : ("Z Max To", 0.0),
            'to_min_x_rot'           : ("X Min To", 0.0),
            'to_max_x_rot'           : ("X Max To", 0.0),
            'to_min_y_rot'           : ("Y Min To", 0.0),
            'to_max_y_rot'           : ("Y Max To", 0.0),
            'to_min_z_rot'           : ("Z Min To", 0.0),
            'to_max_z_rot'           : ("Z Max To", 0.0),
            'to_min_x_scale'         : ("X Min To", 0.0),
            'to_max_x_scale'         : ("X Max To", 0.0),
            'to_min_y_scale'         : ("Y Min To", 0.0),
            'to_max_y_scale'         : ("Y Max To", 0.0),
            'to_min_z_scale'         : ("Z Min To", 0.0),
            'to_max_z_scale'         : ("Z Max To", 0.0),
            'to_euler_order'         : ("Rotation Mode", "AUTO"),
            'mix_mode'               : ("Mix Mode (Translation)", "ADD"),
            'mix_mode_rot'           : ("Mix Mode (Rotation)", "ADD"),
            'mix_mode_scale'         : ("Mix Mode (Scale)", "MULTIPLY"),
            'owner_space'            : ("Owner Space",  'WORLD'),
            'target_space'           : ("Target Space", 'WORLD'),
            'influence'              : ("Influence", 1),
            'mute'                   : ("Enable", False),
        }

class LinkTransformation(MantisLinkNode):
    '''A node representing Copy Transfoms'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship" ,
            "Target Space" ,
            "Owner Space" ,
            "Influence" ,
            "Target" ,
            "Enable" ,
            "Extrapolate" ,
            "Map From" ,
            "Rotation Mode" ,
            "X Min From" ,
            "X Max From" ,
            "Y Min From" ,
            "Y Max From" ,
            "Z Min From" ,
            "Z Max From" ,
            "Map To" ,
            "X Source Axis" ,
            "X Min To" ,
            "X Max To" ,
            "Y Source Axis" ,
            "Y Min To" ,
            "Y Max To" ,
            "Z Source Axis" ,
            "Z Min To" ,
            "Z Max To" ,
            "Mix Mode (Translation)" ,
            "Mix Mode (Rotation)" ,
            "Mix Mode (Scale)" ,
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
        

    
    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        c = self.GetxForm().bGetObject().constraints.new('TRANSFORM')
        get_target_and_subtarget(self, c)
        print(wrapGreen("Creating ")+wrapWhite("Transformation")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        custom_space_owner, custom_space_target = False, False
        if self.inputs["Owner Space"].is_connected and self.inputs["Owner Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_owner=True
            c.owner_space='CUSTOM'
            xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Owner Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        if self.inputs["Target Space"].is_connected and self.inputs["Target Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_target=True
            c.target_space='CUSTOM'
            xf = self.inputs["Target Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Target Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        props_sockets = transformation_props_sockets.copy()
        if custom_space_owner: del props_sockets['owner_space']
        if custom_space_target: del props_sockets['target_space']
        #
        evaluate_sockets(self, c, props_sockets)     
        self.executed = True

    def bFinalize(self, bContext = None):
        finish_drivers(self)
    
        

class LinkLimitLocation(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship" ,
            "Use Max X"          ,
            "Max X"              ,
            "Use Max Y"          ,
            "Max Y"              ,
            "Use Max Z"          ,
            "Max Z"              ,
            "Use Min X"          ,
            "Min X"              ,
            "Use Min Y"          ,
            "Min Y"              ,
            "Use Min Z"          ,
            "Min Z"              ,
            "Affect Transform"   ,
            "Owner Space"        ,
            "Influence"          ,
            "Enable"             ,
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        c = self.GetxForm().bGetObject().constraints.new('LIMIT_LOCATION')
        #
        print(wrapGreen("Creating ")+wrapWhite("Limit Location")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        custom_space_owner = False
        if self.inputs["Owner Space"].is_connected and self.inputs["Owner Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_owner=True
            c.owner_space='CUSTOM'
            xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Owner Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        props_sockets = {
        'use_transform_limit' : ("Affect Transform", False),
        'use_max_x'           : ("Use Max X", False),
        'use_max_y'           : ("Use Max Y", False),
        'use_max_z'           : ("Use Max Z", False),
        'use_min_x'           : ("Use Min X", False),
        'use_min_y'           : ("Use Min Y", False),
        'use_min_z'           : ("Use Min Z", False),
        'max_x'               : ("Max X", 0),
        'max_y'               : ("Max Y", 0),
        'max_z'               : ("Max Z", 0),
        'min_x'               : ("Min X", 0),
        'min_y'               : ("Min Y", 0),
        'min_z'               : ("Min Z", 0),
        'owner_space'         : ("Owner Space", 'WORLD'),
        'influence'           : ("Influence", 1),
        'mute'               : ("Enable", True),
        }
        if custom_space_owner: del props_sockets['owner_space']
        #
        evaluate_sockets(self, c, props_sockets)
        self.executed = True

    def bFinalize(self, bContext = None):
        finish_drivers(self)
    
        
        
class LinkLimitRotation(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship" ,
            "Use X"              ,
            "Use Y"              ,
            "Use Z"              ,
            "Max X"              ,
            "Max Y"              ,
            "Max Z"              ,
            "Min X"              ,
            "Min Y"              ,
            "Min Z"              ,
            "Affect Transform"   ,
            "Owner Space"        ,
            "Influence"          ,
            "Enable"             ,
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
        

    
    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        c = self.GetxForm().bGetObject().constraints.new('LIMIT_ROTATION')
        print(wrapGreen("Creating ")+wrapWhite("Limit Rotation")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        custom_space_owner = False
        if self.inputs["Owner Space"].is_connected and self.inputs["Owner Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_owner=True
            c.owner_space='CUSTOM'
            xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Owner Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        props_sockets = {
        'use_transform_limit' : ("Affect Transform", False),
        'use_limit_x'         : ("Use X", False),
        'use_limit_y'         : ("Use Y", False),
        'use_limit_z'         : ("Use Z", False),
        'max_x'               : ("Max X", 0),
        'max_y'               : ("Max Y", 0),
        'max_z'               : ("Max Z", 0),
        'min_x'               : ("Min X", 0),
        'min_y'               : ("Min Y", 0),
        'min_z'               : ("Min Z", 0),
        'owner_space'         : ("Owner Space", 'WORLD'),
        'influence'           : ("Influence", 1),
        'mute'               : ("Enable", True),
        }
        if custom_space_owner: del props_sockets['owner_space']
        #
        evaluate_sockets(self, c, props_sockets)
        self.executed = True

    def bFinalize(self, bContext = None):
        finish_drivers(self)
    
        
        
class LinkLimitScale(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship" ,
            "Use Max X"          ,
            "Max X"              ,
            "Use Max Y"          ,
            "Max Y"              ,
            "Use Max Z"          ,
            "Max Z"              ,
            "Use Min X"          ,
            "Min X"              ,
            "Use Min Y"          ,
            "Min Y"              ,
            "Use Min Z"          ,
            "Min Z"              ,
            "Affect Transform"   ,
            "Owner Space"        ,
            "Influence"          ,
            "Enable"             ,
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
        

    
    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        c = self.GetxForm().bGetObject().constraints.new('LIMIT_SCALE')
        print(wrapGreen("Creating ")+wrapWhite("Limit Scale")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        custom_space_owner = False
        if self.inputs["Owner Space"].is_connected and self.inputs["Owner Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_owner=True
            c.owner_space='CUSTOM'
            xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Owner Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        props_sockets = {
        'use_transform_limit' : ("Affect Transform", False),
        'use_max_x'           : ("Use Max X", False),
        'use_max_y'           : ("Use Max Y", False),
        'use_max_z'           : ("Use Max Z", False),
        'use_min_x'           : ("Use Min X", False),
        'use_min_y'           : ("Use Min Y", False),
        'use_min_z'           : ("Use Min Z", False),
        'max_x'               : ("Max X", 0),
        'max_y'               : ("Max Y", 0),
        'max_z'               : ("Max Z", 0),
        'min_x'               : ("Min X", 0),
        'min_y'               : ("Min Y", 0),
        'min_z'               : ("Min Z", 0),
        'owner_space'         : ("Owner Space", 'WORLD'),
        'influence'           : ("Influence", 1),
        'mute'               :  ("Enable", True),
        }
        if custom_space_owner: del props_sockets['owner_space']
        #
        evaluate_sockets(self, c, props_sockets)
        self.executed = True

    def bFinalize(self, bContext = None):
        finish_drivers(self)
    
        
        
class LinkLimitDistance(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship" ,
            "Head/Tail"          ,
            "UseBBone"           ,
            "Distance"           ,
            "Clamp Region"       ,
            "Affect Transform"   ,
            "Owner Space"        ,
            "Target Space"       ,
            "Influence"          ,
            "Target"             ,
            "Enable"             ,
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
        


    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        print(wrapGreen("Creating ")+wrapWhite("Limit Distance")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        c = self.GetxForm().bGetObject().constraints.new('LIMIT_DISTANCE')
        get_target_and_subtarget(self, c)
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        #
        # TODO: set distance automagically
        # IMPORTANT TODO BUG
        
        custom_space_owner, custom_space_target = False, False
        if self.inputs["Owner Space"].is_connected and self.inputs["Owner Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_owner=True
            c.owner_space='CUSTOM'
            xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Owner Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        if self.inputs["Target Space"].is_connected and self.inputs["Target Space"].links[0].from_node.node_type == 'XFORM':
            custom_space_target=True
            c.target_space='CUSTOM'
            xf = self.inputs["Target Space"].links[0].from_node.bGetObject(mode="OBJECT")
            if isinstance(xf, Bone):
                c.space_object=self.inputs["Target Space"].links[0].from_node.bGetParentArmature(); c.space_subtarget=xf.name
            else:
                c.space_object=xf
        props_sockets = {
        'distance'            : ("Distance", 0),
        'head_tail'           : ("Head/Tail", 0),
        'limit_mode'          : ("Clamp Region", "LIMITDIST_INSIDE"),
        'use_bbone_shape'     : ("UseBBone", False),
        'use_transform_limit' : ("Affect Transform", 1),
        'owner_space'         : ("Owner Space", 1),
        'target_space'        : ("Target Space", 1),
        'influence'           : ("Influence", 1),
        'mute'               : ("Enable", True),
        }
        if custom_space_owner: del props_sockets['owner_space']
        if custom_space_target: del props_sockets['target_space']
        #
        evaluate_sockets(self, c, props_sockets)
        self.executed = True

    def bFinalize(self, bContext = None):
        finish_drivers(self)
    
        

# Tracking

class LinkStretchTo(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship" ,
            "Head/Tail"          ,
            "UseBBone"           ,
            "Original Length"   ,
            "Volume Variation"   ,
            "Use Volume Min"     ,
            "Volume Min"         ,
            "Use Volume Max"     ,
            "Volume Max"         ,
            "Smooth"             ,
            "Maintain Volume"    ,
            "Rotation"           ,
            "Influence"          ,
            "Target"             ,
            "Enable"             ,
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
        


    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        print(wrapGreen("Creating ")+wrapWhite("Stretch-To")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        c = self.GetxForm().bGetObject().constraints.new('STRETCH_TO')
        get_target_and_subtarget(self, c)
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        props_sockets = {
        'head_tail'       : ("Head/Tail", 0),
        'use_bbone_shape' : ("UseBBone", False),
        'bulge'           : ("Volume Variation", 0),
        'use_bulge_min'   : ("Use Volume Min", False),
        'bulge_min'       : ("Volume Min", 0),
        'use_bulge_max'   : ("Use Volume Max", False),
        'bulge_max'       : ("Volume Max", 0),
        'bulge_smooth'    : ("Smooth", 0),
        'volume'          : ("Maintain Volume", 'VOLUME_XZX'),
        'keep_axis'       : ("Rotation", 'PLANE_X'),
        'rest_length'     : ("Original Length", self.GetxForm().bGetObject().bone.length),
        'influence'       : ("Influence", 1),
        'mute'           : ("Enable", True),
        }
        evaluate_sockets(self, c, props_sockets)
        
        if (self.evaluate_input("Original Length") == 0):
            # this is meant to be set automatically.
            c.rest_length = self.GetxForm().bGetObject().bone.length
        self.executed = True
        
    def bFinalize(self, bContext = None):
        finish_drivers(self)
    
        

class LinkDampedTrack(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship" ,
            "Head/Tail"          ,
            "UseBBone"           ,
            "Track Axis"         ,
            "Influence"          ,
            "Target"             ,
            "Enable"             ,
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
        


    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        print(wrapGreen("Creating ")+wrapWhite("Damped Track")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        c = self.GetxForm().bGetObject().constraints.new('DAMPED_TRACK')
        get_target_and_subtarget(self, c)
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        props_sockets = {
        'head_tail'       : ("Head/Tail", 0),
        'use_bbone_shape' : ("UseBBone", False),
        'track_axis'      : ("Track Axis", 'TRACK_Y'),
        'influence'       : ("Influence", 1),
        'mute'            : ("Enable", True),
        }
        evaluate_sockets(self, c, props_sockets)
        self.executed = True
    
    def bFinalize(self, bContext = None):
        finish_drivers(self)
        
        

class LinkLockedTrack(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship" ,
            "Head/Tail"          ,
            "UseBBone"           ,
            "Track Axis"         ,
            "Lock Axis"          ,
            "Influence"          ,
            "Target"             ,
            "Enable"             ,
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
        


    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        print(wrapGreen("Creating ")+wrapWhite("Locked Track")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        c = self.GetxForm().bGetObject().constraints.new('LOCKED_TRACK')
        get_target_and_subtarget(self, c)
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        props_sockets = {
        'head_tail'       : ("Head/Tail", 0),
        'use_bbone_shape' : ("UseBBone", False),
        'track_axis'      : ("Track Axis", 'TRACK_Y'),
        'lock_axis'       : ("Lock Axis", 'UP_X'),
        'influence'       : ("Influence", 1),
        'mute'           : ("Enable", True),
        }
        evaluate_sockets(self, c, props_sockets)
        self.executed = True

    def bFinalize(self, bContext = None):
        finish_drivers(self)
    
        

class LinkTrackTo(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship" ,
            "Head/Tail"          ,
            "UseBBone"           ,
            "Track Axis"         ,
            "Up Axis"            ,
            "Use Target Z"       ,
            "Influence"          ,
            "Target"             ,
            "Enable"             ,
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
        


    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        print(wrapGreen("Creating ")+wrapWhite("Track-To")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        c = self.GetxForm().bGetObject().constraints.new('TRACK_TO')
        get_target_and_subtarget(self, c)
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        props_sockets = {
        'head_tail'       : ("Head/Tail", 0),
        'use_bbone_shape' : ("UseBBone", False),
        'track_axis'      : ("Track Axis", "TRACK_Y"),
        'up_axis'         : ("Up Axis", "UP_Z"),
        'use_target_z'    : ("Use Target Z", False),
        'influence'       : ("Influence", 1),
        'mute'           : ("Enable", True),
        }
        evaluate_sockets(self, c, props_sockets)
        self.executed = True
    
        

    def bFinalize(self, bContext = None):
        finish_drivers(self)

# relationships & misc.

class LinkInheritConstraint(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship" ,
            "Location"           ,
            "Rotation"           ,
            "Scale"              ,
            "Influence"          ,
            "Target"             ,
            "Enable"             ,
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
        


    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        print(wrapGreen("Creating ")+wrapWhite("Child-Of")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        c = self.GetxForm().bGetObject().constraints.new('CHILD_OF')
        get_target_and_subtarget(self, c)
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        
        props_sockets = {
        'use_location_x'   : (("Location", 0) , 1),
        'use_location_y'   : (("Location", 1) , 1),
        'use_location_z'   : (("Location", 2) , 1),
        'use_rotation_x'   : (("Rotation", 0) , 1),
        'use_rotation_y'   : (("Rotation", 1) , 1),
        'use_rotation_z'   : (("Rotation", 2) , 1),
        'use_scale_x'      : (("Scale"   , 0) , 1),
        'use_scale_y'      : (("Scale"   , 1) , 1),
        'use_scale_z'      : (("Scale"   , 2) , 1),
        'influence'        : ( "Influence"    , 1),
        'mute'             : ("Enable", True),
        }
        evaluate_sockets(self, c, props_sockets)
        c.set_inverse_pending
        self.executed = True
        
        
    
        

    def bFinalize(self, bContext = None):
        finish_drivers(self)

class LinkInverseKinematics(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship"  ,
            "Chain Length"        ,
            "Use Tail"            ,
            "Stretch"             ,
            "Position"            ,
            "Rotation"            ,
            "Influence"           ,
            "Target"              ,
            "Pole Target"         ,
            "Enable"              ,
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
        


    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        print(wrapGreen("Creating ")+wrapOrange("Inverse Kinematics")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        ik_bone = self.GetxForm().bGetObject()
        c = self.GetxForm().bGetObject().constraints.new('IK')
        get_target_and_subtarget(self, c)
        get_target_and_subtarget(self, c, input_name = 'Pole Target')
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        
        self.bObject = c
        c.chain_count = 1 # so that, if there are errors, this doesn't print a whole bunch of circular dependency crap from having infinite chain length
        if (c.pole_target): # Calculate the pole angle, the user shouldn't have to.
            pole_object = c.pole_target
            assert pole_object == c.target, f"Error with {self}: Pole Target must be bone within the same Armature as IK Bone  -- for now."
            pole_location = None
            if (c.pole_subtarget):
                pole_object = c.pole_target.pose.bones[c.pole_subtarget]
                pole_location = pole_object.bone.head_local
            else: #TODO this is a dumb limitation but I don't want to convert to the armature's local space so that some idiot can rig in a stupid way
                raise RuntimeError(f"Error with {self}: Pole Target must be bones within the same Armature as IK Bone -- for now.")
            #HACK HACK
            handle_location = ik_bone.bone.tail_local if (self.evaluate_input("Use Tail")) else ik_bone.bone.head_local
            counter = 0
            parent = ik_bone
            base_bone = ik_bone
            while (parent is not None):
                counter+=1
                if ((self.evaluate_input("Chain Length") != 0) and (counter > self.evaluate_input("Chain Length"))):
                    break
                base_bone = parent
                parent = parent.parent

            def get_main_axis(bone, knee_location):
                # To decide whether the IK mainly bends around the x or z axis....
                x_axis = bone.matrix_local.to_3x3() @ Vector((1,0,0))
                y_axis = bone.matrix_local.to_3x3() @ Vector((0,1,0))
                z_axis = bone.matrix_local.to_3x3() @ Vector((0,0,1))
                # project the knee location onto the plane of the bone.
                from .utilities import project_point_to_plane
                planar_projection = project_point_to_plane(knee_location, bone.head_local, y_axis)
                # and get the dot between the X and Z axes to find which one the knee is displaced on.
                x_dot = x_axis.dot(planar_projection) # whichever axis' dot-product is closer to zero 
                z_dot = z_axis.dot(planar_projection) #  with the base_bone's axis is in-line with it.
                prWhite(bone.name, z_dot, x_dot)
                # knee is in-line with this axis vector, the bend is happening on the perpendicular axis.
                if abs(z_dot) < abs(x_dot): return x_axis # so we return X if Z is in-line with the knee
                else: return z_axis                       # and visa versa

            # modified from https://blender.stackexchange.com/questions/19754/how-to-set-calculate-pole-angle-of-ik-constraint-so-the-chain-does-not-move
            from mathutils import Vector

            def signed_angle(vector_u, vector_v, normal):
                # Normal specifies orientation
                angle = vector_u.angle(vector_v)
                if vector_u.cross(vector_v).angle(normal) < 1:
                    angle = -angle
                return angle

            def get_pole_angle(base_bone, ik_bone, pole_location, main_axis):
                pole_normal = (ik_bone.bone.tail_local - base_bone.bone.head_local).cross(pole_location - base_bone.bone.head_local)
                projected_pole_axis = pole_normal.cross(base_bone.bone.tail_local - base_bone.bone.head_local)
                # note that this normal-axis is the y-axis but flipped
                return signed_angle(main_axis, projected_pole_axis, base_bone.bone.tail_local - base_bone.bone.head_local)

            if self.evaluate_input("Use Tail") == True:
                main_axis = get_main_axis(ik_bone.bone, ik_bone.bone.tail_local)
                # pole angle to the PV:
                pole_angle_in_radians = get_pole_angle(base_bone, ik_bone, pole_location, main_axis)
            elif ik_bone.bone.parent:
                main_axis = get_main_axis(ik_bone.bone.parent, ik_bone.bone.tail_local)
                pole_angle_in_radians = get_pole_angle(base_bone, ik_bone, pole_location, main_axis)
            else: # the bone is not using "Use Tail" and it has no parent -- meaningless.
                pole_angle_in_radians = 0
            
            c.pole_angle = pole_angle_in_radians

            # TODO: the pole target should be a bone in a well-designed rig, but I don't want to force this, so....
            #   in future, calculate all this in world-space so we can use other objects as the pole.
        
        props_sockets = {
        'chain_count'   : ("Chain Length", 1),
        'use_tail'      : ("Use Tail", True),
        'use_stretch'   : ("Stretch", True),
        "weight"        : ("Position", 1.0),
        "orient_weight" : ("Rotation", 0.0),
        "influence"     : ("Influence", 1.0),
        'mute'          : ("Enable", True),
        }
        evaluate_sockets(self, c, props_sockets)
                
        # TODO: handle drivers
        #        (it should be assumed we want it on if it's plugged
        #         into a driver).
        c.use_location   = self.evaluate_input("Position") > 0
        c.use_rotation   = self.evaluate_input("Rotation") > 0
        self.executed = True
    
    def bFinalize(self, bContext = None):
        finish_drivers(self)
        
        

# This is kinda a weird design decision?
class LinkDrivenParameter(MantisLinkNode):
    '''A node representing an armature object'''
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        inputs = [
            "Input Relationship" ,
            "Value"      ,
            "Parameter"   ,
            "Index"       ,
        ]
        self.signature = signature
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, bContext = None,):
        prepare_parameters(self)
        prGreen("Executing Driven Parameter node")
        prop = self.evaluate_input("Parameter")
        index = self.evaluate_input("Index")
        value = self.evaluate_input("Value")
        xf = self.GetxForm()
        ob = xf.bGetObject(mode="POSE")
        # IMPORTANT: this node only works on pose bone attributes.
        self.bObject = ob
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
        finish_drivers(self)
        

        
class LinkArmature(MantisLinkNode):
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree,):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship"   ,
            "Preserve Volume"      ,
            "Use Envelopes"        ,
            "Use Current Location" ,
            "Influence"            ,
            "Enable"               ,
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        setup_custom_props(self)

    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, bContext = None,):
        prGreen("Creating Armature Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        prepare_parameters(self)
        c = self.GetxForm().bGetObject().constraints.new('ARMATURE')
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        # get number of targets
        num_targets = len( list(self.inputs.values())[6:] )//2
        
        props_sockets = {
        'use_deform_preserve_volume' : ("Preserve Volume", 0),
        'use_bone_envelopes'         : ("Use Envelopes", 0),
        'use_current_location'       : ("Use Current Location", 0),
        'influence'                  : ( "Influence"    , 1),
        'mute'                       : ("Enable", True),
        }
        targets_weights = {}
        for i in range(num_targets):
            target = c.targets.new()
            target_input_name = list(self.inputs.keys())[i*2+6  ]
            weight_input_name = list(self.inputs.keys())[i*2+6+1]
            get_target_and_subtarget(self, target, target_input_name)
            weight_value=self.evaluate_input(weight_input_name)
            if not isinstance(weight_value, float):
                weight_value=0
            targets_weights[i]=weight_value

            props_sockets["targets[%d].weight" % i] = (weight_input_name, 0)
            # targets_weights.append({"weight":(weight_input_name, 0)})
        evaluate_sockets(self, c, props_sockets)
        for target, value in targets_weights.items():
            c.targets[target].weight=value
        # for i, (target, weight) in enumerate(zip(c.targets, targets_weights)):
            # evaluate_sockets(self, target, weight)
        self.executed = True

    def bFinalize(self, bContext = None):
        finish_drivers(self)




class LinkSplineIK(MantisLinkNode):
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship" ,
            "Target"             ,
            "Chain Length"       ,
            "Even Divisions"     ,
            "Chain Offset"       ,
            "Use Curve Radius"   ,
            "Y Scale Mode"       ,
            "XZ Scale Mode"      ,
            "Use Original Scale" ,
            "Influence"          ,
        ]
        additional_parameters = { "Name":None }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(["Output Relationship"])
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])

    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, bContext = None,):
        prepare_parameters(self)
        prGreen("Creating Spline-IK Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        c = self.GetxForm().bGetObject().constraints.new('SPLINE_IK')
        get_target_and_subtarget(self, c)
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        props_sockets = {
        'chain_count' : ("Chain Length", 0),
        'use_even_divisions'      : ("Even Divisions", False),
        'use_chain_offset'         : ("Chain Offset", False),
        'use_curve_radius'    : ("Use Curve Radius", False),
        'y_scale_mode'       : ("Y Scale Mode", "FIT_CURVE"),
        'xz_scale_mode'           : ("XZ Scale Mode", "NONE"),
        'use_original_scale'           : ("Use Original Scale", False),
        'influence'       : ("Influence", 1),
        }

        evaluate_sockets(self, c, props_sockets)
        self.executed = True
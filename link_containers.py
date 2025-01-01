from .node_container_common import *
from bpy.types import Node, Bone
from .base_definitions import MantisNode, GraphError

#TODO: get rid of this, it's unnecesary here, we always want to import
#  all classes in this file
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



def default_evaluate_input(nc, input_name):
    # should catch 'Target', 'Pole Target' and ArmatureConstraint targets, too
    if ('Target' in input_name) and input_name not in  ["Target Space", "Use Target Z"]:
        socket = nc.inputs.get(input_name)
        if socket.is_linked:
            return socket.links[0].from_node
        return None
        
    else:
        return evaluate_input(nc, input_name)

# def set_constraint_name(nc):
#     if name := nc.evaluate_input("Name"):
#         return name
#     return nc.__class__.__name__

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

class LinkInherit:
    '''A node representing inheritance'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
         "Parent"           : NodeSocket(is_input = True, name = "Parent", node = self,),
         # bone only:
         "Inherit Rotation" : NodeSocket(is_input = True, name = "Inherit Rotation", node = self,),
         "Inherit Scale"    : NodeSocket(is_input = True, name = "Inherit Scale", node = self,),
         "Connected"        : NodeSocket(is_input = True, name = "Connected", node = self,),
        }
        self.outputs = { "Inheritance" : NodeSocket(name = "Inheritance", node = self) }
        self.parameters = {
         "Parent":None,
         # bone only:
         "Inherit Rotation":None,
         "Inherit Scale":None,
         "Connected":None,
        }
        self.links = {} # leave this empty for now!
        # now set up the traverse target...
        self.inputs["Parent"].set_traverse_target(self.outputs["Inheritance"])
        self.outputs["Inheritance"].set_traverse_target(self.inputs["Parent"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True
    
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)
        
    def GetxForm(self): # DUPLICATED, TODO fix this
        # I think this is only run in display update.
        trace = trace_single_line_up(self, "Inheritance")
        for node in trace[0]:
            if (node.node_type == 'XFORM'):
                return node
        raise GraphError("%s is not connected to a downstream xForm" % self)
    
    
        


class LinkCopyLocation:
    '''A node representing Copy Location'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "Head/Tail"          : NodeSocket(is_input = True, name = "Head/Tail", node = self,),
            "UseBBone"           : NodeSocket(is_input = True, name = "UseBBone", node = self,),
            "Axes"               : NodeSocket(is_input = True, name = "Axes", node = self,),
            "Invert"             : NodeSocket(is_input = True, name = "Invert", node = self,),
            "Target Space"       : NodeSocket(is_input = True, name = "Target Space", node = self,),
            "Owner Space"        : NodeSocket(is_input = True, name = "Owner Space", node = self,),
            "Offset"             : NodeSocket(is_input = True, name = "Offset", node = self,),
            "Influence"          : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Target"             : NodeSocket(is_input = True, name = "Target", node = self,),
            "Enable"             : NodeSocket(is_input = True, name = "Enable", node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name":None,
            "Input Relationship":None,
            "Head/Tail":None,
            "UseBBone":None,
            "Axes":None,
            "Invert":None,
            "Target Space":None,
            "Owner Space":None,
            "Offset":None,
            "Influence":None,
            "Target":None,
            "Enable":None, }
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
        
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)
    
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
            xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
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
    
        
        

class LinkCopyRotation:
    '''A node representing Copy Rotation'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "RotationOrder"      : NodeSocket(is_input = True, name = "RotationOrder", node = self,),
            "Rotation Mix"       : NodeSocket(is_input = True, name = "Rotation Mix", node = self,),
            "Axes"               : NodeSocket(is_input = True, name = "Axes", node = self,),
            "Invert"             : NodeSocket(is_input = True, name = "Invert", node = self,),
            "Target Space"       : NodeSocket(is_input = True, name = "Target Space", node = self,),
            "Owner Space"        : NodeSocket(is_input = True, name = "Owner Space", node = self,),
            "Influence"          : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Target"             : NodeSocket(is_input = True, name = "Target", node = self,),
            "Enable"             : NodeSocket(is_input = True, name = "Enable", node = self,),  }
        self.outputs = {
            "Output Relationship" : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name":None,
            "Input Relationship":None,
            "RotationOrder":None,
            "Rotation Mix":None,
            "Axes":None,
            "Invert":None,
            "Target Space":None,
            "Owner Space":None,
            "Influence":None,
            "Target":None,
            "Enable":None, }
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)
    
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
            xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
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
    
        
        
class LinkCopyScale:
    '''A node representing Copy Scale'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "Offset"             : NodeSocket(is_input = True, name = "Offset", node = self,),
            "Average"            : NodeSocket(is_input = True, name = "Average", node = self,),
            "Additive"           : NodeSocket(is_input = True, name = "Additive", node = self,),
            "Axes"               : NodeSocket(is_input = True, name = "Axes", node = self,),
            #"Invert"             : NodeSocket(is_input = True, name = "Invert", node = self,),
            "Target Space"       : NodeSocket(is_input = True, name = "Target Space", node = self,),
            "Owner Space"        : NodeSocket(is_input = True, name = "Owner Space", node = self,),
            "Influence"          : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Target"             : NodeSocket(is_input = True, name = "Target", node = self,),
            "Enable"             : NodeSocket(is_input = True, name = "Enable", node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name":None,
            "Input Relationship":None,
            "Offset":None,
            "Average":None,
            "Axes":None,
            #"Invert":None,
            "Target Space":None,
            "Owner Space":None,
            "Influence":None,
            "Target":None,
            "Enable":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)
    
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
    
        

class LinkCopyTransforms:
    '''A node representing Copy Transfoms'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "Head/Tail"          : NodeSocket(is_input = True, name = "Head/Tail", node = self,),
            "UseBBone"           : NodeSocket(is_input = True, name = "UseBBone", node = self,),
            "Additive"           : NodeSocket(is_input = True, name = "Additive", node = self,),
            "Mix"                : NodeSocket(is_input = True, name = "Mix", node = self,),
            "Target Space"       : NodeSocket(is_input = True, name = "Target Space", node = self,),
            "Owner Space"        : NodeSocket(is_input = True, name = "Owner Space", node = self,),
            "Influence"          : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Target"             : NodeSocket(is_input = True, name = "Target", node = self,),
            "Enable"             : NodeSocket(is_input = True, name = "Enable", node = self,),  }
        self.outputs = {
            "Output Relationship" : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name":None,
            "Input Relationship":None,
            "Head/Tail":None,
            "UseBBone":None,
            "Mix":None,
            "Target Space":None,
            "Owner Space":None,
            "Influence":None,
            "Target":None,
            "Enable":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)
    
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

class LinkTransformation:
    '''A node representing Copy Transfoms'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship"     : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "Target Space"           : NodeSocket(is_input = True, name = "Target Space", node = self,),
            "Owner Space"            : NodeSocket(is_input = True, name = "Owner Space", node = self,),
            "Influence"              : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Target"                 : NodeSocket(is_input = True, name = "Target", node = self,),
            "Enable"                 : NodeSocket(is_input = True, name = "Enable", node = self,),  
            "Extrapolate"            : NodeSocket(is_input = True, name = "Extrapolate", node = self,),  
            "Map From"               : NodeSocket(is_input = True, name = "Map From", node = self,),
            "Rotation Mode"          : NodeSocket(is_input = True, name = "Rotation Mode", node = self,),
            "X Min From"             : NodeSocket(is_input = True, name = "X Min From", node = self,),
            "X Max From"             : NodeSocket(is_input = True, name = "X Max From", node = self,),
            "Y Min From"             : NodeSocket(is_input = True, name = "Y Min From", node = self,),
            "Y Max From"             : NodeSocket(is_input = True, name = "Y Max From", node = self,),
            "Z Min From"             : NodeSocket(is_input = True, name = "Z Min From", node = self,),
            "Z Max From"             : NodeSocket(is_input = True, name = "Z Max From", node = self,),
            "Map To"                 : NodeSocket(is_input = True, name = "Map To", node = self,),
            "X Source Axis"          : NodeSocket(is_input = True, name = "X Source Axis", node = self,),
            "X Min To"               : NodeSocket(is_input = True, name = "X Min To", node = self,),
            "X Max To"               : NodeSocket(is_input = True, name = "X Max To", node = self,),
            "Y Source Axis"          : NodeSocket(is_input = True, name = "Y Source Axis", node = self,),
            "Y Min To"               : NodeSocket(is_input = True, name = "Y Min To", node = self,),
            "Y Max To"               : NodeSocket(is_input = True, name = "Y Max To", node = self,),
            "Z Source Axis"          : NodeSocket(is_input = True, name = "Z Source Axis", node = self,),
            "Z Min To"               : NodeSocket(is_input = True, name = "Z Min To", node = self,),
            "Z Max To"               : NodeSocket(is_input = True, name = "Z Max To", node = self,),
            "Rotation Mode"          : NodeSocket(is_input = True, name = "Rotation Mode", node = self,),
            "Mix Mode (Translation)" : NodeSocket(is_input = True, name = "Mix Mode (Translation)", node = self,),
            "Mix Mode (Rotation)"    : NodeSocket(is_input = True, name = "Mix Mode (Rotation)", node = self,),
            "Mix Mode (Scale)"       : NodeSocket(is_input = True, name = "Mix Mode (Scale)", node = self,),
            }
        self.outputs = {
            "Output Relationship"    : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name"                   : None,
            "Input Relationship"     : None,
            "Target Space"           : None,
            "Owner Space"            : None,
            "Influence"              : None,
            "Target"                 : None,
            "Enable"                 : None,
            "Extrapolate"            : None,
            "Map From"               : None,
            "Rotation Mode"          : None,
            "X Min From"             : None,
            "X Max From"             : None,
            "Y Min From"             : None,
            "Y Max From"             : None,
            "Z Min From"             : None,
            "Z Max From"             : None,
            "Map To"                 : None,
            "X Source Axis"          : None,
            "X Min To"               : None,
            "X Max To"               : None,
            "Y Source Axis"          : None,
            "Y Min To"               : None,
            "Y Max To"               : None,
            "Z Source Axis"          : None,
            "Z Min To"               : None,
            "Z Max To"               : None,
            "Rotation Order"         : None,
            "Mix Mode (Translation)" : None,
            "Mix Mode (Rotation)"    : None,
            "Mix Mode (Scale)"       : None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)
    
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
            xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
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
    
        

class LinkLimitLocation:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "Use Max X"          : NodeSocket(is_input = True, name = "Use Max X", node = self,),
            "Max X"              : NodeSocket(is_input = True, name = "Max X", node = self,),
            "Use Max Y"          : NodeSocket(is_input = True, name = "Use Max Y", node = self,),
            "Max Y"              : NodeSocket(is_input = True, name = "Max Y", node = self,),
            "Use Max Z"          : NodeSocket(is_input = True, name = "Use Max Z", node = self,),
            "Max Z"              : NodeSocket(is_input = True, name = "Max Z", node = self,),
            "Use Min X"          : NodeSocket(is_input       = True, name = "Use Min X", node = self,),
            "Min X"              : NodeSocket(is_input = True, name = "Min X", node = self,),
            "Use Min Y"          : NodeSocket(is_input = True, name = "Use Min Y", node = self,),
            "Min Y"              : NodeSocket(is_input = True, name = "Min Y", node = self,),
            "Use Min Z"          : NodeSocket(is_input = True, name = "Use Min Z", node = self,),
            "Min Z"              : NodeSocket(is_input = True, name = "Min Z", node = self,),
            "Affect Transform"   : NodeSocket(is_input = True, name = "Affect Transform", node = self,),
            "Owner Space"        : NodeSocket(is_input = True, name = "Owner Space", node = self,),
            "Influence"          : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Enable"             : NodeSocket(is_input = True, name = "Enable", node = self,),  }
        self.outputs = {
            "Output Relationship" : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name":None,
            "Input Relationship":None,
            "Use Max X":None,
            "Max X":None,
            "Use Max Y":None,
            "Max Y":None,
            "Use Max Z":None,
            "Max Z":None,
            "Use Min X":None,
            "Min X":None,
            "Use Min Y":None,
            "Min Y":None,
            "Use Min Z":None,
            "Min Z":None,
            "Affect Transform":None,
            "Owner Space":None,
            "Influence":None,
            "Enable":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)
    
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
    
        
        
class LinkLimitRotation:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "Use X"              : NodeSocket(is_input = True, name = "Use X", node = self,),
            "Use Y"              : NodeSocket(is_input = True, name = "Use Y", node = self,),
            "Use Z"              : NodeSocket(is_input = True, name = "Use Z", node = self,),
            "Max X"              : NodeSocket(is_input = True, name = "Max X", node = self,),
            "Max Y"              : NodeSocket(is_input = True, name = "Max Y", node = self,),
            "Max Z"              : NodeSocket(is_input = True, name = "Max Z", node = self,),
            "Min X"              : NodeSocket(is_input = True, name = "Min X", node = self,),
            "Min Y"              : NodeSocket(is_input = True, name = "Min Y", node = self,),
            "Min Z"              : NodeSocket(is_input = True, name = "Min Z", node = self,),
            "Affect Transform"   : NodeSocket(is_input = True, name = "Affect Transform", node = self,),
            "Owner Space"        : NodeSocket(is_input = True, name = "Owner Space", node = self,),
            "Influence"          : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Enable"             : NodeSocket(is_input = True, name = "Enable", node = self,),  }
        self.outputs = {
            "Output Relationship" : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name":None,
            "Input Relationship":None,
            "Use X":None,
            "Use Y":None,
            "Use Z":None,
            "Max X":None,
            "Max Y":None,
            "Max Z":None,
            "Min X":None,
            "Min Y":None,
            "Min Z":None,
            "Affect Transform":None,
            "Owner Space":None,
            "Influence":None,
            "Enable":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)
    
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
    
        
        
class LinkLimitScale:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "Use Max X"          : NodeSocket(is_input = True, name = "Use Max X", node = self,),
            "Max X"              : NodeSocket(is_input = True, name = "Max X", node = self,),
            "Use Max Y"          : NodeSocket(is_input = True, name = "Use Max Y", node = self,),
            "Max Y"              : NodeSocket(is_input = True, name = "Max Y", node = self,),
            "Use Max Z"          : NodeSocket(is_input = True, name = "Use Max Z", node = self,),
            "Max Z"              : NodeSocket(is_input = True, name = "Max Z", node = self,),
            "Use Min X"          : NodeSocket(is_input = True, name = "Use Min X", node = self,),
            "Min X"              : NodeSocket(is_input = True, name = "Min X", node = self,),
            "Use Min Y"          : NodeSocket(is_input = True, name = "Use Min Y", node = self,),
            "Min Y"              : NodeSocket(is_input = True, name = "Min Y", node = self,),
            "Use Min Z"          : NodeSocket(is_input = True, name = "Use Min Z", node = self,),
            "Min Z"              : NodeSocket(is_input = True, name = "Min Z", node = self,),
            "Affect Transform"   : NodeSocket(is_input = True, name = "Affect Transform", node = self,),
            "Owner Space"        : NodeSocket(is_input = True, name = "Owner Space", node = self,),
            "Influence"          : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Enable"             : NodeSocket(is_input = True, name = "Enable", node = self,),  }
        self.outputs = {
            "Output Relationship" : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name":None,
            "Input Relationship":None,
            "Use Max X":None,
            "Max X":None,
            "Use Max Y":None,
            "Max Y":None,
            "Use Max Z":None,
            "Max Z":None,
            "Use Min X":None,
            "Min X":None,
            "Use Min Y":None,
            "Min Y":None,
            "Use Min Z":None,
            "Min Z":None,
            "Affect Transform":None,
            "Owner Space":None,
            "Influence":None,
            "Enable":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)
    
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
    
        
        
class LinkLimitDistance:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "Head/Tail"          : NodeSocket(is_input = True, name = "Head/Tail", node = self,),
            "UseBBone"           : NodeSocket(is_input = True, name = "UseBBone", node = self,),
            "Distance"           : NodeSocket(is_input = True, name = "Distance", node = self,),
            "Clamp Region"       : NodeSocket(is_input = True, name = "Clamp Region", node = self,),
            "Affect Transform"   : NodeSocket(is_input = True, name = "Affect Transform", node = self,),
            "Owner Space"        : NodeSocket(is_input = True, name = "Owner Space", node = self,),
            "Target Space"       : NodeSocket(is_input = True, name = "Target Space", node = self,),
            "Influence"          : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Target"             : NodeSocket(is_input = True, name = "Target", node = self,),
            "Enable"             : NodeSocket(is_input = True, name = "Enable", node = self,),  }
        self.outputs = {
            "Output Relationship" : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name":None,
            "Input Relationship":None,
            "Head/Tail":None,
            "UseBBone":None,
            "Distance":None,
            "Clamp Region":None,
            "Affect Transform":None,
            "Owner Space":None,
            "Target Space":None,
            "Influence":None,
            "Target":None,
            "Enable":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)

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
            xf = self.inputs["Owner Space"].links[0].from_node.bGetObject(mode="OBJECT")
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

class LinkStretchTo:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "Head/Tail"          : NodeSocket(is_input = True, name = "Head/Tail", node = self,),
            "UseBBone"           : NodeSocket(is_input = True, name = "UseBBone", node = self,),
            "Original Length"    : NodeSocket(is_input = True, name = "Original Length", node = self,),
            "Volume Variation"   : NodeSocket(is_input = True, name = "Volume Variation", node = self,),
            "Use Volume Min"     : NodeSocket(is_input = True, name = "Use Volume Min", node = self,),
            "Volume Min"         : NodeSocket(is_input = True, name = "Volume Min", node = self,),
            "Use Volume Max"     : NodeSocket(is_input = True, name = "Use Volume Max", node = self,),
            "Volume Max"         : NodeSocket(is_input = True, name = "Volume Max", node = self,),
            "Smooth"             : NodeSocket(is_input = True, name = "Smooth", node = self,),
            "Maintain Volume"    : NodeSocket(is_input = True, name = "Maintain Volume", node = self,),
            "Rotation"           : NodeSocket(is_input = True, name = "Rotation", node = self,),
            "Influence"          : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Target"             : NodeSocket(is_input = True, name = "Target", node = self,),
            "Enable"             : NodeSocket(is_input = True, name = "Enable", node = self,),  }
        self.outputs = {
            "Output Relationship" : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name":None,
            "Input Relationship":None,
            "Head/Tail":None,
            "UseBBone":None,
            "Original Length":None,
            "Volume Variation":None,
            "Use Volume Min":None,
            "Volume Min":None,
            "Use Volume Max":None,
            "Volume Max":None,
            "Smooth":None,
            "Maintain Volume":None,
            "Rotation":None,
            "Influence":None,
            "Target":None,
            "Enable":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)

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
    
        

class LinkDampedTrack:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "Head/Tail"          : NodeSocket(is_input = True, name = "Head/Tail", node = self,),
            "UseBBone"           : NodeSocket(is_input = True, name = "UseBBone", node = self,),
            "Track Axis"         : NodeSocket(is_input = True, name = "Track Axis", node = self,),
            "Influence"          : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Target"             : NodeSocket(is_input = True, name = "Target", node = self,),
            "Enable"             : NodeSocket(is_input = True, name = "Enable", node = self,),  }
        self.outputs = {
            "Output Relationship" : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name":None,
            "Input Relationship":None,
            "Head/Tail":None,
            "UseBBone":None,
            "Track Axis":None,
            "Influence":None,
            "Target":None,
            "Enable":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)

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
        
        

class LinkLockedTrack:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "Head/Tail"          : NodeSocket(is_input = True, name = "Head/Tail", node = self,),
            "UseBBone"           : NodeSocket(is_input = True, name = "UseBBone", node = self,),
            "Track Axis"         : NodeSocket(is_input = True, name = "Track Axis", node = self,),
            "Lock Axis"          : NodeSocket(is_input = True, name = "Lock Axis", node = self,),
            "Influence"          : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Target"             : NodeSocket(is_input = True, name = "Target", node = self,),
            "Enable"             : NodeSocket(is_input = True, name = "Enable", node = self,),  }
        self.outputs = {
            "Output Relationship" : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name":None,
            "Input Relationship":None,
            "Head/Tail":None,
            "UseBBone":None,
            "Track Axis":None,
            "Lock Axis":None,
            "Influence":None,
            "Target":None,
            "Enable":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)

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
    
        

class LinkTrackTo:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "Head/Tail"          : NodeSocket(is_input = True, name = "Head/Tail", node = self,),
            "UseBBone"           : NodeSocket(is_input = True, name = "UseBBone", node = self,),
            "Track Axis"         : NodeSocket(is_input = True, name = "Track Axis", node = self,),
            "Up Axis"            : NodeSocket(is_input = True, name = "Up Axis", node = self,),
            "Use Target Z"       : NodeSocket(is_input = True, name = "Use Target Z", node = self,),
            "Influence"          : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Target"             : NodeSocket(is_input = True, name = "Target", node = self,),
            "Enable"             : NodeSocket(is_input = True, name = "Enable", node = self,),  }
        self.outputs = {
            "Output Relationship" : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name":None,
            "Input Relationship":None,
            "Head/Tail":None,
            "UseBBone":None,
            "Track Axis":None,
            "Up Axis":None,
            "Use Target Z":None, 
            "Influence":None,
            "Target":None,
            "Enable":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)

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

class LinkInheritConstraint:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "Location"           : NodeSocket(is_input = True, name = "Location", node = self,),
            "Rotation"           : NodeSocket(is_input = True, name = "Rotation", node = self,),
            "Scale"              : NodeSocket(is_input = True, name = "Scale", node = self,),
            "Influence"          : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Target"             : NodeSocket(is_input = True, name = "Target", node = self,),
            "Enable"             : NodeSocket(is_input = True, name = "Enable", node = self,),  }
        self.outputs = {
            "Output Relationship" : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name":None,
            "Input Relationship":None,
            "Location":None,
            "Rotation":None,
            "Scale":None,
            "Influence":None,
            "Target":None,
            "Enable":None,}
        self.drivers = {}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)

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

class LinkInverseKinematics:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship"  : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
            "Chain Length"        : NodeSocket(is_input = True, name = "Chain Length", node = self,),
            "Use Tail"            : NodeSocket(is_input = True, name = "Use Tail", node = self,),
            "Stretch"             : NodeSocket(is_input = True, name = "Stretch", node = self,),
            "Position"            : NodeSocket(is_input = True, name = "Position", node = self,),
            "Rotation"            : NodeSocket(is_input = True, name = "Rotation", node = self,),
            "Influence"           : NodeSocket(is_input = True, name = "Influence", node = self,),
            "Target"              : NodeSocket(is_input = True, name = "Target", node = self,),
            "Pole Target"         : NodeSocket(is_input = True, name = "Pole Target", node = self,),
            "Enable"              : NodeSocket(is_input = True, name = "Enable", node = self,),  }
        self.outputs = {
            "Output Relationship" : NodeSocket(name = "Output Relationship", node=self) }
        self.parameters = {
            "Name":None,
            "Connected":None,
            "Chain Length":None,
            "Use Tail":None,
            "Stretch":None,
            "Position":None,
            "Rotation":None,
            "Influence":None,
            "Target":None, 
            "Pole Target":None,
            "Enable":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        self.bObject = None
        self.drivers = {}
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)

    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        print(wrapGreen("Creating ")+wrapOrange("Inverse Kinematics")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        myOb = self.GetxForm().bGetObject()
        c = self.GetxForm().bGetObject().constraints.new('IK')
        get_target_and_subtarget(self, c)
        get_target_and_subtarget(self, c, input_name = 'Pole Target')
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        
        self.bObject = c
        c.chain_count = 1 # so that, if there are errors, this doesn't print a whole bunch of circular dependency crap from having infinite chain length
        if (c.pole_target): # Calculate the pole angle, the user shouldn't have to.
            pole_object = c.pole_target
            pole_location = pole_object.matrix_world.decompose()[0]
            if (c.pole_subtarget):
                pole_object = c.pole_target.pose.bones[c.pole_subtarget]
                pole_location += pole_object.bone.head_local
            #HACK HACK
            handle_location = myOb.bone.tail_local if (self.evaluate_input("Use Tail")) else myOb.bone.head_local
            counter = 0
            parent = myOb
            base_bone = myOb
            while (parent is not None):
                if ((self.evaluate_input("Chain Length") != 0) and (counter > self.evaluate_input("Chain Length"))):
                    break
                base_bone = parent
                parent = parent.parent
                counter+=1
            head_location = base_bone.bone.head_local

            # modified from https://blender.stackexchange.com/questions/19754/how-to-set-calculate-pole-angle-of-ik-constraint-so-the-chain-does-not-move
            from mathutils import Vector

            def signed_angle(vector_u, vector_v, normal):
                # Normal specifies orientation
                angle = vector_u.angle(vector_v)
                if vector_u.cross(vector_v).angle(normal) < 1:
                    angle = -angle
                return angle

            def get_pole_angle(base_bone, ik_bone, pole_location):
                pole_normal = (ik_bone.bone.tail_local - base_bone.bone.head_local).cross(pole_location - base_bone.bone.head_local)
                projected_pole_axis = pole_normal.cross(base_bone.bone.tail_local - base_bone.bone.head_local)
                x_axis= base_bone.bone.matrix_local.to_3x3() @ Vector((1,0,0))
                return signed_angle(x_axis, projected_pole_axis, base_bone.bone.tail_local - base_bone.bone.head_local)

            pole_angle_in_radians = get_pole_angle(base_bone,
                                                myOb,
                                                pole_location)
            c.pole_angle = pole_angle_in_radians
        
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
class LinkDrivenParameter:
    '''A node representing an armature object'''
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
        "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
          "Driver"      : NodeSocket(is_input = True, name = "Driver", node = self),
          "Parameter"   : NodeSocket(is_input = True, name = "Parameter", node = self),
          "Index"       : NodeSocket(is_input = True, name = "Index", node = self),
        }
        self.outputs = {
          "Output Relationship" : NodeSocket(name = "Output Relationship", node=self), }
        self.parameters = {
          "Input Relationship":None, 
          "Driver":None, 
          "Parameter":None,
          "Index":None,
        }
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = "LINK"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False

    def GetxForm(self):
        return GetxForm(self)

    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)

    def bExecute(self, bContext = None,):
        prepare_parameters(self)
        prGreen("Executing Driven Parameter node")
        
        # example_ driver ={
                    # "owner":None,
                    # "prop":None, # will be filled out in the node that uses the driver
                    # "ind":-1, # same here
                    # "type": self.evaluate_input("Driver Type"),
                    # "vars": my_vars,
                    # "keys": self.evaluate_input("fCurve"),}
                    
        driver = self.evaluate_input("Driver")
        driver["owner"] = self.GetxForm().bGetObject()
        driver["prop"] = self.evaluate_input("Parameter")
        driver["ind"] = self.evaluate_input("Index")
        
        self.parameters["Driver"] = driver
        self.executed = True

    def bFinalize(self, bContext = None):
        # TODO HACK BUG
        # This probably no longer works
        from .drivers import CreateDrivers
        CreateDrivers( [ self.parameters["Driver"] ] )
        

        
class LinkArmature:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree,):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
        "Input Relationship"   : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
        "Preserve Volume"      : NodeSocket(is_input = True, name = "Preserve Volume", node = self),
        "Use Envelopes"        : NodeSocket(is_input = True, name = "Use Envelopes", node = self),
        "Use Current Location" : NodeSocket(is_input = True, name = "Use Current Location", node = self),
        "Influence"            : NodeSocket(is_input = True, name = "Influence", node = self),
        "Enable"               : NodeSocket(is_input = True, name = "Enable", node = self),
        }
        self.outputs = {
          "Output Relationship" : NodeSocket(name = "Output Relationship", node=self), }
        self.parameters = {
            "Name":None,
            "Input Relationship":None, 
            "Preserve Volume":None, 
            "Use Envelopes":None, 
            "Use Current Location":None, 
            "Influence":None, 
            "Enable":None,
        }
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = "LINK"
        setup_custom_props(self)
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False


    def GetxForm(self):
        return GetxForm(self)

    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)

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




class LinkSplineIK:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
          "Input Relationship" : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
          "Target"             : NodeSocket(is_input = True, name = "Target", node = self),
          "Chain Length"       : NodeSocket(is_input = True, name = "Chain Length", node = self),
          "Even Divisions"     : NodeSocket(is_input = True, name = "Even Divisions", node = self),
          "Chain Offset"       : NodeSocket(is_input = True, name = "Chain Offset", node = self),
          "Use Curve Radius"   : NodeSocket(is_input = True, name = "Use Curve Radius", node = self),
          "Y Scale Mode"       : NodeSocket(is_input = True, name = "Y Scale Mode", node = self),
          "XZ Scale Mode"      : NodeSocket(is_input = True, name = "XZ Scale Mode", node = self),
          "Use Original Scale" : NodeSocket(is_input = True, name = "Use Original Scale", node = self),
          "Influence"          : NodeSocket(is_input = True, name = "Influence", node = self),
        }
        self.outputs = {
          "Output Relationship" : NodeSocket(is_input = False, name = "Output Relationship", node=self), }
        self.parameters = {
          "Name":None,
          "Input Relationship":None, 
          "Target":None, 
          "Chain Length":None, 
          "Even Divisions":None, 
          "Chain Offset":None, 
          "Use Curve Radius":None, 
          "Y Scale Mode":None, 
          "XZ Scale Mode":None, 
          "Use Original Scale":None, 
          "Influence":None, 
        }
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = "LINK"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False

    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)

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


for c in TellClasses():
    setup_container(c)
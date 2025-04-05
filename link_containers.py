from .node_container_common import *
from bpy.types import Bone, NodeTree
from .base_definitions import MantisNode, GraphError, FLOAT_EPSILON
from .base_definitions import MantisSocketTemplate as SockTemplate

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

# Socket Templates we will reuse:
# inputs:
InputRelationshipTemplate : SockTemplate = SockTemplate(
    name="Input Relationship", is_input=True,  bl_idname='RelationshipSocket', )
TargetTemplate : SockTemplate = SockTemplate(
    name="Target", is_input=True,  bl_idname='xFormSocket', )
Head_Tail_Template : SockTemplate = SockTemplate(
    name="Head/Tail", is_input=True,  bl_idname='FloatFactorSocket',
    default_value=1.0, blender_property='head_tail' )
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
    name=name_stub+axis.upper(), is_input=True,  bl_idname='BoolUpdateParentNode',
    default_value=False, blender_property=name_stub.lower().replace(' ', '_')+axis.lower())
LimitAxesSocketTemplates = [] # could generate these with loops, but this is easier to understand
LimitAxesSocketTemplates.append(UseMaxXTemplates := LimitTemplateGenerator("Use Max ", "X"))
LimitAxesSocketTemplates.append(MaxXTemplates    := LimitTemplateGenerator("Max ", "X"))
LimitAxesSocketTemplates.append(UseMaxYTemplates := LimitTemplateGenerator("Use Max ", "Y"))
LimitAxesSocketTemplates.append(MaxYTemplates    := LimitTemplateGenerator("Max ", "Y"))
LimitAxesSocketTemplates.append(UseMaxZTemplates := LimitTemplateGenerator("Use Max ", "Z"))
LimitAxesSocketTemplates.append(MinZTemplates    := LimitTemplateGenerator("Min ", "Z"))
LimitAxesSocketTemplates.append(UseMinXTemplates := LimitTemplateGenerator("Use Min ", "X"))
LimitAxesSocketTemplates.append(MinXTemplates    := LimitTemplateGenerator("Min ", "X"))
LimitAxesSocketTemplates.append(UseMinYTemplates := LimitTemplateGenerator("Use Min ", "Y"))
LimitAxesSocketTemplates.append(MinYTemplates    := LimitTemplateGenerator("Min ", "Y"))
LimitAxesSocketTemplates.append(UseMinZTemplates := LimitTemplateGenerator("Use Min ", "Z"))
LimitAxesSocketTemplates.append(MinZTemplates    := LimitTemplateGenerator("Min ", "Z"))
#
AffectTransformTemplate : SockTemplate = SockTemplate(
    name="Affect Transform", bl_idname='BooleanSocket', is_input=True,
    default_value=False, blender_property='use_transform_limit')
# outputs:
OutputRelationshipTemplate : SockTemplate = SockTemplate(
    name="Output Relationship", is_input=False,  bl_idname='RelationshipSocket', )


# set the name if it is available, otherwise just use the constraint's nice name
set_constraint_name = lambda nc : nc.evaluate_input("Name") if nc.evaluate_input("Name") else nc.__class__.__name__




class MantisLinkNode(MantisNode):
    def __init__(self, signature : tuple,
                 base_tree : NodeTree,
                 socket_templates : list[SockTemplate]=[]):
        super().__init__(signature, base_tree, socket_templates)
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
    
    def gen_property_socket_map(self) -> dict:
        props_sockets = super().gen_property_socket_map()
        if (os := self.inputs["Owner Space"]).is_connected and os.links[0].from_node.node_type == 'XFORM':
            del props_sockets['owner_space']
        if ts := self.inputs.get("Target_Space") and ts.is_connected and ts.links[0].from_node.node_type == 'XFORM':
            del props_sockets['target_space']
        return props_sockets
    
    def set_custom_space(self):
        c = self.bObject
        if (os := self.inputs["Owner Space"]).is_connected and os.links[0].from_node.node_type == 'XFORM':
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

#*#-------------------------------#++#-------------------------------#*#
# L I N K   N O D E S
#*#-------------------------------#++#-------------------------------#*#

def GetxForm(nc):
    trace = trace_single_line_up(nc, "Output Relationship")
    for node in trace[0]:
        if (node.node_type == 'XFORM'):
            return node
    raise GraphError("%s is not connected to a downstream xForm" % nc)

LinkInheritSockets = [   # Name                   is_input         bl_idname                  
    SockTemplate(name="Parent",           is_input=True,   bl_idname='xFormSocket',),
    SockTemplate(name="Inherit Rotation", is_input=True,   bl_idname='BooleanSocket',),
    SockTemplate(name="Inherit Scale",    is_input=True,   bl_idname='EnumInheritScale',),
    SockTemplate(name="Connected",        is_input=True,   bl_idname='BooleanSocket',),
    SockTemplate(name="Inheritance",      is_input=False,  bl_idname='RelationshipSocket',),
]

class LinkInherit(MantisLinkNode):
    '''A node representing inheritance'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkInheritSockets)
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

class LinkCopyLocation(MantisLinkNode):
    '''A node representing Copy Location'''
    
    def __init__(self, signature : tuple,
                 base_tree : NodeTree,):
        super().__init__(signature, base_tree, LinkCopyLocationSockets)
        additional_parameters = { "Name":None }
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        c = self.GetxForm().bGetObject().constraints.new('COPY_LOCATION')
        self.get_target_and_subtarget(c)
        print(wrapGreen("Creating ")+wrapWhite("Copy Location")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        self.set_custom_space()
        props_sockets = self.gen_property_socket_map()
        evaluate_sockets(self, c, props_sockets)
        self.executed = True
        
    def bFinalize(self, bContext = None):
        finish_drivers(self)
    

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

class LinkCopyRotation(MantisLinkNode):
    '''A node representing Copy Rotation'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkCopyRotationSockets)
        additional_parameters = { "Name":None }
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        c = self.GetxForm().bGetObject().constraints.new('COPY_ROTATION')
        self.get_target_and_subtarget(c)
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
        self.set_custom_space()
        props_sockets = self.gen_property_socket_map()
        evaluate_sockets(self, c, props_sockets)
        self.executed = True
            
    def bFinalize(self, bContext = None):
        finish_drivers(self)

LinkCopyScaleSockets = [
    InputRelationshipTemplate,
    OffsetTemplate,
    SockTemplate(name='Average', bl_idname = 'BooleanSocket', is_input=True,
                         default_value=False, blender_property='use_make_uniform'),
    SockTemplate(name='Additive', bl_idname = 'BooleanSocket', is_input=True,
                         default_value=False, blender_property='use_add'),
    AxeSockTemplate,
    TargetSpaceTemplate,
    OwnerSpaceTemplate,
    InfluenceTemplate,
    TargetTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]
        
class LinkCopyScale(MantisLinkNode):
    '''A node representing Copy Scale'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkCopyScaleSockets)
        additional_parameters = { "Name":None }
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
    
    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        c = self.GetxForm().bGetObject().constraints.new('COPY_SCALE')
        self.get_target_and_subtarget(c)
        print(wrapGreen("Creating ")+wrapWhite("Copy Scale")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
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
            
    def bFinalize(self, bContext = None):
        finish_drivers(self)

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

class LinkCopyTransforms(MantisLinkNode):
    '''A node representing Copy Transfoms'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkCopyTransformsSockets)
        additional_parameters = { "Name":None }
        self.init_parameters(additional_parameters=additional_parameters)
        self.set_traverse([("Input Relationship", "Output Relationship")])
        
    def GetxForm(self):
        return GetxForm(self)

    def bExecute(self, context):
        prepare_parameters(self)
        c = self.GetxForm().bGetObject().constraints.new('COPY_TRANSFORMS')
        self.get_target_and_subtarget(c)
        print(wrapGreen("Creating ")+wrapWhite("Copy Transforms")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        self.bObject = c
        self.set_custom_space()
        props_sockets = self.gen_property_socket_map()
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
        self.get_target_and_subtarget(c)
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


LinkLimitLocationSockets = [
    InputRelationshipTemplate,
    *LimitAxesSocketTemplates, # we generated these ahead of time in a list
    AffectTransformTemplate,
    OwnerSpaceTemplate,
    InfluenceTemplate,
    EnableTemplate,
    OutputRelationshipTemplate,
]

class LinkLimitLocation(MantisLinkNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LinkLimitLocationSockets)
        self.init_parameters(additional_parameters={ "Name":None })
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
        self.set_custom_space()
        props_sockets = self.gen_property_socket_map()
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
        self.get_target_and_subtarget(c)
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
        self.get_target_and_subtarget(c)
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
        self.get_target_and_subtarget(c)
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
        self.get_target_and_subtarget(c)
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
        self.get_target_and_subtarget(c)
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
        self.get_target_and_subtarget(c)
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
    def set_pole_angle(self, angle: float) -> None:
        from math import pi
        def wrap(min : float, max : float, value: float) -> float:
            range = max-min; remainder = value % range
            if remainder > max: return min + remainder-max
            else: return remainder
        self.bObject.pole_angle = wrap(-pi, pi, angle)
    
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
                angle = -angle; self.set_pole_angle(angle)
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
        i=0

        while ( True ):
            if (i>=max_iterations):
                prOrange(f"IK Pole Angle Set reached max iterations of {i} in {time()-start_time} seconds")
                break
            if (abs(error)<error_threshhold) or (upper_bounds<=lower_bounds):
                prPurple(f"IK Pole Angle Set converged after {i} iterations with error={error} in {time()-start_time} seconds")
                break
            # get the center-point betweeen the bounds
            try_angle = lower_bounds + (upper_bounds-lower_bounds)/2
            self.set_pole_angle(try_angle); dg.update()
            error=signed_angle((base_ik_bone.tail-center_point), knee_direction, ik_axis)
            if error>0: upper_bounds=try_angle
            if error<0: lower_bounds=try_angle
            i+=1

    def bExecute(self, context):
        prepare_parameters(self)
        print(wrapGreen("Creating ")+wrapOrange("Inverse Kinematics")+
             wrapGreen(" Constraint for bone: ") +
             wrapOrange(self.GetxForm().bGetObject().name))
        ik_bone = self.GetxForm().bGetObject()
        c = self.GetxForm().bGetObject().constraints.new('IK')
        self.get_target_and_subtarget(c)
        self.get_target_and_subtarget(c, input_name = 'Pole Target')
        if constraint_name := self.evaluate_input("Name"):
            c.name = constraint_name
        
        self.bObject = c
        c.chain_count = 1 # so that, if there are errors, this doesn't print a whole bunch of circular dependency crap from having infinite chain length
        if (c.pole_target): # Calculate the pole angle, the user shouldn't have to.
            # my_xf = self.GetxForm()
            # from .xForm_containers import xFormBone
            # if not isinstance(my_xf, xFormBone):
            #     raise GraphError(f"ERROR: Pole Target must be ")
            # if c.target != 
            self.set_pole_angle(self.calc_pole_angle_pre(c, ik_bone))


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
        # adding a test here
        if bContext:
            ik_bone = self.GetxForm().bGetObject(mode='POSE')
            if self.bObject.pole_target:
                prWhite(f"Fine-tuning IK Pole Angle for {self}")
                self.calc_pole_angle_post(self.bObject, ik_bone, bContext)
        finish_drivers(self)
        

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
        self.get_target_and_subtarget(c)
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
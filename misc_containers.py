from .node_container_common import *

# The fact that I need this means that some of these classes should
#  probably be moved to link_containers.py
from .xForm_containers import xFormRoot, xFormArmature, xFormBone

def TellClasses():
    return [
             # utility
             InputFloat,
             InputVector,
             InputBoolean,
             InputBooleanThreeTuple,
             InputRotationOrder,
             InputTransformSpace,
             InputString,
             InputQuaternion,
             InputQuaternionAA,
             InputMatrix,
             InputLayerMask,
             # InputGeometry,
             InputExistingGeometryObject,
             InputExistingGeometryData,
             UtilityMetaRig,
             UtilityBoneProperties,
             UtilityDriverVariable,
             UtilityDriver,
             UtilityFCurve,
             UtilitySwitch,
             UtilityCombineThreeBool,
             UtilityCombineVector,
             UtilityCatStrings,
            ]

#*#-------------------------------#++#-------------------------------#*#
# G E N E R I C   N O D E S
#*#-------------------------------#++#-------------------------------#*#


# in reality, none of these inputs have names
#  so I am using the socket name for now
#  I suppose I could use any name :3

# TODO: the inputs that do not have names should have an empty string
#   TODO after that: make this work with identifiers instead, stupid.

class InputFloat:
    '''A node representing float input'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"Float Input" : NodeSocket(name = "Float Input", node=self) }
        self.parameters = {"Float Input":None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["Float Input"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self):
        fill_parameters(self)
    
class InputVector:
    '''A node representing vector input'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"VectorSocket" : NodeSocket(name = 'VectorSocket', node=self) }
        self.parameters = {'VectorSocket':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["VectorSocket"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self):
        fill_parameters(self)

class InputBoolean:
    '''A node representing boolean input'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"BooleanSocket" : NodeSocket(name = 'BooleanSocket', node=self) }
        self.parameters = {'BooleanSocket':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["BooleanSocket"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self):
        fill_parameters(self)

class InputBooleanThreeTuple:
    '''A node representing inheritance'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"BooleanThreeTupleSocket" : NodeSocket(name = 'BooleanThreeTupleSocket', node=self) }
        self.parameters = {'BooleanThreeTupleSocket':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["BooleanThreeTupleSocket"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self):
        fill_parameters(self)

class InputRotationOrder:
    '''A node representing string input for rotation order'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"RotationOrderSocket" : NodeSocket(name = 'RotationOrderSocket', node=self) }
        self.parameters = {'RotationOrderSocket':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["RotationOrderSocket"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self):
        fill_parameters(self)

class InputTransformSpace:
    '''A node representing string input for transform space'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"TransformSpaceSocket" : NodeSocket(name = 'TransformSpaceSocket', node=self) }
        self.parameters = {'TransformSpaceSocket':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["TransformSpaceSocket"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self):
        fill_parameters(self)

class InputString:
    '''A node representing string input'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"" : NodeSocket(name = '', node=self) }
        self.parameters = {'':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters[""]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self):
        fill_parameters(self)

class InputQuaternion:
    '''A node representing quaternion input'''
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"QuaternionSocket" : NodeSocket(name = 'QuaternionSocket', node=self) }
        self.parameters = {'QuaternionSocket':None, "Mute":None}
        self.node_type = 'UTILITY'
        
        
    def evaluate_input(self, input_name):
        return self.parameters["QuaternionSocket"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self):
        fill_parameters(self)

class InputQuaternionAA:
    '''A node representing axis-angle quaternion input'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs  = {"QuaternionSocketAA" : NodeSocket(name = 'QuaternionSocketAA', node=self) }
        self.parameters = {'QuaternionSocketAA':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["QuaternionSocketAA"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self):
        fill_parameters(self)


class InputMatrix:
    '''A node representing axis-angle quaternion input'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs  = {"Matrix" : NodeSocket(name = 'Matrix', node=self) }
        self.parameters = {'Matrix':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["Matrix"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        # this node is peculiar for how its data is input
        # It uses node properties that are not addressable as sockets.
        from mathutils import Matrix
        
        matrix = ( node_prototype.first_row[ 0], node_prototype.first_row[ 1], node_prototype.first_row[ 2], node_prototype.first_row[ 3],
                   node_prototype.second_row[0], node_prototype.second_row[1], node_prototype.second_row[2], node_prototype.second_row[3],
                   node_prototype.third_row[ 0], node_prototype.third_row[ 1], node_prototype.third_row[ 2], node_prototype.third_row[ 3],
                   node_prototype.fourth_row[0], node_prototype.fourth_row[1], node_prototype.fourth_row[2], node_prototype.fourth_row[3], )
        self.parameters["Matrix"] = Matrix([matrix[0:4], matrix[4:8], matrix[8:12], matrix[12:16]])
        # print (self.parameters["Matrix"])
        

# # NOT YET IMPLEMENTED:
# class InputMatrixNode(Node, MantisNode):
    # '''A node representing matrix input'''
    # inputs = 
    # # the node is implemented as a set of sixteen float inputs
    # # but I think I can boil it down to one matrix input


# class ScaleBoneLengthNode(Node, MantisNode):
    # '''Scale Bone Length'''
    # pass

 
class UtilityMetaRig:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Meta-Armature" : NodeSocket(is_input = True, name = "Meta-Armature", node=self),
          "Meta-Bone"     : NodeSocket(is_input = True, name = "Meta-Bone", node=self),
        }
        self.outputs = {
          "Matrix" : NodeSocket(name = "Matrix", node=self),
        }
        self.parameters = {
          "Meta-Armature" : None,
          "Meta-Bone" : None,
        }
        self.node_type = "UTILITY"

    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)

    def bExecute(self, bContext = None,):
        #kinda clumsy, whatever
        import bpy
        from mathutils import Matrix
        m = Matrix.Identity(4)
        
        meta_rig  = self.evaluate_input("Meta-Armature")
        meta_bone = self.evaluate_input("Meta-Bone")
        
        if meta_rig:
            if ( armOb := bpy.data.objects.get(meta_rig) ):
                m = armOb.matrix_world
                if ( b := armOb.data.bones.get(meta_bone)):
                    # calculate the correct object-space matrix
                    m = Matrix.Identity(3)
                    bones = []
                    while (b): bones.append(b); b = b.parent
                    while (bones): b = bones.pop(); m = m @ b.matrix
                    m = Matrix.Translation(b.head_local) @ m.to_4x4()
                    m[3][3] = b.length # this is where I arbitrarily decided to store length
        
        
        self.parameters["Matrix"] = m


    def __repr__(self):
        return self.signature.__repr__()

    def fill_parameters(self):
        fill_parameters(self)
        self.parameters["Matrix"] = None


class UtilityBoneProperties:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {}
        self.outputs = {
          "matrix" : NodeSocket(name = "matrix", node=self),
          "matrix_local" : NodeSocket(name = "matrix_local", node=self),
          "matrix_basis" : NodeSocket(name = "matrix_basis", node=self),
          "head" : NodeSocket(name = "head", node=self),
          "tail" : NodeSocket(name = "tail", node=self),
          "length" : NodeSocket(name = "length", node=self),
          "rotation" : NodeSocket(name = "rotation", node=self),
          "location" : NodeSocket(name = "location", node=self),
          "scale" : NodeSocket(name = "scale", node=self),
        }
        self.parameters = {

          "matrix":None, 
          "matrix_local":None, 
          "matrix_basis":None, 
          "head":None, 
          "tail":None, 
          "length":None, 
          "rotation":None, 
          "location":None, 
          "scale":None, 
        }
        self.node_type = "UTILITY"

    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)

    def bExecute(self, bContext = None,):
        pass

    def __repr__(self):
        return self.signature.__repr__()

    def fill_parameters(self):
        pass#fill_parameters(self)
        
class UtilityDriverVariable:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Variable Type"   : NodeSocket(is_input = True, name = "Variable Type", node = self),
          "Property"   : NodeSocket(is_input = True, name = "Property", node = self),
          "Property Index"   : NodeSocket(is_input = True, name = "Property Index", node = self),
          "Evaluation Space"   : NodeSocket(is_input = True, name = "Evaluation Space", node = self),
          "Rotation Mode"   : NodeSocket(is_input = True, name = "Rotation Mode", node = self),
          "xForm 1"   : NodeSocket(is_input = True, name = "xForm 1", node = self),
          "xForm 2"   : NodeSocket(is_input = True, name = "xForm 2", node = self),
        }
        self.outputs = {
          "Driver Variable" : NodeSocket(name = "Driver Variable", node=self),
        }
        self.parameters = {
          "Variable Type":None, 
          "Property":None, 
          "Property Index":None, 
          "Evaluation Space":None, 
          "Rotation Mode":None, 
          "xForm 1":None, 
          "xForm 2":None,
        }
        self.node_type = "LINK" # MUST be run in Pose mode
        
    def evaluate_input(self, input_name):
        if input_name == 'Property':
            if self.inputs['Property'].is_linked:
            # get the name instead...
                trace = trace_single_line(self, input_name)
                return trace[1].name # the name of the socket
            return self.parameters["Property"]
        return evaluate_input(self, input_name)
        
    def GetxForm(self, index=1):
        trace = trace_single_line(self, "xForm 1" if index == 1 else "xForm 2")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node #this will fetch the first one, that's good!
        return None

    def bExecute(self, bContext = None,):
        prepare_parameters(self)
        #prPurple ("Executing Driver Variable Node")
        xForm1 = self.GetxForm()
        xForm2 = self.GetxForm(index=2)
        # kinda clumsy
        if xForm1 : xForm1 = xForm1.bGetObject()
        if xForm2 : xForm2 = xForm2.bGetObject()
        
        v_type = self.evaluate_input("Variable Type")
        i = self.evaluate_input("Property Index"); dVarChannel = ""
        if (i >= 0): #negative values will use the vector property.
            if self.evaluate_input("Property") == 'location':
                if   i == 0: dVarChannel = "LOC_X"
                elif i == 1: dVarChannel = "LOC_Y"
                elif i == 2: dVarChannel = "LOC_Z"
                else: raise RuntimeError("Invalid property index for %s" % self)
            if self.evaluate_input("Property") == 'rotation':
                if   i == 0: dVarChannel = "ROT_X"
                elif i == 1: dVarChannel = "ROT_Y"
                elif i == 2: dVarChannel = "ROT_Z"
                elif i == 3: dVarChannel = "ROT_W"
                else: raise RuntimeError("Invalid property index for %s" % self)
            if self.evaluate_input("Property") == 'scale':
                if   i == 0: dVarChannel = "SCALE_X"
                elif i == 1: dVarChannel = "SCALE_Y"
                elif i == 2: dVarChannel = "SCALE_Z"
                elif i == 3: dVarChannel = "SCALE_AVG"
                else: raise RuntimeError("Invalid property index for %s" % self)
        if dVarChannel: v_type = "TRANSFORMS"
        
        my_var = {
            "owner"         : xForm1, # will be filled in by Driver
            "prop"          : self.evaluate_input("Property"), # will be filled in by Driver
            "type"          : v_type,
            "space"         : self.evaluate_input("Evaluation Space"),
            "rotation_mode" : self.evaluate_input("Rotation Mode"),
            "xForm 1"       : self.GetxForm(index = 1),
            "xForm 2"       : self.GetxForm(index = 2),
            "channel"       : dVarChannel,}
        
        # Push parameter to downstream connected node.connected:
        if (out := self.outputs["Driver Variable"]).is_linked:
            self.parameters[out.name] = my_var
            for link in out.links:
                link.to_node.parameters[link.to_socket] = my_var
            

    def __repr__(self):
        return self.signature.__repr__()

    def fill_parameters(self):
        fill_parameters(self)

class UtilityFCurve:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {}
        self.outputs = {
          "fCurve" : NodeSocket(name = "fCurve", node=self),
        }
        self.parameters = {
          "fCurve":None, 
        }
        self.node_type = "UTILITY"
        setup_custom_props(self)

    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)

    def bExecute(self, bContext = None,):
        prepare_parameters(self)
        from .utilities import get_node_prototype
        np = get_node_prototype(self.signature, self.base_tree)
        keys = []
        #['amplitude', 'back', 'bl_rna', 'co', 'co_ui', 'easing', 'handle_left', 'handle_left_type', 'handle_right', 'handle_right_type',
        # 'interpolation', 'period', 'rna_type', 'select_control_point', 'select_left_handle', 'select_right_handle', 'type']

        if np.use_kf_nodes:
            pass # for now
        else:
            fc_ob = np.fake_fcurve_ob
            fc = fc_ob.animation_data.action.fcurves[0]
            for k in fc.keyframe_points:
                key = {}
                for prop in dir(k):
                    if ("__" in prop) or ("bl_" in prop): continue
                    #it's __name__ or bl_rna or something
                    key[prop] = getattr(k, prop)
                keys.append(key)
        
        # Push parameter to downstream connected node.connected:
        # TODO: find out if this is necesary, even
        if (out := self.outputs["fCurve"]).is_linked:
            self.parameters[out.name] = keys
            for link in out.links:
                link.to_node.parameters[link.to_socket] = keys
                

    def __repr__(self):
        return self.signature.__repr__()

    def fill_parameters(self):
        fill_parameters(self)

class UtilityDriver:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Driver Type"   : NodeSocket(is_input = True, name = "Driver Type", node = self),
          "Expression"   : NodeSocket(is_input = True, name = "Expression", node = self),
          "fCurve"   : NodeSocket(is_input = True, name = "fCurve", node = self),
        }
        self.outputs = {
          "Driver" : NodeSocket(name = "Driver", node=self),
        }
        from .drivers import MantisDriver
        self.parameters = {
          "Driver Type":None, 
          "Expression":None, 
          "fCurve":None,
          "Driver":MantisDriver(), 
        }
        self.node_type = "DRIVER" # MUST be run in Pose mode
        setup_custom_props(self)

    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)

    def bExecute(self, bContext = None,):
        prepare_parameters(self)
        from .drivers import MantisDriver
        #prPurple("Executing Driver Node")
        my_vars = []
        
        for inp in list(self.inputs.keys() )[3:]:
            if (new_var := self.evaluate_input(inp)):
                new_var["name"] = inp
                my_vars.append(new_var)
            else:
                raise RuntimeError("Failed to initialize Driver variable")
        my_driver ={ "owner"      :  None,
                     "prop"       :  None, # will be filled out in the node that uses the driver
                     "expression" :  self.evaluate_input("Expression"),
                     "ind"        :  -1, # same here
                     "type"       :  self.evaluate_input("Driver Type"),
                     "vars"       :  my_vars,
                     "keys"       :  self.evaluate_input("fCurve"), }
        
        my_driver = MantisDriver(my_driver)
        
        self.parameters["Driver"].update(my_driver)
        print("Initializing driver %s " % (wrapPurple(self.__repr__())) )

    def __repr__(self):
        return self.signature.__repr__()

    def fill_parameters(self):
        fill_parameters(self)

class UtilitySwitch:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "xForm"   : NodeSocket(is_input = True, name = "xForm", node = self),
          "Parameter"   : NodeSocket(is_input = True, name = "Parameter", node = self),
          "Parameter Index"   : NodeSocket(is_input = True, name = "Parameter Index", node = self),
          "Invert Switch" : NodeSocket(is_input = True, name = "Invert Switch", node = self),
        }
        self.outputs = {
          "Driver" : NodeSocket(name = "Driver", node=self),
        }
        from .drivers import MantisDriver
        self.parameters = {
          "xForm":None, 
          "Parameter":None,
          "Parameter Index":None, 
          "Invert Switch":None,
          "Driver":MantisDriver(), # empty for now
        }
        self.node_type = "DRIVER" # MUST be run in Pose mode

    def evaluate_input(self, input_name):
        if input_name == 'Parameter':
            if self.inputs['Parameter'].is_connected:
                trace = trace_single_line(self, input_name)
                return trace[1].name # the name of the socket
            return self.parameters["Parameter"]
        return evaluate_input(self, input_name)

    def GetxForm(self,):
        trace = trace_single_line(self, "xForm" )
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node #this will fetch the first one, that's good!
        return None

    def bExecute(self, bContext = None,):
        #prepare_parameters(self)
        #prPurple ("Executing Switch Node")
        xForm = self.GetxForm()
        if xForm : xForm = xForm.bGetObject() 
        if not xForm:
            raise RuntimeError("Could not evaluate xForm for %s" % self)
        from .drivers import MantisDriver
        my_driver ={ "owner" : None,
                     "prop"  : None, # will be filled out in the node that uses the driver 
                     "ind"   : -1, # same here
                     "type"  : "SCRIPTED",
                     "vars"  : [ { "owner" : xForm,
                                   "prop"  : self.evaluate_input("Parameter"),
                                   "name"  : "a",
                                   "type"  : "SINGLE_PROP", } ],
                     "keys"  : [ { "co":(0,0),
                                   "interpolation": "LINEAR",
                                   "type":"KEYFRAME",}, #display type
                                 { "co":(1,1),
                                   "interpolation": "LINEAR",
                                   "type":"KEYFRAME",},], }
        my_driver   ["expression"] = "a"
        
        my_driver = MantisDriver(my_driver)
        # this makes it so I can check for type later!
        
        if self.evaluate_input("Invert Switch") == True:
            my_driver   ["expression"] = "1 - a"
        
        # this way, regardless of what order things are handled, the
        #  driver is sent to the next node.
        # In the case of some drivers, the parameter may be sent out
        #  before it's filled in (because there is a circular dependency)
        # I want to support this behaviour because Blender supports it,
        #  but I also do not want to support it because it makes things
        #  more complex and IMO it's bad practice.
        # We do not make a copy. We update the driver, so that
        #  the same instance is filled out. 
        self.parameters["Driver"].update(my_driver)
        print("Initializing driver %s " % (wrapPurple(self.__repr__())) )

    def __repr__(self):
        return self.signature.__repr__()

    def fill_parameters(self):
        fill_parameters(self)
        
class UtilityCombineThreeBool:
    '''A node for combining three booleans into a boolean three-tuple'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "X"   : NodeSocket(is_input = True, name = "X", node = self),
          "Y"   : NodeSocket(is_input = True, name = "Y", node = self),
          "Z"   : NodeSocket(is_input = True, name = "Z", node = self),
        }
        self.outputs = {
          "Three-Bool" : NodeSocket(name = "Three-Bool", node=self),
        }
        self.parameters = {
          "X":None,
          "Y":None,
          "Z":None, }
        self.node_type = "UTILITY"

    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)

    def bExecute(self, bContext = None,):
        #prPurple("Executing CombineThreeBool Node")
        #prepare_parameters(self)
        self.parameters["Three-Bool"] = (
          self.evaluate_input("X"),
          self.evaluate_input("Y"),
          self.evaluate_input("Z"), )
        # DO:
        # figure out how to get the driver at execute-time
        #  because Blender allows circular dependencies in drivers
        #  (sort of), I need to adopt a more convoluted way of doing
        #  things here or elsewhere.

    def __repr__(self):
        return self.signature.__repr__()

    def fill_parameters(self):
        fill_parameters(self)

# Note this is a copy of the above. This needs to be de-duplicated into
  # a simpler CombineVector node_container.
  # TODO
class UtilityCombineVector:
    '''A node for combining three floats into a vector'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "X"   : NodeSocket(is_input = True, name = "X", node = self),
          "Y"   : NodeSocket(is_input = True, name = "Y", node = self),
          "Z"   : NodeSocket(is_input = True, name = "Z", node = self),
        }
        self.outputs = {
          "Vector" : NodeSocket(name = "Vector", node=self),
        }
        self.parameters = {
          "X":None,
          "Y":None,
          "Z":None, }
        self.node_type = "UTILITY"

    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)

    def bExecute(self, bContext = None,):
        #prPurple("Executing CombineVector Node")
        prepare_parameters(self)
        self.parameters["Vector"] = (
          self.evaluate_input("X"),
          self.evaluate_input("Y"),
          self.evaluate_input("Z"), )

    def __repr__(self):
        return self.signature.__repr__()

    def fill_parameters(self):
        fill_parameters(self)

class UtilityCatStrings:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "String_1"   : NodeSocket(is_input = True, name = "String_1", node = self),
          "String_2"   : NodeSocket(is_input = True, name = "String_2", node = self),
        }
        self.outputs = {
          "OutputString" : NodeSocket(name = "OutputString", node=self),
        }
        self.parameters = {
          "String_1":None, 
          "String_2":None,
        }
        self.node_type = "UTILITY"

    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)

    def bExecute(self, bContext = None,):
        self.parameters["OutputString"] = self.evaluate_input("String_1")+self.evaluate_input("String_2")

    def __repr__(self):
        return self.signature.__repr__()

    def fill_parameters(self):
        fill_parameters(self)

class InputLayerMask:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
        }
        self.outputs = {
          "Layer Mask" : NodeSocket(is_input = True, name = "Layer Mask", node = self),
        }
        self.parameters = {

          "Layer Mask":None, 
        }
        self.node_type = "UTILITY"

    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)

    def bExecute(self, bContext = None,):
        pass

    def __repr__(self):
        return self.signature.__repr__()

    def fill_parameters(self):
        fill_parameters(self)

# class InputGeometry:
    # '''A node representing an armature object'''

    # def __init__(self, signature, base_tree):
        # self.base_tree=base_tree
        # self.executed = False
        # self.signature = signature
        # self.inputs = {
          # "Geometry Name"   : NodeSocket(is_input = True, to_socket = "Geometry Name", to_node = self),
        # }
        # self.outputs = {
          # "Geometry" : NodeSocket(from_socket = "Geometry", from_node=self),
        # }
        # self.parameters = {

          # "Geometry Name":None, 
          # "Geometry":None, 
        # }
        # self.node_type = "UTILITY"

    # def evaluate_input(self, input_name):
        # return evaluate_input(self, input_name)

    # def bExecute(self, bContext = None,):
        # pass

    # def __repr__(self):
        # return self.signature.__repr__()

    # def fill_parameters(self, node_prototype):
        # fill_parameters(self, node_prototype)

class InputExistingGeometryObject:
    '''A node representing an existing object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Name"   : NodeSocket(is_input = True, name = "Name", node = self),
        }
        self.outputs = {
          "Object" : NodeSocket(is_input = False, name = "Object", node=self),
        }
        self.parameters = {
          "Name":None, 
          "Object":None, 
        }
        self.node_type = "UTILITY"
        
    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)

    def bGetObject(self):
        from bpy import data
        return data.objects.get( self.evaluate_input("Name") )
        
    def bExecute(self, bContext = None,):
        pass

        # DO: make this data, of course
        # try curve and then mesh
        # probably should print a warning on the node if it is ambiguous

    def __repr__(self):
        return self.signature.__repr__()

    def fill_parameters(self):
        fill_parameters(self)

class InputExistingGeometryData:
    '''A node representing existing object data'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Name"   : NodeSocket(is_input = True, name = "Name", node = self),
        }
        self.outputs = {
          "Geometry" : NodeSocket(is_input = False, name = "Geometry", node=self),
        }
        self.parameters = {

          "Name":None, 
          "Geometry":None, 
        }
        self.node_type = "UTILITY"

    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)

    def bGetObject(self):
        from bpy import data
        # first try Curve, then try Mesh
        bObject = data.curves.get(self.evaluate_input("Name"))
        if not bObject:
            bObject = data.meshes.get(self.evaluate_input("Name"))
        return bObject
        
    def bExecute(self, bContext = None,):
        pass

    def __repr__(self):
        return self.signature.__repr__()

    def fill_parameters(self):
        fill_parameters(self)

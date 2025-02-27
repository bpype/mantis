from .node_container_common import *

# The fact that I need this means that some of these classes should
#  probably be moved to link_containers.py
from .xForm_containers import xFormArmature, xFormBone

from math import pi, tau

def TellClasses():
    return [
             # utility
             InputFloat,
             InputIntNode,
             InputVector,
             InputBoolean,
             InputBooleanThreeTuple,
             InputRotationOrder,
             InputTransformSpace,
             InputString,
             InputMatrix,
             InputExistingGeometryObject,
             InputExistingGeometryData,
             UtilityGeometryOfXForm,
             UtilityNameOfXForm,
             UtilityPointFromCurve,
             UtilityMatrixFromCurve,
             UtilityMatricesFromCurve,
             UtilityMetaRig,
             UtilityBoneProperties,
             UtilityDriverVariable,
             UtilityDriver,
             UtilityFCurve,
             UtilityKeyframe,
             UtilitySwitch,
             UtilityCombineThreeBool,
             UtilityCombineVector,
             UtilitySeparateVector,
             UtilityCatStrings,
             UtilityGetBoneLength,
             UtilityPointFromBoneMatrix,
             UtilitySetBoneLength,
             UtilityMatrixSetLocation,
             UtilityMatrixGetLocation,
             UtilityMatrixFromXForm,
             UtilityAxesFromMatrix,
             UtilityBoneMatrixHeadTailFlip,
             UtilityMatrixTransform,
             UtilityTransformationMatrix,
             UtilityIntToString,
             UtilityArrayGet,
             UtilitySetBoneMatrixTail,
             # Control flow switches
             UtilityCompare,
             UtilityChoose,
             # useful NoOp:
             UtilityPrint,
            ]


def matrix_from_head_tail(head, tail):
    from mathutils import Vector, Quaternion, Matrix
    rotation = Vector((0,1,0)).rotation_difference((tail-head).normalized()).to_matrix()
    m= Matrix.LocRotScale(head, rotation, None)
    m[3][3] = (tail-head).length
    return m

#*#-------------------------------#++#-------------------------------#*#
# U T I L I T Y   N O D E S
#*#-------------------------------#++#-------------------------------#*#

class InputFloat:
    '''A node representing float input'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"Float Input" : NodeSocket(name = "Float Input", node=self) }
        self.parameters = {"Float Input":None, "Mute":None}
        self.node_type = 'UTILITY'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True
        
    def evaluate_input(self, input_name):
        return self.parameters["Float Input"]

class InputIntNode:
    '''A node representing integer input'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"Integer" : NodeSocket(name = "Integer", node=self) }
        self.parameters = {"Integer":None, "Mute":None}
        self.node_type = 'UTILITY'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True
        
    def evaluate_input(self, input_name):
        return self.parameters["Integer"]
    
class InputVector:
    '''A node representing vector input'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"" : NodeSocket(name = '', node=self) }
        self.parameters = {'':None, "Mute":None}
        self.node_type = 'UTILITY'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True
        
    def evaluate_input(self, input_name):
        return self.parameters[""]
    

class InputBoolean:
    '''A node representing boolean input'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"" : NodeSocket(name = '', node=self) }
        self.parameters = {'':None, "Mute":None}
        self.node_type = 'UTILITY'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True
        
    def evaluate_input(self, input_name):
        return self.parameters[""]

class InputBooleanThreeTuple:
    '''A node representing a tuple of three booleans'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"" : NodeSocket(name = '', node=self) }
        self.parameters = {'':None, "Mute":None}
        self.node_type = 'UTILITY'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True
        
    def evaluate_input(self, input_name):
        return self.parameters[""]
    
class InputRotationOrder:
    '''A node representing string input for rotation order'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"" : NodeSocket(name = '', node=self) }
        self.parameters = {'':None, "Mute":None}
        self.node_type = 'UTILITY'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True
        
    def evaluate_input(self, input_name):
        return self.parameters[""]
    

class InputTransformSpace:
    '''A node representing string input for transform space'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"" : NodeSocket(name = '', node=self) }
        self.parameters = {'':None, "Mute":None}
        self.node_type = 'UTILITY'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True
        
    def evaluate_input(self, input_name):
        return self.parameters[""]
    
class InputString:
    '''A node representing string input'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"" : NodeSocket(name = '', node=self) }
        self.parameters = {'':None, "Mute":None}
        self.node_type = 'UTILITY'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True
        
    def evaluate_input(self, input_name):
        return self.parameters[""]
    
class InputMatrix:
    '''A node representing axis-angle quaternion input'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs  = {"Matrix" : NodeSocket(name = 'Matrix', node=self) }
        self.parameters = {'Matrix':None, "Mute":None}
        self.node_type = 'UTILITY'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True
        #
        from mathutils import Matrix
        from .utilities import get_node_prototype
        node_prototype = get_node_prototype(self.signature, self.base_tree)
        
        matrix = ( node_prototype.first_row[ 0], node_prototype.first_row[ 1], node_prototype.first_row[ 2], node_prototype.first_row[ 3],
                   node_prototype.second_row[0], node_prototype.second_row[1], node_prototype.second_row[2], node_prototype.second_row[3],
                   node_prototype.third_row[ 0], node_prototype.third_row[ 1], node_prototype.third_row[ 2], node_prototype.third_row[ 3],
                   node_prototype.fourth_row[0], node_prototype.fourth_row[1], node_prototype.fourth_row[2], node_prototype.fourth_row[3], )
        self.parameters["Matrix"] = Matrix([matrix[0:4], matrix[4:8], matrix[8:12], matrix[12:16]])
        
    def evaluate_input(self, input_name):
        return self.parameters["Matrix"]
    
    def fill_parameters(self):
        return

class UtilityMatrixFromCurve:
    '''Get a matrix from a curve'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Curve"            : NodeSocket(is_input = True, name = "Curve", node=self),
          "Total Divisions"  : NodeSocket(is_input = True, name = "Total Divisions", node=self),
          "Matrix Index"     : NodeSocket(is_input = True, name = "Matrix Index", node=self),
        }
        self.outputs = {
          "Matrix" : NodeSocket(name = "Matrix", node=self),
        }
        self.parameters = {
          "Curve"            : None,
          "Total Divisions"  : None,
          "Matrix Index"     : None,
          "Matrix"           : None,
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies, self.dependencies = [], []
        self.prepared, self.executed = False, False

    def bPrepare(self, bContext = None,):
        from mathutils import Matrix
        import bpy
        m = Matrix.Identity(4)
        curve = bpy.data.objects.get(self.evaluate_input("Curve"))
        if not curve:
            prRed(f"No curve found for {self}. Using an Identity matrix instead.")
            m[3][3] = 1.0
        else:
            from .utilities import mesh_from_curve, data_from_ribbon_mesh
            if not bContext:
                # TODO find out if this is bad or a HACK or if it is OK
                bContext = bpy.context
            # IMPORTANT TODO: I need to be able to reuse this m
            # First, try to get the one we made before
            m_name = curve.name+'.'+self.base_tree.execution_id
            if not (m := bpy.data.meshes.get(m_name)):
                m = mesh_from_curve(curve, bContext)
                m.name = m_name
            #
            num_divisions = self.evaluate_input("Total Divisions")
            m_index = self.evaluate_input("Matrix Index")
            factors = [1/num_divisions*m_index, 1/num_divisions*(m_index+1)]
            data = data_from_ribbon_mesh(m, [factors], curve.matrix_world)
            # print(data)
            # this is in world space... let's just convert it back
            m = matrix_from_head_tail(data[0][0][0], data[0][0][1])
            m.translation -= curve.location
            # TODO HACK TODO
            # all the nodes should work in world-space, and it should be the responsibility
            # of the xForm node to convert!

        self.parameters["Matrix"] = m
        self.prepared = True
        self.executed = True
    
    def bFinalize(self, bContext=None):
        import bpy
        curve_name = self.evaluate_input("Curve")
        curve = bpy.data.objects.get(curve_name)
        m_name = curve.name+'.'+self.base_tree.execution_id
        if (mesh := bpy.data.meshes.get(m_name)):
            bpy.data.meshes.remove(mesh)

    def fill_parameters(self):
        fill_parameters(self)


class UtilityPointFromCurve:
    '''Get a point from a curve'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Curve"             : NodeSocket(is_input = True, name = "Curve", node=self),
          "Factor"            : NodeSocket(is_input = True, name = "Factor", node=self),
        }
        self.outputs = {
          "Point" : NodeSocket(name = "Point", node=self),
        }
        self.parameters = {
          "Curve"       : None,
          "Factor"      : None,
          "Point"       : None,
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies, self.dependencies = [], []
        self.prepared, self.executed = False, False

    def bPrepare(self, bContext = None,):
        from mathutils import Matrix
        import bpy
        curve = bpy.data.objects.get(self.evaluate_input("Curve"))
        if not curve:
            raise RuntimeError(f"No curve found for {self}.")
        else:
            from .utilities import mesh_from_curve, data_from_ribbon_mesh
            if not bContext:
                # TODO find out if this is bad or a HACK or if it is OK
                bContext = bpy.context
            # IMPORTANT TODO: I need to be able to reuse this m
            # First, try to get the one we made before
            m_name = curve.name+'.'+self.base_tree.execution_id
            if not (m := bpy.data.meshes.get(m_name)):
                m = mesh_from_curve(curve, bContext)
                m.name = m_name
            #
            num_divisions = 1
            factors = [self.evaluate_input("Factor")]
            data = data_from_ribbon_mesh(m, [factors], curve.matrix_world)
            p = data[0][0][0] - curve.location
        self.parameters["Point"] = p
        self.prepared, self.executed = True, True
    
    def bFinalize(self, bContext=None):
        import bpy
        curve_name = self.evaluate_input("Curve")
        curve = bpy.data.objects.get(curve_name)
        m_name = curve.name+'.'+self.base_tree.execution_id
        if (mesh := bpy.data.meshes.get(m_name)):
            bpy.data.meshes.remove(mesh)

    def fill_parameters(self):
        fill_parameters(self)

class UtilityMatricesFromCurve:
    '''Get matrices from a curve'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Curve"            : NodeSocket(is_input = True, name = "Curve", node=self),
          "Total Divisions"  : NodeSocket(is_input = True, name = "Total Divisions", node=self),
        #   "Matrix Index"     : NodeSocket(is_input = True, name = "Matrix Index", node=self),
        }
        self.outputs = {
          "Matrices" : NodeSocket(name = "Matrices", node=self),
        }
        self.parameters = {
          "Curve"            : None,
          "Total Divisions"  : None,
        #   "Matrix Index"     : None,
          "Matrices"           : None,
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def bPrepare(self, bContext = None,):
        import time
        # start_time = time.time()
        #
        from mathutils import Matrix
        import bpy
        m = Matrix.Identity(4)
        curve_name = self.evaluate_input("Curve")
        curve = bpy.data.objects.get(curve_name)
        if not curve:
            prRed(f"No curve found for {self}. Using an Identity matrix instead.")
            m[3][3] = 1.0
        else:
            from .utilities import mesh_from_curve, data_from_ribbon_mesh
            if not bContext:
                bContext = bpy.context
            m_name = curve.name+'.'+self.base_tree.execution_id
            if not (mesh := bpy.data.meshes.get(m_name)):
                mesh = mesh_from_curve(curve, bContext)
                mesh.name = m_name
            num_divisions = self.evaluate_input("Total Divisions")
            factors = [0.0] + [(1/num_divisions*(i+1)) for i in range(num_divisions)]
            data = data_from_ribbon_mesh(mesh, [factors], curve.matrix_world)
            
            # 0 is the spline index. 0 selects points as opposed to normals or whatever.
            matrices = [matrix_from_head_tail(data[0][0][i], data[0][0][i+1]) for i in range(num_divisions)]
        

        for link in self.outputs["Matrices"].links:
            for i, m in enumerate(matrices):
                name = "Matrix"+str(i).zfill(4)
                if not (out := self.outputs.get(name)): # reuse them if there are multiple links.
                    out = self.outputs[name] = NodeSocket(name = name, node=self)
                c = out.connect(link.to_node, link.to_socket)
                # prOrange(c)
                self.parameters[name] = m
                # print (mesh)
            link.die()

        self.prepared = True
        self.executed = True
        # prGreen(f"Matrices from curves took {time.time() - start_time} seconds.")
    
    def bFinalize(self, bContext=None):
        import bpy
        curve_name = self.evaluate_input("Curve")
        curve = bpy.data.objects.get(curve_name)
        m_name = curve.name+'.'+self.base_tree.execution_id
        if (mesh := bpy.data.meshes.get(m_name)):
            prGreen(f"Freeing mesh data {m_name}...")
            bpy.data.meshes.remove(mesh)

    def fill_parameters(self):
        fill_parameters(self)

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
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def bPrepare(self, bContext = None,):
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
                    bones = [] # from the last ancestor, mult the matrices until we get to b
                    while (b): bones.append(b); b = b.parent
                    while (bones): b = bones.pop(); m = m @ b.matrix
                    m = Matrix.Translation(b.head_local) @ m.to_4x4()
                    #
                    m[3][3] = b.length # this is where I arbitrarily decided to store length
                # else:
                #     prRed("no bone for MetaRig node ", self)
        else:
            raise RuntimeError(wrapRed(f"No meta-rig input for MetaRig node {self}"))
        
        self.parameters["Matrix"] = m
        self.prepared = True
        self.executed = True

    def fill_parameters(self):
        fill_parameters(self)
        # self.parameters["Matrix"] = None # why in the


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
        #
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True

    def fill_parameters(self):
        pass#fill_parameters(self)
        
# TODO this should probably be moved to Links
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
        self.node_type = "DRIVER" # MUST be run in Pose mode
        #
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        
    def evaluate_input(self, input_name):
        if input_name == 'Property':
            if self.inputs.get('Property'):
                if self.inputs['Property'].is_linked:
                # get the name instead...
                    trace = trace_single_line(self, input_name)
                    return trace[1].name # the name of the socket
            return self.parameters["Property"]
        return evaluate_input(self, input_name)
        
    def GetxForm(self, index=1):
        trace = trace_single_line(self, "xForm 1" if index == 1 else "xForm 2")
        for node in trace[0]:
            if (node.__class__ in [xFormArmature, xFormBone]):
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
            if self.evaluate_input("Property") == 'scale_average':
                dVarChannel = "SCALE_AVG"
        if dVarChannel: v_type = "TRANSFORMS"
        
        my_var = {
            "owner"         : xForm1, # will be filled in by Driver
            "prop"          : self.evaluate_input("Property"), # will be filled in by Driver
            "type"          : v_type,
            "space"         : self.evaluate_input("Evaluation Space"),
            "rotation_mode" : self.evaluate_input("Rotation Mode"),
            "xForm 1"       : xForm1,#self.GetxForm(index = 1),
            "xForm 2"       : xForm2,#self.GetxForm(index = 2),
            "channel"       : dVarChannel,}
        
        # Push parameter to downstream connected node.connected:
        if (out := self.outputs["Driver Variable"]).is_linked:
            self.parameters[out.name] = my_var
            for link in out.links:
                link.to_node.parameters[link.to_socket] = my_var
        self.executed = True
            



class UtilityKeyframe:
    '''A node representing a keyframe for a F-Curve'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Frame"   : NodeSocket(is_input = True, name = "Frame", node = self),
          "Value"   : NodeSocket(is_input = True, name = "Value", node = self),
        }
        self.outputs = {
          "Keyframe" : NodeSocket(name = "Keyframe", node=self),
        }

        self.parameters = {
          "Frame":None, 
          "Value":None, 
          "Keyframe":{}, # for some reason I have to initialize this and then use the dict... why? TODO find out
        }
        self.node_type = "DRIVER" # MUST be run in Pose mode
        setup_custom_props(self)
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def bPrepare(self, bContext = None,):
        key = self.parameters["Keyframe"]
        from mathutils import Vector
        key["co"]= Vector( (self.evaluate_input("Frame"), self.evaluate_input("Value"),))
        key["type"]="GENERATED"
        key["interpolation"] = "LINEAR"
        # eventually this will have the right data, TODO
        # self.parameters["Keyframe"] = key
        self.prepared = True
        self.executed = True


class UtilityFCurve:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
            "Extrapolation Mode" : NodeSocket(is_input = True, name = "Extrapolation Mode", node = self),
        }
        self.outputs = {
          "fCurve" : NodeSocket(name = "fCurve", node=self),
        }
        self.parameters = {
          "Extrapolation Mode":None,
          "fCurve":None, 
        }
        self.node_type = "UTILITY"
        setup_custom_props(self)
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)

    def bExecute(self, bContext = None,):
        prepare_parameters(self)
        from .utilities import get_node_prototype
        np = get_node_prototype(self.signature, self.base_tree)
        extrap_mode = self.evaluate_input("Extrapolation Mode")
        keys = [] # ugly but whatever
        #['amplitude', 'back', 'bl_rna', 'co', 'co_ui', 'easing', 'handle_left', 'handle_left_type', 'handle_right', 'handle_right_type',
        # 'interpolation', 'period', 'rna_type', 'select_control_point', 'select_left_handle', 'select_right_handle', 'type']
        for k in self.inputs.keys():
            if k == 'Extrapolation Mode' : continue
            # print (self.inputs[k])
            if (key := self.evaluate_input(k)) is None:
                prOrange(f"WARN: No keyframe connected to {self}:{k}. Skipping Link.")
            else:
                keys.append(key)
        if len(keys) <1:
            prOrange(f"WARN: no keys in fCurve {self}.")
        keys.append(extrap_mode)
        print (keys)
        self.parameters["fCurve"] = keys
        self.prepared = True
        self.executed = True
#TODO make the fCurve data a data class instead of a dict 

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
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True

    def bExecute(self, bContext = None,):
        prepare_parameters(self)
        from .drivers import MantisDriver
        #prPurple("Executing Driver Node")
        my_vars = []
        keys = self.evaluate_input("fCurve")
        if len(keys) <2:
            prWhite(f"INFO: no fCurve connected to {self}; using default fCurve.")
            from mathutils import Vector
            keys = [
                {"co":Vector( (0, 0,)), "type":"GENERATED", "interpolation":"LINEAR" },
                {"co":Vector( (1, 1,)), "type":"GENERATED", "interpolation":"LINEAR" },
                "CONSTANT",]
        for inp in list(self.inputs.keys() )[3:]:
            if (new_var := self.evaluate_input(inp)):
                new_var["name"] = inp
                my_vars.append(new_var)
            else:
                raise RuntimeError(f"Failed to initialize Driver variable for {self}")
        my_driver ={ "owner"         :  None,
                     "prop"          :  None, # will be filled out in the node that uses the driver
                     "expression"    :  self.evaluate_input("Expression"),
                     "ind"           :  -1, # same here
                     "type"          :  self.evaluate_input("Driver Type"),
                     "vars"          :  my_vars,
                     "keys"          :  keys[:-1],
                     "extrapolation" :  keys[-1] }
        
        my_driver = MantisDriver(my_driver)
        
        self.parameters["Driver"].update(my_driver)
        print("Initializing driver %s " % (wrapPurple(self.__repr__())) )
        self.executed = True


class UtilitySwitch:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
        #   "xForm"   : NodeSocket(is_input = True, name = "xForm", node = self),
          "Parameter"   : NodeSocket(is_input = True, name = "Parameter", node = self),
          "Parameter Index"   : NodeSocket(is_input = True, name = "Parameter Index", node = self),
          "Invert Switch" : NodeSocket(is_input = True, name = "Invert Switch", node = self),
        }
        self.outputs = {
          "Driver" : NodeSocket(name = "Driver", node=self),
        }
        from .drivers import MantisDriver
        self.parameters = {
        #   "xForm":None, 
          "Parameter":None,
          "Parameter Index":None, 
          "Invert Switch":None,
          "Driver":MantisDriver(), # empty for now
        }
        self.node_type = "DRIVER" # MUST be run in Pose mode
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False

    def evaluate_input(self, input_name):
        if input_name == 'Parameter':
            if self.inputs['Parameter'].is_connected:
                trace = trace_single_line(self, input_name)
                return trace[1].name # the name of the socket
            return self.parameters["Parameter"]
        return evaluate_input(self, input_name)

    def GetxForm(self,):
        trace = trace_single_line(self, "Parameter" )
        for node in trace[0]:
            if (node.__class__ in [xFormArmature, xFormBone]):
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
                                   "type":"KEYFRAME",},],
                      "extrapolation": 'CONSTANT', }
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
        self.executed = True



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
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def bPrepare(self, bContext = None,):
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
        self.prepared = True
        self.executed = True


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
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def bPrepare(self, bContext = None,):
        #prPurple("Executing CombineVector Node")
        prepare_parameters(self)
        self.parameters["Vector"] = (
          self.evaluate_input("X"),
          self.evaluate_input("Y"),
          self.evaluate_input("Z"), )
        self.prepared = True
        self.executed = True
  

  # TODO
class UtilitySeparateVector:
    '''A node for separating a vector into three floats'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Vector" : NodeSocket(is_input = True, name = "Vector", node=self),
        }
        self.outputs = {
          "X"   : NodeSocket(name = "X", node = self),
          "Y"   : NodeSocket(name = "Y", node = self),
          "Z"   : NodeSocket(name = "Z", node = self),
        }
        self.parameters = {
          "X"   : None,
          "Y"   : None,
          "Z"   : None, }
        self.node_type = "UTILITY"
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies, self.dependencies = [], []
        self.prepared, self.executed = False, False

    def bPrepare(self, bContext = None,):
        # prepare_parameters(self)
        self.parameters["X"] = self.evaluate_input("Vector")[0]
        self.parameters["Y"] = self.evaluate_input("Vector")[1]
        self.parameters["Z"] = self.evaluate_input("Vector")[2]
        self.prepared = True
        self.executed = True

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
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False
    
    def bPrepare(self, bContext = None,):
        self.parameters["OutputString"] = self.evaluate_input("String_1")+self.evaluate_input("String_2")
        self.prepared = True
        self.executed = True

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
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True


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
        self.node_type = "XFORM"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False
    
    def bPrepare(self, bContext=None):
        from bpy import data
        name = self.evaluate_input("Name")
        if name:
          self.bObject = data.objects.get( name  )
        else:
          self.bObject = None
        if self is None and (name := self.evaluate_input("Name")):
          prRed(f"No object found with name {name} in {self}")
        self.prepared = True; self.executed = True
    def bGetObject(self, mode=''):
        return self.bObject

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
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True
    # mode for interface consistency
    def bGetObject(self, mode=''):
        from bpy import data
        # first try Curve, then try Mesh
        bObject = data.curves.get(self.evaluate_input("Name"))
        if not bObject:
            bObject = data.meshes.get(self.evaluate_input("Name"))
        if bObject is None:
            raise RuntimeError(f"Could not find a mesh or curve datablock named \"{self.evaluate_input('Name')}\" for node {self}")
        return bObject

class UtilityGeometryOfXForm:
    '''A node representing existing object data'''
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "xForm"   : NodeSocket(is_input = True, name = "xForm", node = self),
        }
        self.outputs = {
          "Geometry" : NodeSocket(is_input = False, name = "Geometry", node=self),
        }
        self.parameters = {

          "xForm":None, 
          "Geometry":None, 
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies,self.dependencies = [], []
        self.prepared, self.executed = True, True

    # mode for interface consistency
    def bGetObject(self, mode=''):
        if not (self.inputs.get('xForm') and self.inputs['xForm'].links):
            prOrange(f"WARN: Cannot retrieve data from {self}, there is no xForm node connected.")
            return None
        xf = self.inputs["xForm"].links[0].from_node
        if xf.node_type == 'XFORM':
            xf_ob = xf.bGetObject()
            if xf_ob.type in ['MESH', 'CURVE']:
                return xf_ob.data
        prOrange(f"WARN: Cannot retrieve data from {self}, the connected xForm is not a mesh or curve.")
        return None


class UtilityNameOfXForm:
    '''A node representing existing object data'''
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "xForm"   : NodeSocket(is_input = True, name = "xForm", node = self),
        }
        self.outputs = {
          "Name" : NodeSocket(is_input = False, name = "Name", node=self),
        }
        self.parameters = {

          "xForm":None, 
          "Name":'', 
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies,self.dependencies = [], []
        self.prepared, self.executed = False, False

    # mode for interface consistency
    def bPrepare(self, bContext = None,):
        if not (self.inputs.get('xForm') and self.inputs['xForm'].links):
            prOrange(f"WARN: Cannot retrieve data from {self}, there is no xForm node connected.")
            return ''
        xf = self.inputs["xForm"].links[0].from_node
        self.parameters["Name"] = xf.evaluate_input('Name')
        self.prepared, self.executed = True, True

class UtilityGetBoneLength:
    '''A node to get the length of a bone matrix'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Bone Matrix"   : NodeSocket(is_input = True, name = "Bone Matrix", node = self),
        }
        self.outputs = {
          "Bone Length"   : NodeSocket(name = "Bone Length", node = self),
        }
        self.parameters = {

          "Bone Length":None, 
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def bPrepare(self, bContext = None,):
        # print (self.inputs['Bone Matrix'].links)
        if l := self.evaluate_input("Bone Matrix"):
            self.parameters["Bone Length"] = l[3][3]
        self.prepared = True
        self.executed = True

class UtilityPointFromBoneMatrix:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Bone Matrix"   : NodeSocket(is_input = True, name = "Bone Matrix", node = self),
          "Head/Tail"     : NodeSocket(is_input = True, name = "Head/Tail", node = self),
        }
        self.outputs = {
          "Point"     : NodeSocket(name = "Point", node = self),
        }
        self.parameters = {

          "Bone Matrix":None, 
          "Head/Tail":None,
          "Point":None,
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    # TODO: find out why this is sometimes not ready at bPrepare phase
    def bPrepare(self, bContext = None,):
        from mathutils import Vector
        matrix = self.evaluate_input("Bone Matrix")
        head, rotation, _scale = matrix.copy().decompose()
        tail = head.copy() + (rotation @ Vector((0,1,0)))*matrix[3][3]
        self.parameters["Point"] = head.lerp(tail, self.evaluate_input("Head/Tail"))
        self.prepared = True
        self.executed = True


class UtilitySetBoneLength:
    '''Sets the length of a Bone's matrix'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Bone Matrix"   : NodeSocket(is_input = True, name = "Bone Matrix", node = self),
          "Length"        : NodeSocket(is_input = True, name = "Length", node = self),
        }
        self.outputs = {
          "Bone Matrix"   : NodeSocket(name = "Bone Matrix", node = self),
        }
        self.parameters = {

          "Bone Matrix":None, 
          "Length":None,
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False
    
    def bPrepare(self, bContext = None,):
        from mathutils import Vector
        if matrix := self.evaluate_input("Bone Matrix"):
            matrix = matrix.copy()
            # print (self.inputs["Length"].links)
            matrix[3][3] = self.evaluate_input("Length")
            self.parameters["Length"] = self.evaluate_input("Length")
            self.parameters["Bone Matrix"] = matrix
        self.prepared = True
        self.executed = True

  
class UtilityMatrixSetLocation:
    '''Sets the location of a matrix'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Matrix"        : NodeSocket(is_input = True, name = "Matrix", node = self),
          "Location"      : NodeSocket(is_input = True, name = "Location", node = self),
        }
        self.outputs = {
          "Matrix"        : NodeSocket(name = "Matrix", node = self),
        }
        self.parameters = {

          "Matrix"   : None, 
          "Location" : None,
        }
        self.node_type = "UTILITY"
        self.connections, self.hierarchy_connections = [], []
        self.dependencies, self.hierarchy_dependencies = [], []
        self.prepared, self.executed = False,False
    
    def bPrepare(self, bContext = None,):
        from mathutils import Vector
        if matrix := self.evaluate_input("Matrix"):
            matrix = matrix.copy()
            # print (self.inputs["Length"].links)
            loc = self.evaluate_input("Location")
            matrix[0][3] = loc[0]; matrix[1][3] = loc[1]; matrix[2][3] = loc[2]
            self.parameters["Matrix"] = matrix
        self.prepared = True
        self.executed = True

class UtilityMatrixGetLocation:
    '''Gets the location of a matrix'''
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
          "Matrix"        : NodeSocket(is_input = True, name = "Matrix", node = self),
        }
        self.outputs = {
          "Location"      : NodeSocket(name = "Location", node = self),
        }
        self.parameters = {

          "Matrix"   : None, 
          "Location" : None,
        }
        self.node_type = "UTILITY"
        self.connections, self.hierarchy_connections = [], []
        self.dependencies, self.hierarchy_dependencies = [], []
        self.prepared, self.executed = False,False
    
    def bPrepare(self, bContext = None,):
        from mathutils import Vector
        if matrix := self.evaluate_input("Matrix"):
            self.parameters["Location"] = matrix.to_translation()
        self.prepared = True; self.executed = True


class UtilityMatrixFromXForm:
    """Returns the matrix of the given xForm node."""
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
          "xForm"        : NodeSocket(is_input = True, name = "xForm", node = self),
        }
        self.outputs = {
          "Matrix"      : NodeSocket(name = "Matrix", node = self),
        }
        self.parameters = {
          "Matrix"   : None,
        }
        self.node_type = "UTILITY"
        self.connections, self.hierarchy_connections = [], []
        self.dependencies, self.hierarchy_dependencies = [], []
        self.prepared, self.executed = False,False
    
    def GetxForm(self):
        trace = trace_single_line(self, "xForm")
        for node in trace[0]:
            if (node.node_type == 'XFORM'):
                return node
        raise GraphError("%s is not connected to an xForm" % self)
        
    def bPrepare(self, bContext = None,):
        from mathutils import Vector, Matrix
        self.parameters["Matrix"] = Matrix.Identity(4)
        if matrix := self.GetxForm().parameters.get("Matrix"):
            self.parameters["Matrix"] = matrix.copy()
        elif hasattr(self.GetxForm().bObject, "matrix"):
            self.parameters["Matrix"] = self.GetxForm().bObject.matrix.copy()
        elif hasattr(self.GetxForm().bObject, "matrix_world"):
            self.parameters["Matrix"] = self.GetxForm().bObject.matrix_world.copy()
        else:
          prRed(f"Could not find matrix for {self} - check if the referenced object exists.")
        self.prepared = True; self.executed = True


class UtilityAxesFromMatrix:
    """Returns the axes of the given matrix."""
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
          "Matrix"        : NodeSocket(is_input = True, name = "Matrix", node = self),
        }
        self.outputs = {
          "X Axis"      : NodeSocket(name = "X Axis", node = self),
          "Y Axis"      : NodeSocket(name = "Y Axis", node = self),
          "Z Axis"      : NodeSocket(name = "Z Axis", node = self),
        }
        self.parameters = {
          "Matrix"   : None,
          "X Axis"   : None,
          "Y Axis"   : None,
          "Z Axis"   : None,
        }
        self.node_type = "UTILITY"
        self.connections, self.hierarchy_connections = [], []
        self.dependencies, self.hierarchy_dependencies = [], []
        self.prepared, self.executed = False,False
        
    def bPrepare(self, bContext = None,):
        from mathutils import Vector
        if matrix := self.evaluate_input("Matrix"):
            matrix= matrix.copy().to_3x3()
            self.parameters['X Axis'] = matrix @ Vector((1,0,0))
            self.parameters['Y Axis'] = matrix @ Vector((0,1,0))
            self.parameters['Z Axis'] = matrix @ Vector((0,0,1))
        self.prepared = True; self.executed = True


class UtilityBoneMatrixHeadTailFlip:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Bone Matrix"   : NodeSocket(is_input = True, name = "Bone Matrix", node = self),
        }
        self.outputs = {
          "Bone Matrix"   : NodeSocket(name = "Bone Matrix", node = self),
        }
        self.parameters = {
          "Bone Matrix":None, 
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def bPrepare(self, bContext = None,):
        from mathutils import Vector, Matrix, Quaternion
        from bpy.types import Bone
        if matrix := self.evaluate_input("Bone Matrix"):
            axis, roll = Bone.AxisRollFromMatrix(matrix.to_3x3())
            new_mat = Bone.MatrixFromAxisRoll(-1*axis, roll)
            length = matrix[3][3]
            new_mat.resize_4x4()         # last column contains
            new_mat[0][3] = matrix[0][3] + axis[0]*length # x location
            new_mat[1][3] = matrix[1][3] + axis[1]*length # y location
            new_mat[2][3] = matrix[2][3] + axis[2]*length # z location
            new_mat[3][3] = length                           # length
            self.parameters["Bone Matrix"] = new_mat
        self.prepared, self.executed = True, True


class UtilityMatrixTransform:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Matrix 1"   : NodeSocket(is_input = True, name = "Matrix 1", node = self),
          "Matrix 2"   : NodeSocket(is_input = True, name = "Matrix 2", node = self),
        }
        self.outputs = {
          "Out Matrix"     : NodeSocket(name = "Out Matrix", node = self),
        }
        self.parameters = {
          "Matrix 1"   : None,
          "Matrix 2"   : None,
          "Out Matrix" : None,
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def bPrepare(self, bContext = None,):
        from mathutils import Vector
        mat1 = self.evaluate_input("Matrix 1"); mat2 = self.evaluate_input("Matrix 2")
        if mat1 and mat2:
            mat1copy = mat1.copy()
            self.parameters["Out Matrix"] = mat2 @ mat1copy
            self.parameters["Out Matrix"].translation = mat1copy.to_translation()+ mat2.to_translation()
        else:
            raise RuntimeError(wrapRed(f"Node {self} did not receive all matrix inputs... found input 1? {mat1 is not None}, 2? {mat2 is not None}"))
        self.prepared = True
        self.executed = True



class UtilityTransformationMatrix:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Operation"   : NodeSocket(is_input = True, name = "Operation", node = self),
          "Vector"        : NodeSocket(is_input = True, name = "Vector", node = self),
          "W"   : NodeSocket(is_input = True, name = "W", node = self),
        }
        self.outputs = {
          "Matrix"     : NodeSocket(name = "Matrix", node = self),
        }
        self.parameters = {
          "Operation"   : None,
          "Origin"      : None,
          "Vector"        : None,
          "W"   : None,
          "Matrix"      : None,
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def bPrepare(self, bContext = None,):
        from mathutils import Matrix, Vector
        if (operation := self.evaluate_input("Operation")) == 'ROTATE_AXIS_ANGLE':
            # this can, will, and should fail if the axis is 0,0,0
            self.parameters["Matrix"] = rotMat = Matrix.Rotation(self.evaluate_input("W"), 4, Vector(self.evaluate_input("Vector")).normalized())
        elif (operation := self.evaluate_input("Operation")) == 'TRANSLATE':
            m = Matrix.Identity(4)
            if axis := self.evaluate_input("Vector"):
                m[0][3]=axis[0];m[1][3]=axis[1];m[2][3]=axis[2]
            self.parameters['Matrix'] = m
        elif (operation := self.evaluate_input("Operation")) == 'SCALE':
            self.parameters["Matrix"] = Matrix.Scale(self.evaluate_input("W"), 4, Vector(self.evaluate_input("Vector")).normalized())
        else:
            raise NotImplementedError(self.evaluate_input("Operation").__repr__()+ "  Operation not yet implemented.")
        self.prepared = True
        self.executed = True



class UtilityIntToString:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Number"        : NodeSocket(is_input = True, name = "Number", node = self),
          "Zero Padding"  : NodeSocket(is_input = True, name = "Zero Padding", node = self),
        }
        self.outputs = {
          "String"        : NodeSocket(name = "String", node = self),
        }
        self.parameters = {
          "Number"        : None,
          "Zero Padding"  : None,
          "String"        : None,
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def bPrepare(self, bContext = None,):
        number = self.evaluate_input("Number")

        zeroes = self.evaluate_input("Zero Padding")
        # I'm casting to int because I want to support any number, even though the node asks for int.
        self.parameters["String"] = str(int(number)).zfill(int(zeroes))
        self.prepared = True
        self.executed = True

class UtilityArrayGet:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Index"          : NodeSocket(is_input = True, name = "Index", node = self),
          "OoB Behaviour"  : NodeSocket(is_input = True, name = "OoB Behaviour", node = self),
          "Array"          : NodeSocket(is_input = True, name = "Array", node = self),
        }
        self.outputs = {
          "Output"        : NodeSocket(name = "Output", node = self),
        }
        self.parameters = {
          "Index"          : None,
          "OoB Behaviour"  : None,
          "Array"          : None,
          "Output"         : None,
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def bPrepare(self, bContext = None,):
      if self.prepared == False:
        # sort the array entries
        for inp in self.inputs.values():
            inp.links.sort(key=lambda a : -a.multi_input_sort_id)
        oob   = self.evaluate_input("OoB Behaviour")
        index = self.evaluate_input("Index")

        from .utilities import cap, wrap
        
        # we must assume that the array has sent the correct number of links

        if oob == 'WRAP':
            index = index % len(self.inputs['Array'].links)
        if oob == 'HOLD':
            index = cap(index, len(self.inputs['Array'].links)-1)

        # relink the connections and then kill all the links to and from the array
        from .utilities import init_connections, init_dependencies
        l = self.inputs["Array"].links[index]
        for link in self.outputs["Output"].links:
            to_node = link.to_node
            l.from_node.outputs[l.from_socket].connect(to_node, link.to_socket)
            link.die()
            init_dependencies(to_node)
        from_node=l.from_node
        for inp in self.inputs.values():
            for l in inp.links:
              l.die()
        init_connections(from_node)
        if self in from_node.hierarchy_connections:
          raise RuntimeError()
        # this is intentional because the Array Get is kind of a weird hybrid between a Utility and a Schema
        # so it should be removed from the tree when it is done. it has already dealt with the actual links.
        # however I think this is redundant. Check.
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies, self.dependencies = [], []

        self.prepared = True
        self.executed = True

class UtilitySetBoneMatrixTail:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Matrix"          : NodeSocket(is_input = True, name = "Matrix", node = self),
          "Tail Location"  : NodeSocket(is_input = True, name = "Tail Location", node = self),
        }
        self.outputs = {
          "Result"        : NodeSocket(name = "Result", node = self),
        }
        self.parameters = {
          "Matrix"     : None,
          "Tail Location"   : None,
          "Result"     : None,
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies, self.dependencies = [], []
        self.prepared, self.executed = False, False

    def bPrepare(self, bContext = None,):
      from mathutils import Matrix
      matrix = self.evaluate_input("Matrix")
      if matrix is None: matrix = Matrix.Identity(4)
      #just do this for now lol
      self.parameters["Result"] = matrix_from_head_tail(matrix.translation, self.evaluate_input("Tail Location"))



class UtilityPrint:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Input"          : NodeSocket(is_input = True, name = "Input", node = self),
        }
        self.outputs = {}
        self.parameters = {
          "Input"          : None,
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def bPrepare(self, bContext = None,):
        if my_input := self.evaluate_input("Input"):
            print("Preparation phase: ", wrapWhite(self), wrapGreen(my_input))
        # else:
        #     prRed("No input to print.")
        self.prepared = True

    def bExecute(self, bContext = None,):
        if my_input := self.evaluate_input("Input"):
            print("Execution phase: ", wrapWhite(self), wrapGreen(my_input))
        # else:
        #     prRed("No input to print.")
        self.executed = True


class UtilityCompare:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "A"           : NodeSocket(is_input = True, name = "A", node = self),
          "B"           : NodeSocket(is_input = True, name = "B", node = self),
        }
        self.outputs = {
          "Result"      : NodeSocket(name = "Result", node = self),
        }
        self.parameters = {
          "A"           : None,
          "B"           : None,
          "Result"      : None,
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies, self.dependencies = [], []
        self.prepared, self.executed = False, False

    def bPrepare(self, bContext = None,):
        self.parameters["Result"] = self.evaluate_input("A") == self.evaluate_input("B")
        self.prepared = True; self.executed = True


class UtilityChoose:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Condition"   : NodeSocket(is_input = True, name = "Condition", node = self),
          "A"           : NodeSocket(is_input = True, name = "A", node = self),
          "B"           : NodeSocket(is_input = True, name = "B", node = self),
        }
        self.outputs = {
          "Result"      : NodeSocket(name = "Result", node = self),
        }
        self.parameters = {
          "Condition"   : None,
          "A"           : None,
          "B"           : None,
          "Result"      : None,
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies, self.dependencies = [], []
        self.prepared, self.executed = False, False

    def bPrepare(self, bContext = None,):
        condition = self.evaluate_input("Condition")
        if condition:
            self.parameters["Result"] = self.evaluate_input("B")
        else:
            self.parameters["Result"] = self.evaluate_input("A")
        self.prepared = True
        self.executed = True



for c in TellClasses():
    setup_container(c)
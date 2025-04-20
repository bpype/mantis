from .node_container_common import *
from .base_definitions import MantisNode, NodeSocket
from .xForm_containers import xFormArmature, xFormBone
from .misc_nodes_socket_templates import *
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
             UtilityNumberOfCurveSegments,
             UtilityMatrixFromCurveSegment,
             UtilityGetCurvePoint,
             UtilityGetNearestFactorOnCurve,
             UtilityKDChoosePoint,
             UtilityKDChooseXForm,
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
             UtilityArrayLength,
             UtilitySetBoneMatrixTail,
             # Control flow switches
             UtilityCompare,
             UtilityChoose,
             # useful NoOp:
             UtilityPrint,
            ]


def matrix_from_head_tail(head, tail, normal=None):
    from mathutils import Vector, Quaternion, Matrix
    if normal is None:
        rotation = Vector((0,1,0)).rotation_difference((tail-head).normalized()).to_matrix()
        m= Matrix.LocRotScale(head, rotation, None)
        m[3][3] = (tail-head).length
    else: # construct a basis matrix
        m = Matrix.Identity(3)
        axis = (tail-head).normalized()
        conormal = axis.cross(normal)
        m[0]=conormal
        m[1]=axis
        m[2]=normal
        m = m.transposed().to_4x4()
    return m

def get_mesh_from_curve(curve_name : str, execution_id : str, bContext, ribbon=True):
        from bpy import data
        curve = data.objects.get(curve_name)
        assert curve.type == 'CURVE', f"ERROR: object is not a curve: {curve_name}"
        from .utilities import mesh_from_curve
        curve_type='ribbon' if ribbon else 'wire'
        m_name = curve_name+'.'+str(hash(curve_name+'.'+curve_type+'.'+execution_id))
        if not (m := data.meshes.get(m_name)):
            m = mesh_from_curve(curve, bContext, ribbon)
            m.name = m_name
        return m

def cleanup_curve(curve_name : str, execution_id : str) -> None:
        import bpy
        curve = bpy.data.objects.get(curve_name)
        m_name = curve_name+'.'+str(hash(curve.name+'.'+ execution_id))
        if (mesh := bpy.data.meshes.get(m_name)):
            bpy.data.meshes.remove(mesh)

def kd_find(node, points, ref_pt, num_points):
        if num_points == 0:
            raise RuntimeError(f"Cannot find 0 points for {node}")
        from mathutils import kdtree
        kd = kdtree.KDTree(len(points))
        for i, pt in enumerate(points):
            try:
                kd.insert(pt, i)
            except (TypeError, ValueError) as e:
                prRed(f"Cannot get point from for {node}")
                raise e
        kd.balance()
        try:
            if num_points == 1: # make it a list to keep it consistent with
                result = [kd.find(ref_pt)] # find_n which returns a list
            else:
                result = kd.find_n(ref_pt, num_points)
            # the result of kd.find has some other stuff we don't care about
        except (TypeError, ValueError) as e:
            prRed(f"Reference Point {ref_pt} invalid for {node}")
            raise e
        return result


def array_choose_relink(node, indices, array_input, output, ):
    """
        Used to choose the correct link to send out of an array-choose node.
    """
    from .utilities import init_dependencies
    keep_links = []
    init_my_connections=[]
    for index in indices:
        l = node.inputs[array_input].links[index]
        keep_links.append(l)
        init_my_connections.append(l.from_node)
    for link in node.outputs[output].links:
        to_node = link.to_node
        for l in keep_links:
            l.from_node.outputs[l.from_socket].connect(to_node, link.to_socket)
        link.die()


def array_choose_data(node, data, output):
    """
        Used to choose the correct data to send out of an array-choose node.
    """
    from .utilities import init_dependencies
    # We need to make new outputs and link from each one based on the data in the array...
    node.outputs.init_sockets([output+"."+str(i).zfill(4) for i in range(len(data)) ])
    for i, data_item in enumerate(data):
        node.parameters[output+"."+str(i).zfill(4)] = data_item
    for link in node.outputs[output].links:
        to_node = link.to_node
        for i in range(len(data)):
            # Make a link from the new output.
            node.outputs[output+"."+str(i).zfill(4)].connect(to_node, link.to_socket)
        link.die()

#*#-------------------------------#++#-------------------------------#*#
# U T I L I T Y   N O D E S
#*#-------------------------------#++#-------------------------------#*#

class InputFloat(MantisNode):
    '''A node representing float input'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        outputs = ["Float Input"]
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = 'UTILITY'
        self.prepared = True
        self.executed = True

class InputIntNode(MantisNode):
    '''A node representing integer input'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        outputs = ["Integer"]
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = 'UTILITY'
        self.prepared = True
        self.executed = True
    
class InputVector(MantisNode):
    '''A node representing vector input'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        outputs = [""]
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = 'UTILITY'
        self.prepared = True
        self.executed = True

class InputBoolean(MantisNode):
    '''A node representing boolean input'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        outputs = [""]
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = 'UTILITY'
        self.prepared = True
        self.executed = True

class InputBooleanThreeTuple(MantisNode):
    '''A node representing a tuple of three booleans'''
        
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        outputs = [""]
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = 'UTILITY'
        self.prepared = True
        self.executed = True
    
class InputRotationOrder(MantisNode):
    '''A node representing string input for rotation order'''
        
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        outputs = [""]
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = 'UTILITY'
        self.prepared = True
        self.executed = True
    

class InputTransformSpace(MantisNode):
    '''A node representing string input for transform space'''
        
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        outputs = [""]
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = 'UTILITY'
        self.prepared = True
        self.executed = True
        
    def evaluate_input(self, input_name):
        return self.parameters[""]
    
class InputString(MantisNode):
    '''A node representing string input'''
        
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        outputs = [""]
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = 'UTILITY'
        self.prepared = True
        self.executed = True

    
class InputMatrix(MantisNode):
    '''A node representing axis-angle quaternion input'''
        
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        outputs  = ["Matrix",]
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = 'UTILITY'
        self.prepared = True
        self.executed = True

class UtilityMatrixFromCurve(MantisNode):
    '''Get a matrix from a curve'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Curve"            ,
          "Total Divisions"  ,
          "Matrix Index"     ,
        ]
        outputs = [
          "Matrix" ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        from mathutils import Matrix
        import bpy
        mat = Matrix.Identity(4)
        curve_name = self.evaluate_input("Curve")
        curve = bpy.data.objects.get(curve_name)
        if not curve:
            prRed(f"WARN: No curve found for {self}. Using an identity matrix instead.")
            mat[3][3] = 1.0
        elif curve.type != "CURVE":
            prRed(f"WARN: Object {curve.name} is not a curve. Using an identity matrix instead.")
            mat[3][3] = 1.0
        else:
            if bContext is None: bContext = bpy.context # is this wise?
            m = get_mesh_from_curve(curve.name, self.base_tree.execution_id, bContext)
            from .utilities import data_from_ribbon_mesh
            #
            num_divisions = self.evaluate_input("Total Divisions")
            m_index = self.evaluate_input("Matrix Index")
            factors = [1/num_divisions*m_index, 1/num_divisions*(m_index+1)]
            data = data_from_ribbon_mesh(m, [factors], curve.matrix_world)
            head=data[0][0][0]
            tail= data[0][0][1]
            axis = (tail-head).normalized()
            normal=data[0][2][0]
            # make sure the normal is perpendicular to the tail
            from .utilities import make_perpendicular
            normal = make_perpendicular(axis, normal)
            mat = matrix_from_head_tail(head, tail, normal)
            # this is in world space... let's just convert it back
            mat.translation = head - curve.location
            mat[3][3]=(tail-head).length

            # TODO HACK TODO
            # all the nodes should work in world-space, and it should be the responsibility
            # of the xForm node to convert!

        self.parameters["Matrix"] = mat
        self.prepared = True
        self.executed = True
    
    def bFinalize(self, bContext=None):
        cleanup_curve(self.evaluate_input("Curve"), self.base_tree.execution_id)


class UtilityPointFromCurve(MantisNode):
    '''Get a point from a curve'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Curve"       ,
          "Factor"      ,
        ]
        outputs = [
          "Point" ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        import bpy
        curve = bpy.data.objects.get(self.evaluate_input("Curve"))
        if not curve:
            raise RuntimeError(f"No curve found for {self}.")
        elif curve.type != "CURVE":
            raise GraphError(f"ERROR: Object {curve.name} is not a curve.")
        else:
            if bContext is None: bContext = bpy.context # is this wise?
            m = get_mesh_from_curve(curve.name, self.base_tree.execution_id, bContext)
            from .utilities import data_from_ribbon_mesh
            #
            num_divisions = 1
            factors = [self.evaluate_input("Factor")]
            data = data_from_ribbon_mesh(m, [factors], curve.matrix_world)
            p = data[0][0][0] - curve.location
        self.parameters["Point"] = p
        self.prepared, self.executed = True, True
    
    def bFinalize(self, bContext=None):
        cleanup_curve(self.evaluate_input("Curve"), self.base_tree.execution_id)

class UtilityMatricesFromCurve(MantisNode):
    '''Get matrices from a curve'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Curve"            ,
          "Total Divisions"  ,
        ]
        outputs = [
          "Matrices" ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

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
            prRed(f"WARN: No curve found for {self}. Using an identity matrix instead.")
            m[3][3] = 1.0
        elif curve.type != "CURVE":
            prRed(f"WARN: Object {curve.name} is not a curve. Using an identity matrix instead.")
            m[3][3] = 1.0
        else:
            if bContext is None: bContext = bpy.context # is this wise?
            mesh = get_mesh_from_curve(curve.name, self.base_tree.execution_id, bContext)
            from .utilities import data_from_ribbon_mesh
            num_divisions = self.evaluate_input("Total Divisions")
            factors = [0.0] + [(1/num_divisions*(i+1)) for i in range(num_divisions)]
            data = data_from_ribbon_mesh(mesh, [factors], curve.matrix_world)
            
            # 0 is the spline index. 0 selects points as opposed to normals or whatever.
            from .utilities import make_perpendicular
            matrices = [matrix_from_head_tail(
                data[0][0][i], 
                data[0][0][i+1],
                make_perpendicular((data[0][0][i+1]-data[0][0][i]).normalized(), data[0][2][i]),) \
                    for i in range(num_divisions)]
        

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

class UtilityNumberOfCurveSegments(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Curve"            ,
          "Spline Index"     ,
        ]
        outputs = [
          "Number of Segments" ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"
    
    def bPrepare(self, bContext = None,):
        import bpy
        curve_name = self.evaluate_input("Curve")
        curve = bpy.data.objects.get(curve_name)
        spline = curve.data.splines[self.evaluate_input("Spline Index")]
        if spline.type == "BEZIER":
            self.parameters["Number of Segments"] = len(spline.bezier_points)-1
        else:
            self.parameters["Number of Segments"] = len(spline.points)-1
        self.prepared = True
        self.executed = True

class UtilityMatrixFromCurveSegment(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Curve"            ,
          "Spline Index"     ,
          "Segment Index"    ,
        ]
        outputs = [
          "Matrix"           ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        import bpy
        curve = bpy.data.objects.get(self.evaluate_input("Curve"))
        if not curve:
            raise RuntimeError(f"No curve found for {self}.")
        elif curve.type != "CURVE":
            raise GraphError(f"ERROR: Object {curve.name} is not a curve.")
        else:
            if bContext is None: bContext = bpy.context # is this wise?
            m = get_mesh_from_curve(curve.name, self.base_tree.execution_id, bContext)
            from .utilities import data_from_ribbon_mesh
            # this section is dumb, but it is because the data_from_ribbon_mesh
            #  function is designed to pull data from many splines at once (for optimization)
            #  so we have to give it empty splines for each one we skip.
            # TODO: Refactor this to make it so I can select spline index
            spline_index = self.evaluate_input("Spline Index")
            spline = curve.data.splines[spline_index]
            splines_factors = [ [] for i in range (spline_index)]
            factors = [0.0]
            points = spline.bezier_points if spline.type == 'BEZIER' else spline.points
            total_length=0.0
            for i in range(len(points)-1):
                total_length+= (seg_length := (points[i+1].co - points[i].co).length)
                factors.append(seg_length)
            prev_length = 0.0
            for i in range(len(factors)):
                factors[i] = prev_length+factors[i]/total_length
                prev_length=factors[i]
                # Why does this happen? Floating point error?
                if factors[i]>1.0: factors[i] = 1.0
            splines_factors.append(factors)
            #
            data = data_from_ribbon_mesh(m, splines_factors, curve.matrix_world)
            segment_index = self.evaluate_input("Segment Index")
            head=data[spline_index][0][segment_index]
            tail= data[spline_index][0][segment_index+1]
            axis = (tail-head).normalized()
            normal=data[spline_index][2][segment_index]
            # make sure the normal is perpendicular to the tail
            from .utilities import make_perpendicular
            normal = make_perpendicular(axis, normal)
            m = matrix_from_head_tail(head, tail, normal)
            m.translation = head - curve.location
            m[3][3]=(tail-head).length
            self.parameters["Matrix"] = m
        self.prepared, self.executed = True, True
    
    def bFinalize(self, bContext=None):
        cleanup_curve(self.evaluate_input("Curve"), self.base_tree.execution_id)

class UtilityGetCurvePoint(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, GetCurvePointSockets)
        self.init_parameters()
        self.node_type = "UTILITY"
    
    def bPrepare(self, bContext=None):
        import bpy
        curve = bpy.data.objects.get(self.evaluate_input("Curve"))
        if not curve:
            raise RuntimeError(f"No curve found for {self}.")
        elif curve.type != "CURVE":
            raise GraphError(f"ERROR: Object {curve.name} is not a curve.")
        spline = curve.data.splines[self.evaluate_input("Spline Index")]
        if spline.type == 'BEZIER':
            bez_pt = spline.bezier_points[self.evaluate_input("Index")]
            self.parameters["Point"]=bez_pt.co
            self.parameters["Left Handle"]=bez_pt.handle_left
            self.parameters["Right Handle"]=bez_pt.handle_right
        else:
            pt = spline.points[self.evaluate_input("Index")]
            self.parameters["Point"]=(pt.co[0], pt.co[1], pt.co[2])
        self.prepared, self.executed = True, True

class UtilityGetNearestFactorOnCurve(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, GetNearestFactorOnCurveSockets)
        self.init_parameters()
        self.node_type = "UTILITY"
    
    def bPrepare(self, bContext = None,):
        import bpy
        curve = bpy.data.objects.get(self.evaluate_input("Curve"))
        if not curve:
            raise RuntimeError(f"No curve found for {self}.")
        elif curve.type != "CURVE":
            raise GraphError(f"ERROR: Object {curve.name} is not a curve.")
        else:
            if bContext is None: bContext = bpy.context # is this wise?
            m = get_mesh_from_curve(curve.name,
                                    self.base_tree.execution_id,
                                    bContext, ribbon=False)
            # this is confusing but I am not re-writing these old functions
            from .utilities import FindNearestPointOnWireMesh as nearest_point
            spline_index = self.evaluate_input("Spline Index")
            ref_pt = self.evaluate_input("Reference Point")
            splines_points = [ [] for i in range (spline_index)]
            splines_points.append([ref_pt])
            pt =  nearest_point(m, splines_points)[spline_index][0]
            self.parameters["Factor"] = pt
        self.prepared, self.executed = True, True

class UtilityKDChoosePoint(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Reference Point"  ,
          "Points"           ,
          "Number to Find"   ,
        ]
        outputs = [
          "Result Point"     ,
          "Result Index"     ,
          "Result Distance"  ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        from mathutils import Vector
        points= []
        ref_point = self.evaluate_input('Reference Point')
        num_points = self.evaluate_input('Number to Find')
        for i, l in enumerate(self.inputs['Points'].links):
            pt = self.evaluate_input('Points', i)
            points.append(pt)
            if not isinstance(pt, Vector):
                prRed(f"Cannot get point from {l.from_node} for {self}")
        assert ref_point is not None, wrapRed(f"Reference Point {ref_point} is invalid in node {self}")
        result = kd_find(self, points, ref_point, num_points)
        indices = [ found_point[1] for found_point in result  ]
        distances  = [ found_point[2] for found_point in result  ]
        array_choose_relink(self, indices, "Points", "Result Point")
        array_choose_data(self, indices, "Result Index")
        array_choose_data(self, distances, "Result Distance")
        self.prepared, self.executed = True, True
        


class UtilityKDChooseXForm(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Reference Point"      ,
          "xForm Nodes"          ,
          "Get Point Head/Tail"  ,
          "Number to Find"       ,
        ]
        outputs = [
          "Result xForm"     ,
          "Result Index"     ,
          "Result Distance"  ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        if len(self.hierarchy_dependencies)==0 and len(self.hierarchy_connections)==0 and \
                 len(self.connections)==0 and len(self.dependencies)==0:
            self.prepared, self.executed = True, True
            return #Either it is already done or it doesn't matter.
        from mathutils import Vector
        points= []
        ref_point = self.evaluate_input('Reference Point')
        num_points = self.evaluate_input('Number to Find')
        for i, l in enumerate(self.inputs['xForm Nodes'].links):
            matrix = l.from_node.evaluate_input('Matrix')
            if matrix is None:
                raise GraphError(f"Cannot get point from {l.from_node} for {self}. Does it have a matrix?")
            pt = matrix.translation
            if head_tail := self.evaluate_input("Get Point Head/Tail"):
                # get the Y-axis of the basis, assume it is normalized
                y_axis = Vector((matrix[0][1],matrix[1][1], matrix[2][1]))
                pt = pt.lerp(pt+y_axis*matrix[3][3], head_tail)
            points.append(pt)
            if not isinstance(pt, Vector):
                prRed(f"Cannot get point from {l.from_node} for {self}")
        assert ref_point is not None, wrapRed(f"Reference Point {ref_point} is invalid in node {self}")
        result = kd_find(self, points, ref_point, num_points)
        indices = [ found_point[1] for found_point in result  ]
        distances  = [ found_point[2] for found_point in result  ]
        array_choose_relink(self, indices, "xForm Nodes", "Result xForm")
        array_choose_data(self, indices, "Result Index")
        array_choose_data(self, distances, "Result Distance")
        self.prepared, self.executed = True, True

class UtilityMetaRig(MantisNode):
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Meta-Armature" ,
          "Meta-Bone"     ,
        ]
        outputs = [
          "Matrix" ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

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


class UtilityBoneProperties(MantisNode):
    '''A node representing a bone's gettable properties'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        outputs = [
            "matrix"        ,
            "matrix_local"  ,
            "matrix_basis"  ,
            "head"          ,
            "tail"          ,
            "length"        ,
            "rotation"      ,
            "location"      ,
            "scale"         ,
        ]
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"
        self.prepared = True
        self.executed = True

    def fill_parameters(self, prototype=None):
        return
        
# TODO this should probably be moved to Links
class UtilityDriverVariable(MantisNode):
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Variable Type"   ,
            "Property"       ,
            "Property Index" ,
            "Evaluation Space",
            "Rotation Mode"   ,
            "xForm 1"         ,
            "xForm 2"         ,
        ]
        outputs = [
          "Driver Variable",
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "DRIVER" # MUST be run in Pose mode
        self.prepared = True
        
    def evaluate_input(self, input_name):
        if input_name == 'Property':
            if self.inputs.get('Property'):
                if self.inputs['Property'].is_linked:
                # get the name instead...
                    trace = trace_single_line(self, input_name)
                    return trace[1].name # the name of the socket
            return self.parameters["Property"]
        return super().evaluate_input(input_name)
        
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
            



class UtilityKeyframe(MantisNode):
    '''A node representing a keyframe for a F-Curve'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Frame"   ,
          "Value"   ,
        ]
        outputs = [
          "Keyframe" ,
        ]
        additional_parameters = {"Keyframe":{}}
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters( additional_parameters=additional_parameters)
        self.node_type = "DRIVER" # MUST be run in Pose mode
        setup_custom_props(self)

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


class UtilityFCurve(MantisNode):
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Extrapolation Mode",
        ]
        outputs = [
          "fCurve",
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"
        setup_custom_props(self)
        self.prepared = True

    def evaluate_input(self, input_name):
        return super().evaluate_input(input_name)

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
        self.parameters["fCurve"] = keys
        self.executed = True
#TODO make the fCurve data a data class instead of a dict 

class UtilityDriver(MantisNode):
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Driver Type"   ,
          "Expression"    ,
          "fCurve"        ,
        ]
        outputs = [
          "Driver",
        ]
        from .drivers import MantisDriver
        additional_parameters = {
          "Driver":MantisDriver(), 
        }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters(additional_parameters=additional_parameters)
        self.node_type = "DRIVER" # MUST be run in Pose mode
        setup_custom_props(self)
        self.prepared = True

    def bExecute(self, bContext = None,):
        prepare_parameters(self)
        from .drivers import MantisDriver
        #prPurple("Executing Driver Node")
        my_vars = []
        keys = self.evaluate_input("fCurve")
        if keys is None or len(keys) <2:
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


class UtilitySwitch(MantisNode):
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = {
          "Parameter"            ,
          "Parameter Index"      ,
          "Invert Switch"        ,
        }
        outputs = [
          "Driver",
        ]
        from .drivers import MantisDriver
        additional_parameters = {
          "Driver":MantisDriver(), 
        }
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters(additional_parameters=additional_parameters)
        self.node_type = "DRIVER" # MUST be run in Pose mode
        self.prepared = True

    def evaluate_input(self, input_name):
        if input_name == 'Parameter':
            if self.inputs['Parameter'].is_connected:
                trace = trace_single_line(self, input_name)
                return trace[1].name # the name of the socket
            return self.parameters["Parameter"]
        return super().evaluate_input(input_name)

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
        # I want to support this behaviour because Blender supports it.
        # We do not make a copy. We update the driver, so that
        #  the same instance is filled out.
        self.parameters["Driver"].update(my_driver)
        print("Initializing driver %s " % (wrapPurple(self.__repr__())) )
        self.executed = True



class UtilityCombineThreeBool(MantisNode):
    '''A node for combining three booleans into a boolean three-tuple'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "X"   ,
          "Y"   ,
          "Z"   ,
        ]
        outputs = [
          "Three-Bool",
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        self.parameters["Three-Bool"] = (
          self.evaluate_input("X"),
          self.evaluate_input("Y"),
          self.evaluate_input("Z"), )
        self.prepared = True
        self.executed = True


# Note this is a copy of the above. This needs to be de-duplicated.
class UtilityCombineVector(MantisNode):
    '''A node for combining three floats into a vector'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        super().__init__(signature, base_tree)
        inputs = [
          "X"   ,
          "Y"   ,
          "Z"   ,
        ]
        outputs = [
          "Vector",
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        #prPurple("Executing CombineVector Node")
        prepare_parameters(self)
        self.parameters["Vector"] = (
          self.evaluate_input("X"),
          self.evaluate_input("Y"),
          self.evaluate_input("Z"), )
        self.prepared = True
        self.executed = True
  

class UtilitySeparateVector(MantisNode):
    '''A node for separating a vector into three floats'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Vector"
        ]
        outputs = [
          "X"   ,
          "Y"   ,
          "Z"   ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        self.parameters["X"] = self.evaluate_input("Vector")[0]
        self.parameters["Y"] = self.evaluate_input("Vector")[1]
        self.parameters["Z"] = self.evaluate_input("Vector")[2]
        self.prepared = True
        self.executed = True

class UtilityCatStrings(MantisNode):
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "String_1"   ,
          "String_2"   ,
        ]
        outputs = [
          "OutputString" ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"
    
    def bPrepare(self, bContext = None,):
        self.parameters["OutputString"] = self.evaluate_input("String_1")+self.evaluate_input("String_2")
        self.prepared = True
        self.executed = True

class InputExistingGeometryObject(MantisNode):
    '''A node representing an existing object'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Name"  ,
        ]
        outputs = [
          "Object" ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "XFORM"
    
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

class InputExistingGeometryData(MantisNode):
    '''A node representing existing object data'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Name"  ,
        ]
        outputs = [
          "Geometry" ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"
        self.prepared = True
        self.executed = True
    # the mode argument is only for interface consistency
    def bGetObject(self, mode=''):
        from bpy import data
        # first try Curve, then try Mesh
        bObject = data.curves.get(self.evaluate_input("Name"))
        if not bObject:
            bObject = data.meshes.get(self.evaluate_input("Name"))
        if bObject is None:
            raise RuntimeError(f"Could not find a mesh or curve datablock named \"{self.evaluate_input('Name')}\" for node {self}")
        return bObject

class UtilityGeometryOfXForm(MantisNode):
    '''A node representing existing object data'''
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "xForm"  ,
        ]
        outputs = [
          "Geometry" ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"
        self.prepared = True
        self.executed = True

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


class UtilityNameOfXForm(MantisNode):
    '''A node representing existing object data'''
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "xForm"  ,
        ]
        outputs = [
          "Name" ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    # mode for interface consistency
    def bPrepare(self, bContext = None,):
        if not (self.inputs.get('xForm') and self.inputs['xForm'].links):
            prOrange(f"WARN: Cannot retrieve data from {self}, there is no xForm node connected.")
            return ''
        xf = self.inputs["xForm"].links[0].from_node
        self.parameters["Name"] = xf.evaluate_input('Name')
        self.prepared, self.executed = True, True

class UtilityGetBoneLength(MantisNode):
    '''A node to get the length of a bone matrix'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Bone Matrix" ,
        ]
        outputs = [
          "Bone Length" ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        if (l := self.evaluate_input("Bone Matrix")) is not None:
            self.parameters["Bone Length"] = l[3][3]
        else:
            other = self.inputs["Bone Matrix"].links[0].from_node
            raise RuntimeError(f"Cannot get matrix for {self} from {other}")
        self.prepared = True
        self.executed = True

class UtilityPointFromBoneMatrix(MantisNode):
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Bone Matrix"   ,
          "Head/Tail"     ,
        ]
        outputs = [
          "Point"     ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    # TODO: find out why this is sometimes not ready at bPrepare phase
    def bPrepare(self, bContext = None,):
        from mathutils import Vector
        matrix = self.evaluate_input("Bone Matrix")
        head, rotation, _scale = matrix.copy().decompose()
        tail = head.copy() + (rotation @ Vector((0,1,0)))*matrix[3][3]
        self.parameters["Point"] = head.lerp(tail, self.evaluate_input("Head/Tail"))
        self.prepared = True
        self.executed = True


class UtilitySetBoneLength(MantisNode):
    '''Sets the length of a Bone's matrix'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Bone Matrix"   ,
          "Length"        ,
        ]
        outputs = [
          "Bone Matrix"   ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"
    
    def bPrepare(self, bContext = None,):
        from mathutils import Vector
        if matrix := self.evaluate_input("Bone Matrix"):
            matrix = matrix.copy()
            # print (self.inputs["Length"].links)
            matrix[3][3] = self.evaluate_input("Length")
            self.parameters["Length"] = self.evaluate_input("Length")
            self.parameters["Bone Matrix"] = matrix
        else:
            raise RuntimeError(f"Cannot get matrix for {self}")
        self.prepared = True
        self.executed = True

  
class UtilityMatrixSetLocation(MantisNode):
    '''Sets the location of a matrix'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Matrix"        ,
          "Location"      ,
        ]
        outputs = [
          "Matrix"        ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"
    
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

class UtilityMatrixGetLocation(MantisNode):
    '''Gets the location of a matrix'''
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Matrix"        ,
        ]
        outputs = [
          "Location"    ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"
    
    def bPrepare(self, bContext = None,):
        from mathutils import Vector
        if matrix := self.evaluate_input("Matrix"):
            self.parameters["Location"] = matrix.to_translation()
        self.prepared = True; self.executed = True


class UtilityMatrixFromXForm(MantisNode):
    """Returns the matrix of the given xForm node."""
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "xForm"        ,
        ]
        outputs = [
          "Matrix"       ,
        ]
        self.node_type = "UTILITY"
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
    
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


class UtilityAxesFromMatrix(MantisNode):
    """Returns the axes of the given matrix."""
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Matrix"       ,
        ]
        outputs = [
          "X Axis"      ,
          "Y Axis"      ,
          "Z Axis"      ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"
        
    def bPrepare(self, bContext = None,):
        from mathutils import Vector
        if matrix := self.evaluate_input("Matrix"):
            matrix= matrix.copy().to_3x3()
            self.parameters['X Axis'] = matrix @ Vector((1,0,0))
            self.parameters['Y Axis'] = matrix @ Vector((0,1,0))
            self.parameters['Z Axis'] = matrix @ Vector((0,0,1))
        self.prepared = True; self.executed = True


class UtilityBoneMatrixHeadTailFlip(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Bone Matrix"     ,
        ]
        outputs = [
          "Bone Matrix"     ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

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


class UtilityMatrixTransform(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Matrix 1"   ,
          "Matrix 2"   ,
        ]
        outputs = [
          "Out Matrix"    ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

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



class UtilityTransformationMatrix(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Operation"   ,
          "Vector"      ,
          "W"           ,
        ]
        outputs = [
          "Matrix"    ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

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



class UtilityIntToString(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Number"         ,
          "Zero Padding"   ,
        ]
        outputs = [
          "String"         ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        number = self.evaluate_input("Number")

        zeroes = self.evaluate_input("Zero Padding")
        # I'm casting to int because I want to support any number, even though the node asks for int.
        self.parameters["String"] = str(int(number)).zfill(int(zeroes))
        self.prepared = True
        self.executed = True

class UtilityArrayGet(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Index"           ,
          "OoB Behaviour"   ,
          "Array"           ,
        ]
        outputs = [
          "Output"          ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        if len(self.hierarchy_dependencies)==0 and len(self.hierarchy_connections)==0 and \
                 len(self.connections)==0 and len(self.dependencies)==0:
            self.prepared, self.executed = True, True
            return #Either it is already done or it doesn't matter.
        elif self.prepared == False:
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
            array_choose_relink(self, [index], "Array", "Output")
        self.prepared, self.executed = True, True

class UtilityArrayLength(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Array"           ,
        ]
        outputs = [
          "Length"          ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        self.parameters["Length"] = len(self.inputs["Array"].links)
        self.prepared, self.executed = True, True

class UtilitySetBoneMatrixTail(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = {
          "Matrix"        ,
          "Tail Location" ,
        }
        outputs = [
          "Result"       ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
      from mathutils import Matrix
      matrix = self.evaluate_input("Matrix")
      if matrix is None: matrix = Matrix.Identity(4)
      #just do this for now lol
      self.parameters["Result"] = matrix_from_head_tail(matrix.translation, self.evaluate_input("Tail Location"))
      self.prepared = True
      self.executed = True



class UtilityPrint(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Input"         ,
        ]
        self.inputs.init_sockets(inputs)
        self.init_parameters()
        self.node_type = "UTILITY"

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


class UtilityCompare(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "A"           ,
          "B"           ,
        ]
        outputs = [
          "Result"      ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        self.parameters["Result"] = self.evaluate_input("A") == self.evaluate_input("B")
        self.prepared = True; self.executed = True


class UtilityChoose(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Condition"   ,
          "A"           ,
          "B"           ,
        ]
        outputs = [
          "Result"      ,
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        condition = self.evaluate_input("Condition")
        if condition:
            self.parameters["Result"] = self.evaluate_input("B")
        else:
            self.parameters["Result"] = self.evaluate_input("A")
        self.prepared = True
        self.executed = True

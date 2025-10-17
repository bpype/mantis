from .node_common import *
from .base_definitions import MantisNode, NodeSocket

def TellClasses():
    return [
            MathStaticInt,
            MathStaticFloat,
            MathStaticVector,
           ]

def math_operation(operation, a, b):
    match operation:
        case "ADD":
            return a+b
        case "SUBTRACT":
            return a-b
        case "MULTIPLY":
            return a*b
        case "DIVIDE":
            return a/b
        case "FLOOR_DIVIDE":
            return a//b
        case "MODULUS":
            return a%b
        case "POWER":
            return a**b
        case "ABSOLUTE":
            return abs(a)
        case "MAXIMUM":
            return max(a, b)
        case "MINIMUM":
            return min(a, b)
        case "GREATER THAN":
            return float(a > b)
        case "LESS THAN":
            return float(a < b)
        case "ARCTAN2":
            from math import atan2
            return atan2(a,b)
        case "FLOOR":
            from math import floor
            return floor(a)
        case "CEIL":
            from math import ceil
            return ceil(a)
        case "ROUND":
            return round(a)

#*#-------------------------------#++#-------------------------------#*#
# M A T H  N O D E S
#*#-------------------------------#++#-------------------------------#*#
class MathStaticInt(MantisNode):
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Operation",
          "Int A",
          "Int B",
        ]
        outputs = [
          "Result Int",
        ]
        additional_parameters = {}
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters(additional_parameters=additional_parameters)
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        a = self.evaluate_input("Int A"); b = self.evaluate_input("Int B")
        result = math_operation(self.evaluate_input("Operation"), a, b)
        self.parameters["Result Int"] = int(result)
        self.prepared, self.executed = True, True

class MathStaticFloat(MantisNode):
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Operation",
          "Float A",
          "Float B",
        ]
        outputs = [
          "Result Float",
        ]
        additional_parameters = {}
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters(additional_parameters=additional_parameters)
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        a = self.evaluate_input("Float A"); b = self.evaluate_input("Float B")
        result = math_operation(self.evaluate_input("Operation"), a, b)
        self.parameters["Result Float"] = result
        self.prepared, self.executed = True, True

class MathStaticVector(MantisNode):
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
          "Operation",
          "Vector A",
          "Vector B",
          "Scalar A",
        ]
        outputs = [
          "Result Vector",
          "Result Float",
        ]
        additional_parameters = {}
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters(additional_parameters=additional_parameters)
        self.node_type = "UTILITY"

    def bPrepare(self, bContext = None,):
        from mathutils import Vector
        a = Vector(self.evaluate_input("Vector A")).copy()
        b = Vector(self.evaluate_input("Vector B")).copy()
        s = self.evaluate_input("Scalar A")
        if hasattr(s, '__iter__'):
            average = lambda iterable : sum(iterable)/len(iterable)
            s = average(s)
        f_result = float("NaN")
        v_result = None
        if self.evaluate_input("Operation") == "ADD":
            v_result = a+b
        if self.evaluate_input("Operation") == "SUBTRACT":
            v_result = a-b
        if self.evaluate_input("Operation") == "MULTIPLY":
            v_result = a*b
        if self.evaluate_input("Operation") == "DIVIDE":
            v_result = a/b
        if self.evaluate_input("Operation") == "POWER":
            v_result = a**b
        # since these are unary, we need to make a copy lest we create spooky effects elsewhere.
        a = a.copy()
        if self.evaluate_input("Operation") == "SCALE":
            v_result = a.normalized() * s
        if self.evaluate_input("Operation") == "LENGTH":
            f_result =  a.magnitude
        if self.evaluate_input("Operation") == "CROSS":
            v_result =  a.cross(b)
        if self.evaluate_input("Operation") == "DOT":
            f_result =  a.dot(b)
        if self.evaluate_input("Operation") == "NORMALIZE":
            v_result =  a.normalized()
        if self.evaluate_input("Operation") == "LINEAR_INTERP":
            v_result =  a.lerp(b, s).copy()
        self.parameters["Result Float"] = f_result
        # if v_result:
        self.parameters["Result Vector"] = v_result
        self.prepared = True
        self.executed = True

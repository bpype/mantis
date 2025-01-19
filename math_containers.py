from .node_container_common import *

def TellClasses():
    return [
            MathStaticInt,
            MathStaticFloat,
            MathStaticVector,
           ]

#*#-------------------------------#++#-------------------------------#*#
# M A T H  N O D E S
#*#-------------------------------#++#-------------------------------#*#
class MathStaticInt:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Operation" : NodeSocket(is_input = True, name = "Operation", node = self),
          "Int A"   : NodeSocket(is_input = True, name = "Int A", node = self),
          "Int B"   : NodeSocket(is_input = True, name = "Int B", node = self),
        }
        self.outputs = {
          "Result Int" : NodeSocket(name = "Result Int", node=self),
        }
        self.parameters = {
          "Operation":None,
          "Int A":None, 
          "Int B":None, 
          "Result Int":None, 
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def bPrepare(self, bContext = None,):
        a = self.evaluate_input("Int A"); b = self.evaluate_input("Int B")
        result = float("NaN")
        if self.evaluate_input("Operation") == "ADD":
            result = int(a+b)
        if self.evaluate_input("Operation") == "SUBTRACT":
            result = int(a-b)
        if self.evaluate_input("Operation") == "MULTIPLY":
            result = int(a*b)
        if self.evaluate_input("Operation") == "FLOOR_DIVIDE":
            result = a//b
        if self.evaluate_input("Operation") == "MODULUS":
            result = int(a%b)
        if self.evaluate_input("Operation") == "POWER":
            result = int(a**b)
        if self.evaluate_input("Operation") == "ABSOLUTE":
            result = int(abs(a))
        if self.evaluate_input("Operation") == "MAXIMUM":
            result = int(a if a <= b else b)
        if self.evaluate_input("Operation") == "MINIMUM":
            result = int(a if a >= b else b)
        if self.evaluate_input("Operation") == "GREATER THAN":
            result = int(a > b)
        if self.evaluate_input("Operation") == "LESS THAN":
            result = int(a < b)
        self.parameters["Result Int"] = result

        self.prepared = True
        self.executed = True

class MathStaticFloat:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Operation" : NodeSocket(is_input = True, name = "Operation", node = self),
          "Float A"   : NodeSocket(is_input = True, name = "Float A", node = self),
          "Float B"   : NodeSocket(is_input = True, name = "Float B", node = self),
        }
        self.outputs = {
          "Result Float" : NodeSocket(name = "Result Float", node=self),
        }
        self.parameters = {
          "Operation":None,
          "Float A":None, 
          "Float B":None, 
          "Result Float":None, 
        }
        self.node_type = "UTILITY"
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = False
        self.executed = False

    def bPrepare(self, bContext = None,):
        a = self.evaluate_input("Float A"); b = self.evaluate_input("Float B")
        result = float("NaN")
        if self.evaluate_input("Operation") == "ADD":
            result = a+b
        if self.evaluate_input("Operation") == "SUBTRACT":
            result = a-b
        if self.evaluate_input("Operation") == "MULTIPLY":
            result = a*b
        if self.evaluate_input("Operation") == "DIVIDE":
            result = a/b
        if self.evaluate_input("Operation") == "FLOOR_DIVIDE":
            result = a//b
        if self.evaluate_input("Operation") == "MODULUS":
            result = a%b
        if self.evaluate_input("Operation") == "POWER":
            result = a**b
        if self.evaluate_input("Operation") == "ABSOLUTE":
            result = abs(a)
        if self.evaluate_input("Operation") == "MAXIMUM":
            result = a if a <= b else b
        if self.evaluate_input("Operation") == "MINIMUM":
            result = a if a >= b else b
        if self.evaluate_input("Operation") == "GREATER THAN":
            result = float(a > b)
        if self.evaluate_input("Operation") == "LESS THAN":
            result = float(a < b)
        self.parameters["Result Float"] = result
        self.prepared = True
        self.executed = True


# enumVectorOperations = (('ADD', 'Add', 'Add (Component-wise)'),
#                         ('SUBTRACT', "Subtract", "Subtract (Component-wise)"),
#                         ('MULTIPLY', "Multiply", "Multiply (Component-wise)"),
#                         ('SCALE', "Scale", "Scales vector by input float or average magnitude of input vector's components."),
#                         ('DIVIDE', "Divide", "Divide (Component-wise)"),
#                         ('POWER', "Power", "Power (Component-wise)"),
#                         ('LENGTH', "Length", "Length"),
#                         ('CROSS', "Cross Product", "Cross product of A X B"),
#                         ('DOT', "Dot Product", "Dot product of A . B"),


class MathStaticVector:
    '''A node representing an armature object'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Operation"  : NodeSocket(is_input = True, name = "Operation", node = self),
          "Vector A"   : NodeSocket(is_input = True, name = "Vector A", node = self),
          "Vector B"   : NodeSocket(is_input = True, name = "Vector B", node = self),
          "Scalar A"   : NodeSocket(is_input = True, name = "Scalar A", node = self),
        }
        self.outputs = {
          "Result Vector" : NodeSocket(name = "Result Vector", node=self),
          "Result Float" : NodeSocket(name = "Result Float", node=self),
        }
        self.parameters = {
          "Operation":None,
          "Vector A":None, 
          "Vector B":None, 
          "Scalar A":None, 
          "Result Vector":None, 
          "Result Float":None, 
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


for c in TellClasses():
    setup_container(c)
from .node_container_common import *
from math import pi, tau

def TellClasses():
    return [
        SchemaIndex,
        SchemaArrayInput,
        SchemaArrayInputGet,
        SchemaArrayOutput,
        SchemaConstInput,
        SchemaConstOutput,
        SchemaOutgoingConnection,
        SchemaIncomingConnection,
    ]


def init_parameters(nc, is_input = True, in_out='INPUT', category=''):
    from .utilities import tree_from_nc
    parent_tree = tree_from_nc(nc.signature, nc.base_tree)
    if is_input:
        sockets=nc.inputs
    else:
        sockets=nc.outputs
    if category in ['Constant', 'Array', 'Connection']:
        for item in parent_tree.interface.items_tree:
            if item.item_type == 'PANEL': continue
            if item.parent and item.parent.name == category:
                if item.in_out == in_out:
                    sockets[item.name] = NodeSocket(
                        is_input=is_input,
                        name=item.name,
                        node=nc)
                    nc.parameters[item.name] = None



class SchemaIndex:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}#{
        #   "X"   : NodeSocket(is_input = True, name = "X", node = self),
        #   "Y"   : NodeSocket(is_input = True, name = "Y", node = self),
        #   "Z"   : NodeSocket(is_input = True, name = "Z", node = self),
        # }
        self.outputs = {
          "Index" : NodeSocket(name = "Index", node=self),
          "Schema Length" : NodeSocket(name = "Schema Length", node=self),
        }
        self.parameters = {
          "Index":None,
          "Schema Length":None,
        }
        self.node_type = 'SCHEMA'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True



class SchemaArrayInput:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {}
        self.parameters = {}
        init_parameters(self, is_input=False, in_out='INPUT', category='Array')
        self.node_type = 'SCHEMA'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True


class SchemaArrayInputGet:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "OoB Behaviour"  :  NodeSocket(is_input = True, name = "OoB Behaviour", node = self),
            "Index"          :  NodeSocket(is_input = True, name = "Index", node = self),
        }
        self.outputs = {}
        self.parameters = {
            "OoB Behaviour"  :  None,
            "Index"          :  None,

        }
        init_parameters(self, is_input=False, in_out='INPUT', category='Array')
        self.node_type = 'SCHEMA'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True


class SchemaArrayOutput:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {}
        self.parameters = {}
        init_parameters(self, is_input=True, in_out='OUTPUT', category='Array')
        self.node_type = 'SCHEMA'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True


        

class SchemaConstInput:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {}
        self.parameters = {}
        init_parameters(self, is_input=False, in_out='INPUT', category='Constant')
        self.node_type = 'SCHEMA'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True





class SchemaConstOutput:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {"Expose when N==":NodeSocket(is_input=True, name="Expose when N==", node=self)}
        self.outputs = {}
        self.parameters = {"Expose when N==":None}
        init_parameters(self, is_input=True, in_out='OUTPUT', category='Constant')
        self.node_type = 'SCHEMA'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True


        
class SchemaOutgoingConnection:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {}
        self.parameters = {}
        init_parameters(self, is_input=True, in_out='INPUT', category='Connection')
        self.node_type = 'SCHEMA'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True


        
class SchemaIncomingConnection:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {}
        self.parameters = {}
        init_parameters(self, is_input=False, in_out='OUTPUT', category='Connection')
        self.node_type = 'SCHEMA'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True



# class SchemaChoose:
#     def __init__(self, signature, base_tree):
#         self.base_tree=base_tree
#         self.signature = signature
#         init_parameters(self)
#         self.node_type = 'UTILITY'
        
#     def evaluate_input(self, input_name):
#         return evaluate_input(self, input_name)
    
#     def bExecute(self, bContext = None,):
#         pass
    
#     def __repr__(self):
#         return self.signature.__repr__()
        
#     def fill_parameters(self):
#         fill_parameters(self)


for c in TellClasses():
    setup_container(c)
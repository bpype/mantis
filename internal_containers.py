from .node_container_common import *
from bpy.types import Node
from .base_definitions import MantisNode


class DummyNode:
    def __init__(self, signature, base_tree, prototype = None):
        self.signature = signature
        self.base_tree = base_tree
        self.prototype = prototype
        self.inputs={}
        self.outputs={}
        self.parameters = {}
        self.node_type = 'DUMMY'
        if prototype:
            for sock in prototype.inputs:
                if sock.name == "__extend__":
                    continue
                self.inputs[sock.identifier] = NodeSocket(is_input = True, name = sock.identifier, node = self)
            for sock in prototype.outputs:
                if sock.name == "__extend__":
                    continue
                self.outputs[sock.identifier] = NodeSocket(is_input = False, name = sock.identifier, node = self)
                self.parameters[sock.identifier]=None

    def evaluate_input(self, input_name):
        pass
        # return evaluate_input(self, input_name)
    
    def bExecute(self, bContext = None,):
        pass
        
    def bFinalize(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self,):
        pass# fill_parameters(self)
        # I don't think I am using this but it doesn't hurt


# a class for duplicating an existing node for e.g. temporary
#  traces
class DupeNode:
    def __init__(self, signature, base_tree):
        self.signature = signature
        self.base_tree = base_tree
        self.prototype = prototype
        self.inputs={}
        self.outputs={}
        self.parameters = {}
        self.node_type = 'DUMMY'

    def evaluate_input(self, input_name):
        pass
        # return evaluate_input(self, input_name)
    
    def bExecute(self, bContext = None,):
        pass
        
    def bFinalize(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self,):
        fill_parameters(self)
        # I don't think I am using this but it doesn't hurt

from .node_container_common import *
from bpy.types import Node
from .base_definitions import MantisNode
from uuid import uuid4

class DummyNode:
    def __init__(self, signature, base_tree, prototype = None, natural_signature=None):
        self.signature = signature
        self.base_tree = base_tree
        self.prototype = prototype
        self.inputs={}
        self.outputs={}
        self.parameters = {}
        self.node_type = 'DUMMY'
        self.prepared = True
        if prototype.bl_idname in ["MantisSchemaGroup"]:
            self.node_type = 'DUMMY_SCHEMA'
            self.prepared = False
            self.uuid = uuid4()
        if prototype:
            for sock in prototype.inputs:
                if sock.identifier == "__extend__" or sock.name == "__extend__":
                    continue
                self.inputs[sock.identifier] = NodeSocket(is_input = True, name = sock.identifier, node = self)
            for sock in prototype.outputs:
                if sock.identifier == "__extend__" or sock.name == "__extend__":
                    continue
                self.outputs[sock.identifier] = NodeSocket(is_input = False, name = sock.identifier, node = self)
                self.parameters[sock.identifier]=None
        #HACK
        if natural_signature:
            self.natural_signature=natural_signature
        #HACK
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.executed = False

setup_container(DummyNode)


class NoOpNode:
    def __init__(self, signature, base_tree):
        self.signature = signature
        self.base_tree = base_tree
        self.inputs={
          "Input"   : NodeSocket(is_input = True, name = "Input", node = self),
        }
        self.outputs = {
          "Output" : NodeSocket(name = "Output", node=self),
        }
        self.parameters = {
            "Input"  : None,
            "Output" : None,
        }
        self.inputs["Input"].set_traverse_target(self.outputs["Output"])
        self.outputs["Output"].set_traverse_target(self.inputs["Input"])
        self.node_type = 'UTILITY'
        self.prepared = True
        self.hierarchy_connections = [];  self.connections = []
        self.hierarchy_dependencies = []; self.dependencies = []
        self.executed = True
    
    # this node is useful for me to insert in the tree and use for debugging especially connections.

setup_container(NoOpNode)
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
        #
        # 
        self.pre_pass_done = False
        self.execute_pass_done = False

setup_container(DummyNode)
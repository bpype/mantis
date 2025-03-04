from .node_container_common import *
from bpy.types import Node
from .base_definitions import MantisNode
from uuid import uuid4

class DummyNode(MantisNode):
    def __init__(self, signature, base_tree, prototype = None, natural_signature=None):
        super().__init__(signature, base_tree)
        self.prototype = prototype
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
        # keep track of the "natural signature" of Schema nodes - so that they are unambiguous
        self.natural_signature=self.signature
        if natural_signature:
            self.natural_signature=natural_signature
        # This is necessary for Schema to work if there are multiple Schema nodes using the same Schema tree.
        # this is ugly and I hate it.


class NoOpNode(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        self.inputs.init_sockets(["Input"])
        self.outputs.init_sockets(["Output"])
        self.init_parameters()
        self.set_traverse([("Input", "Output")])
        self.node_type = 'UTILITY'
        self.prepared = True
        self.executed = True
    
    # this node is useful for me to insert in the tree and use for debugging especially connections.

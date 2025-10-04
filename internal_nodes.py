from .node_common import *
from bpy.types import Node
from .base_definitions import MantisNode, MantisSocketTemplate
from uuid import uuid4

class DummyNode(MantisNode):
    def __init__(self, signature, base_tree, ui_node = None, ui_signature=None):
        super().__init__(signature, base_tree)
        self.ui_node = ui_node
        self.node_type = 'DUMMY'
        self.prepared = True
        self.uuid = uuid4()
        self.solver = None
        if ui_node:
            if ui_node.bl_idname in ["MantisSchemaGroup"]:
                self.node_type = 'DUMMY_SCHEMA'
                self.prepared = False
            for sock in ui_node.inputs:
                if sock.identifier == "__extend__" or sock.name == "__extend__":
                    continue
                self.inputs[sock.identifier] = NodeSocket(is_input = True, name = sock.identifier, node = self)
            for sock in ui_node.outputs:
                if sock.identifier == "__extend__" or sock.name == "__extend__":
                    continue
                self.outputs[sock.identifier] = NodeSocket(is_input = False, name = sock.identifier, node = self)
                self.parameters[sock.identifier]=None
        # keep track of the "natural signature" of Schema nodes - so that they are unambiguous
        self.ui_signature=self.signature
        if ui_signature:
            self.ui_signature=ui_signature
        # This is necessary for Schema to work if there are multiple Schema nodes using the same Schema tree.
        # this is ugly and I hate it.
        self.execution_prepared=True # in case it gets left behind in the tree as a dependency


class NoOpNode(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        self.inputs.init_sockets(["Input"])
        self.outputs.init_sockets(["Output"])
        self.init_parameters()
        self.set_traverse([("Input", "Output")])
        self.node_type = 'UTILITY'
        self.prepared, self.executed = True, True
        self.execution_prepared=True
    # this node is useful for me to insert in the tree and use for debugging especially connections.

class AutoGenNode(MantisNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        self.node_type = 'UTILITY'
        self.prepared, self.executed = True, True
        self.execution_prepared=True

    def reset_execution(self):
        super().reset_execution()
        self.prepared, self.executed = True, True


# The Group Interface node is responsible for gathering node connections
#   going in or out of the group and connecting back out the other side
# this is also where caching and overlays live
class GroupInterface(MantisNode):
    def __init__(self, signature, base_tree, ui_node, in_out):
        super().__init__(signature, base_tree)
        self.node_type = 'UTILITY'
        self.prepared, self.executed = True, True; sockets = []
        self.in_out = in_out
        # init the sockets based on in/out, then set up traversal
        collection = ui_node.inputs if in_out == 'INPUT' else ui_node.outputs
        for socket in collection: sockets.append(socket.identifier)
        self.inputs.init_sockets(sockets); self.outputs.init_sockets(sockets)
        for socket in self.inputs.keys(): self.set_traverse( [(socket, socket)] )
        self.execution_prepared=True

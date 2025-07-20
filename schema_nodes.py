from .node_container_common import *
from math import pi, tau
from .base_definitions import MantisNode, NodeSocket

def TellClasses():
    return [
        SchemaIndex,
        SchemaArrayInput,
        SchemaArrayInputGet,
        SchemaArrayInputAll,
        SchemaArrayOutput,
        SchemaConstInput,
        SchemaConstOutput,
        SchemaOutgoingConnection,
        SchemaIncomingConnection,
    ]

def schema_init_sockets(nc, is_input = True, in_out='INPUT', category=''):
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
                    sockets.init_sockets([item.name])
    nc.init_parameters()


class SchemaNode(MantisNode):
    def __init__(self, signature, base_tree, socket_templates=[]):
        super().__init__(signature, base_tree, socket_templates)
        self.node_type = 'SCHEMA'
        self.prepared = True; self.executed = True
        self.execution_prepared = True # should not affect execution!

    def reset_execution(self):
        super().reset_execution()
        self.prepared, self.executed = True, True
        raise RuntimeError( "43 Code thought to unreachable has been reached."
                           f"Please report this as a bug. {self}")


class SchemaIndex(SchemaNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        outputs = [
          "Index",
          "Schema Length",
        ]
        self.outputs.init_sockets(outputs)
        self.init_parameters()

class SchemaArrayInput(SchemaNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        schema_init_sockets(self, is_input=False, in_out='INPUT', category='Array')


class SchemaArrayInputGet(SchemaNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "OoB Behaviour" ,
            "Index"         ,
        ]
        self.inputs.init_sockets(inputs)
        schema_init_sockets(self, is_input=False, in_out='INPUT', category='Array')

class SchemaArrayInputAll(SchemaNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        schema_init_sockets(self, is_input=False, in_out='INPUT', category='Array')

class SchemaArrayOutput(SchemaNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        schema_init_sockets(self, is_input=True, in_out='OUTPUT', category='Array')

class SchemaConstInput(SchemaNode):
    def __init__(self, signature, base_tree, parent_schema_node=None):
        super().__init__(signature, base_tree)
        if parent_schema_node:
            # this allows us to generate the Constant Input from a normal Node Group
            # and treat the node group as a schema
            parent_tree = parent_schema_node.prototype.node_tree
            sockets=self.outputs
            for item in parent_tree.interface.items_tree:
                if item.item_type == 'PANEL': continue
                if item.in_out == 'INPUT':
                    sockets.init_sockets([item.name])
            self.init_parameters()
            
        else:
            schema_init_sockets(self, is_input=False, in_out='INPUT', category='Constant')


class SchemaConstOutput(SchemaNode):
    def __init__(self, signature, base_tree, parent_schema_node=None):
        super().__init__(signature, base_tree)
        inputs = [
            "Expose at Index",
        ]
        self.inputs.init_sockets(inputs)
        if parent_schema_node:
            # this allows us to generate the Constant Input from a normal Node Group
            # and treat the node group as a schema
            parent_tree = parent_schema_node.prototype.node_tree
            sockets=self.inputs
            for item in parent_tree.interface.items_tree:
                if item.item_type == 'PANEL': continue
                if item.in_out == 'OUTPUT':
                    sockets.init_sockets([item.name, "Expose at Index",])
            self.init_parameters()
            self.parameters['Expose at Index"']=1

        else:
            schema_init_sockets(self, is_input=True, in_out='OUTPUT', category='Constant')


        
class SchemaOutgoingConnection(SchemaNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        schema_init_sockets(self, is_input=True, in_out='INPUT', category='Connection')

        
class SchemaIncomingConnection(SchemaNode):
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        schema_init_sockets(self, is_input=False, in_out='OUTPUT', category='Connection')
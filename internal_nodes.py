from .utilities.node_common import *
from bpy.types import Node
from .base_definitions import MantisNode, MantisSocketTemplate
from uuid import uuid4


# this function is kind of confusing and is very important,
# so it bears a full explanation: its purpose is to connect
# the links going into a group to the nodes in that group.
# FIRST we connect all the incoming links into the Group Node to
# a Group Interface node that does nothing but mark the entrance.
# Then, we connect all the outgoing links back to the nodes
# that had incoming links, so the nodes OUTSIDE the Node Group
# are connected directly to BOTH the GroupInterface and the
# nodes INSIDE the node group.
# we give the GroupInterface nodes an obscenely high
# multi_input_sort_id so that they are always last.
# but since these links are going IN, they shouldn't cause any problems.
# the sub_sort_id is set here in case there are UI links which represent
# multiple Mantis links - the mantis links are sorted within the UI links
# and the UI links are sorted as normal, so all the links are in the right
# order.... probably. BUG here?
# I want the Group Interface nodes to be part of the hierarchy...
# but I want to cut the links. hmmm what to do? Fix it if it causes problems.
# solution to hypothetical BUG could be to do traversal on the links
# instead of the sockets.
# NOTE: using NodeSocket.links is slow, it should be cached
def grp_node_reroute_common(in_node, out_node, interface):
    from .base_definitions import links_sort_key
    for in_node_input in in_node.inputs:
        i = 0
        if len(in_node_input.links)>1: # sort here to ensure correct sub_sort_id
            in_node_input.links.sort(key=links_sort_key)
        while (in_node_input.links):
            in_link = in_node_input.links.pop()
            from_node = in_link.from_node; from_socket = in_link.from_socket
            link = from_node.outputs[from_socket].connect(
                interface,in_node_input.name, sort_id = 2**16, sub_sort_id=i)
            i += 1; in_link.die()
    for out_node_output in out_node.outputs:
        while (out_node_output.links):
            out_link = out_node_output.links.pop()
            to_node = out_link.to_node; to_socket = out_link.to_socket
            for j, l in enumerate(interface.inputs[out_node_output.name].links):
                # we are connecting the link from the ORIGINAL output to the FINAL input.
                link = l.from_node.outputs[l.from_socket].connect(
                    to_node, to_socket, sort_id = out_link.multi_input_sort_id)
                link.sub_sort_id = j
            out_link.die()

def reroute_links_grp(group, all_nodes):
    interface = all_nodes.get( ( *group.signature, "InputInterface") )
    if group.inputs:
        if group_input := all_nodes.get(( *group.signature, "NodeGroupInput")):
            grp_node_reroute_common(group, group_input, interface)
        else:
            raise RuntimeError("internal error: failed to enter a node group ")

def reroute_links_grpout(group_output, all_nodes):
    if (group_output_node := all_nodes.get( ( *group_output.signature[:-1],) )):
        interface = all_nodes.get( ( *group_output_node.signature, "OutputInterface") )
        grp_node_reroute_common(group_output, group_output_node, interface)
    else:
        prOrange(f"WARN: unconnected outputs from a node group "
                 "(maybe you are running the tree from inside a node group?)")


# TODO: make node_type a class property like it is for everything else
# I can't do this without making some changes to schema and anything that
# checks for DUMMY SCHEMA
class DummyNode(MantisNode):
    __slots__ = ("node_type", "ui_node", "solver", "uuid", "reroute_links_type")
    def __init__(self, signature, base_tree, ui_node = None, ui_signature=None):
        super().__init__(signature, base_tree)
        self.ui_node = ui_node
        self.prepared = True
        self.uuid = uuid4()
        self.solver = None
        self.node_type = 'DUMMY'
        self.reroute_links_type=""
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

    def reroute_links(self, all_nodes):
        match self.reroute_links_type:
            case "group":
                reroute_links_grp(self, all_nodes)
            case "out":
                reroute_links_grpout(self, all_nodes)

class NoOpNode(MantisNode):
    __slots__ = ()
    node_type = 'UTILITY'
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        self.inputs['Input'] = NodeSocket(is_input=True, node=self, name='Input')
        self.outputs['Output'] = NodeSocket(is_input=False, node=self, name='Output')
        self.init_parameters()
        self.set_traverse([("Input", "Output")])
        self.prepared, self.executed = True, True
        self.execution_prepared=True
    # this node is useful for me to insert in the tree and use for debugging especially connections.

from .socket_definitions import no_default_value
from .execution.overlays import handle_overlay_detect, get_socket_idname_data_type, parser_handle_text
from mathutils import Matrix

class AutoGenNode(MantisNode):
    __slots__ = ()
    node_type = 'UTILITY'
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        self.prepared, self.executed = True, True
        self.execution_prepared=True

    def reset_execution(self):
        super().reset_execution()
        self.prepared, self.executed = True, True

    # This is a re-implementation of the fill parameters in the base class
    # but it is possible to streamline a few things here
    # so rather than add another branch in the main class I have
    # decided to duplicate some code. This isn't great but it's a little faster.
    def fill_parameters(self, ui_node=None)  -> None:
        ui_inputs = ui_node.inputs
        for key in self.parameters.keys():
            if node_socket := ui_inputs.get(key):
                if node_socket.bl_idname in no_default_value: continue
                elif node_socket.is_linked: continue
                # unlike the general case, we don't need to bother with outputs at all for autogen nodes
                if node_socket.bl_idname == 'MatrixSocket':
                    v = node_socket.default_value
                    self.parameters[key] = Matrix(( tuple(v[0:4]),
                                                    tuple(v[4:8]),
                                                    tuple(v[8:12]),
                                                    tuple(v[12:16]) ))
                elif (value := node_socket.default_value) is not None:
                    if hasattr(node_socket, 'use_overlay') and node_socket.use_overlay:
                        value = node_socket.overlay_text
                        if get_socket_idname_data_type(node_socket.bl_idname) != str:
                            value = parser_handle_text(value)
                    # THIS is the most important reason I am using a custom fill here:
                    # The overlay for this kind of node must use the identifier, not the name
                    if isinstance(value, str) and "$" in value:
                        value = handle_overlay_detect(self,
                            node_socket.identifier, node_socket.bl_idname, value)
                    self.parameters[key] = value
                else:
                    raise RuntimeError(wrapRed("No value found for " + self.__repr__() + " when filling out node parameters for " + ui_node.name + "::"+node_socket.name))



    

# The Group Interface node is responsible for gathering node connections
#   going in or out of the group and connecting back out the other side
# this is also where caching and overlays live
class GroupInterface(MantisNode):
    __slots__ = ("in_out", "tree_name")
    node_type = 'INTERFACE'
    def __init__(self, signature, base_tree, in_out, mContext, ui_node = None, items_tree = None, ):
        super().__init__(signature, base_tree)
        self.prepared, self.executed = True, True
        self.in_out = in_out
        if hasattr(ui_node, "node_tree"):
            self.tree_name = ui_node.node_tree.name
        else: # It is an output node
            self.tree_name = ui_node.id_data.name
        # init the sockets based on in/out, then set up traversal
        
        # the index and length are like constant inputs.
        if self.in_out == 'SCHEMA_INPUT':
            self.outputs["Schema Length"] = NodeSocket(is_input=False, node=self, name="Schema Length")
        if 'SCHEMA' in self.in_out: 
            self.outputs["Index"]  = NodeSocket(is_input=False, node=self, name="Index")
               
        for i, item in enumerate(items_tree):
            if item.item_type == 'PANEL': continue
            is_connection = False; is_array = False
            if  hasattr(item, 'is_connection'): # in older files and for some types this happens
                is_connection = item.is_connection # BUG really every socket should be a Mantis interface type
                is_array = item.is_array
            if (self.in_out in {'INPUT', 'OUTPUT'} and item.in_out == self.in_out):
                source = self.inputs[item.identifier] = NodeSocket(is_input=True, node=self, name=item.identifier)
                target = self.outputs[item.identifier] = NodeSocket(is_input=False, node=self, name=item.identifier)
                self.set_traverse( [(source.name, target.name)] )
            elif self.in_out == 'SCHEMA_INPUT':
                if is_array: continue  # I'll skip these for now
                source = self.inputs[item.identifier] = NodeSocket(is_input=True, node=self, name=item.identifier)
                target = self.outputs[item.identifier] = NodeSocket(is_input=False, node=self, name=item.identifier)
                self.set_traverse( [(source.name, target.name)] )
            elif self.in_out == 'SCHEMA_BETWEEN':
                if is_connection: # we need these at every in-between because they are modified between
                    source = self.inputs[item.identifier] = NodeSocket(is_input=True, node=self, name=item.identifier)
                    target = self.outputs[item.identifier] = NodeSocket(is_input=False, node=self, name=item.identifier)
                    self.set_traverse( [(source.name, target.name)] )
        if self.in_out in {'INPUT', 'SCHEMA_INPUT', 'SCHEMA_BETWEEN'}:
            # We need to store the input interface nodes for looking up overlay variables
            # Important to set the mContext's interface stuff up so the rest of the tree has access to this
            # Why not include the name of the node? It's easier to look up based on tree path
            # And in order to prevent ambiguity, we make lists for each one so that schema interfaces come together
            if mContext.input_interface_nodes.get(self.signature[:-1], None) is None:
                mContext.input_interface_nodes[ self.signature[:-1] ] = [ self ]
            else: # it's a schema so we add the next interface to the list
                mContext.input_interface_nodes[ self.signature[:-1] ].append(self)
        self.execution_prepared=True

    def get_tree_interface_items(self):
        from bpy import data as bpy_data
        if tree := bpy_data.node_groups.get(self.tree_name):
            return tree.interface.items_tree

    def evaluate_input(self, input_name, index=0):
        # I'm hardcoding this so that the schema length overlay is available as just 'length'
        if input_name == 'Length': input_name = 'Schema'
        value = super().evaluate_input(input_name, index)
        # This node should cache the result for faster lookup later
        self.parameters[input_name] = value
        return value
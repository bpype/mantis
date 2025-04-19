#Mantis Nodes Base
import bpy
from bpy.props import (BoolProperty, StringProperty, EnumProperty, CollectionProperty, \
    IntProperty, IntVectorProperty, PointerProperty, BoolVectorProperty)
from . import ops_nodegroup
from bpy.types import NodeTree, Node, PropertyGroup, Operator, UIList, Panel

from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

from .utilities import get_socket_maps, relink_socket_map, do_relink

FLOAT_EPSILON=0.0001 # used to check against floating point inaccuracy

def TellClasses():
    #Why use a function to do this? Because I don't need every class to register.
    return [ MantisTree,
             SchemaTree,
             MantisNodeGroup,
             SchemaGroup,
           ]
def error_popup_draw(self, context):
    self.layout.label(text="Error executing tree. See Console.")

mantis_root = ".".join(__name__.split('.')[:-1]) # absolute HACK


# https://docs.blender.org/api/master/bpy.types.NodeTree.html#bpy.types.NodeTree.valid_socket_type
# thank you, Sverchok
def valid_interface_types(cls : NodeTree, socket_idname : str):
    from .socket_definitions import tell_valid_bl_idnames, TellClasses
    #TODO: do the versioning code to handle this so it can be in all versions
    if bpy.app.version <= (4,4,0): # should work in 4.4.1
        return socket_idname in [cls.bl_idname for cls in TellClasses()]
    else: # once versioning is finished this will be unnecesary.
        return socket_idname in tell_valid_bl_idnames()


def fix_reroute_colors(tree):
    context = bpy.context
    if any((tree.is_executing, tree.is_exporting, tree.do_live_update==False, context.space_data is None) ):
        return
    from collections import deque
    from .utilities import socket_seek
    from .socket_definitions import MantisSocket
    reroutes_without_color = deque()
    for n in tree.nodes:
        if n.bl_idname=='NodeReroute' and n.inputs[0].bl_idname == "NodeSocketColor":
            reroutes_without_color.append(n)
    try:
        while reroutes_without_color:
            rr = reroutes_without_color.pop()
            if rr.inputs[0].is_linked:
                link = rr.inputs[0].links[0]
                from_node = link.from_node
                socket = socket_seek(link, tree.links)
                if isinstance(socket, MantisSocket):
                    rr.socket_idname = socket.bl_idname
    except Exception as e:
        print(wrapOrange("WARN: Updating reroute color failed with exception: ")+wrapWhite(f"{e.__class__.__name__}"))

class MantisTree(NodeTree):
    '''A custom node tree type that will show up in the editor type list'''
    bl_idname = 'MantisTree'
    bl_label = "Rigging Nodes"
    bl_icon = 'OUTLINER_OB_ARMATURE'
    
    tree_valid:BoolProperty(default=False)
    do_live_update:BoolProperty(default=True) # use this to disable updates for e.g. scripts
    num_links:IntProperty(default=-1)
    filepath:StringProperty(default="", subtype='FILE_PATH')
    is_executing:BoolProperty(default=False)
    is_exporting:BoolProperty(default=False)
    execution_id:StringProperty(default='')
    mantis_version:IntVectorProperty(default=[0,9,2])
    # this prevents the node group from executing on the next depsgraph update
    # because I don't always have control over when the dg update happens.
    prevent_next_exec:BoolProperty(default=False)
    
    parsed_tree={}

    if (bpy.app.version < (4, 4, 0)):  # in 4.4 this leads to a crash
        @classmethod
        def valid_socket_type(cls : NodeTree, socket_idname: str):
            return valid_interface_types(cls, socket_idname)
    
    def update(self): # set the reroute colors
        if (bpy.app.version >= (4,4,0)):
            fix_reroute_colors(self)

    def update_tree(self, context = None):
        if self.is_exporting:
            return
        # return
        self.is_executing = True
        from . import readtree
        prGreen("Validating Tree: %s" % self.name)
        try:
            self.parsed_tree = readtree.parse_tree(self)
            if context:
                self.display_update(context)
            self.is_executing = False
            self.tree_valid = True
        except GraphError as e:
            prRed("Failed to update node tree due to error.")
            self.tree_valid = False
            self.is_executing = False
            raise e
        finally:
            self.is_executing = False

    
    def display_update(self, context):
        if self.is_exporting:
            return
        self.is_executing = True
        current_tree = bpy.context.space_data.path[-1].node_tree
        for node in current_tree.nodes:
            if hasattr(node, "display_update"):
                try:
                    node.display_update(self.parsed_tree, context)
                except Exception as e:
                    print("Node \"%s\" failed to update display with error: %s" %(wrapGreen(node.name), wrapRed(e)))
        self.is_executing = False
        
        # TODO: deal with invalid links properly.
        #    - Non-hierarchy links should be ignored in the circle-check and so the links should be marked valid in such a circle
        #    - hierarchy-links should be marked invalid and prevent the tree from executing.

    def execute_tree(self,context, error_popups = False):
        self.prevent_next_exec = False
        if self.is_exporting:
            return
        # return
        prGreen("Executing Tree: %s" % self.name)
        self.is_executing = True
        from . import readtree
        try:
            readtree.execute_tree(self.parsed_tree, self, context, error_popups)
        except RecursionError as e:
            prRed("Recursion error while parsing tree.")
        finally:
            self.is_executing = False

class SchemaTree(NodeTree):
    '''A node tree representing a schema to generate a Mantis tree'''
    bl_idname = 'SchemaTree'
    bl_label = "Rigging Nodes Schema"
    bl_icon = 'RIGID_BODY_CONSTRAINT'

    # these are only needed for consistent interface, but should not be used
    do_live_update:BoolProperty(default=True) # default to true so that updates work
    is_executing:BoolProperty(default=False)
    is_exporting:BoolProperty(default=False)

    mantis_version:IntVectorProperty(default=[0,9,2])

    if (bpy.app.version < (4, 4, 0)):  # in 4.4 this leads to a crash
        @classmethod
        def valid_socket_type(cls : NodeTree, socket_idname: str):
            return valid_interface_types(cls, socket_idname)

    def update(self): # set the reroute colors
        if (bpy.app.version >= (4,4,0)):
            fix_reroute_colors(self)


from dataclasses import dataclass, field
from typing import Any

@dataclass
class MantisSocketTemplate():
    name             : str = field(default="")
    bl_idname        : str = field(default="")
    traverse_target  : str = field(default="")
    identifier       : str = field(default="")
    display_shape    : str = field(default="") # for arrays
    category         : str = field(default="") # for use in display update
    blender_property : str | tuple[str] = field(default="") # for props_sockets -> evaluate sockets
    is_input         : bool = field(default=False)
    hide             : bool = field(default=False)
    use_multi_input  : bool = field(default=False)
    default_value    : Any = field(default=None)
    


#TODO: do a better job explaining how MantisNode and MantisUINode relate.

class MantisUINode:
    """
        This class contains the common user-interface features of Mantis nodes.
        MantisUINode objects will spawn one or more MantisNode objects when the graph is evaluated.
        The MantisNode objects will pull the data from the UI node and use it to generate the graph.
    """
    mantis_node_library=''
    mantis_node_class_name=''
    mantis_class=None
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['MantisTree', 'SchemaTree'])
                
    @classmethod
    def set_mantis_class(self):
        from importlib import import_module
        # do not catch errors, they should cause a failure.
        try:
            module = import_module(self.mantis_node_library, package=mantis_root)
            self.mantis_class=getattr(module, self.mantis_node_class_name)
        except Exception as e:
            print(self)
            raise e

    def insert_link(self, link):
        if (bpy.app.version >= (4, 4, 0)):
            return # this causes a crash due to a bug.
        context = bpy.context
        if context.space_data:
            node_tree = context.space_data.path[0].node_tree
            if node_tree.do_live_update:
                node_tree.update_tree(context)
                if (link.to_socket.is_linked == False):
                    node_tree.num_links+=1
                elif (link.to_socket.is_multi_input):
                    node_tree.num_links+=1
    
    def init_sockets(self, socket_templates : tuple[MantisSocketTemplate]):
        for template in socket_templates:
            collection = self.outputs
            if template.is_input:
                collection = self.inputs
            identifier = template.name
            if template.identifier:
                identifier = template.identifier
            socket = collection.new(
                template.bl_idname,
                template.name,
                identifier=identifier,
                use_multi_input=template.use_multi_input
            )
            socket.hide= template.hide
            if template.category:
                # a custom property for the UI functions to use.
                socket['category'] = template.category
            if template.default_value is not None:
                socket.default_value = template.default_value
                # this can throw a TypeError - it is the caller's
                #   responsibility to send the right type.
        
            
class SchemaUINode(MantisUINode):
    mantis_node_library='.schema_containers'
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['SchemaTree'])

class LinkNode(MantisUINode):
    mantis_node_library='.link_containers'
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['MantisTree', 'SchemaTree'])
    
class xFormNode(MantisUINode):
    mantis_node_library='.xForm_containers'
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['MantisTree', 'SchemaTree'])

class DeformerNode(MantisUINode):
    mantis_node_library='.deformer_containers'
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['MantisTree', 'SchemaTree'])


def poll_node_tree(self, object):
    forbid = []
    context = bpy.context
    if context.space_data:
        if context.space_data.path:
            for path_item in context.space_data.path:
                forbid.append(path_item.node_tree.name)
    if isinstance(object, MantisTree) and object.name not in forbid:
        return True
    return False

# TODO: try and remove the extra loop used here... but it is OK for now
def should_remove_socket(node, socket):
    # a function to check if the socket is in the interface
    id_found = False
    for item in node.node_tree.interface.items_tree:
        if item.item_type != "SOCKET": continue
        if item.identifier == socket.identifier:
            id_found = True; break
    return not id_found


# TODO: try to check identifiers instead of name.
def node_group_update(node, force = False):
    if not node.is_updating:
        raise RuntimeError("Cannot update node while it is not marked as updating.")
    if not force:
        if (node.id_data.do_live_update == False) or  \
           (node.id_data.is_executing == True) or \
           (node.id_data.is_exporting == True):
            return
    # note: if (node.id_data.is_exporting == True) I need to be able to update so I can make links.

    toggle_update = node.id_data.do_live_update
    node.id_data.do_live_update = False

    identifiers_in={socket.identifier:socket for socket in node.inputs}
    identifiers_out={socket.identifier:socket for socket in node.outputs}
    indices_in,indices_out={},{} # check by INDEX to see if the socket's name/type match.
    for collection, map in [(node.inputs, indices_in), (node.outputs, indices_out)]:
        for i, socket in enumerate(collection):
            map[socket.identifier]=i

    if node.node_tree is None:
        node.inputs.clear(); node.outputs.clear()
        node.id_data.do_live_update = toggle_update
        return
    found_in, found_out = [], []
    update_input, update_output = False, False
    for item in node.node_tree.interface.items_tree:
        if item.item_type != "SOCKET": continue
        if item.in_out == 'OUTPUT':
            if s:= identifiers_out.get(item.identifier): # if the requested output doesn't exist, update
                found_out.append(item.identifier)
                if (indices_out[s.identifier]!=item.index): update_output=True; continue
                if update_output: continue
                if s.bl_idname != item.socket_type: update_output = True; continue
            else: update_output = True; continue
        else:
            if s:= identifiers_in.get(item.identifier): # if the requested input doesn't exist, update
                found_in.append(item.identifier)
                if (indices_in[s.identifier]!=item.index): update_input=True; continue
                if update_input: continue # done here
                if s.bl_idname != item.socket_type: update_input = True; continue
            else: update_input = True; continue
    
    # Schema has an extra input for Length and for Extend.
    if node.bl_idname == 'MantisSchemaGroup':
        found_in.extend(['Schema Length', ''])

    # if we have too many elements, just get rid of the ones we don't need
    if len(node.inputs) > len(found_in):#
        for inp in node.inputs:
            if inp.identifier in found_in: continue
            node.inputs.remove(inp)
    if len(node.outputs) > len(found_out):
        for out in node.outputs:
            if out.identifier in found_out: continue
            node.outputs.remove(out)
    #
    if len(node.inputs) > 0 and (inp := node.inputs[-1]).bl_idname == 'WildcardSocket' and inp.is_linked:
        update_input = True
    #
    if not (update_input or update_output):
        node.id_data.do_live_update = toggle_update
        return

    if update_input or update_output:
        socket_maps = get_socket_maps(node,)
        if socket_maps:
            socket_map_in, socket_map_out = socket_maps
        if node.bl_idname == "MantisSchemaGroup" and \
            len(node.inputs)+len(node.outputs)<=2 and\
                len(node.node_tree.interface.items_tree) > 0:
            socket_map_in, socket_map_out = None, None
            # We have to initialize the node because it only has its base inputs.
        elif socket_maps is None:
            node.id_data.do_live_update = toggle_update
            return

        if update_input :
            if node.bl_idname == 'MantisSchemaGroup':
                schema_length=0
                if sl := node.inputs.get("Schema Length"):
                    schema_length = sl.default_value
                # sometimes this isn't available yet # TODO not happy about this solution
            remove_me=[]
            # remove all found map items but the Schema Length input (reuse it)
            for i, socket in enumerate(node.inputs):
                if socket.identifier == "Schema Length" and i == 0:
                    continue
                elif (socket_map_in is None) or socket.identifier in socket_map_in.keys():
                    remove_me.append(socket)
                elif should_remove_socket(node, socket):
                    remove_me.append(socket)
            while remove_me:
                node.inputs.remove(remove_me.pop())
            
        if update_output:
            remove_me=[]
            for socket in node.outputs:
                if (socket_map_out is None) or socket.identifier in socket_map_out.keys():
                    remove_me.append(socket)
                elif should_remove_socket(node, socket):
                    remove_me.append(socket)
            while remove_me:
                node.inputs.remove(remove_me.pop())


        from .utilities import relink_socket_map_add_socket

        reorder_me_input = []; input_index = 0
        reorder_me_output = []; output_index = 0

        def update_group_sockets(interface_item, is_input):
            socket_map = socket_map_in if is_input else socket_map_out
            socket_collection = node.inputs if is_input else node.outputs
            counter = input_index if is_input else output_index
            reorder_collection = reorder_me_input if is_input else reorder_me_output
            if socket_map:
                if item.identifier in socket_map.keys():
                    socket = relink_socket_map_add_socket(node, socket_collection, item)
                    do_relink(node, socket, socket_map, item.in_out)
                else:
                    for has_socket in socket_collection:
                        if has_socket.bl_idname == item.socket_type and \
                            has_socket.name == item.name:
                            reorder_collection.append((has_socket, counter))
                            break
                    else:
                        socket = relink_socket_map_add_socket(node, socket_collection, item)
            else:
                socket = relink_socket_map_add_socket(node, socket_collection, item)
            counter += 1

        for item in node.node_tree.interface.items_tree:
            if item.item_type != "SOCKET": continue
            if (item.in_out == 'INPUT' and update_input):
                update_group_sockets(item, True)
            if (item.in_out == 'OUTPUT' and update_output):
                update_group_sockets(item, False)

        both_reorders = zip([reorder_me_input, reorder_me_output], [node.inputs, node.outputs])
        for reorder_task, collection in both_reorders:
            for socket, position in reorder_task:
                for i, s  in enumerate(collection): # get the index
                    if s.identifier == socket.identifier: break
                else:
                    prRed(f"WARN: could not reorder socket {socket.name}")
                to_index = position
                if (not socket.is_output) and node.bl_idname == "MantisSchemaGroup":
                    to_index+=1
                collection.move(i, to_index)

        # at this point there is no wildcard socket
        if socket_map_in and '__extend__' in socket_map_in.keys():
            do_relink(node, None, socket_map_in, in_out='INPUT', parent_name='Constant' )

        node.id_data.do_live_update = toggle_update


def node_tree_prop_update(self, context):
    if self.is_updating: # update() can be called from update() and that leads to an infinite loop.
        return           # so we check if an update is currently running.
    self.is_updating = True
    def init_schema(self, context):
        if len(self.inputs) == 0:
            self.inputs.new("UnsignedIntSocket", "Schema Length", identifier='Schema Length')
        if self.inputs[-1].bl_idname != "WildcardSocket":
            self.inputs.new("WildcardSocket", "", identifier="__extend__")
    init_schema(self, context)
    try:
        node_group_update(self, force=True)
    finally: # ensure this line is run even if there is an error
        self.is_updating = False
    if self.bl_idname in ['MantisSchemaGroup'] and self.node_tree is not None:
        init_schema(self, context)

from bpy.types import NodeCustomGroup

def group_draw_buttons(self, context, layout):
    row = layout.row(align=True)
    row.prop(self, "node_tree", text="")
    if self.node_tree is None:
        row.operator("mantis.new_node_tree", text="", icon='PLUS', emboss=True)
    else:
        row.operator("mantis.edit_group", text="", icon='NODETREE', emboss=True)

class MantisNodeGroup(Node, MantisUINode):
    bl_idname = "MantisNodeGroup"
    bl_label = "Node Group"

    node_tree:PointerProperty(type=NodeTree, poll=poll_node_tree, update=node_tree_prop_update,)
    is_updating:BoolProperty(default=False)

    def draw_label(self):
        if self.node_tree is None:
            return "Node Group"
        else:
            return self.node_tree.name
    
    def draw_buttons(self, context, layout):
        group_draw_buttons(self, context, layout)
        
    def update(self):
        if self.node_tree is None:
            return
        if self.is_updating: # update() can be called from update() and that leads to an infinite loop.
            return           # so we check if an update is currently running.
        live_update = self.id_data.do_live_update
        self.is_updating = True
        try:
            node_group_update(self)
        finally: # we need to reset this regardless of whether or not the operation succeeds!
            self.is_updating = False
            self.id_data.do_live_update = live_update # ensure this remains the same


class GraphError(Exception):
    pass

def get_signature_from_edited_tree(node, context):
    sig_path=[None,]
    for item in context.space_data.path[:-1]:
        sig_path.append(item.node_tree.nodes.active.name)
    return tuple(sig_path+[node.name])

def poll_node_tree_schema(self, object):
    if isinstance(object, SchemaTree):
        return True
    return False


# TODO tiny UI problem - inserting new links into the tree will not place them in the right place.

class SchemaGroup(Node, MantisUINode):
    bl_idname = "MantisSchemaGroup"
    bl_label = "Node Schema"
    
    node_tree:PointerProperty(type=NodeTree, poll=poll_node_tree_schema, update=node_tree_prop_update,)
    is_updating:BoolProperty(default=False)

    def draw_buttons(self, context, layout):
        group_draw_buttons(self, context, layout)

    def draw_label(self):
        if self.node_tree is None:
            return "Schema Group"
        else:
            return self.node_tree.name
        
    def update(self):
        if self.is_updating: # update() can be called from update() and that leads to an infinite loop.
            return           # so we check if an update is currently running.
        if self.node_tree is None:
            return
        live_update = self.id_data.do_live_update
        self.is_updating = True
        try:
            node_group_update(self)
            # reset things if necessary:
            if self.node_tree:
                if len(self.inputs) == 0:
                    self.inputs.new("UnsignedIntSocket", "Schema Length", identifier='Schema Length')
                if self.inputs[-1].identifier != "__extend__":
                    self.inputs.new("WildcardSocket", "", identifier="__extend__")
        finally: # we need to reset this regardless of whether or not the operation succeeds!
            self.is_updating = False
            self.id_data.do_live_update = live_update # ensure this remains the same



NODES_REMOVED=["xFormRootNode"]
                 # Node bl_idname, # Socket Name
SOCKETS_REMOVED=[("UtilityDriverVariable", "Transform Channel"),
                 ("xFormRootNode","World Out"),
                 ("UtilitySwitch","xForm"),
                 ("LinkDrivenParameter", "Enable")]
                  # Node Class           #Prior bl_idname  # prior name # new bl_idname # new name, # Multi
SOCKETS_RENAMED=[ ("LinkDrivenParameter", "DriverSocket",   "Driver",     "FloatSocket",  "Value",  False)]

                # NODE CLASS NAME             IN_OUT    SOCKET TYPE     SOCKET NAME     INDEX   MULTI     DEFAULT
SOCKETS_ADDED=[("DeformerMorphTargetDeform", 'INPUT', 'BooleanSocket', "Use Shape Key", 1,      False,    False),
               ("DeformerMorphTargetDeform", 'INPUT', 'BooleanSocket', "Use Offset",    2,      False,    True),
               ("UtilityFCurve",             'INPUT',  "eFCrvExtrapolationMode", "Extrapolation Mode", 0, False, 'CONSTANT'),
               ("LinkCopyScale",             'INPUT',  "BooleanSocket", "Additive",     3,      False, False)]

# replace names with bl_idnames for reading the tree and solving schemas.
replace_types = ["NodeGroupInput", "NodeGroupOutput", "SchemaIncomingConnection",
                 "SchemaArrayInput", "SchemaArrayInputAll", "SchemaConstInput", "SchemaConstOutput",
                 "SchemaIndex", "SchemaOutgoingConnection", "SchemaArrayOutput","SchemaArrayInputGet",
                ]

# anything that gets properties added in the graph... this is a clumsy approach but I need to watch for this
#   in schema generation and this is the easiest way to do it for now.
custom_props_types = ["LinkArmature", "UtilityKeyframe", "UtilityFCurve", "UtilityDriver", "xFormBone"]

# filters for determining if a link is a hierarchy link or a non-hierarchy (cyclic) link.
from_name_filter = ["Driver",]
to_name_filter = [
                   "Custom Object xForm Override",
                   "Custom Object",
                   "Deform Bones",
                 ]

# nodes that must be solved as if they were Schema because they send arrays out.
array_output_types = [
    'UtilityArrayGet', 'UtilityKDChoosePoint', 'UtilityKDChooseXForm',
]

class MantisNode:
    """
        This class contains the basic interface for a Mantis Node.
        A MantisNode is used internally by Mantis to represent the final evaluated node graph.
        It gets generated with data from a MantisUINode when the graph is read.
    """
    def __init__(self, signature : tuple,
                 base_tree : bpy.types.NodeTree,
                 socket_templates : list[MantisSocketTemplate]=[]):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = MantisNodeSocketCollection(node=self, is_input=True)
        self.outputs = MantisNodeSocketCollection(node=self, is_input=False)
        self.parameters = {}
        self.drivers = {}
        self.node_type='UNINITIALIZED'
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies, self.dependencies = [], []
        self.prepared = False
        self.executed = False
        self.socket_templates = socket_templates
        if self.socket_templates:
            self.init_sockets()

    def init_sockets(self) -> None:
        self.inputs.init_sockets(self.socket_templates)
        self.outputs.init_sockets(self.socket_templates)

    def init_parameters(self, additional_parameters = {}) -> None:
        for socket in self.inputs:
            self.parameters[socket.name] = None
        for socket in self.outputs:
            self.parameters[socket.name] = None
        for key, value in additional_parameters.items():
            self.parameters[key]=value
    
    def gen_property_socket_map(self) -> dict:
        props_sockets = {}
        for s_template in self.socket_templates:
            if not s_template.blender_property:
                continue
            if isinstance(s_template.blender_property, str):
                props_sockets[s_template.blender_property]=(s_template.name, s_template.default_value)
            elif isinstance(s_template.blender_property, tuple):
                for index, sub_prop in enumerate(s_template.blender_property):
                    props_sockets[sub_prop]=( (s_template.name, index),s_template.default_value[index] )
        return props_sockets
    
    def set_traverse(self, traversal_pairs = [(str, str)]) -> None:
        for (a, b) in traversal_pairs:
            self.inputs[a].set_traverse_target(self.outputs[b])
            self.outputs[b].set_traverse_target(self.inputs[a])
            

    def flush_links(self) -> None:
        for inp in self.inputs.values():
            inp.flush_links()
        for out in self.outputs.values():
            out.flush_links()
    
    def evaluate_input(self, input_name, index=0)  -> Any:
        from .node_container_common import trace_single_line
        if not (self.inputs.get(input_name)): # get the named parameter if there is no input
            return self.parameters.get(input_name) # this will return None if the parameter does not exist.
        # this trace() should give a key error if there is a problem
        #  it is NOT handled here because it should NOT happen - so I want the error message.
        trace = trace_single_line(self, input_name, index)
        prop = trace[0][-1].parameters[trace[1].name] #trace[0] = the list of traced nodes; read its parameters
        return prop
    
    def fill_parameters(self, ui_node=None)  -> None:
        from .utilities import get_node_prototype
        from .node_container_common import get_socket_value
        if not ui_node:
            if ( (self.signature[0] in  ["MANTIS_AUTOGENERATED", "SCHEMA_AUTOGENERATED" ]) or 
                (self.signature[-1] in ["NodeGroupOutput", "NodeGroupInput"]) ): # I think this is harmless
                return None
            else:
                ui_node = get_node_prototype(self.signature, self.base_tree)
            if not ui_node:
                raise RuntimeError(wrapRed("No node prototype found for... %s" % ( [self.base_tree] + list(self.signature[1:]) ) ) )
        for key in self.parameters.keys():
            node_socket = ui_node.inputs.get(key)
            if self.parameters[key] is not None: # the parameters are usually initialized as None.
                continue # will be filled by the node itself
            if not node_socket: #maybe the node socket has no name
                if ( ( len(ui_node.inputs) == 0) and ( len(ui_node.outputs) == 1) ):
                    # this is a simple input node.
                    node_socket = ui_node.outputs[0]
                elif key == 'Name': # for Links we just use the Node Label, or if there is no label, the name.
                    self.parameters[key] = ui_node.label if ui_node.label else ui_node.name
                    continue
                else:
                    pass
            if node_socket:
                if node_socket.bl_idname in  ['RelationshipSocket', 'xFormSocket']:
                    continue
                elif node_socket.is_linked and (not node_socket.is_output):
                    pass # we will get the value from the link, because this is a linked input port.
                # very importantly, we do not pass linked outputs- fill these because they are probably Input nodes.
                elif hasattr(node_socket, "default_value"):
                    if (value := get_socket_value(node_socket)) is not None:
                        self.parameters[key] = value
                        # TODO: try and remove the input if it is not needed (for performance speed)
                    else:
                        raise RuntimeError(wrapRed("No value found for " + self.__repr__() + " when filling out node parameters for " + ui_node.name + "::"+node_socket.name))
                else:
                    pass
    # I don't think this works! but I like the idea
    def call_on_all_ancestors(self, *args, **kwargs):
        """Resolve the dependencies of this node with the named method and its arguments.
           First, dependencies are discovered by walking backwards through the tree. Once the root
           nodes are discovered, the method is called by each node in dependency order.
           The first argument MUST be the name of the method as a string.
        """
        prGreen(self)
        if args[0] == 'call_on_all_ancestors': raise RuntimeError("Very funny!")
        from .utilities import get_all_dependencies
        from collections import deque
        # get all dependencies by walking backward through the tree.
        all_dependencies = get_all_dependencies(self)
        # get just the roots
        can_solve = deque(filter(lambda a : len(a.hierarchy_connections) == 0, all_dependencies))
        solved = set()
        while can_solve:
            node = can_solve.pop()
            print(node)
            method = getattr(node, args[0])
            method(*args[0:], **kwargs)
            solved.add(node)
            can_solve.extendleft(filter(lambda a : a in all_dependencies, node.hierarchy_connections))
            # prPurple(can_solve)
            if self in solved:
                break
        # else:
        #     for dep in all_dependencies:
        #         if dep not in solved:
        #             prOrange(dep)
        return
    
    # gets targets for constraints and deformers and should handle all cases
    def get_target_and_subtarget(self, constraint_or_deformer, input_name = "Target"):
        from bpy.types import PoseBone, Object, SplineIKConstraint
        subtarget = ''; target = self.evaluate_input(input_name)
        if target:
            if not hasattr(target, "bGetObject"):
                prRed(f"No {input_name} target found for {constraint_or_deformer.name} in {self} because there is no connected node, or node is wrong type")
                return 
            if (isinstance(target.bGetObject(), PoseBone)):
                subtarget = target.bGetObject().name
                target = target.bGetParentArmature()
            elif (isinstance(target.bGetObject(), Object) ):
                target = target.bGetObject()
            else:
                raise RuntimeError("Cannot interpret constraint or deformer target!")
        
        if   (isinstance(constraint_or_deformer, SplineIKConstraint)):
                if target and target.type not in ["CURVE"]:
                    raise GraphError(wrapRed("Error: %s requires a Curve input, not %s" %
                                    (self, type(target))))
                constraint_or_deformer.target = target# don't get a subtarget
        if (input_name == 'Pole Target'):
            constraint_or_deformer.pole_target, constraint_or_deformer.pole_subtarget = target, subtarget
        else:
            if hasattr(constraint_or_deformer, "target"):
                constraint_or_deformer.target = target
            if hasattr(constraint_or_deformer, "object"):
                constraint_or_deformer.object = target
            if hasattr(constraint_or_deformer, "subtarget"):
                constraint_or_deformer.subtarget = subtarget

    def bPrepare(self, bContext=None):
        return
    def bExecute(self, bContext=None):
        return
    def bFinalize(self, bContext=None):
        return
    def __repr__(self): 
        return self.signature.__repr__()

# do I need this and the link class above?
class DummyLink:
    #gonna use this for faking links to keep the interface consistent
    def __init__(self, from_socket, to_socket, nc_from=None, nc_to=None, original_from=None, multi_input_sort_id=0):
        self.from_socket = from_socket
        self.to_socket = to_socket
        self.nc_from = nc_from
        self.nc_to = nc_to
        self.multi_input_sort_id = multi_input_sort_id
        # self.from_node = from_socket.node
        # self.to_node = to_socket.node
        if (original_from):
            self.original_from = original_from
        else:
            self.original_from = self.from_socket
    def __repr__(self):
        return(self.nc_from.__repr__()+":"+self.from_socket.name + " -> " + self.nc_to.__repr__()+":"+self.to_socket.name)


def detect_hierarchy_link(from_node, from_socket, to_node, to_socket,):
    if to_node.node_type in ['DUMMY_SCHEMA', 'SCHEMA']:
        return False
    if (from_socket in from_name_filter) or (to_socket in to_name_filter):
        return False
    # if from_node.__class__.__name__ in ["UtilityCombineVector", "UtilityCombineThreeBool"]:
    #     return False
    return True

class NodeLink:
    from_node = None
    from_socket = None
    to_node = None
    to_socket = None
    
    def __init__(self, from_node, from_socket, to_node, to_socket, multi_input_sort_id=0):
        if from_node.signature == to_node.signature:
            raise RuntimeError("Cannot connect a node to itself.")
        self.from_node = from_node
        self.from_socket = from_socket
        self.to_node = to_node
        self.to_socket = to_socket
        self.from_node.outputs[self.from_socket].links.append(self)
        # it is the responsibility of the node that uses these links to sort them correctly based on the sort_id
        self.multi_input_sort_id = multi_input_sort_id
        self.to_node.inputs[self.to_socket].links.append(self)
        self.is_hierarchy = detect_hierarchy_link(from_node, from_socket, to_node, to_socket,)
        self.is_alive = True
    
    def __repr__(self):
        return self.from_node.outputs[self.from_socket].__repr__() + " --> " + self.to_node.inputs[self.to_socket].__repr__()
        # link_string =   # if I need to colorize output for debugging.
        # if self.is_hierarchy:
        #     return wrapOrange(link_string)
        # else:
        #     return wrapWhite(link_string)
    
    def die(self):
        if "Choose" in "".join(self.from_node.signature[1:]):
            prRed(f"End of life: {self}")
        self.is_alive = False
        self.to_node.inputs[self.to_socket].flush_links()
        self.from_node.outputs[self.from_socket].flush_links()
    
    def insert_node(self, middle_node, middle_node_in, middle_node_out, re_init_hierarchy = True):
        to_node = self.to_node
        to_socket = self.to_socket
        self.to_node = middle_node
        self.to_socket = middle_node_in
        middle_node.outputs[middle_node_out].connect(to_node, to_socket)
        if re_init_hierarchy:
            from .utilities import init_connections, init_dependencies
            init_connections(self.from_node)
            init_connections(middle_node)
            init_dependencies(middle_node)
            init_dependencies(to_node)

class NodeSocket:
    # @property # this is a read-only property.
    # def is_linked(self):
    #     return bool(self.links)
        
    def __init__(self, is_input = False,
                 node = None, name = None,
                 traverse_target = None):
        self.can_traverse = False # to/from the other side of the parent node
        self.traverse_target = None
        self.node = node
        self.name = name
        self.is_input = is_input
        self.links = []
        self.is_linked = False
        if (traverse_target):
            self.can_traverse = True
        
    def connect(self, node, socket, sort_id=0):
        if  (self.is_input):
            to_node   = self.node; from_node = node
            to_socket = self.name; from_socket = socket
        else:
            from_node   = self.node; to_node   = node
            from_socket = self.name; to_socket = socket
        from_node.outputs[from_socket].is_linked = True
        to_node.inputs[to_socket].is_linked = True
        for l in from_node.outputs[from_socket].links:
            if l.to_node==to_node and l.to_socket==to_socket:
                return None
        new_link = NodeLink(
                from_node,
                from_socket,
                to_node,
                to_socket,
                sort_id)
        return new_link
    
    def set_traverse_target(self, traverse_target):
        self.traverse_target = traverse_target
        self.can_traverse = True
    
    def flush_links(self):
        """ Removes dead links from this socket."""
        self.links = [l for l in self.links if l.is_alive]
        self.links.sort(key=lambda a : -a.multi_input_sort_id)
        self.is_linked = bool(self.links)
        
    @property
    def is_connected(self):
        return len(self.links)>0
    
    
    def __repr__(self):
        return self.node.__repr__() + "::" + self.name

class MantisNodeSocketCollection(dict):
    def __init__(self, node, is_input=False):
        self.is_input = is_input
        self.node = node
    
    def init_sockets(self, sockets):
        for socket in sockets:
            if isinstance(socket, str):
                self[socket] = NodeSocket(is_input=self.is_input, name=socket, node=self.node)
            elif isinstance(socket, MantisSocketTemplate):
                if socket.is_input != self.is_input: continue
                self[socket.name] = NodeSocket(is_input=self.is_input, name=socket.name, node=self.node)
            else:
                raise RuntimeError(f"NodeSocketCollection keys must be str or MantisSocketTemplate, not {type(socket)}")
            
    def __delitem__(self, key):
        """Deletes a node socket by name, and all its links."""
        socket = self[key]
        for l in socket.links:
            l.die()
        super().__delitem__(key)
    
    def __iter__(self):
        """Makes the class iterable"""
        return iter(self.values())

# The Mantis Solver class is used to store the execution-specific variables that are used
#   when executing the tree
class MantisSolver():
    pass

# GOAL: make the switch to "group overlay" paradigm
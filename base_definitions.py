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


def TellClasses():
    #Why use a function to do this? Because I don't need every class to register.
    return [ MantisTree,
             SchemaTree,
             MantisNodeGroup,
             SchemaGroup,
           ]
def error_popup_draw(self, context):
    self.layout.label(text="Error executing tree. See Console.")

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

    if bpy.app.version >= (3, 2):  # in 3.1 this can lead to a crash
        @classmethod
        def valid_socket_type(cls, socket_type: str):
            # https://docs.blender.org/api/master/bpy.types.NodeTree.html#bpy.types.NodeTree.valid_socket_type
            from .socket_definitions import Tell_bl_idnames
            return socket_type in Tell_bl_idnames()
            # thank you, Sverchok
            
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

    if bpy.app.version >= (3, 2):  # in 3.1 this can lead to a crash
        @classmethod
        def valid_socket_type(cls, socket_type: str):
            # https://docs.blender.org/api/master/bpy.types.NodeTree.html#bpy.types.NodeTree.valid_socket_type
            from .socket_definitions import Tell_bl_idnames
            return socket_type in Tell_bl_idnames()
            # thank you, Sverchok
            



class MantisNode:
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['MantisTree', 'SchemaTree'])
                
    def insert_link(self, link):
        context = bpy.context
        if context.space_data:
            node_tree = context.space_data.path[0].node_tree
            from . import readtree
            if node_tree.do_live_update:
                node_tree.update_tree(context)
                if (link.to_socket.is_linked == False):
                    node_tree.num_links+=1
                elif (link.to_socket.is_multi_input):
                    node_tree.num_links+=1
            
class SchemaNode:
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['SchemaTree'])

class LinkNode(MantisNode):
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['MantisTree', 'SchemaTree'])

class xFormNode(MantisNode):
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['MantisTree', 'SchemaTree'])

class DeformerNode(MantisNode):
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['MantisTree', 'SchemaTree'])


def poll_node_tree(self, object):
    if isinstance(object, MantisTree):
        return True
    return False

# TODO: try to check identifiers instead of name.
def node_group_update(node, force = False):
    if not force:
        if (node.id_data.do_live_update == False) or (node.id_data.is_executing == True):
            return
    # note: if (node.id_data.is_exporting == True) I need to be able to update so I can make links.
    toggle_update = node.id_data.do_live_update
    node.id_data.do_live_update = False

    identifiers_in={socket.identifier:socket for socket in node.inputs}
    identifiers_out={socket.identifier:socket for socket in node.outputs}

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
                if update_output: continue
                if s.bl_idname != item.socket_type: update_output = True; continue
            else: update_output = True; continue
        else:
            if s:= identifiers_in.get(item.identifier): # if the requested input doesn't exist, update
                found_in.append(item.identifier)
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
    if len(node.outputs) > 0 and  (out := node.outputs[-1]).bl_idname == 'WildcardSocket' and out.is_linked:
        update_output = True
    #
    if not (update_input or update_output):
        node.id_data.do_live_update = toggle_update
        return

    if update_input or update_output:
        socket_map_in, socket_map_out = get_socket_maps(node)

        if update_input :
            if node.bl_idname == 'MantisSchemaGroup':
                schema_length=0
                if sl := node.inputs.get("Schema Length"):
                    schema_length = sl.default_value
                # sometimes this isn't available yet # TODO not happy about this solution

            node.inputs.clear()
            if node.bl_idname == 'MantisSchemaGroup':
                node.inputs.new("IntSocket", "Schema Length", identifier='Schema Length')
                node.inputs['Schema Length'].default_value = schema_length

        if update_output: node.outputs.clear()


        for item in node.node_tree.interface.items_tree:
            if item.item_type != "SOCKET": continue
            if (item.in_out == 'INPUT' and update_input):
                relink_socket_map(node, node.inputs, socket_map_in, item)
            if (item.in_out == 'OUTPUT' and update_output):
                relink_socket_map(node, node.outputs, socket_map_out, item)
        
        # at this point there is no wildcard socket
        if '__extend__' in socket_map_in.keys():
            do_relink(node, None, socket_map_in, in_out='INPUT', parent_name='Constant' )



        node.id_data.do_live_update = toggle_update




def node_tree_prop_update(self, context):
    if self.is_updating: # update() can be called from update() and that leads to an infinite loop.
        return           # so we check if an update is currently running.
    self.is_updating = True
    node_group_update(self)
    self.is_updating = False
    if self.bl_idname in ['MantisSchemaGroup'] and self.node_tree is not None:
        if len(self.inputs) == 0:
            self.inputs.new("IntSocket", "Schema Length", identifier='Schema Length')
        if self.inputs[-1].bl_idname != "WildcardSocket":
            self.inputs.new("WildcardSocket", "", identifier="__extend__")

from bpy.types import NodeCustomGroup

class MantisNodeGroup(Node, MantisNode):
    bl_idname = "MantisNodeGroup"
    bl_label = "Node Group"

    node_tree:PointerProperty(type=NodeTree, poll=poll_node_tree, update=node_tree_prop_update,)
    is_updating:BoolProperty(default=False)
    
    def update(self):
        live_update = self.id_data.do_live_update
        if self.is_updating: # update() can be called from update() and that leads to an infinite loop.
            return           # so we check if an update is currently running.
        try:
            self.is_updating = True
            node_group_update(self)
            self.is_updating = False
        finally: # we need to reset this regardless of whether or not the operation succeeds!
            self.is_updating = False
            self.id_data.do_live_update = live_update # ensure this remains the same

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "node_tree", text="")
        row.operator("mantis.edit_group", text="", icon='NODETREE', emboss=True)
        

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

class SchemaGroup(Node, MantisNode):
    bl_idname = "MantisSchemaGroup"
    bl_label = "Node Schema"
    
    node_tree:PointerProperty(type=NodeTree, poll=poll_node_tree_schema, update=node_tree_prop_update,)
    is_updating:BoolProperty(default=False)

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "node_tree", text="")
        row.operator("mantis.edit_group", text="", icon='NODETREE', emboss=True)

    def update(self):
        live_update = self.id_data.do_live_update
        if self.is_updating: # update() can be called from update() and that leads to an infinite loop.
            return           # so we check if an update is currently running.
        self.is_updating = True
        try:
            node_group_update(self)
            # reset things if necessary:
            if self.node_tree:
                if len(self.inputs) == 0:
                    self.inputs.new("IntSocket", "Schema Length", identifier='Schema Length')
                if self.inputs[-1].bl_idname != "WildcardSocket":
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
               ("DeformerMorphTargetDeform", 'INPUT', 'BooleanSocket', "Use Offset", 2,         False,     True),
               ("UtilityFCurve",             'INPUT',  "eFCrvExtrapolationMode", "Extrapolation Mode", 0, False, 'CONSTANT')]

# replace names with bl_idnames for reading the tree and solving schemas.
replace_types = ["NodeGroupInput", "NodeGroupOutput", "SchemaIncomingConnection",
                 "SchemaArrayInput", "SchemaConstInput", "SchemaConstOutput", "SchemaIndex",
                 "SchemaOutgoingConnection", "SchemaConstantOutput", "SchemaArrayOutput",
                 "SchemaArrayInputGet",]

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

#Mantis Nodes Base
import bpy
from bpy.props import (BoolProperty, StringProperty, EnumProperty, CollectionProperty, \
    IntProperty, IntVectorProperty, PointerProperty, BoolVectorProperty)
from . import ops_nodegroup
from bpy.types import NodeTree, Node, PropertyGroup, Operator, UIList, Panel

from .utilities.utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

from .utilities.utilities import get_socket_maps, relink_socket_map, do_relink
from .mantis_dataclasses import MantisSocketTemplate

MANTIS_VERSION_MAJOR=0
MANTIS_VERSION_MINOR=13
MANTIS_VERSION_SUB=5

FLOAT_EPSILON=0.0001 # used to check against floating point inaccuracy
links_sort_key= lambda a : (-a.multi_input_sort_id, -a.sub_sort_id)

selection_sync_node_to_object = {} # what objects a node spawns
selection_sync_object_to_node = {} # what node an object comes from

# The reroute cache is used to accelerate reading reroute nodes
# it uses the tree name and hash to ensure reroutes are only updated when needed
# reroutes recursively find their source and remember it
reroute_cache = {}

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

from os import environ

# https://docs.blender.org/api/master/bpy.types.NodeTree.html#bpy.types.NodeTree.valid_socket_type
# thank you, Sverchok
def valid_interface_types(cls : NodeTree, socket_idname : str):
    from .socket_definitions import tell_valid_bl_idnames, TellClasses
    #TODO: do the versioning code to handle this so it can be in all versions
    if bpy.app.version <= (4,4,0): # should work in 4.4.1
        return socket_idname in [cls.bl_idname for cls in TellClasses()]
    elif bpy.app.version == (4,5,0): # workaround for a BUG
        return ['NodeSocketGeometry']
    else: # once versioning is finished this will be unnecesary.
        return socket_idname in tell_valid_bl_idnames()
def fix_reroute_colors(tree):
    context = bpy.context
    if any((tree.is_executing, tree.is_exporting, tree.do_live_update==False, context.space_data is None) ):
        return
    from .utilities.utilities import find_reroute_start_socket
    from .socket_definitions import MantisSocket
    reroutes_without_color = []
    for n in tree.nodes:
        if n.bl_idname=='NodeReroute' and n.inputs[0].bl_idname == "NodeSocketColor":
            reroutes_without_color.append(n)
    try:
        while reroutes_without_color:
            rr = reroutes_without_color.pop()
            if rr.inputs[0].is_linked:
                link = rr.inputs[0].links[0]
                socket = find_reroute_start_socket(rr)
                if isinstance(socket, MantisSocket):
                    rr.socket_idname = socket.bl_idname
    except Exception as e:
        print(wrapOrange("WARN: Updating reroute color failed with exception: ")+wrapWhite(f"{e.__class__.__name__}"))

#functions to identify the state of the system using hashes
# this function runs a lot so it should be optimized as well as possible.
def hash_tree(tree, recurse=True):
    trees=set(); links=[]; hash_data=""
    for node in tree.nodes:
        hash_data+=str(node.name)
        if recurse and hasattr(node, 'node_tree') and node.node_tree:
            trees.add(node.node_tree)
    for other_tree in trees:
        hash_data+=str(hash_tree(other_tree))
    for link in tree.links:
        links.append( link.from_node.name+link.from_socket.name+
                      link.to_node.name+link.to_socket.name+
                      str(link.multi_input_sort_id) )
    links.sort(); hash_data+=''.join(links)
    return hash(hash_data)

# TODO: I should see if I can make these work without every using NodeSocket.links
#  as that getter is very slow at scale
# however with the cache in place it is probably negligible
def update_reroute_cache_item_source_recursively(reroute, tree_cache, source):
    # find all the inputs to this reroute and update their destination sets
    # every reroute ancestor pushes to this destination... but not every recursive-child
    #   of the root reroute necessarily does, so pushing back like this is right
    # since each reroute node only has one ancestor, this is easy
    from .mantis_dataclasses import RerouteCacheItem
    tree= reroute.id_data
    reroutes = {reroute}
    while(reroutes):
        reroute = reroutes.pop()
        # for making a new cache item
        if (cache_object := tree_cache.get(reroute.name)) is None:
            cache_object = RerouteCacheItem(
                    reroute_name=reroute.name,
                    reroute_tree_name=tree.name,
                )
            tree_cache[reroute.name] = cache_object
        cache_object.source = source
        if reroute.outputs[0].is_linked: # reroutes are always single-output
            for l in reroute.outputs[0].links: # with potentially many links
                if l.to_node.bl_idname == 'NodeReroute':
                    reroutes.add(l.to_node)

def update_reroute_cache_item_destination_recursively(reroute, tree_cache, destination):
    # find all the inputs to this reroute and update their destination sets
    # every reroute ancestor pushes to this destination... but not every recursive-child
    #   of the root reroute necessarily does, so pushing back like this is right
    # since each reroute node only has one ancestor, this is easy
    from .mantis_dataclasses import RerouteCacheItem
    tree= reroute.id_data
    while(reroute):
        # for making a new cache item
        if (cache_object := tree_cache.get(reroute.name)) is None:
            cache_object = RerouteCacheItem(
                    reroute_name=reroute.name,
                    reroute_tree_name=tree.name,
                    destinations= {destination},
                )
            tree_cache[reroute.name] = cache_object
        else:
            cache_object.destinations.add(destination)
        # Odd: if I check reroute.inputs[0].is_linked with live updates, CRASH.
        if rr_links := reroute.inputs[0].links:
            # reroutes are always single-input with at most 1 link
            if (l := rr_links[0]).from_node == 'NodeReroute':
                reroute = l.from_node
                continue
        reroute = None

# Update the reroute cache from the link
# NOTE this is updated as the user adds links by the node.insert_link() callback
def reroute_cache_handle_link(tree, tree_cache, link):
    from .mantis_dataclasses import RerouteCacheItem
    # if it is a link to or from a reroute, add or update the cache item
    # first check if the cache item is stale
    # then try and fill the source and destination - make sure to recursively fill them
    # if it isn't connected to a source or destination, it's part of a network
    # We only need to check the ends, and we can do both the destination and source
    #  passes simultaneously since they don't depend on each other.
    # NOTE that we use socket index to make things explicit and fast
    if link.from_node.bl_idname == 'NodeReroute' and link.to_node.bl_idname != 'NodeReroute':
        other_node = link.to_node
        other_socket = link.to_socket
        for socket_index, check_socket in enumerate(other_node.inputs):
            if check_socket.identifier == other_socket.identifier: break
        else:
            raise RuntimeError("Error, cannot make reroute cache for link: "
                               f"{link.from_node.name}:{link.from_socket.name} ==>"
                               f"{link.to_node.name}:{link.to_socket.name}")
        reroute = link.from_node
        destination = (other_node.name, socket_index)
        if (cache_object := tree_cache.get(reroute.name)) is None:
            cache_object = RerouteCacheItem(
                reroute_name=reroute.name,
                reroute_tree_name=tree.name,
                destinations= {destination},
            )
            tree_cache[reroute.name]=cache_object
        update_reroute_cache_item_destination_recursively(reroute, tree_cache,
            destination=destination)
    elif link.from_node.bl_idname != 'NodeReroute' and link.to_node.bl_idname == 'NodeReroute':
        other_node = link.from_node
        other_socket = link.from_socket
        for socket_index, check_socket in enumerate(other_node.outputs):
            if check_socket.identifier == other_socket.identifier: break
        else:
            raise RuntimeError("Error, cannot make reroute cache for link: "
                               f"{link.from_node.name}:{link.from_socket.name} ==>"
                               f"{link.to_node.name}:{link.to_socket.name}")
        reroute = link.to_node
        source = (link.from_node.name, socket_index)
        if (cache_object := tree_cache.get(reroute.name)) is None:
            cache_object = RerouteCacheItem(
                reroute_name=reroute.name,
                reroute_tree_name=tree.name,
                source = source,
            )
            tree_cache[reroute.name]=cache_object
        update_reroute_cache_item_source_recursively(reroute, tree_cache,
            source=source)

def build_reroute_cache(tree, links):
    # we'll track this to know if a tree update should invalidate the hash on incremental update
    tree.number_of_reroute_links = 0
    # make sure to clear the previous cache or confusing things will happen
    tree_cache = {}; reroute_cache[tree.name] = tree_cache
    tree_cache['_MANTIS_RESERVED_TREE_HASH'] = tree.hash
    for link in links:
        if link.from_node.bl_idname == 'NodeReroute' or link.to_node.bl_idname == 'NodeReroute':
            tree.number_of_reroute_links += 1
        reroute_cache_handle_link(tree, tree_cache, link)

def tree_update_common(tree): # set the reroute colors
    if tree.is_quitting: return
    if (bpy.app.version == (4,4,0)): # CTD bug in that version
        return
    fix_reroute_colors(tree)
    # intialize it if e.g the tree is new.
    if (tree_cache := reroute_cache.get(tree.name)) is None:
        tree_cache = {}; reroute_cache[tree.name] = tree_cache
    # events fire in this order:
    #   - node.insert_link (one for each node)
    #   - node.update (one for each node)
    #   - tree.update
    # so if the node's insert_link handled things, we don't need to check
    tree.hash = str(hash_tree(tree, recurse=False))
    if tree.reroute_link_handled: # we can update the hash, it's still good.
        if tree_cache := reroute_cache.get(tree.name):
            tree_cache["_MANTIS_RESERVED_TREE_HASH"]=tree.hash
        tree.reroute_link_handled = False # always make sure to reset the flag
    else:
        reroute_links = []
        # set the UI tree hash for e.g. reroute cache
        for link in tree.links:
            if link.from_node.bl_idname == 'NodeReroute' or link.to_node.bl_idname == 'NodeReroute':
                reroute_links.append(link)
        if len(reroute_links) == tree.number_of_reroute_links:
            if tree_cache := reroute_cache.get(tree.name): # we can update the hash, it's still good.
                tree_cache["_MANTIS_RESERVED_TREE_HASH"] = tree.hash
            else: # there is no cache after all. How did that happen?
                build_reroute_cache(tree, reroute_links)
            # NOTE I put a lot of effort into catching deleted links but it just isn't practical
            #      to catch this and it is almost free to rebuild the cache.
        else:
            build_reroute_cache(tree, reroute_links)
            # reset the count but do not update the hash.
        tree.number_of_reroute_links = len(reroute_links)


class MantisTree(NodeTree):
    '''A custom node tree type that will show up in the editor type list'''
    bl_idname = 'MantisTree'
    bl_label = "Rigging Nodes"
    bl_icon = 'OUTLINER_OB_ARMATURE'

    tree_valid:BoolProperty(default=False)
    hash:StringProperty(default='') # use for UI updates, reroute cache
    hash_recursive:StringProperty(default='') # use for checking Mantis state
    do_live_update:BoolProperty(default=True) # use this to disable updates for e.g. scripts
    # operator settings for re-exporting the tree.
    filepath:StringProperty(default="", subtype='FILE_PATH')
    export_all_subtrees_together:BoolProperty(default=True)
    #
    is_executing:BoolProperty(default=False)
    is_exporting:BoolProperty(default=False)
    is_quitting:BoolProperty(default=False)
    execution_id:StringProperty(default='')
    # prev_execution_id:StringProperty(default='')
    mantis_version:IntVectorProperty(default=[
        MANTIS_VERSION_MAJOR, MANTIS_VERSION_MINOR-1, MANTIS_VERSION_SUB-1])
    # this prevents the node group from executing on the next depsgraph update
    # because I don't always have control over when the dg upadte happens.
    prevent_next_exec:BoolProperty(default=False)

    #added to work around a bug in 4.5.0 LTS
    interface_helper : StringProperty(default='')

    # for reroute cache, to check if it is still good
    number_of_reroute_links : IntProperty(default=0)
    # flag to indicate a link was already handled this update
    reroute_link_handled : BoolProperty(default=False)

    parsed_tree={}

    # NOTE that these are class properties that should be serialized
    #      to per-instance bpy properties when switching trees.
    #      The class properties should, however, be associated to specific
    #      trees by name so that the user can edit multiple trees at once.
    # Selection Sync Dicts
    node_to_object_map = {}
    object_to_node_map = {}

    if (bpy.app.version < (4, 4, 0) or bpy.app.version >= (4,5,0)):  # in 4.4 this leads to a crash
        @classmethod
        def valid_socket_type(cls : NodeTree, socket_idname: str):
            return valid_interface_types(cls, socket_idname)

    def update(self):
        tree_update_common(self)

    def update_tree(self, context = None, force=False, error_popups=False):
        if self.is_exporting:
            return
        my_hash = str( hash_tree(self) )
        my_ui_hash = str( hash_tree(self, recurse=False))
        tree_cache = reroute_cache.get(self.name)
        if tree_cache['_MANTIS_RESERVED_TREE_HASH'] != my_ui_hash:
            build_reroute_cache(self, self.links) # somehow it became invalid, rebuild it.
        if (my_hash != self.hash_recursive) or force:
            self.hash_recursive = my_hash
            self.is_executing = True
            from .execution import readtree
            prGreen("Validating Tree: %s" % self.name)
            try:
                import bpy # I am importing here so that the context passed in
                # is used for display update... but I always want to do this
                scene = bpy.context.scene
                scene.render.use_lock_interface = True
                self.parsed_tree = readtree.parse_tree(self, error_popups)
                if context:
                    self.display_update(context)
                self.tree_valid = bool(self.parsed_tree)
            except Exception as e:
                prRed("Failed to update node tree due to error.")
                self.tree_valid = False
                self.hash_recursive='' # unset the hash to mark the tree as un-parsed.
                raise e
            finally:
                scene.render.use_lock_interface = False
                self.is_executing = False
        if self.parsed_tree is None:
            self.parsed_tree = {}
            return 1 # failure
        return 0 # success

    def display_update(self, context):
        if self.is_exporting:
            return
        self.is_executing = True
        try:
            current_tree = bpy.context.space_data.path[-1].node_tree
            for node in current_tree.nodes:
                if hasattr(node, "display_update"):
                    try:
                        node.display_update(self.parsed_tree, context)
                    except Exception as e:
                        print("Node \"%s\" failed to update display with error: %s" %(wrapGreen(node.name), wrapRed(e)))
        finally:
            self.is_executing = False

        # TODO: deal with invalid links properly.
        #    - Non-hierarchy links should be ignored in the circle-check and so the links should be marked valid in such a circle
        #    - hierarchy-links should be marked invalid and prevent the tree from executing.

    def execute_tree(self,context, error_popups = False, profile=False):
        self.prevent_next_exec = False
        if not self.hash_recursive:
            return
        if not self.parsed_tree:
            return
        if self.is_exporting or self.is_executing:
            return
        prGreen("Executing Tree: %s" % self.name)
        self.is_executing = True
        from .execution import readtree
        try:
            context.scene.render.use_lock_interface = True
            readtree.execute_tree(self.parsed_tree, self, context, error_popups, profile=profile)
        except RecursionError as e:
            prRed("Recursion error while parsing tree.")
        finally:
            context.scene.render.use_lock_interface = False
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
    is_quitting:BoolProperty(default=False)

    mantis_version:IntVectorProperty(default=[
        MANTIS_VERSION_MAJOR, MANTIS_VERSION_MINOR, MANTIS_VERSION_SUB])
    # see the note in MantisTree
    interface_helper : StringProperty(default='')

    # for reroute cache, to check if it is still good
    number_of_reroute_links : IntProperty(default=0)
    # flag to indicate a link was already handled this update
    reroute_link_handled : BoolProperty(default=False)

    if (bpy.app.version < (4, 4, 0) or bpy.app.version >= (4,5,0)):  # in 4.4 this leads to a crash
        @classmethod
        def valid_socket_type(cls : NodeTree, socket_idname: str):
            return valid_interface_types(cls, socket_idname)

    def update(self):
        tree_update_common(self)


#TODO: do a better job explaining how MantisNode and MantisUINode relate.

# TODO: I want to avoid doing any kind of class mutation at runtime
#       so in the future I will try to do this directly rather than
#       running this function once for each class while registering
#       however this is not very important for UI classes since they
#       are not a performance bottleneck.
def mantis_class_from_library(library, class_name):
    from importlib import import_module
    return getattr(import_module(library, package=mantis_root), class_name)

class MantisUINode:
    """
        This class contains the common user-interface features of Mantis nodes.
        MantisUINode objects will spawn one or more MantisNode objects when the graph is evaluated.
        The MantisNode objects will pull the data from the UI node and use it to generate the graph.
    """
    # blender stuff, I'll need to split this into a mixin class later
    bl_icon = 'NODE'
    initialized : bpy.props.BoolProperty(default = False)
    #
    mantis_node_class_name=''
    mantis_class=None
    socket_templates=None

    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['MantisTree', 'SchemaTree'])

    def init(self, context):
        self.init_sockets(self.socket_templates)
        self.initialized = True

    def init_sockets(self, socket_templates : tuple[MantisSocketTemplate]):
        for template in socket_templates:
            collection = self.outputs
            if template.is_input:
                collection = self.inputs
            identifier = template.name
            if template.identifier:
                identifier = template.identifier
            use_multi_input = template.use_multi_input if template.is_input else False
            socket = collection.new(
                template.bl_idname,
                template.name,
                identifier=identifier,
                use_multi_input=use_multi_input
            )
            socket.hide= template.hide
            if template.category:
                from . import DOERROR
                # a custom property for the UI functions to use.
                if hasattr(socket, "category"):
                    socket.category = template.category
                elif DOERROR:
                    print (f"WARN: socket type {socket.bl_idname} has no category attribute")
            if template.default_value is not None:
                socket.default_value = template.default_value
                # this can throw a TypeError - it is the caller's
                #   responsibility to send the right type.
            if template.use_multi_input: # this is an array
                socket.display_shape = 'SQUARE_DOT'

    def insert_link(self, link):
        if (bpy.app.version == (4, 4, 0)):
            return # this causes a crash due to a bug.
        tree = self.id_data
        if tree.reroute_link_handled: return
        if ( link.from_node.bl_idname == 'NodeReroute' or
             link.to_node.bl_idname == 'NodeReroute' ):
                tree.number_of_reroute_links+=1
                reroute_cache_handle_link(tree=tree,
                    tree_cache=reroute_cache.get(tree.name), link=link)
                tree.reroute_link_handled = True
        
# NOTE
# MantisUINode has no proper mantis libraryclass on its own, so:
# register()'s are in SUBclasses; they have to run AFTER library is defined

class SchemaUINode(MantisUINode):
    is_updating:BoolProperty(default=False)
    @classmethod
    def register(cls):
        cls.mantis_class = mantis_class_from_library('.schema_nodes', cls.mantis_node_class_name)

class LinkNode(MantisUINode):
    mantis_node_library='.link_nodes'
    category_color=[0.5,0.5,0.5]
    @classmethod
    def register(cls):
        cls.mantis_class = mantis_class_from_library('.link_nodes', cls.mantis_node_class_name)
    def init(self, context):
        super().init(context)
        self.use_custom_color = True
        self.color = self.category_color

class xFormNode(MantisUINode):
    @classmethod
    def register(cls):
        cls.mantis_class = mantis_class_from_library('.xForm_nodes', cls.mantis_node_class_name)
    def init(self, context):
        super().init(context)
        from mathutils import Color
        xFormColor = Color((0.093172, 0.047735, 0.028036)).from_scene_linear_to_srgb()
        self.use_custom_color = True
        self.color = xFormColor # must not have alpha

class DeformerNode(MantisUINode):
    @classmethod
    def register(cls):
        cls.mantis_class = mantis_class_from_library('.deformer_nodes', cls.mantis_node_class_name)

class GeometryPrimitiveNode(MantisUINode):
    @classmethod
    def register(cls):
        cls.mantis_class = mantis_class_from_library('.primitives_nodes', cls.mantis_node_class_name)

class MantisMiscNode(MantisUINode):
    @classmethod
    def register(cls):
        cls.mantis_class = mantis_class_from_library('.misc_nodes', cls.mantis_node_class_name)

class MantisMathUINode(MantisUINode):
    @classmethod
    def register(cls):
        cls.mantis_class = mantis_class_from_library('.math_nodes', cls.mantis_node_class_name)


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
    if node.node_tree is None:
        node.inputs.clear(); node.outputs.clear()
        return
    toggle_update = node.id_data.do_live_update
    node.id_data.do_live_update = False

    identifiers_in={socket.identifier:socket for socket in node.inputs}
    identifiers_out={socket.identifier:socket for socket in node.outputs}
    interface_names_in, interface_names_out = {}, {}
    for interface_item in node.node_tree.interface.items_tree:
        if interface_item.item_type != 'SOCKET': continue
        if interface_item.in_out == 'INPUT':
            interface_names_in[interface_item.identifier] = interface_item.name
        else:
            interface_names_out[interface_item.identifier] = interface_item.name
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
                if interface_names_out.get(item.identifier) != s.name: update_output = True; continue
                found_out.append(item.identifier)
                if (indices_out[s.identifier]!=item.index): update_output=True; continue
                if update_output: continue
                if s.bl_idname != item.bl_socket_idname: update_output = True; continue
            else: update_output = True; continue
        else:
            if s:= identifiers_in.get(item.identifier): # if the requested input doesn't exist, update
                if interface_names_in.get(item.identifier) != s.name: update_input = True; continue
                found_in.append(item.identifier)
                if (indices_in[s.identifier]!=item.index): update_input=True; continue
                if update_input: continue # done here
                if s.bl_idname != item.bl_socket_idname: update_input = True; continue
            else: update_input = True; continue

    # Schema has an extra input for Length and for Extend.
    if node.bl_idname == 'MantisSchemaGroup':
        found_in.extend(['Schema Length', ''])

    # get the socket maps before modifying stuff
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

    if update_input or update_output and (socket_maps is not None):
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


        from .utilities.utilities import relink_socket_map_add_socket

        reorder_me_input = []; input_index = 0
        reorder_me_output = []; output_index = 0

        def update_group_sockets(interface_item, is_input):
            socket_map = socket_map_in if is_input else socket_map_out
            socket_collection = node.inputs if is_input else node.outputs
            counter = input_index if is_input else output_index
            reorder_collection = reorder_me_input if is_input else reorder_me_output
            if socket_map:
                if item.identifier in socket_map.keys():
                    socket = relink_socket_map_add_socket(node, socket_collection, item, item.in_out)
                    do_relink(node, socket, socket_map, item.in_out)
                else:
                    for has_socket in socket_collection:
                        if has_socket.bl_idname == item.bl_socket_idname and \
                                has_socket.name == item.name:
                            reorder_collection.append((has_socket, counter))
                            break
                    else:
                        socket = relink_socket_map_add_socket(node, socket_collection, item, item.in_out)
            else:
                socket = relink_socket_map_add_socket(node, socket_collection, item, item.in_out)
            counter += 1

        # TODO: de-duplicate this hideous stuff
        for item in node.node_tree.interface.items_tree:
            if item.item_type != "SOCKET": continue
            if (item.in_out == 'INPUT' and update_input):
                # check and see if it exists... should only happen in curves on startup
                if item.bl_socket_idname in ['EnumCurveSocket']:
                    for exists in node.inputs: # NOTE: check if the socket was not deleted
                        if exists.identifier == item.identifier:
                            # this happens for curve inputs because of some shennanigans with how
                            # blender loads IDs - I can't set the ID until the file has loaded
                            # so I have to avoid touching the socket until then...
                            break
                    else:
                        update_group_sockets(item, True)
                else:
                    update_group_sockets(item, True)
                input_index += 1
            if (item.in_out == 'OUTPUT' and update_output):
                if item.bl_socket_idname in ['EnumCurveSocket']: # LOOK up there at the comment!
                    for exists in node.outputs:
                        if exists.identifier == item.identifier:
                            break
                    else:
                        update_group_sockets(item, False)
                else:
                    update_group_sockets(item, False)
                output_index += 1

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

class BlenderVersionError(Exception):
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

# replace names with bl_idnames for reading the tree and solving schemas.
replace_types = ["NodeGroupInput", "NodeGroupOutput", "SchemaIncomingConnection",
                 "SchemaArrayInput", "SchemaArrayInputAll", "SchemaConstInput", "SchemaConstOutput",
                 "SchemaIndex", "SchemaOutgoingConnection", "SchemaArrayOutput","SchemaArrayInputGet",
                ]

# anything that gets properties added in the graph... this is a clumsy approach but I need to watch for this
#   in schema generation and this is the easiest way to do it for now.
custom_props_types = ["LinkArmature", "UtilityKeyframe", "UtilityFCurve", "UtilityDriver", "xFormBone",
                      "xFormArmature", "xFormGeometryObject", "xFormObjectInstance", "xFormCurvePin",]

# filters for determining if a link is a hierarchy link or a non-hierarchy (cyclic) link.
from_name_filter = frozenset({"Driver",})
to_name_filter = frozenset({
                   "Custom Object xForm Override",
                   "Custom Object",
                   "Deform Bones",
                 })

# nodes that must be solved as if they were Schema because they send arrays out.
array_output_types = [
    'UtilityArrayGet', 'UtilityKDChoosePoint', 'UtilityKDChooseXForm',
]

def can_remove_socket_for_autogen(node, socket) -> bool:
    """ Whether to enable socket removal optimization for the socket
        This should be disallowed if e.g. it is a custom property.
    """
    return False # for now! This doesn't seem to be working...
    # the problem is that Schema does this, and so does Readtree
    # and they can try and both do it. That's bad.
    if node.socket_templates:
        for s_template in node.socket_templates:
            if s_template.name == socket:
                # raise NotImplementedError
                return True
    elif node.node_type == 'UTILITY':
        return True # HACK because most utilities don't have socket templates yet
    return False

# The MantisExecutionContext class is used to store the execution-specific variables
# that are used when executing the tree
# Importantly, it is NOT used to store variables between solutions, these belong to the
#   tree class.
class MantisExecutionContext():
    def __init__(
            self,
            base_tree,
    ):
        self.base_tree = base_tree
        self.execution_id = base_tree.execution_id
        self.execution_failed=False
        self.interface_nodes = {}
        self.b_objects={} # objects created by Mantis during execution
        self.tagged_for_overlay = [] # nodes mutated by overlay system
        self.overlay_data = [] # dict of list of Overlay objects

from typing import Any

# using these frozen sets accelerate lookup when checking for this
FILL_PARAMETERS_SKIP_ROOTS = frozenset({ 'MANTIS_AUTOGENERATED', 'SCHEMA_AUTOGENERATED', })
FILL_PARAMETERS_SKIP_NAMES = frozenset({ "NodeGroupOutput", "NodeGroupInput", })
FILL_PARAMETERS_SKIP_SOCKETS = frozenset({ 'RelationshipSocket', 'xFormSocket', })
from .socket_definitions import no_default_value

class MantisNode:
    """
        This class contains the basic interface for a Mantis Node.
        A MantisNode is used internally by Mantis to represent the final evaluated node graph.
        It gets generated with data from a MantisUINode when the graph is read.
    """
    __slots__ = (
        "base_tree", "signature", "ui_signature",
        "inputs", "outputs",
        "parameters", "drivers", "bObject",
        "hierarchy_connections", "connections",
        "hierarchy_dependencies", "dependencies",
        "unmet_hierarchy_dependency_count",
        "prepared", "executed", "execution_prepared",
        "mContext", "is_schema_prototype",
        "generated_at_schema_index",
        )
    node_type = 'UNINITIALIZED'
    socket_templates = None
    property_socket_map = {}
    passes=frozenset({})
    def __init__(self, signature : tuple,
                 base_tree : bpy.types.NodeTree,
                 socket_templates : list[MantisSocketTemplate]=[],
                 additional_parameters :dict = {}, ):
        self.base_tree=base_tree
        self.signature = signature
        self.ui_signature = signature
        self.inputs = MantisNodeSocketCollection(node=self, is_input=True)
        self.outputs = MantisNodeSocketCollection(node=self, is_input=False)
        self.parameters, self.drivers = {}, []; self.bObject=None
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies, self.dependencies = [], []
        self.unmet_hierarchy_dependency_count = float("inf") # we will set this when filling the dependencies lists
        self.prepared, self.executed = False, False
        self.execution_prepared = False
        # execution_prepared is for tracking prep state in execution, so that I can avoid preparing nodes
        #  again without changing the readtree code much.
        self.mContext = None # for now I am gonna set this at runtime
        self.is_schema_prototype = False
        # For nodes generated in a schema, it's a list so that we can store the whole path
        # this is not strictly necessary for interface resolution but it is much easier
        # initialize it as all -1, we'll modify this if we need to, e.g. in the schema
        self.generated_at_schema_index = [-1] * len(self.signature)
        # I know it isn't "beautiful OOP" or whatever, but it is just easier
        # code should be simple and do things in the simplest way.
        # in the future I can refactor it, but it will require changes to 100+
        #  classes, instead of adding about 5 lines of code elsewhere.
        if self.socket_templates:
            self.init_sockets( additional_parameters )

    @property
    def name(self):
        return self.ui_signature[-1]

    @property
    def bl_idname(self): # this and the above exist solely to maintain interface w/bpy.types.Node
        from .utilities.utilities import get_ui_node
        return get_ui_node(self.ui_signature, self.base_tree).bl_idname
    
    def reset_execution(self) -> None:
        """ Reset the node for additional execution without re-building the tree."""
        self.drivers.clear(); self.bObject=None
        self.executed = False
        self.execution_prepared = False

    def init_sockets(self, additional_parameters : dict = {}) -> None:
        # Formerly I was doing this:
        # self.inputs.init_sockets(self.socket_templates)
        # self.outputs.init_sockets(self.socket_templates)
        # Since doing each one causes some redundancy, we'll just reimplement it
        # This is a highly used and therefore expensive function so we have to make small
        # optimizations like this, even tho it is ugly.
        traverse_in, traverse_out = {}, {}
        for socket in self.socket_templates:
            if socket.traverse_target:
                if socket.is_input:
                    traverse_in[socket.name] = socket.traverse_target
                else:
                    traverse_out[socket.name] = socket.traverse_target
            if socket.ui_only == True: continue # used in UI but not in generation
            if socket.is_input:
                self.inputs[socket.name] = NodeSocket(is_input=True, name=socket.name,
                                    node=self,)
            else:
                self.outputs[socket.name] = NodeSocket(is_input=False, name=socket.name,
                                    node=self,)
            self.parameters[socket.name] = None
        for traverse_owner, traverse_target in traverse_in.items():
            self.inputs[traverse_owner].traverse_target = self.outputs[traverse_target]
            self.inputs[traverse_owner].can_traverse = True
        for traverse_owner, traverse_target in traverse_out.items():
            self.outputs[traverse_owner].traverse_target = self.inputs[traverse_target]
            self.outputs[traverse_owner].can_traverse = True
        for key, value in additional_parameters.items():
            self.parameters[key]=value

    def init_parameters(self, additional_parameters = {}) -> None:
        for socket in self.inputs:
            self.parameters[socket.name] = None
        for socket in self.outputs:
            self.parameters[socket.name] = None
        for key, value in additional_parameters.items():
            self.parameters[key]=value

    # We really only need to do this once at class registration
    # Therefore the goal is not to have any mutable data here
    # ======================= READ BELOW =======================
    # We have the following classes of Mantis Socket ==> Blender Proeprty relationships:
    # Scalar: 1 Mantis scalar ==> 1 Blender property. 1 Filler.
    # Vector: 1 Mantis Vector socket ==> Blender vector property. 1 Filler.
    # Scalar Combo: 1 Mantis scalar ==> many Blender scalars. 1 Filler per property.
    # Vector Combo: 1 Mantis vector ==> vector of Blender vector property. 1 Filler per property.
    # In every case, 1 filler per Blender property.
    @classmethod
    def gen_property_socket_map(cls, prop_owner_group=None) -> dict:
        from .mantis_dataclasses import MantisSocketFiller
        from dataclasses import replace
        from bpy.app import version as bpy_version
        if cls.property_socket_map: # retrieve the cache if possible
            return cls.property_socket_map
        props_sockets = {}
        for s_template in cls.socket_templates:
            if s_template.min_bpy_version:
                if bpy_version < s_template.min_bpy_version:
                    prPurple(f"Skipping socket {s_template.name} because "
                             f"it requires Blender {s_template.min_bpy_version} or higher")
                    continue # We can't set or drive this obviously.
            if prop_owner_group is not None and s_template.prop_owner_group != prop_owner_group:
                continue # for composite objects like bones
            if not s_template.blender_property: # this one has to be handled by the node itself.
                continue # Or maybe it is UI-only, in any case we don't need to do anything here.
            # Default to (Scalar <==> Scalar), as tuples for compatibility with other code paths
            vector_property, combo = False, False # TODO: make socket templates pre-tuple-ize this
            defaults = ( s_template.default_value, ); properties = ( s_template.blender_property, )
            if isinstance( s_template.default_value, (list, tuple) ):
                vector_property = True # this tells us if MANTIS provides a vector
                # if Blender consumes a vector, then we map the vector to the vector. Easy.
            if isinstance(s_template.blender_property, (tuple, list)):
                # But maybe we provide data from one Mantis Socket to many Blender properties...
                combo=True; properties = s_template.blender_property
                if vector_property: # we have to break the default value up so we can map
                                    # mantis data element-wise to a vector of Blender properties 
                    defaults = s_template.default_value 
            # Now iteratre through the properties and make 1 filler per.
            for i, property in enumerate(properties):
                default_index = i if vector_property and combo else 0 # only needed for Combo Vector
                default = defaults[default_index] # usually 1:1 except for Combo Scalar
                key = s_template.name + f"_{default_index}" + (f"_{property}" if combo else "")
                value_index = default_index if combo and vector_property else None
                from .utilities import socket_filler_operators as operators
                property_value_operator = None
                if s_template.property_value_operator:
                    property_value_operator = getattr(operators, s_template.property_value_operator)
                props_sockets[key] = MantisSocketFiller(
                    socket_name = s_template.name,     # This is a dict because node
                    property_name = property,          # instances should be able 
                    value_index = value_index,         # to edit Fillers.
                    default_value = default,           # The keys are not inherently
                    combo_property = combo,            # meaningful and are
                    vector_property = vector_property, # NOT USED DOWNSTREAM!
                    is_animatable = s_template.is_animatable,
                    property_group = s_template.prop_owner_group,
                    property_value_operator = property_value_operator)
        if prop_owner_group is None:
            cls.property_socket_map = props_sockets  # We should cache this one!
        return props_sockets

    def set_traverse(self, traversal_pairs = [(str, str)]) -> None:
        for (a, b) in traversal_pairs:
            self.inputs[a].set_traverse_target(self.outputs[b])
            self.outputs[b].set_traverse_target(self.inputs[a])

    def clear_traverse(self, inputs = [str], outputs = [str]) -> None:
        for inp in inputs:
            self.inputs[inp].set_traverse(None)
        for out in outputs:
            self.inputs[out].set_traverse(None)

    def flush_links(self) -> None:
        for inp in self.inputs.values():
            inp.flush_links()
        for out in self.outputs.values():
            out.flush_links()

    def update_socket_value(self, blender_property, value) -> bool:
        change_handled=False
        if self.node_type == 'LINK':
            if len(self.bObject) == 0: # - there are no downstream xForms
                return True # so there is nothing to do here
            for b_ob in self.bObject:
                try:
                    setattr(b_ob, blender_property, value)
                    change_handled=True
                except Exception as e:
                    print("Failed to update mantis socket because of %s" % e,
                            "Updating tree instead.")
        else:
            try:
                b_ob = self.bObject
                if self.node_type == 'XFORM': # HACK
                    b_ob = self.bGetObject()
                setattr(b_ob, blender_property, value)
                change_handled=True
            except Exception as e:
                print("Failed to update mantis socket because of %s" % e,
                        "Updating tree instead.")
        return change_handled

    def ui_modify_socket(self, ui_socket, socket_name=None) -> bool:
        """ Handle changes in the node's UI. Updates the rig if possible."""
        # Always update the node's data
        change_handled=False
        if socket_name is None: socket_name = ui_socket.name
        value = ui_socket.default_value
        # apply overlay variables here so this updates predictably
        if (isinstance(value, str) and
                (self.signature, ui_socket.identifier) in self.mContext.tagged_for_overlay):
            from .execution.readtree import node_scan_overlays
            value = node_scan_overlays(self, ui_socket.identifier)
        # TODO: I need to make Node Groups apply overlays downstream, but since
        #       they don't update live anyway, no need just yet
        if socket_name == 'Enable': value = not value
        try:
            self.parameters[ui_socket.name]=value
        except KeyError:
            prRed(f"Unhandled change occured in socket {ui_socket.name} in node"
                    f" {ui_socket.node.name} in tree {ui_socket.node.id_data.name}.")
        for s_template in self.socket_templates:
            if s_template.name==ui_socket.name:
                change_handled = True
                if not s_template.blender_property: return False
                elif isinstance(s_template.blender_property, str):
                    change_handled &= self.update_socket_value(
                        s_template.blender_property, value)
                else: # it is a tuple
                    for i, prop in enumerate(s_template.blender_property):
                        try:
                            change_handled &= self.update_socket_value(
                                prop, value[i])
                        except IndexError:
                            prRed(f"{ui_socket.name} does not have enough values to unpack"
                                  " to update the Mantis tree. Please report this as a bug.")
                            change_handled=False
                break # we don't have to look through any more socket templates
        return change_handled

    # the goal here is to tag the node as unprepared
    # but some nodes are always prepared, so we have to kick it forward.
    def reset_execution_recursive(self):
        self.reset_execution()
        if self.prepared==False: return # all good from here
        for conn in self.hierarchy_connections:
            conn.reset_execution_recursive()

    def evaluate_input(self, input_name, index=0)  -> Any:
        from .utilities.node_common import trace_single_line
        if not (self.inputs.get(input_name)): # get the named parameter if there is no input
            return self.parameters.get(input_name) # this will return None if the parameter does not exist.
        # this trace() should give a key error if there is a problem
        #  it is NOT handled here because it should NOT happen - so I want the error message.
        trace = trace_single_line(self, input_name, index)
        prop = trace[0][-1].parameters[trace[1].name] #trace[0] = the list of traced nodes; read its parameters
        return prop

    def fill_parameters(self, ui_node=None)  -> None:
        from mathutils import Matrix
        from .utilities.utilities import handle_overlay_detect
        if not ui_node:
            if ( (self.signature[0] in FILL_PARAMETERS_SKIP_ROOTS) or
                (self.signature[-1] in FILL_PARAMETERS_SKIP_NAMES) ): # I think this is harmless
                return None
            raise RuntimeError(wrapRed("No UI Node found for... %s" % ( [self.base_tree] + list(self.signature[1:]) ) ) )
        ui_inputs = ui_node.inputs; ui_outputs = ui_node.outputs
        for key in self.parameters.keys():
            if self.parameters[key] is not None: # the parameters are usually initialized as None.
                continue # will be filled by the node itself
            if node_socket := ui_inputs.get(key):
                if node_socket.bl_idname in FILL_PARAMETERS_SKIP_SOCKETS: continue
                elif node_socket.is_linked and (not node_socket.is_output): continue
                # we will get the value from the link, because this is a linked input port.
                # very importantly, we do not pass linked outputs
                # fill these because they are probably Input nodes.
                if node_socket.bl_idname in no_default_value: continue
                if node_socket.bl_idname == 'MatrixSocket':
                    v = node_socket.default_value
                    self.parameters[key] = Matrix(( tuple(v[0:4]),
                                                    tuple(v[4:8]),
                                                    tuple(v[8:12]),
                                                    tuple(v[12:16]) ))
                elif (value := node_socket.default_value) is not None:
                    if isinstance(value, str) and "$" in value:
                        value = handle_overlay_detect(self, node_socket.identifier, value)
                    self.parameters[key] = value
                else:
                    raise RuntimeError(wrapRed("No value found for " + self.__repr__() + " when filling out node parameters for " + ui_node.name + "::"+node_socket.name))

    # I don't think this works! but I like the idea
    def call_on_all_ancestors(self, *args, **kwargs):
        """Resolve the dependencies of this node with the named method and its arguments.
           First, dependencies are discovered by walking backwards through the tree. Once the root
           nodes are discovered, the method is called by each node in dependency order.
           The first argument MUST be the name of the method as a string.
        """
        if args[0] == 'call_on_all_ancestors': raise RuntimeError("Very funny!")
        from .utilities.utilities import get_all_dependencies
        from collections import deque
        # get all dependencies by walking backward through the tree.
        all_dependencies = get_all_dependencies(self)
        # get just the roots
        can_solve = deque(filter(lambda a : len(a.hierarchy_connections) == 0, all_dependencies))
        solved = set()
        while can_solve:
            node = can_solve.pop()
            method = getattr(node, args[0])
            method(*args[0:], **kwargs)
            solved.add(node)
            can_solve.extendleft(filter(lambda a : a in all_dependencies, node.hierarchy_connections))
            if self in solved:
                break
        return

    # gets targets for constraints and deformers and should handle all cases
    def get_target_and_subtarget(self, constraint_or_deformer, input_name = "Target", index = 0,):
        from bpy.types import PoseBone, Object, SplineIKConstraint
        subtarget = ''; target = self.evaluate_input(input_name, index)
        if target:
            if not hasattr(target, "bGetObject"):
                if hasattr(constraint_or_deformer, 'name'):
                    name = constraint_or_deformer.name
                else:
                    name = 'NAME NOT FOUND'
                prRed(f"No {input_name} target found for {name} in {self} because there is no connected node, or node is wrong type")
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

    # This function is for registering the objects a node creates in the global dict
    # The goal is to have a global map of node <==> object and object <==> node
    # so that we can do e.g. selection syncing, etc.
    # NOTE: I'm not registering with mContext here, that happens elsewhere
    #       but it is probably a good idea to refactor this together.
    def bRegisterObject(self, ob_type, ob_value, sub_ob_value = None):
        ui_signature = self.ui_signature
        if selection_sync_node_to_object.get(ui_signature) is None:
            selection_sync_node_to_object[ui_signature] = []
        ob_name = ob_value.name
        sub_ob_name = sub_ob_value.name if sub_ob_value else None
        key = (ob_name, sub_ob_name)
        if ob_type in ['OBJECT', 'BONE']:
            selection_sync_object_to_node[key] = ui_signature
            selection_sync_node_to_object[ui_signature].append( key )


# PASSES DEFINED HERE!
    def bPrepare(self, bContext=None):
        return # This one runs BEFORE anything else
    def bTransformPass(self, bContext=None):
        return # This one runs in EDIT MODE
    def bRelationshipPass(self, bContext=None):
        return # This one runs in POSE MODE
    def bFinalize(self, bContext=None):
        return
    def bModifierApply(self, bContext=None):
        return

    if environ.get("DOERROR"):
        def __repr__(self):
            return self.signature.__repr__()
    else:
        def __repr__(self):
            return self.ui_signature.__repr__()

# do I need this and the link class above?
class DummyLink:
    __slots__ = ("from_socket", "to_socket",
                 "from_mantis_node", "to_mantis_node",
                 "multi_input_sort_id",
                 "original_from")
    #gonna use this for faking links to keep the interface consistent
    def __init__(self, from_socket, to_socket, from_mantis_node=None, to_mantis_node=None, original_from=None, multi_input_sort_id=0):
        self.from_socket = from_socket
        self.to_socket = to_socket
        self.from_mantis_node = from_mantis_node
        self.to_mantis_node = to_mantis_node
        self.multi_input_sort_id = multi_input_sort_id
        # self.from_node = from_socket.node
        # self.to_node = to_socket.node
        if (original_from):
            self.original_from = original_from
        else:
            self.original_from = self.from_socket
    def __repr__(self):
        return(self.from_mantis_node.__repr__()+":"+self.from_socket.name + " -> " + self.to_mantis_node.__repr__()+":"+self.to_socket.name)


def detect_hierarchy_link(from_node, from_socket, to_node, to_socket,):
    if to_node.node_type in ['DUMMY_SCHEMA', 'SCHEMA']:
        return False #TODO: find out if filtering SCHEMA types is wise
    if from_socket in from_name_filter and to_socket in {"Array"}:
        # SPECIAL CASE: arrays essentially extend the non-hierarchy edge
        #       so if the connection to the array isn't hierarchy, the array node
        #       in the middle gets disconnected and never executes.
        #       SO we need to make all the edges until the end hierarchy.
        #       TODO: test the graph for cycles and tag the "last" edge in the cycle
        #             is the general solution but that is toooooo slow in Python
        return True
    if (from_socket in from_name_filter) or (to_socket in to_name_filter):
        return False
    # if from_node.__class__.__name__ in ["UtilityCombineVector", "UtilityCombineThreeBool"]:
    #     return False
    return True

class NodeLink:
    __slots__ = (
        "from_node",
        "from_socket",
        "to_node",
        "to_socket",
        "multi_input_sort_id",
        "sub_sort_id",
        "is_hierarchy",
        "is_alive",
    )

    def __init__(self, from_node, from_socket, to_node, to_socket, multi_input_sort_id=0, sub_sort_id=0):
        if from_node.signature == to_node.signature:
            raise RuntimeError("Cannot connect a node to itself.")
        self.from_node = from_node
        self.from_socket = from_socket
        self.to_node = to_node
        self.to_socket = to_socket
        self.from_node.outputs[self.from_socket].links.append(self)
        # it is the responsibility of the node that uses these links to sort them correctly based on the sort_id
        self.multi_input_sort_id = multi_input_sort_id # this is the sort_id of the link in the UI
        self.sub_sort_id = sub_sort_id # this is for sorting within a  bundled link (one link in the UI)
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
            from .utilities.utilities import init_connections, init_dependencies
            init_connections(self.from_node)
            init_connections(middle_node)
            init_dependencies(middle_node)
            init_dependencies(to_node)

class NodeSocket:
    __slots__ = (
        "can_traverse",
        "traverse_target",
        "node",
        "name",
        "is_input",
        "links",
        "is_linked",
    )
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

    def connect(self, node, socket, sort_id=0, sub_sort_id=0):
        if  (self.is_input):
            to_node   = self.node; from_node = node
            to_socket = self.name; from_socket = socket
        else:
            from_node   = self.node; to_node   = node
            from_socket = self.name; to_socket = socket
        from_node.outputs[from_socket].is_linked = True
        to_node.inputs[to_socket].is_linked = True
        # NOTE: I have removed a check for duplicate links here.
        # Schemas sometimes have valid duplicate links.
        # It is conceivable that this will lead to bugs, but I judge it unlikely.
        new_link = NodeLink(
                from_node,
                from_socket,
                to_node,
                to_socket,
                sort_id,
                sub_sort_id)
        return new_link

    def set_traverse_target(self, traverse_target):
        self.traverse_target = traverse_target
        if traverse_target: self.can_traverse = True
        else: self.can_traverse = False
    
    def flush_links(self):
        """ Removes dead links from this socket."""
        self.links = [l for l in self.links if l.is_alive]
        self.links.sort(key=links_sort_key)
        self.is_linked = bool(self.links)

    @property
    def is_connected(self):
        return len(self.links)>0

    def __repr__(self):
        return self.node.__repr__() + "::" + self.name

class MantisNodeSocketCollection(dict):
    __slots__ = ("is_input", "node",)
    def __init__(self, node, is_input=False):
        self.is_input = is_input
        self.node = node

    def init_sockets(self, sockets):
        for socket in sockets:
            if socket.ui_only == True: continue # used in UI but not in generation
            if socket.is_input != self.is_input: continue
            self[socket.name] = NodeSocket(is_input=self.is_input, name=socket.name, node=self.node)
    def __delitem__(self, key):
        """Deletes a node socket by name, and all its links."""
        socket = self[key]
        for l in socket.links:
            l.die()
        super().__delitem__(key)

    def __iter__(self):
        """Makes the class iterable"""
        return iter(self.values())

#Mantis Nodes Base
import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, CollectionProperty, IntProperty, PointerProperty, BoolVectorProperty
from . import ops_nodegroup
from bpy.types import NodeTree, Node, PropertyGroup, Operator, UIList, Panel

from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

from .utilities import get_socket_maps, relink_socket_map, do_relink

from bpy.app.handlers import persistent

def TellClasses():
    #Why use a function to do this? Because I don't need every class to register.
    return [ MantisTree,
             SchemaTree,
            #  MantisNode,
            #  SchemaNode,
             MantisNodeGroup,
             SchemaGroup,
             MantisVisualizeTree,
             MantisVisualizeNode,
           ]

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

    
    parsed_tree={}
    
    def interface_update(self, context):
        # no idea what this does
        print ("Update Interface function in MantisTree class") 


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

    
    def display_update(self, context):
        current_tree = bpy.context.space_data.path[-1].node_tree
        for node in current_tree.nodes:
            if hasattr(node, "display_update"):
                try:
                    node.display_update(self.parsed_tree, context)
                except Exception as e:
                    print("Node \"%s\" failed to update display with error: %s" %(wrapGreen(node.name), wrapRed(e)))
                    # raise e
        
    
    def execute_tree(self,context):
        if self.is_exporting:
            return
        # return
        prGreen("Executing Tree: %s" % self.name)
        self.is_executing = True
        from . import readtree
        try:
            readtree.execute_tree(self.parsed_tree, self, context)
        except RecursionError as e:
            prRed("Recursion error while parsing tree.")
            # prRed(e); node_tree.do_live_update = False
        # except Exception:
        #     pass
        finally: # first time I have ever used a finally block in my life.
            self.is_executing = False

    

# class SchemaPropertyGroup(bpy.types.PropertyGroup):

class SchemaTree(NodeTree):
    '''A node tree representing a schema to generate a Mantis tree'''
    bl_idname = 'SchemaTree'
    bl_label = "Rigging Nodes Schema"
    bl_icon = 'RIGID_BODY_CONSTRAINT'

    tree_valid:BoolProperty(default=False)
    do_live_update:BoolProperty(default=True) # use this to disable updates for e.g. scripts
    is_executing:BoolProperty(default=False)
    num_links:IntProperty(default=-1)
    # filepath:StringProperty(default="", subtype='FILE_PATH')
    
    parsed_tree={}

    # def update(self):
    #     for n in self.nodes:
    #         if hasattr(n, "update"): n.update()

    # def update_tree(self, context):
    #     prRed("update tree for Schema Tree!")
    #     # self.tree_valid = True
    #     # return
    #     from . import readtree
    #     prGreen("Validating Tree: %s" % self.name)
    #     parsed_tree = readtree.parse_tree(self)
    #     self.parsed_tree=parsed_tree
    #     current_tree = bpy.context.space_data.path[-1].node_tree
    #     self.tree_valid = True
    #     prWhite("Number of Nodes: %s" % (len(self.parsed_tree)))
    #     self.display_update(context)
    
    # def display_update(self, context):
    #     prRed("display update for Schema Tree!")
    #     return
    #     current_tree = bpy.context.space_data.path[-1].node_tree
    #     for node in current_tree.nodes:
    #         if hasattr(node, "display_update"):
    #             try:
    #                 node.display_update(self.parsed_tree, context)
    #             except Exception as e:
    #                 print("Node \"%s\" failed to update display with error: %s" %(wrapGreen(node.name), wrapRed(e)))
    #                 # raise e

    # def execute_tree(self,context):
    #     self.is_executing = True
    #     prRed("executing Schema Tree!")
    #     self.tree_valid = False
    #     self.is_executing = False
    #     return
    #     prGreen("Executing Tree: %s" % self.name)
    #     from . import readtree
    #     try:
    #         readtree.execute_tree(self.parsed_tree, self, context)
    #     except RecursionError as e:
    #         prRed("Recursion error while parsing tree.")
    #         prRed(e); node_tree.do_live_update = False

    if bpy.app.version >= (3, 2):  # in 3.1 this can lead to a crash
        @classmethod
        def valid_socket_type(cls, socket_type: str):
            # https://docs.blender.org/api/master/bpy.types.NodeTree.html#bpy.types.NodeTree.valid_socket_type
            from .socket_definitions import Tell_bl_idnames
            return socket_type in Tell_bl_idnames()
            # thank you, Sverchok
            



class MantisNode:
    # num_links:IntProperty(default=-1) # is this used anywhere?

    # is_triggering_execute:BoolProperty(default=False)

    # do_display_update:BoolProperty(default=False)
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['MantisTree', 'SchemaTree'])
                
    def insert_link(self, link):
        context = bpy.context
        if context.space_data:
            node_tree = context.space_data.path[0].node_tree
            from . import readtree
            if node_tree.do_live_update:
                # prOrange("Updating from insert_link callback")
                node_tree.update_tree(context)
                if (link.to_socket.is_linked == False):
                    node_tree.num_links+=1
                elif (link.to_socket.is_multi_input):# and 
                    #len(link.to_socket.links) < link.to_socket.link_limit ):
                    # the above doesn't work and I can't be bothered to fix it right now TODO
                    node_tree.num_links+=1
            
class SchemaNode:
    # is_triggering_execute:BoolProperty(default=False)
    # do_display_update:BoolProperty(default=False)
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['SchemaTree'])


                

class LinkNode(MantisNode):
    useTarget : BoolProperty(default=False)
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




# from bpy.types import NodeCustomGroup

def poll_node_tree(self, object):
    if isinstance(object, MantisTree):
        return True
    return False


# TODO this should check ID's instead of name
def node_group_update(node):
    toggle_update = node.id_data.do_live_update
    node.id_data.do_live_update = False
    # prWhite (node.name, len(node.inputs), len(node.outputs))

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
                if update_output: continue # done here
                if s.bl_idname != item.socket_type: update_output = True; continue
            else: update_output = True; continue # prRed(f"Not found: {item.name}"); 
        else:
            if s:= identifiers_in.get(item.identifier): # if the requested input doesn't exist, update
                found_in.append(item.identifier)
                if update_input: continue # done here
                if s.bl_idname != item.socket_type: update_input = True; continue
            else: update_input = True; continue # prGreen(f"Not found: {item.name}");
    

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
        # prPurple("oink! I am a piggy!")
        update_input = True
    if len(node.outputs) > 0 and  (out := node.outputs[-1]).bl_idname == 'WildcardSocket' and out.is_linked:
        # prPurple("woof! I am a doggy!")
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
    if self.is_updating: # this looks dumb... but update() can be called from update() in a sort of accidental way.
        return
    # prGreen("updating me...")
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
        if self.is_updating: # this looks dumb... but update() can be called from update() in a sort of accidental way.
            return
        self.is_updating = True
        node_group_update(self)
        self.is_updating = False

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "node_tree", text="")
        row.operator("mantis.edit_group", text="", icon='NODETREE', emboss=True)
        

class CircularDependencyError(Exception):
    pass
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

# def update_schema_length(self, context):
#     pass # for now


# TODO tiny UI problem - inserting new links into the tree will not place them in the right place.

#this is a schema node in a mantis tree... kinda confusing
class SchemaGroup(Node, MantisNode):
    bl_idname = "MantisSchemaGroup"
    bl_label = "Node Schema"
    
    node_tree:PointerProperty(type=NodeTree, poll=poll_node_tree_schema, update=node_tree_prop_update,)
    # schema_length:IntProperty(default=5, update=update_schema_length)
    is_updating:BoolProperty(default=False)


    # incoming link
    # from-node = name
    # from socket = index or identifier or something
    # property is unset as soon as it is used
    # so the update function checks this property and handles the incoming link in an allowed place
    # and actually the handle-link function can work as a switch - when the property is unset, it allows new links
    # otherwise it unsets the property and returns.
    
    # def init(self, context):
    #     self.inputs.new("IntSocket", "Schema Length")
    #     self.inputs.new("WildcardSocket", "")

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "node_tree", text="")
        row.operator("mantis.edit_group", text="", icon='NODETREE', emboss=True)
        # layout.prop(self, "schema_length", text="n=")
    
    # WHAT IF:
    #   - the function that creates the input/output map returns to a property in the node
    #   - then the node handles the update in its update function.

    def update(self):
        if self.is_updating: # this looks dumb... but update() can be called from update() in a sort of accidental way.
            return
        self.is_updating = True
        node_group_update(self)
        # kinda dumb but necessary since update doesn't always fix this
        if self.node_tree:
            if len(self.inputs) == 0:
                self.inputs.new("IntSocket", "Schema Length", identifier='Schema Length')
            if self.inputs[-1].bl_idname != "WildcardSocket":
                self.inputs.new("WildcardSocket", "", identifier="__extend__")
        self.is_updating = False

    # def insert_link(self, link):
    #     if self.node_tree is None:
    #         link.is_valid = False
    #         return
    #     sock_type = link.from_socket.bl_idname
    #     for i, sock in enumerate(self.inputs):
    #         if sock == link.to_socket: # dumb but whatever
    #             identifier = link.to_socket.identifier
    #             if sock.bl_idname not in ["WildcardSocket"]:
    #                 if sock.is_linked == True:
    #                     links = [ getattr(l, "from_socket") for l in sock.links ]
    #                     name = sock.name
    #                     # self.inputs.remove(sock)
    #                     # new_input = self.inputs.new(sock_type, name, identifier=identifier, use_multi_input=True); self.inputs.move(-1, i)
    #                     sock.display_shape = 'SQUARE_DOT'
    #                     interface_item = self.node_tree.interface.items_tree[name]
    #                     if not (interface_parent := self.node_tree.interface.items_tree.get('Array')):
    #                         interface_parent = self.node_tree.interface.new_panel(name='Array')
    #                     self.node_tree.interface.move_to_parent(interface_item, interface_parent, len(interface_parent.interface_items))
    #                     # sock.link_limit = self.schema_length TODO this will be very hard to get at this point
    #                     # self.id_data.links.new()
    #             else: #if link.to_socket  == self.inputs[-1]:
    #                     self.inputs.remove(sock)#self.inputs[-1])
    #                     #
    #                     name_stem = link.from_socket.bl_idname.replace('Socket',''); num=0
    #                     if hasattr(link.from_socket, "default_value"):
    #                         name_stem = type(link.from_socket.default_value).__name__
    #                     for n in self.inputs:
    #                         if name_stem in n.name: num+=1
    #                     name = name_stem + '.' + str(num).zfill(3)
    #                     #
    #                     new_input = self.inputs.new(sock_type, name, identifier=identifier, use_multi_input=False); self.inputs.move(-1, i+1)
    #                     new_input.link_limit = 1
    #                     # link.to_socket = new_input
    #                     # this seems to work

    #                     self.inputs.new("WildcardSocket", "")
    #                     if not (interface_parent := self.node_tree.interface.items_tree.get('Constant')):
    #                         interface_parent = self.node_tree.interface.new_panel(name='Constant')
    #                     self.node_tree.interface.new_socket(name=name,in_out='INPUT', socket_type=sock_type, parent=interface_parent)
    #                     return
            
    # TODO: investigate whether this is necessary
    # @classmethod
    # def poll(cls, ntree):
    #     return (ntree.bl_idname in ['MantisTree'])




# handlers!

#annoyingly these have to be persistent
@persistent
def update_handler(scene):
    context=bpy.context
    if context.space_data:
        if not hasattr(context.space_data, "path"):
            return
        trees = [p.node_tree for p in context.space_data.path]
        if not trees: return
        if (node_tree := trees[0]).bl_idname in ['MantisTree']:
            if node_tree.do_live_update and not (node_tree.is_executing or node_tree.is_exporting):
                prev_links = node_tree.num_links
                node_tree.num_links = len(node_tree.links)
                if (prev_links == -1):
                    return
                if prev_links != node_tree.num_links:
                    node_tree.tree_valid = False
                if node_tree.tree_valid == False:
                        node_tree.update_tree(context)

@persistent
def execute_handler(scene):
    context = bpy.context
    if context.space_data:
        if not hasattr(context.space_data, "path"):
            return
        trees = [p.node_tree for p in context.space_data.path]
        if not trees: return
        if (node_tree := trees[0]).bl_idname in ['MantisTree']:
            if node_tree.tree_valid and node_tree.do_live_update and not (node_tree.is_executing or node_tree.is_exporting):
                node_tree.execute_tree(context)
                node_tree.tree_valid = False

# @persistent
# def load_post_handler(scene):
#     print ("cuss and darn")

#     # import bpy
#     import sys

#     def wrapRed(skk):    return "\033[91m{}\033[00m".format(skk)
#     def intercept(fn, *args):
#         print(wrapRed("Intercepting:"), fn)
#         sys.stdout.flush()

#         fn(*args)

#         print(wrapRed("... done"))
#         sys.stdout.flush()

#     for attr in dir(bpy.app.handlers):
#         if attr.startswith("_"):
#             continue

#         handler_list = getattr(bpy.app.handlers, attr)
#         if attr =='load_post_handler':
#             continue
#         if not isinstance(handler_list, list):
#             continue
#         if not handler_list:
#             continue

#         print("Intercept Setup:", attr)

#         handler_list[:] = [lambda *args: intercept(fn, *args) for fn in handler_list]

#         # import cProfile
#         from os import environ
#         do_profile=False
#         print (environ.get("DOPROFILE"))
#         if environ.get("DOPROFILE"):
#             do_profile=True
#         if do_profile:
#             # cProfile.runctx("tree.update_tree(context)", None, locals())
#             # cProfile.runctx("tree.execute_tree(context)", None, locals())
#             import hunter
#             hunter.trace(stdlib=False, action=hunter.CallPrinter(force_colors=False))
# #     def msgbus_callback(*args):
# #         # print("something changed!")
# #         print("Something changed!", args)
# #     owner = object()

#     subscribe_to = (bpy.types.Node, "location")
#     subscribe_to = (bpy.types.Node, "color")
#     subscribe_to = (bpy.types.Node, "dimensions")
#     subscribe_to = (bpy.types.Node, "height")
#     subscribe_to = (bpy.types.Node, "width")
#     subscribe_to = (bpy.types.Node, "inputs")
#     subscribe_to = (bpy.types.Node, "outputs")
#     subscribe_to = (bpy.types.Node, "select")
#     subscribe_to = (bpy.types.Node, "name")
#     subscribe_to = (bpy.types.NodeSocket, "name")
#     subscribe_to = (bpy.types.NodeSocket, "display_shape")


#     bpy.msgbus.subscribe_rna(
#         key=subscribe_to,
#         owner=owner,
#         args=(1, 2, 3),
#         notify=msgbus_callback,
#     )


# print ("cuss and darn")

# bpy.app.handlers.load_post.append(set_tree_invalid)
bpy.app.handlers.depsgraph_update_pre.append(update_handler)
bpy.app.handlers.depsgraph_update_post.append(execute_handler)
# bpy.app.handlers.load_post.append(load_post_handler)

# # import bpy
# import sys

# def wrapRed(skk):    return "\033[91m{}\033[00m".format(skk)
# def intercept(fn, *args):
#     print(wrapRed("Intercepting:"), fn)
#     sys.stdout.flush()

#     fn(*args)

#     print(wrapRed("... done"))
#     sys.stdout.flush()

# for attr in dir(bpy.app.handlers):
#     if attr.startswith("_"):
#         continue

#     handler_list = getattr(bpy.app.handlers, attr)
#     if attr =='load_post_handler':
#         continue
#     if not isinstance(handler_list, list):
#         continue
#     if not handler_list:
#         continue

#     print("Intercept Setup:", attr)

#     handler_list[:] = [lambda *args: intercept(fn, *args) for fn in handler_list]

class MantisVisualizeTree(NodeTree):
    '''A custom node tree type that will show up in the editor type list'''
    bl_idname = 'MantisVisualizeTree'
    bl_label = "mantis output"
    bl_icon = 'HIDE_OFF'


class MantisVisualizeNode(Node):
    bl_idname = "MantisVisualizeNode"
    bl_label = "Node"
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['MantisVisualizeTree'])
    
    def init(self, context):
        pass
    
    def gen_data(self, nc, np = None):
        self.use_custom_color = True
        if nc.node_type == 'XFORM':
            self.color = (1.0 ,0.5, 0.0)
        if nc.node_type == 'LINK':
            self.color = (0.4 ,0.2, 1.0)
        if nc.node_type == 'UTILITY':
            self.color = (0.2 ,0.2, 0.2)
        if nc.node_type == 'SCHEMA':
            self.color = (0.85 ,0.95, 0.9)
        if nc.node_type == 'DUMMY':
            self.color = (0.05 ,0.05, 0.15)
        self.name = ''.join(nc.signature[1:])

        if np:
            if np.label:
                self.label=np.label
            else:
                self.label=np.name
            for inp in nc.inputs:
                s = self.inputs.new('WildcardSocket', inp)
                try:
                    if sock := np.inputs.get(inp):
                        s.color = inp.color
                except AttributeError: #default bl_idname types like Float and Vector, no biggie
                    pass
                except KeyError:
                    pass
            for out in nc.outputs:
                s = self.outputs.new('WildcardSocket', out)
                try:
                    if sock := np.outputs.get(out):
                        s.color = out.color
                except AttributeError: #default bl_idname types like Float and Vector, no biggie
                    pass
                except KeyError:
                    pass
            self.location = np.location # will get overwritten by Grandalf later.
        else:
            self.label = nc.signature[-1] # which is be the unique name.
            for inp in nc.inputs:
                self.inputs.new('WildcardSocket', inp)
            for out in nc.outputs:
                self.outputs.new('WildcardSocket', out)

                
# replace names with bl_idnames for reading the tree and solving schemas.
replace_types = ["NodeGroupInput", "NodeGroupOutput", "SchemaIncomingConnection",
                 "SchemaArrayInput", "SchemaConstInput", "SchemaConstOutput", "SchemaIndex",
                 "SchemaOutgoingConnection", "SchemaConstantOutput", "SchemaArrayOutput",
                 "SchemaArrayInputGet",]

# anything that gets properties added in the graph... this is a clumsy approach but I need to watch for this
#   in schema generation and this is the easiest way to do it for now.
custom_props_types = ["LinkArmature", "UtilityKeyframe", "UtilityFCurve", "UtilityDriver", "xFormBone"]

from_name_filter = ["Driver", ]
to_name_filter = [
                   "Custom Object xForm Override",
                   "Custom Object",
                   "Deform Bones",
                 ]

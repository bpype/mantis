#Mantis Nodes Base
import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, CollectionProperty, IntProperty
from . import ops_nodegroup
from bpy.types import NodeTree, Node, PropertyGroup, Operator, UIList, Panel

from mantis.utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

from bpy.app.handlers import persistent

def TellClasses():
    #Why use a function to do this? Because I don't need every class to register.
    return [MantisNodeGroup, MantisTree, ]

class MantisTree(NodeTree):
    '''A custom node tree type that will show up in the editor type list'''
    bl_idname = 'MantisTree'
    bl_label = "Rigging Nodes"
    bl_icon = 'OUTLINER_OB_ARMATURE'
    
    tree_valid:BoolProperty(default=False)
    do_live_update:BoolProperty(default=True)
    # use this to disable updates for e.g. scripts
    locked:BoolProperty(default=True)
    
    num_links:IntProperty(default=-1)
    
    parsed_tree={}
    
    def interface_update(self, context):
        # no idea what this does
        print ("Update Interface function in MantisTree class")

           
    def interface_update(self, context):
        prGreen("interface_update")
        


    if bpy.app.version >= (3, 2):  # in 3.1 this can lead to a crash
        @classmethod
        def valid_socket_type(cls, socket_type: str):
            # https://docs.blender.org/api/master/bpy.types.NodeTree.html#bpy.types.NodeTree.valid_socket_type
            from mantis.socket_definitions import Tell_bl_idnames
            return socket_type in Tell_bl_idnames()
            # thank you, Sverchok
            
    def update_tree(self, context):
        if self.do_live_update == False:
            return
        from mantis import readtree
        prGreen("Validating Tree: %s" % self.name)
        parsed_tree = readtree.parse_tree(self)
        self.parsed_tree=parsed_tree
        current_tree = bpy.context.space_data.path[-1].node_tree
        self.tree_valid = True
        prWhite("Number of Nodes: %s" % (len(self.parsed_tree)))
        self.display_update(context)
    
    def display_update(self, context):
        if self.do_live_update == False:
            return
        current_tree = bpy.context.space_data.path[-1].node_tree
        for node in current_tree.nodes:
            if hasattr(node, "display_update"):
                try:
                    node.display_update(self.parsed_tree, context)
                except Exception as e:
                    print("Node \"%s\" failed to update display with error: %s" %(wrapGreen(node.name), wrapRed(e)))
                    # raise e
        
    
    def execute_tree(self,context):
        prGreen("Executing Tree: %s" % self.name)
        from mantis import readtree
        readtree.execute_tree(self.parsed_tree, self, context)

    

def update_handler(scene):
    context=bpy.context
    if context.space_data:
        node_tree = context.space_data.path[0].node_tree
        if node_tree.do_live_update:
            prev_links = node_tree.num_links
            node_tree.num_links = len(node_tree.links)
            if (prev_links == -1):
                return
            if prev_links != node_tree.num_links:
                node_tree.tree_valid = False
            if node_tree.tree_valid == False:
                from mantis import readtree
                node_tree.update_tree(context)

def execute_handler(scene):
    context = bpy.context
    if context.space_data:
        node_tree = context.space_data.path[0].node_tree
        if node_tree.tree_valid and node_tree.do_live_update:
            node_tree.execute_tree(context)
            self.tree_valid = False

# bpy.app.handlers.load_post.append(set_tree_invalid)
bpy.app.handlers.depsgraph_update_pre.append(update_handler)
bpy.app.handlers.depsgraph_update_post.append(execute_handler)
    

class MantisNode:
    num_links:IntProperty(default=-1)
    # do_display_update:BoolProperty(default=False)
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname == 'MantisTree')
                
    def insert_link(self, link):
        context = bpy.context
        if context.space_data:
            node_tree = context.space_data.path[0].node_tree
            from mantis import readtree
            prOrange("Updating from insert_link callback")
            node_tree.update_tree(context)
            if (link.to_socket.is_linked == False):
                node_tree.num_links+=1
            elif (link.to_socket.is_multi_input and 
                  link.to_socket.links < link.to_socket.link_limit ):
                node_tree.num_links+=1
            
                

class LinkNode(MantisNode):
    useTarget : BoolProperty(default=False)
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname == 'MantisTree')

class xFormNode(MantisNode):
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname == 'MantisTree')

class DeformerNode(MantisNode):
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname == 'MantisTree')



from bpy.types import NodeCustomGroup
# TODO: make this one's traverse() function actually work
class MantisNodeGroup(NodeCustomGroup, MantisNode):
    bl_idname = "MantisNodeGroup"
    bl_label = "Node Group"
    
    # def poll_node_tree(self, object):
        # if object.bl_idname not in "MantisTree":
            # return False
        # context=bpy.context
        # context = bpy.context
        # if context.space_data:
            # used_trees = [ pathitem.node_tree for pathitem in context.space_data.path]
            # if object in used_trees:
                # return False
    # node_tree:bpy.props.PointerProperty(type=bpy.types.NodeTree, poll=poll_node_tree)
    
    def init(self, context):
        pass
    
    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "node_tree", text="")
        row.operator("mantis.edit_group", text="", icon='NODETREE', emboss=True)
        
# I don't remember why I need this?
class GroupOutputDummySocket:
    # a dummy class for acting like a socket that is coming from every
    #  group output node
    def __init__(self, tree, identifier, is_input=True):
        #
        # So, we need to go through the node tree and find all 
        #   the Group Input sockets that match this
        #   socket's identifier
        #
        sockets = []
        s = None
        for node in tree.nodes:
            if (is_input):
                if node.bl_idname == 'NodeGroupInput':
                    # Group Inputs have outputs... confusing.
                    for s in node.outputs:
                        if (s.identifier == identifier):
                            sockets.append(s)
            else:
                if node.bl_idname == 'NodeGroupOutput':
                    for s in node.inputs:
                        if (s.identifier == identifier):
                            sockets.append(s)
        sock = sockets[-1]
        # whatever the last socket is should be OK for most of this stuff
        self.bl_idname=sock.bl_idname
        self.identifier = identifier
        self.name = sock.name
        is_linked = False
        for s in sockets:
            if s.is_linked:
                is_linked = True; break
        self.is_linked = is_linked
        self.is_output = not is_input
        # hopefully this doesn't matter, since it is a group node...
        self.node = sock.node
        self.links = []
        for s in sockets:
            self.links.extend(s.links)
        # seems to werk

class CircularDependencyError(Exception):
    pass
class GraphError(Exception):
    pass

def get_signature_from_edited_tree(self, context):
    sig_path=[None,]
    for item in context.space_data.path[:-1]:
        sig_path.append(item.node_tree.nodes.active.name)
    return tuple(sig_path+[self.name])

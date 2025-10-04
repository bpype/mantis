""" Optional file providing a tool to visualize Mantis Graphs, for debugging and development"""

from bpy.types import Node, NodeTree, Operator
from bpy.props import StringProperty

from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

class MantisVisualizeTree(NodeTree):
    '''A custom node tree type that will show up in the editor type list'''
    bl_idname = 'MantisVisualizeTree'
    bl_label = "mantis output"
    bl_icon = 'HIDE_OFF'

class MantisVisualizeNode(Node):
    bl_idname = "MantisVisualizeNode"
    bl_label = "Node"
    signature : StringProperty(default = '')
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['MantisVisualizeTree'])

    def init(self, context):
        pass

    def draw_label(self):
        label=''
        exploded = self.signature.separate('|')
        for elem in exploded:
            label+=elem+', '
        label = label[:-2] # cut the last comma
        return label

    def gen_data(self, mantis_node, mode='DEBUG_CONNECTIONS'):
        from .utilities import get_ui_node
        if mantis_node.node_type in ['SCHEMA', 'DUMMY']:
            np=None
        elif mantis_node.ui_signature is None:
            np=None
        else:
            np=get_ui_node(mantis_node.ui_signature, mantis_node.base_tree)
        self.use_custom_color = True
        match mantis_node.node_type:
            case 'XFORM':        self.color = (1.0 ,0.5, 0.0)
            case 'LINK':         self.color = (0.4 ,0.2, 1.0)
            case 'UTILITY':      self.color = (0.2 ,0.2, 0.2)
            case 'DRIVER':       self.color = (0.7, 0.05, 0.8)
            case 'DUMMY_SCHEMA': self.color = (0.85 ,0.95, 0.9)
            case 'DUMMY':        self.color = (0.05 ,0.05, 0.15)


        self.name = '.'.join(mantis_node.signature[1:]) # this gets trunc'd
        self.signature = '|'.join(mantis_node.signature[1:])


        if np:
            if np.label:
                self.label=np.label
            else:
                self.label=np.name
            for inp in mantis_node.inputs:
                match mode:
                    case "DEBUG_CONNECTIONS":
                        if not inp.is_connected:
                            continue
                multi = False
                if len(inp.links) > 1: multi = True
                s = self.inputs.new('WildcardSocket', inp.name, use_multi_input=multi)
                s.link_limit = 4000
                try:
                    if sock := np.inputs.get(inp.name):
                        s.color = sock.color_simple
                except AttributeError: #default bl_idname types like Float and Vector, no biggie
                    pass
                except KeyError:
                    pass
            for out in mantis_node.outputs:
                match mode:
                    case "DEBUG_CONNECTIONS":
                        if not out.is_connected:
                            continue

                s = self.outputs.new('WildcardSocket', out.name)
                try:
                    if sock := np.outputs.get(out.name):
                        s.color = sock.color_simple
                except AttributeError: #default bl_idname types like Float and Vector, no biggie
                    pass
                except KeyError:
                    pass
            self.location = np.location # will get overwritten by Grandalf later.
        else:
            self.label = mantis_node.signature[-1] # which is be the unique name.
            for inp in mantis_node.inputs:
                match mode:
                    case "DEBUG_CONNECTIONS":
                        if not inp.is_connected:
                            continue
                multi = False
                if len(inp.links) > 1: multi = True
                s = self.inputs.new('WildcardSocket', inp.name)
                s.link_limit = 4000
            for out in mantis_node.outputs:
                match mode:
                    case "DEBUG_CONNECTIONS":
                        if not out.is_connected:
                            continue
                self.outputs.new('WildcardSocket', out.name)

def gen_vis_node( mantis_node,
                  vis_tree,
                  links,
                  omit_simple=False,
                 ):
    from .base_definitions import array_output_types
    # if mantis_node.node_type == 'UTILITY' and \
    #      mantis_node.execution_prepared == True:
    #         return
    base_tree= mantis_node.base_tree
    vis = vis_tree.nodes.new('MantisVisualizeNode')
    vis.gen_data(mantis_node)
    for inp in mantis_node.inputs.values():
        for l in inp.links:
            if l.from_node in mantis_node.hierarchy_dependencies:
                links.add(l)
    for out in mantis_node.outputs.values():
        for l in out.links:
            if l.to_node in mantis_node.hierarchy_connections:
                links.add(l)
    return vis

def visualize_tree(m_nodes, base_tree, context):
    # first create a MantisVisualizeTree
    from .readtree import check_and_add_root
    from .utilities import trace_all_nodes_from_root
    import bpy

    base_tree.is_executing=True
    import cProfile
    import pstats, io
    from pstats import SortKey
    cull_no_links = False
    with cProfile.Profile() as pr:
        try:
            trace_from_roots = True
            all_links = set(); mantis_nodes=set(); nodes={}
            if trace_from_roots:
                roots=[]
                for n in m_nodes.values():
                    check_and_add_root(n, roots)
                for r in roots:
                    trace_all_nodes_from_root(r, mantis_nodes)
                if len(mantis_nodes) ==  0:
                    print ("No nodes to visualize")
                    return
            else:
                mantis_keys  = list(base_tree.parsed_tree.keys())
                mantis_nodes = list(base_tree.parsed_tree.values())

            vis_tree = bpy.data.node_groups.new(base_tree.name+'_visualized', type='MantisVisualizeTree')

            for i, m in enumerate(mantis_nodes):
                nodes[m.signature]=gen_vis_node(m, vis_tree, all_links)
                # useful for debugging: check the connections for nodes that are
                # not in the parsed tree or available from trace_all_nodes_from_root.

            for l in all_links:
                # if l.to_node.node_type in ['DUMMY_SCHEMA', 'DUMMY'] or \
                # l.from_node.node_type in ['DUMMY_SCHEMA', 'DUMMY']:
                #     pass
                from_node = nodes.get(l.from_node.signature)
                to_node   = nodes.get(l.to_node.signature)
                from_socket, to_socket = None, None
                if from_node and to_node:
                    from_socket = from_node.outputs.get(l.from_socket)
                    to_socket = to_node.inputs.get(l.to_socket)
                if from_socket and to_socket:
                    try:
                        vis_tree.links.new(
                            input=from_socket,
                            output=to_socket,
                            )
                    except Exception as e:
                        print (type(e)); print(e)
                        raise e
            # at this point not all links are in the tree yet!

            def has_links (n):
                for input in n.inputs:
                    if input.is_linked:
                        return True
                for output in n.outputs:
                    if output.is_linked:
                        return True
                return False

            no_links=[]
            if cull_no_links == True:
                for n in vis_tree.nodes:
                    if not has_links(n):
                        no_links.append(n)
                while (no_links):
                    n = no_links.pop()
                    vis_tree.nodes.remove(n)

        finally:
            s = io.StringIO()
            sortby = SortKey.TIME
            ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats(sortby)
            ps.print_stats(40) # print the top 20
            print(s.getvalue())
            base_tree.prevent_next_exec=True
            base_tree.is_executing=False


from .ops_nodegroup import mantis_tree_poll_op

class MantisVisualizeOutput(Operator):
    """Mantis Visualize Output Operator"""
    bl_idname = "mantis.visualize_output"
    bl_label = "Visualize Output"

    @classmethod
    def poll(cls, context):
        return (mantis_tree_poll_op(context))

    def execute(self, context):
        from time import time
        from .utilities import wrapGreen, prGreen

        tree=context.space_data.path[0].node_tree
        tree.update_tree(context)
        prGreen(f"Visualize Tree: {tree.name}")
        nodes = tree.parsed_tree
        visualize_tree(nodes, tree, context)
        return {"FINISHED"}

""" Optional file providing a tool to visualize Mantis Graphs, for debugging and development"""

from bpy.types import Node, NodeTree, Operator

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
    @classmethod
    def poll(cls, ntree):
        return (ntree.bl_idname in ['MantisVisualizeTree'])
    
    def init(self, context):
        pass
    
    def gen_data(self, mantis_node, mode='DEBUG_CONNECTIONS'):
        from .utilities import get_node_prototype
        np=get_node_prototype(mantis_node.ui_signature, mantis_node.base_tree)
        self.use_custom_color = True
        match mantis_node.node_type:
            case 'XFORM':        self.color = (1.0 ,0.5, 0.0)
            case 'LINK':         self.color = (0.4 ,0.2, 1.0)
            case 'UTILITY':      self.color = (0.2 ,0.2, 0.2)
            case 'DUMMY_SCHEMA': self.color = (0.85 ,0.95, 0.9)
            case 'DUMMY':        self.color = (0.05 ,0.05, 0.15)
        self.name = '.'.join(mantis_node.signature[1:])

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
                s = self.inputs.new('WildcardSocket', inp.name)
                try:
                    if sock := np.inputs.get(inp.name):
                        s.color = inp.color_simple
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
                        s.color = out.color_simple
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
                self.inputs.new('WildcardSocket', inp.name)
            for out in mantis_node.outputs:
                match mode:
                    case "DEBUG_CONNECTIONS":
                        if not out.is_connected:
                            continue
                self.outputs.new('WildcardSocket', out.name)

def gen_vis_node(mantis_node, vis_tree, links):
    from .utilities import get_node_prototype
    base_tree= mantis_node.base_tree
    vis = vis_tree.nodes.new('MantisVisualizeNode')
    vis.gen_data(mantis_node)
    for inp in mantis_node.inputs.values():
        for l in inp.links:
            links.add(l)
    for out in mantis_node.outputs.values():
        for l in out.links:
            links.add(l)
    return vis
                
def visualize_tree(nodes, base_tree, context):
    # first create a MantisVisualizeTree
    from .readtree import check_and_add_root
    from .utilities import trace_all_nodes_from_root
    import bpy
    trace_all_nodes=True
    if trace_all_nodes:
        roots=[]
        for n in nodes.values():
            check_and_add_root(n, roots)
        mantis_nodes=set()
        for r in roots:
            nodes_from_root = ( trace_all_nodes_from_root(r, mantis_nodes))
        if len(mantis_nodes) ==  0:
            print ("No nodes to visualize")
            return
        all_links = set()
        nodes={}
        vis_tree = bpy.data.node_groups.new(base_tree.name+'_visualized', type='MantisVisualizeTree')
    else:
        mantis_nodes = list(base_tree.parsed_tree.values())

    for m in mantis_nodes:
        nodes[m.signature]=gen_vis_node(m, vis_tree,all_links)

    for l in all_links:
        if l.to_node.node_type in ['DUMMY_SCHEMA', 'DUMMY'] or \
           l.from_node.node_type in ['DUMMY_SCHEMA', 'DUMMY']:
            pass
        # print (l.from_node.node_type, l.to_node.node_type)
        # n_name_in = '.'.join(l.from_node.signature[1:])
        # s_name_in = l.from_socket
        # n_name_out = '.'.join(l.to_node.signature[1:])
        # s_name_out = l.to_socket
        # print (n_name_in, s_name_in, " --> ", n_name_out, s_name_out)
        from_node=nodes[l.from_node.signature]
        to_node=nodes[l.to_node.signature]
        from_socket = from_node.outputs[l.from_socket]
        to_socket = to_node.inputs[l.to_socket]
        try:
            vis_tree.links.new(
                input=from_socket,
                output=to_socket,
                )
        except Exception as e:
            print (type(e))
            prRed(f"Could not make link {n_name_in}:{s_name_in}-->{n_name_out}:{s_name_out}")
            print(e)
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

    for n in vis_tree.nodes:
        if not has_links(n):
            no_links.append(n)
    
    def side_len(n):
        from math import floor
        side = floor(n**(1/2)) + 1
        return side
    side=side_len(len(no_links))
    break_me = True
    for i in range(side):
        for j in range(side):
            index = side*i+j
            try:
                n = no_links[index]
                n.location.x = i*200
                n.location.y = j*200
            except IndexError:
                break_me = True # it's too big, that's OK the square is definitely bigger
                break
        if break_me:
            break


    from .utilities import SugiyamaGraph
    SugiyamaGraph(vis_tree, 1) # this can take a really long time

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
        # tree.execute_tree(context)
        prGreen(f"Visualize Tree: {tree.name}")
        nodes = tree.parsed_tree
        visualize_tree(nodes, tree, context)
        return {"FINISHED"}
#Node Graph Functions

        
        
def SeekNodePathUntil(node, input_name, nodeType, direction = 'BACK'):
    from .node_container_common import trace_single_line, trace_single_line_up
    if direction == 'BACK':
        return trace_single_line(node, input_name)
    else: # 'FORWARD'
        return trace_single_line_up(node, input_name)
    

def get_node_container(node, context):
    from .utilities import parse_node_tree, print_lines
    base_tree = context.space_data.path[0].node_tree
    from .readtree import get_tree_data
    parsed_tree = parse_node_tree(base_tree)
    nodes = get_tree_data(parsed_tree, base_tree)
    node_container = None
    if (node.id_data != context.space_data.path[-1].node_tree):
        return None, None
    if (node.id_data == base_tree):
        try:
            #other_node = node.inputs['Parent'].links[0].from_node
            node_container = nodes.get( ('NONE', node.name) )
        except IndexError: # node just isn't connected'
            nodes = None
        return node_container, nodes
    else: # find it in Node-Groups
          # I am checking the active node, which should always
          #  be the path of Group Nodes.
          # if not, then the user is doing something sp0oky
        for node_container in nodes.values():
            if len(node_container.signature) != len(context.space_data.path)+1:
                continue
            tree = base_tree; found = False
            for name in node_container.signature[0:]:
                g_node = tree.nodes.get(name)
                if not (g_node == tree.nodes.active): continue 
                if (hasattr(g_node, 'node_tree')):
                    tree = g_node.node_tree
                elif name == node.name: found = True; break
            else:
                found = False
                continue
            if found == True:
                return node_container, nodes
        else:
            return None, None
    return None, None
                
def GetUpstreamXFormNodes(node_container, context):
    if (node_container):
        input_name=None
        if node_container.node_type == 'LINK':
            input_name = 'Input Relationship'
            if node_container.__class__.__name__ == 'LinkInherit':
                input_name = 'Parent'
        elif node_container.node_type == 'XFORM':
            input_name = 'Relationship'
        xF = SeekNodePathUntil(node_container, input_name, ['xFormArmature', 'xFormBone', 'xFormRoot'])
        return xF
        
    else:
        return None
        
def GetDownstreamXFormNodes(node_container, context):
    if (node_container):
        output_name=None
        if node_container.node_type == 'LINK':
            output_name = 'Output Relationship'
            if node_container.__class__.__name__ == 'LinkInherit':
                output_name = 'Inheritance'
        elif node_container.node_type == 'XFORM':
            output_name = 'xForm Out'
        xF = SeekNodePathUntil(node_container, output_name, ['xFormArmature', 'xFormBone', 'xFormRoot'], direction = 'FORWARD')
        return xF
    else:
        return None
    
        
# def get_parent(node_container):
    # node_line, socket = trace_single_line(node_container, "Relationship")
    # parent_nc = None
    # for i in range(len(node_line)):
        # print (node_line[i])
        # # check each of the possible parent types.
        # if ( (node_line[ i ].__class__.__name__ == 'LinkInherit') ):
            # try: # it's the next one
                # return node_line[ i + 1 ]
            # except IndexError: # if there is no next one...
                # return None # then there's no parent!
    # return None
    # # TO DO!
    # #
    # # make this do shorthand parenting - if no parent, then use World
    # #  if the parent node is skipped, use the previous node (an xForm)
    # #  with default settings.
    # # it is OK to generate a new, "fake" node container for this!
    
    # #my_sig = get_node_signature(node, tree)
    
    
    
def FindIKNode():
    pass
 



#fool: should be wrColor like prColor... dumb

def wrapRed(skk):    return "\033[91m{}\033[00m".format(skk)
def wrapGreen(skk):  return "\033[92m{}\033[00m".format(skk)
def wrapPurple(skk): return "\033[95m{}\033[00m".format(skk)
def wrapWhite(skk):  return "\033[97m{}\033[00m".format(skk)
def wrapOrange(skk):  return "\033[0;33m{}\033[00m".format(skk)

# these should reimplement the print interface..
def prRed(*args): print (*[wrapRed(arg) for arg in args])
def prGreen(*args): print (*[wrapGreen(arg) for arg in args])
def prPurple(*args): print (*[wrapPurple(arg) for arg in args])
def prWhite(*args): print (*[wrapWhite(arg) for arg in args])
def prOrange(*args): print (*[wrapOrange(arg) for arg in args])

# add THIS to the top of a file for easy access:
# from mantis.utilities import (prRed, prGreen, prPurple, prWhite,
#                               prOrange,
#                               wrapRed, wrapGreen, wrapPurple, wrapWhite,
#                               wrapOrange,)





#  SOME PRINTS

#DO! Figure out what the hell this does
# then re-write it in a simpler, cleaner way
# that ignores groups because it gets lines from a parsed tree
# ideally I can use the seeking-lines instead of the socket/tree lines
# since those allow the function to travel through the tree.

# not sure if the above comment still has any place here....

def print_lines(lines): 
    printstring, string = "", ""
    cur_g = 0
    for line in lines:
        string += wrapRed("%i: " % len(line))
        for s, g in line:
            new_g = len(g) -1
            difference = new_g - cur_g
            if difference > 0:
                string = string[:-1] # get rid of leading space
                for i in range(difference):
                    string += " [ "
            elif difference < 0:
                string = string[:-4]# get rid of arrow
                for i in range(abs(difference)):
                    string += " ] "
                string += "-> "
            cur_g = new_g
            wrap=wrapWhite
            if (s.node.bl_idname in ['UtilitySwitch', 'UtilityDriver', 'UtilityDriverVariable']):
                wrap = wrapPurple
            elif (s.node.bl_idname in ['xFormArmatureNode', 'xFormBoneNode']):
                wrap = wrapOrange
            elif (s.node.bl_idname in ['LinkStretchTo']):
                wrap = wrapRed
            elif ('Link' in s.node.bl_idname):
                wrap = wrapGreen
            string += wrap(s.node.name + ":" + s.name) + " -> "
        string = string[:-4]
        while cur_g > 0:
            cur_g -= 1
            string += " ] "
        cur_g, difference = 0,0
        printstring +=string + "\n\n"; string = ""
    return printstring
    # why is this not printing groups in brackets?

def print_socket_signature(sig):
    string = ""
    for i, e in enumerate(sig):
        if (e == "NONE"):
            continue
        wrap = wrapWhite
        if (i == len(sig)-2):
            wrap = wrapRed
        elif (i == len(sig) - 1):
            wrap = wrapGreen
        string+= wrap(e) + ":"
    return string[:-1]
    
def print_node_signature(sig,):
    string = ""
    for i, e in enumerate(sig):
        if (e == "NONE"):
            continue
        wrap = wrapWhite
        if (i == len(sig)-2):
            wrap = wrapRed
        elif (i == len(sig) - 1):
            continue
        string+= wrap(e) + ":"
    return string[:-1]

def print_parsed_node(parsed_node):
    # do: make this consistent with the above
    string = ""
    for k, v in parsed_node.items():
        if isinstance(v, dict):
            string += "%s:\n" % (k)
            for k1, v1 in v.items():
                string += "    %s:                %s\n" % (k1, v1)
        else:
            string += "%s:    %s\n" % (k, v )
    return string


## SIGNATURES ##
def get_socket_signature(line_element):
    """
    This function creates a convenient, hashable signature for
    identifying a node path.
    """
    if not line_element:
        return None
    signature, socket, tree_path = [], line_element[0], line_element[1]
    for n in tree_path:
        if hasattr(n, "name"):
            signature.append(n.name)
        else:
            signature.append("NONE")
    signature.append(socket.node.name); signature.append(socket.identifier)
    return tuple(signature)

def tuple_of_line(line):
    # For creating a set of lines
    return tuple(tuple_of_line_element(e) for e in line)
def tuple_of_line_element(line_element):
    return (line_element[0], tuple(line_element[1]))

# A fuction for getting to the end of a Reroute.
def socket_seek(start_link, links):
    link = start_link
    while(link.from_socket):
        for newlink in links:
            if link.from_socket.node.inputs:
                if newlink.to_socket == link.from_socket.node.inputs[0]:
                    link=newlink; break
        else:
            break
    return link.from_socket

# this creates fake links that have the same interface as Blender's
# so that I can bypass Reroutes
def clear_reroutes(links):
    from .node_container_common import DummyLink
    kept_links, rerouted_starts = [], []
    rerouted = []
    all_links = links.copy()
    while(all_links):
        link = all_links.pop()
        to_cls = link.to_socket.node.bl_idname
        from_cls = link.from_socket.node.bl_idname
        reroute_classes = ["NodeReroute"]
        if (to_cls in reroute_classes and
            from_cls in reroute_classes):
                rerouted.append(link)
        elif (to_cls in reroute_classes and not
            from_cls in reroute_classes):
                rerouted.append(link)
        elif (from_cls in reroute_classes and not
            to_cls in reroute_classes):
                rerouted_starts.append(link)
        else:
            kept_links.append(link)
    for start in rerouted_starts:
        from_socket = socket_seek(start, rerouted)
        new_link = DummyLink(from_socket=from_socket, to_socket=start.to_socket, nc_from=None, nc_to=None)
        kept_links.append(new_link)
    return kept_links


def tree_from_nc(sig, base_tree):
    if (sig[0] == 'MANTIS_AUTOGENERATED'):
        sig = sig[:-2] # cut off the end part of the signature. (Why am I doing this??) # because it uses socket.name and socket.identifier
        # this will lead to totally untraceble bugs in the event of a change in how signatures are assigned
    tree = base_tree
    for i, path_item in enumerate(sig):
        if (i == 0) or (i == len(sig) - 1):
            continue
        tree = tree.nodes.get(path_item).node_tree
    return tree
    
def get_node_prototype(sig, base_tree):
    return tree_from_nc(sig, base_tree).nodes.get( sig[-1] )


##################################################################################################
# groups and changing sockets -- this is used extensively by Schema.
##################################################################################################

def get_socket_maps(node):
    maps = [{}, {}]
    node_collection = ["inputs", "outputs"]
    links = ["from_socket", "to_socket"]
    for collection, map, link in zip(node_collection, maps, links):
        for sock in getattr(node, collection):
            if sock.is_linked:
                map[sock.identifier]=[ getattr(l, link) for l in sock.links ]
            else:
                map[sock.identifier]=sock.get("default_value")
    return maps

def do_relink(node, s, map, in_out='INPUT', parent_name = ''):
    tree = node.id_data; interface_in_out = 'OUTPUT' if in_out == 'INPUT' else 'INPUT'
    if hasattr(node, "node_tree"):
        tree = node.node_tree
        interface_in_out=in_out
    from bpy.types import NodeSocket
    get_string = '__extend__'
    if s: get_string = s.identifier
    if val := map.get(get_string):
        if isinstance(val, list):
            for sub_val in val:
                # this will only happen once because it assigns s, so it is safe to do in the for loop.
                if s is None:
                    # prGreen("zornpt")
                    name = unique_socket_name(node, sub_val, tree)
                    sock_type = sub_val.bl_idname
                    if parent_name:
                        interface_socket = update_interface(tree.interface, name, interface_in_out, sock_type, parent_name)
                    if in_out =='INPUT':
                        s = node.inputs.new(sock_type, name, identifier=interface_socket.identifier)
                    else:
                        s = node.outputs.new(sock_type, name, identifier=interface_socket.identifier)
                    if parent_name == 'Array': s.display_shape='SQUARE_DOT'
                    # then move it up and delete the other link.
                    # this also needs to modify the interface of the node tree.
                    
                    
                #
                if isinstance(sub_val, NodeSocket):
                    if in_out =='INPUT':
                        node.id_data.links.new(input=sub_val, output=s)
                    else:
                        node.id_data.links.new(input=s, output=sub_val)
        else:
            try:
                s.default_value = val
            except (AttributeError, ValueError): # must be readonly or maybe it doesn't have a d.v.
                pass

def update_interface(interface, name, in_out, sock_type, parent_name):
    if parent_name:
        if not (interface_parent := interface.items_tree.get(parent_name)):
            interface_parent = interface.new_panel(name=parent_name)
        socket = interface.new_socket(name=name,in_out=in_out, socket_type=sock_type, parent=interface_parent)
        if parent_name == 'Connection':
            in_out = 'OUTPUT' if in_out == 'INPUT' else 'INPUT' # flip this make sure connections always do both
            interface.new_socket(name=name,in_out=in_out, socket_type=sock_type, parent=interface_parent)
        return socket
    else:
        raise RuntimeError(wrapRed("Cannot add interface item to tree without specifying type."))

def relink_socket_map(node, node_collection, map, item, in_out=None):
    from bpy.types import NodeSocket
    if not in_out: in_out=item.in_out
    if node.bl_idname in ['MantisSchemaGroup'] and item.parent and item.parent.name == 'Array':
        multi = False
        if in_out == 'INPUT':
            multi=True
        s = node_collection.new(type=item.socket_type, name=item.name, identifier=item.identifier,  use_multi_input=multi)
        # s.link_limit = node.schema_length TODO
    else:
        s = node_collection.new(type=item.socket_type, name=item.name, identifier=item.identifier)
    if item.parent.name == 'Array': s.display_shape = 'SQUARE_DOT'
    do_relink(node, s, map)

def unique_socket_name(node, other_socket, tree):
    name_stem = other_socket.bl_label; num=0
    # if hasattr(other_socket, "default_value"):
    #     name_stem = type(other_socket.default_value).__name__
    for item in tree.interface.items_tree:
        if item.item_type == 'PANEL': continue
        if other_socket.is_output and item.in_out == 'INPUT': continue
        if not other_socket.is_output and item.in_out == 'OUTPUT': continue
        if name_stem in item.name: num+=1
    name = name_stem + '.' + str(num).zfill(3)
    return name



##############################
#  READ TREE and also Schema Solve!
##############################

def init_connections(nc):
    c, hc = [], []
    for i in nc.outputs.values():
        for l in i.links:
            # if l.from_node != nc:
            #     continue
            if l.is_hierarchy:
                hc.append(l.to_node)
            c.append(l.to_node)
    nc.hierarchy_connections = hc
    nc.connections = c

def init_dependencies(nc):
    c, hc = [], []
    for i in nc.inputs.values():
        for l in i.links:
            # if l.to_node != nc:
            #     continue
            if l.is_hierarchy:
                hc.append(l.from_node)
            c.append(l.from_node)
    nc.hierarchy_dependencies = hc
    nc.dependencies = c

# schema_input_types = [
#         'SchemaIndex',
#         'SchemaArrayInput',
#         'SchemaArrayInputGet',
#         'SchemaConstInput',
#         'SchemaIncomingConnection',
# ]
# schema_output_types = [
#         'SchemaArrayOutput',
#         'SchemaConstOutput',
#         'SchemaOutgoingConnection',
# ]

from .base_definitions import from_name_filter, to_name_filter

def init_schema_dependencies(schema, all_nc):
    schema_name = schema.signature[-1]
    all_input_nodes = []
    all_output_nodes = []
    # all_inernal_nodes = []
    # for nc in all_nc.values():
    #     for t in schema_input_types:
    #         if nc.signature == (*schema.signature, t):
    #             all_input_nodes.append(nc)
    #     for t in schema_output_types:
    #         if nc.signature == (*schema.signature, t):
    #             all_output_nodes.append(nc)
    # prOrange (schema.connections)
    # print (schema.hierarchy_connections)
    # prOrange (schema.dependencies)
    # prOrange (schema.hierarchy_dependencies)

    # so the challenge is to map these and check both ends
    from .base_definitions import from_name_filter, to_name_filter
    # go through the interface items then of course
    from .utilities import get_node_prototype
    np = get_node_prototype(schema.signature, schema.base_tree)
    tree = np.node_tree
    schema.dependencies = []
    schema.hierarchy_dependencies = []
    for item in tree.interface.items_tree:
        if item.item_type == 'PANEL':
            continue
        hierarchy = True
        hierarchy_reason=""
        if item.in_out == 'INPUT':
            c = schema.dependencies
            hc = schema.hierarchy_dependencies
            if item.parent and item.parent.name == 'Array':
                for t in ['SchemaArrayInput', 'SchemaArrayInputGet']:
                    if (nc := all_nc.get( (*schema.signature, t) )):
                        for to_link in nc.outputs[item.name].links:
                            if to_link.to_socket in to_name_filter:
                                # hierarchy_reason='a'
                                hierarchy = False
                        for from_link in schema.inputs[item.identifier].links:
                            if from_link.from_socket in from_name_filter:
                                hierarchy = False
                                # hierarchy_reason='b'
                        if from_link.from_node not in c:
                            if hierarchy:
                                hc.append(from_link.from_node)
                            c.append(from_link.from_node)
            if item.parent and item.parent.name == 'Constant':
                if nc := all_nc.get((*schema.signature, 'SchemaConstInput')):
                    for to_link in nc.outputs[item.name].links:
                        if to_link.to_socket in to_name_filter:
                            # hierarchy_reason='c'
                            hierarchy = False
                    for from_link in schema.inputs[item.identifier].links:
                        if from_link.from_socket in from_name_filter:
                            # hierarchy_reason='d'
                            hierarchy = False
                    if from_link.from_node not in c:
                        if hierarchy:
                            hc.append(from_link.from_node)
                        c.append(from_link.from_node)
            if item.parent and item.parent.name == 'Connection':
                if nc := all_nc.get((*schema.signature, 'SchemaIncomingConnection')):
                    for to_link in nc.outputs[item.name].links:
                        if to_link.to_socket in to_name_filter:
                            # hierarchy_reason='e'
                            hierarchy = False
                    for from_link in schema.inputs[item.identifier].links:
                        if from_link.from_socket in from_name_filter:
                            # hierarchy_reason='f'
                            hierarchy = False
                    if from_link.from_node not in c:
                        if hierarchy:
                            hc.append(from_link.from_node)
                        c.append(from_link.from_node)
        # prPurple(item.in_out)
        # if hierarchy:
        #     prOrange(item.name)
        # else:
        #     prWhite(item.name)
        #     print(hierarchy_reason)

        # else:
        #     c = schema.connections
        #     hc = schema.hierarchy_connections
        #     if item.parent and item.parent.name == 'Array':
        #         if nc := all_nc.get((*schema.signature, 'SchemaArrayOutput')):
        #             for from_link in nc.inputs[item.name].links:
        #                 if from_link.from_socket in from_name_filter:
        #                     hierarchy = False
        #             for to_link in schema.outputs[item.identifier].links:
        #                 if to_link.to_socket in to_name_filter:
        #                     hierarchy = False
        #     if item.parent and item.parent.name == 'Constant':
        #         if nc := all_nc.get((*schema.signature, 'SchemaConstOutput')):
        #             for from_link in nc.inputs[item.name].links:
        #                 if from_link.from_socket in from_name_filter:
        #                     hierarchy = False
        #             for to_link in schema.outputs[item.identifier].links:
        #                 if to_link.to_socket in to_name_filter:
        #                     hierarchy = False
        #     if item.parent and item.parent.name == 'Connection':
        #         if nc := all_nc.get((*schema.signature, 'SchemaOutgoingConnection')):
        #             for from_link in nc.inputs[item.name].links:
        #                 if from_link.from_socket in from_name_filter:
        #                     hierarchy = False
        #             for to_link in schema.outputs[item.identifier].links:
        #                 if to_link.to_socket in to_name_filter:
        #                     hierarchy = False
    # for nc in all_input_nodes:
    #     for output in nc.outputs.values():
    #         for l in output.links:
    #             if l.to_socket in to_name_filter:
    #                 print("not hierarchy", l.to_socket)
    #             else:
    #                 print("hierarchy", l.to_socket)
    # for inp in schema.inputs.values():
    #     for l in inp.links:
    #         if l.from_socket in from_name_filter:
    #             print("not hierarchy", l.from_socket)
    #         else:
    #             print("hierarchy", l.from_socket)
    
    # we need to get dependencies and connections
    # but we can use the same method to do each


    # prPurple (schema.connections)
    # # print (schema.hierarchy_connections)
    # prPurple (schema.dependencies)
    # prPurple (schema.hierarchy_dependencies)
    # #


def check_and_add_root(n, roots, include_non_hierarchy=False):
    # if not (hasattr(n, 'inputs')) or ( len(n.inputs) == 0):
    #     roots.append(n)
    # elif (hasattr(n, 'inputs')):
    #     for inp in n.inputs.values():
    #         if inp.is_linked: return
    if include_non_hierarchy == True and len(n.dependencies) > 0:
        return 
    elif len(n.hierarchy_dependencies) > 0:
        return
    roots.append(n)

def get_link_in_out(link):
    from .base_definitions import replace_types
    from_name, to_name = link.from_socket.node.name, link.to_socket.node.name
    # catch special bl_idnames and bunch the connections up
    if link.from_socket.node.bl_idname in replace_types:
        from_name = link.from_socket.node.bl_idname 
    if link.to_socket.node.bl_idname in replace_types:
        to_name = link.to_socket.node.bl_idname
    return from_name, to_name

def link_node_containers(tree_path_names, link, local_nc, from_suffix='', to_suffix=''):
    dummy_types = ["DUMMY", "DUMMY_SCHEMA"]
    from_name, to_name = get_link_in_out(link)
    nc_from = local_nc.get( (*tree_path_names, from_name+from_suffix) )
    nc_to = local_nc.get( (*tree_path_names, to_name+to_suffix))
    if (nc_from and nc_to):
        from_s, to_s = link.from_socket.name, link.to_socket.name
        if nc_to.node_type in dummy_types: to_s = link.to_socket.identifier
        if nc_from.node_type in dummy_types: from_s = link.from_socket.identifier
        try:
            connection = nc_from.outputs[from_s].connect(node=nc_to, socket=to_s)
            if connection is None:
                prWhite(f"Already connected: {from_name}:{from_s}->{to_name}:{to_s}")
            return connection
        except KeyError as e:
            prRed(f"{nc_from}:{from_s} or {nc_to}:{to_s} missing; review the connections printed below:")
            print (nc_from.outputs.keys())
            print (nc_to.inputs.keys())
            raise e
    else:
        prRed(nc_from, nc_to, (*tree_path_names, from_name+from_suffix), (*tree_path_names, to_name+to_suffix))
        # for nc in local_nc.values():
        #     prOrange(nc)
        raise RuntimeError(wrapRed("Link not connected: %s -> %s in tree %s" % (from_name, to_name, tree_path_names[-1])))
    
def get_all_dependencies(nc):
    """ Given a NC, find all dependencies for the NC as a dict of nc.signature:nc"""
    nodes = []
    can_descend = True
    check_nodes = [nc]
    while (len(check_nodes) > 0): # this seems innefficient, why 2 loops?
        new_nodes = []
        while (len(check_nodes) > 0):
            node = check_nodes.pop()
            connected_nodes = node.hierarchy_dependencies.copy()
            for new_node in connected_nodes:
                if new_node in nodes: continue 
                new_nodes.append(new_node)
                nodes.append(new_node)
        check_nodes = new_nodes
    return nodes
            
##################################################################################################
# misc
##################################################################################################


# this function is used a lot, so it is a good target for optimization.
def to_mathutils_value(socket):
    if hasattr(socket, "default_value"):
        from mathutils import Matrix, Euler, Quaternion, Vector
        val = socket.default_value
        # if socket.bl_idname in [
        #     'NodeSocketVector',
        #     'NodeSocketVectorAcceleration',
        #     'NodeSocketVectorDirection',
        #     'NodeSocketVectorTranslation',
        #     'NodeSocketVectorXYZ',
        #     'NodeSocketVectorVelocity',
        #     'VectorSocket',
        #     'VectorEulerSocket',
        #     'VectorTranslationSocket',
        #     'VectorScaleSocket',
        #     'ParameterVectorSocket',]:
        # # if "Vector" in socket.bl_idname:
        #     return (Vector(( val[0], val[1], val[2], )))
        # if socket.bl_idname in ['NodeSocketVectorEuler']:
        #     return (Euler(( val[0], val[1], val[2])), 'XYZ',) #TODO make choice
        if socket.bl_idname in ['MatrixSocket']:
            return socket.TellValue()
        # elif socket.bl_idname in ['QuaternionSocket']:
        #     return (Quaternion( (val[0], val[1], val[2], val[3],)) )
        # elif socket.bl_idname in ['QuaternionSocketAA']:
        #     return (Quaternion( (val[1], val[2], val[3],), val[0], ) )
        # elif socket.bl_idname in ['BooleanThreeTupleSocket']:
        #     return (val[0], val[1], val[2]) 
        else:
            return val
    else:
        return None


def all_trees_in_tree(base_tree, selected=False):
    """ Recursively finds all trees referenced in a given base-tree."""
    # note that this is recursive but not by tail-end recursion
    # a while-loop is a better way to do recursion in Python.
    trees = [base_tree]
    can_descend = True
    check_trees = [base_tree]
    while (len(check_trees) > 0): # this seems innefficient, why 2 loops?
        new_trees = []
        while (len(check_trees) > 0):
            tree = check_trees.pop()
            for node in tree.nodes:
                if selected == True and node.select == False:
                    continue
                if new_tree := getattr(node, "node_tree", None):
                    if new_tree in trees: continue 
                    new_trees.append(new_tree)
                    trees.append(new_tree)
        check_trees = new_trees
    return trees

# this is a destructive operation, not a pure function or whatever. That isn't good but I don't care.
def SugiyamaGraph(tree, iterations):
        from grandalf.graphs import Vertex, Edge, Graph, graph_core
        class defaultview(object):
            w,h = 1,1
            xz = (0,0)
        
        no_links = set()
        verts = {}
        for n in tree.nodes:
            has_links=False
            for inp in n.inputs:
                if inp.is_linked:
                    has_links=True
                    break
            else:
                no_links.add(n.name)
            for out in n.outputs:
                if out.is_linked:
                    has_links=True
                    break
            else:
                try:
                    no_links.remove(n.name)
                except KeyError:
                    pass
            if not has_links:
                continue
                
            v = Vertex(n.name)
            v.view = defaultview()
            v.view.xy = n.location
            v.view.h = n.height*2.5
            v.view.w = n.width*2.2
            verts[n.name] = v
            
        edges = []
        for link in tree.links:
            weight = 1 # maybe this is useful
            edges.append(Edge(verts[link.from_node.name], verts[link.to_node.name], weight) )
        graph = Graph(verts.values(), edges)

        from grandalf.layouts import SugiyamaLayout
        sug = SugiyamaLayout(graph.C[0]) # no idea what .C[0] is
        roots=[]
        for node in tree.nodes:
            
            has_links=False
            for inp in node.inputs:
                if inp.is_linked:
                    has_links=True
                    break
            for out in node.outputs:
                if out.is_linked:
                    has_links=True
                    break
            if not has_links:
                continue
                
            if len(node.inputs)==0:
                roots.append(verts[node.name])
            else:
                for inp in node.inputs:
                    if inp.is_linked==True:
                        break
                else:
                    roots.append(verts[node.name])
        
        sug.init_all(roots=roots,)
        sug.draw(iterations)
        for v in graph.C[0].sV:
            for n in tree.nodes:
                if n.name == v.data:
                    n.location.x = v.view.xy[1]
                    n.location.y = v.view.xy[0]
        
        # now we can take all the input nodes and try to put them in a sensible place

        for n_name in no_links:
            n = tree.nodes.get(n_name)
            next_n = None
            next_node = None
            for output in n.outputs:
                if output.is_linked == True:
                    next_node = output.links[0].to_node
                    break
            # let's see if the next node
            if next_node:
                # need to find the other node in the same layer...
                other_node = None
                for s_input in next_node.inputs:
                    if s_input.is_linked:
                        other_node = s_input.links[0].from_node
                        if other_node is n:
                            continue
                        else:
                            break
                if other_node:
                    n.location = other_node.location
                    n.location.y -= other_node.height*2
                else: # we'll just position it next to the next node
                    n.location = next_node.location
                    n.location.x -= next_node.width*1.5
        



##################################################################################################
# stuff I should probably refactor!!
##################################################################################################

# what in the cuss is this horrible abomination??
def class_for_mantis_prototype_node(prototype_node):
    """ This is a class which returns a class to instantiate for
        the given prototype node."""
    #from .node_container_classes import TellClasses
    from . import xForm_containers, link_containers, misc_containers, primitives_containers, deformer_containers, math_containers, schema_containers
    classes = {}
    for module in [xForm_containers, link_containers, misc_containers, primitives_containers, deformer_containers, math_containers, schema_containers]:
        for cls in module.TellClasses():
            classes[cls.__name__] = cls
    # I could probably do a string.replace() here
    # But I actually think this is a bad idea since I might not
    #  want to use this name convention in the future
    #  this is easy enough for now, may refactor.
    #
    # kek, turns out it was completely friggin' inconsistent already
    if prototype_node.bl_idname == 'xFormRootNode':
        return classes["xFormRoot"]
    elif prototype_node.bl_idname == 'xFormArmatureNode':
        return classes["xFormArmature"]
    elif prototype_node.bl_idname == 'xFormBoneNode':
        return classes["xFormBone"]
    elif prototype_node.bl_idname == 'xFormGeometryObject':
        return classes["xFormGeometryObject"]
    elif prototype_node.bl_idname == 'linkInherit':
        return classes["LinkInherit"]
    elif prototype_node.bl_idname == 'InputFloatNode':
        return classes["InputFloat"]
    elif prototype_node.bl_idname == 'InputVectorNode':
        return classes["InputVector"]
    elif prototype_node.bl_idname == 'InputBooleanNode':
        return classes["InputBoolean"]
    elif prototype_node.bl_idname == 'InputBooleanThreeTupleNode':
        return classes["InputBooleanThreeTuple"]
    elif prototype_node.bl_idname == 'InputRotationOrderNode':
        return classes["InputRotationOrder"]
    elif prototype_node.bl_idname == 'InputTransformSpaceNode':
        return classes["InputTransformSpace"]
    elif prototype_node.bl_idname == 'InputStringNode':
        return classes["InputString"]
    elif prototype_node.bl_idname == 'InputQuaternionNode':
        return classes["InputQuaternion"]
    elif prototype_node.bl_idname == 'InputQuaternionNodeAA':
        return classes["InputQuaternionAA"]
    elif prototype_node.bl_idname == 'InputMatrixNode':
        return classes["InputMatrix"]
    elif prototype_node.bl_idname == 'MetaRigMatrixNode':
        return classes["InputMatrix"]
    elif prototype_node.bl_idname == 'InputLayerMaskNode':
        return classes["InputLayerMask"]
    elif prototype_node.bl_idname == 'GeometryCirclePrimitive':
        return classes["CirclePrimitive"]
        
    # every node before this point is not guarenteed to follow the pattern
    # but every node not checked above does follow the pattern.
    
    try:
        return classes[ prototype_node.bl_idname ]
    except KeyError:
        # prGreen(prototype_node.bl_idname)
        # prWhite(classes.keys())
        pass
    
    if prototype_node.bl_idname in [ 
                                    "NodeReroute",
                                    "NodeGroupInput",
                                    "NodeGroupOutput",
                                    "MantisNodeGroup",
                                    "NodeFrame",
                                    "MantisSchemaGroup",
                                   ]:
           return None
    
    prRed(prototype_node.bl_idname)
    raise RuntimeError(wrapOrange("Failed to create node container for: ")+wrapRed("%s" % prototype_node.bl_idname))
    return None


# This is really, really stupid HACK
def gen_nc_input_for_data(socket):
    # Class List #TODO deduplicate
    from . import xForm_containers, link_containers, misc_containers, primitives_containers, deformer_containers, math_containers, schema_containers
    classes = {}
    for module in [xForm_containers, link_containers, misc_containers, primitives_containers, deformer_containers, math_containers, schema_containers]:
        for cls in module.TellClasses():
            classes[cls.__name__] = cls
    #
    socket_class_map = {
                        "MatrixSocket"                         : classes["InputMatrix"],
                        "xFormSocket"                          : None,
                        "RelationshipSocket"                   : classes["xFormRoot"], # world in
                        "DeformerSocket"                       : classes["xFormRoot"], # world in
                        "GeometrySocket"                       : classes["InputExistingGeometryData"],
                        "EnableSocket"                         : classes["InputBoolean"],
                        "HideSocket"                           : classes["InputBoolean"],
                        #
                        "DriverSocket"                         : None,
                        "DriverVariableSocket"                 : None, 
                        "FCurveSocket"                         : None, 
                        "KeyframeSocket"                       : None,
                        # "LayerMaskInputSocket"               : classes["InputLayerMask"],
                        # "LayerMaskSocket"                    : classes["InputLayerMask"],
                        "BoneCollectionSocket"                 : classes["InputString"],
                        "BoneCollectionInputSocket"            : classes["InputString"],
                        #
                        "xFormParameterSocket"                 : None,
                        "ParameterBoolSocket"                  : classes["InputBoolean"],
                        "ParameterIntSocket"                   : classes["InputFloat"],  #TODO: make an Int node for this
                        "ParameterFloatSocket"                 : classes["InputFloat"],
                        "ParameterVectorSocket"                : classes["InputVector"],
                        "ParameterStringSocket"                : classes["InputString"],
                        #
                        "TransformSpaceSocket"                 : classes["InputTransformSpace"],
                        "BooleanSocket"                        : classes["InputBoolean"],
                        "BooleanThreeTupleSocket"              : classes["InputBooleanThreeTuple"],
                        "RotationOrderSocket"                  : classes["InputRotationOrder"],
                        "QuaternionSocket"                     : classes["InputQuaternion"],
                        "QuaternionSocketAA"                   : classes["InputQuaternionAA"],
                        "IntSocket"                            : classes["InputFloat"],
                        "StringSocket"                         : classes["InputString"],
                        #
                        "BoolUpdateParentNode"                 : classes["InputBoolean"],
                        "IKChainLengthSocket"                  : classes["InputFloat"],
                        "EnumInheritScale"                     : classes["InputString"],
                        "EnumRotationMix"                      : classes["InputString"],
                        "EnumRotationMixCopyTransforms"        : classes["InputString"],
                        "EnumMaintainVolumeStretchTo"          : classes["InputString"],
                        "EnumRotationStretchTo"                : classes["InputString"],
                        "EnumTrackAxis"                        : classes["InputString"],
                        "EnumUpAxis"                           : classes["InputString"],
                        "EnumLockAxis"                         : classes["InputString"],
                        "EnumLimitMode"                        : classes["InputString"],
                        "EnumYScaleMode"                       : classes["InputString"],
                        "EnumXZScaleMode"                      : classes["InputString"],
                        "EnumCurveSocket"                      : classes["InputString"],
                        # Deformers
                        "EnumSkinning"                         : classes["InputString"],
                        #
                        "FloatSocket"                          : classes["InputFloat"],
                        "FloatFactorSocket"                    : classes["InputFloat"],
                        "FloatPositiveSocket"                  : classes["InputFloat"],
                        "FloatAngleSocket"                     : classes["InputFloat"],
                        "VectorSocket"                         : classes["InputVector"],
                        "VectorEulerSocket"                    : classes["InputVector"],
                        "VectorTranslationSocket"              : classes["InputVector"],
                        "VectorScaleSocket"                    : classes["InputVector"],
                        # Drivers             
                        "EnumDriverVariableType"               : classes["InputString"],
                        "EnumDriverVariableEvaluationSpace"    : classes["InputString"],
                        "EnumDriverRotationMode"               : classes["InputString"],
                        "EnumDriverType"                       : classes["InputString"],
                        "EnumKeyframeInterpolationTypeSocket"  : classes["InputString"],
                        "EnumKeyframeBezierHandleTypeSocket"   : classes["InputString"],
                        # Math
                        "MathFloatOperation"                   : classes["InputString"],
                        "MathVectorOperation"                  : classes["InputString"],
                        "MatrixTransformOperation"             : classes["InputString"],
                        # Schema
                        "WildcardSocket"                       : None,
                       }
    return socket_class_map.get(socket.bl_idname, None)

####################################
# CURVE STUFF
####################################

def rotate(l, n):
    if ( not ( isinstance(n, int) ) ): #print an error if n is not an int:
        raise TypeError("List slice must be an int, not float.")
    return l[n:] + l[:n]
#from stack exchange, thanks YXD

# this stuff could be branchless but I don't use it much TODO
def cap(val, maxValue):
    if (val > maxValue):
        return maxValue
    return val

def capMin(val, minValue):
    if (val < minValue):
        return minValue
    return val

# def wrap(val, min=0, max=1):
#     raise NotImplementedError

#wtf this doesn't do anything even remotely similar to wrap, or useful in
# HACK BAD FIXME UNBREAK ME BAD
# I don't understand what this function does but I am using it in multiple places?
def wrap(val, maxValue, minValue = None):
    if (val > maxValue):
        return (-1 * ((maxValue - val) + 1))
    if ((minValue) and (val < minValue)):
        return (val + maxValue)
    return val
    #TODO clean this up


def layerMaskCompare(mask_a, mask_b):
    compare = 0
    for a, b in zip(mask_a, mask_b):
        if (a != b):
            compare+=1
    if (compare == 0):
        return True
    return False

def lerpVal(a, b, fac = 0.5):
    return a + ( (b-a) * fac)

def RibbonMeshEdgeLengths(m, ribbon):
    tE = ribbon[0]; bE = ribbon[1]; c = ribbon[2]
    lengths = []
    for i in range( len( tE ) ): #tE and bE are same length
        if (c == True):
            v1NextInd = tE[wrap((i+1), len(tE) - 1)]
        else:
            v1NextInd = tE[cap((i+1) , len(tE) - 1 )]
        v1 = m.vertices[tE[i]]; v1Next = m.vertices[v1NextInd]
        if (c == True):
            v2NextInd = bE[wrap((i+1), len(bE) - 1)]
        else:
            v2NextInd = bE[cap((i+1) , len(bE) - 1 )]
        v2 = m.vertices[bE[i]]; v2Next = m.vertices[v2NextInd]
        
        v = v1.co.lerp(v2.co, 0.5); vNext = v1Next.co.lerp(v2Next.co, 0.5)
        # get the center, edges may not be straight so total length 
        #  of one edge may be more than the ribbon center's length
        lengths.append(( v - vNext ).length)
    return lengths

def EnsureCurveIsRibbon(crv, defaultRadius = 0.1):
    crvRadius = 0
    if (crv.data.bevel_depth == 0):
        crvRadius = crv.data.extrude
    else: #Set ribbon from bevel depth
        crvRadius = crv.data.bevel_depth
        crv.data.bevel_depth = 0
        crv.data.extrude = crvRadius
    if (crvRadius == 0):
        crv.data.extrude = defaultRadius

def SetRibbonData(m, ribbon):
    #maybe this could be incorporated into the DetectWireEdges function?
    #maybe I can check for closed poly curves here? under what other circumstance
    # will I find the ends of the wire have identical coordinates?
    ribbonData = []
    tE = ribbon[0].copy(); bE = ribbon[1].copy()# circle = ribbon[2]
    #
    lengths = RibbonMeshEdgeLengths(m, ribbon)
    lengths.append(0)
    totalLength = sum(lengths)
    # m.calc_normals() #calculate normals
    # it appears this has been removed.
    for i, (t, b) in enumerate(zip(tE, bE)):
        ind = wrap( (i + 1), len(tE) - 1 )
        tNext = tE[ind]; bNext = bE[ind]
        ribbonData.append(  ( (t,b), (tNext, bNext), lengths[i] ) )
        #if this is a circle, the last v in vertData has a length, otherwise 0
    return ribbonData, totalLength


def mesh_from_curve(crv, context,):
    """Utility function for converting a mesh to a curve
       which will return the correct mesh even with modifiers"""
    import bpy
    if (len(crv.modifiers) > 0):
        do_unlink = False
        if (not context.scene.collection.all_objects.get(crv.name)):
            context.collection.objects.link(crv) # i guess this forces the dg to update it?
            do_unlink = True
        dg = context.view_layer.depsgraph
        # just gonna modify it for now lol
        EnsureCurveIsRibbon(crv)
        # try:
        dg.update()
        mOb = crv.evaluated_get(dg)
        m = bpy.data.meshes.new_from_object(mOb)
        m.name=crv.data.name+'_mesh'
        if (do_unlink):
            context.collection.objects.unlink(crv)
        return m
        # except: #dg is None?? # FIX THIS BUG BUG BUG
        #     print ("Warning: could not apply modifiers on curve")
        #     return bpy.data.meshes.new_from_object(crv)
    else: # (ಥ﹏ಥ) why can't I just use this !
        # for now I will just do it like this
        EnsureCurveIsRibbon(crv)
        return bpy.data.meshes.new_from_object(crv)


# def DataFromRibbon(obCrv, factorsList, context, fReport=None,):
#     # BUG
#     # no reasonable results if input is not  a ribbon
#     import time
#     start = time.time()
#     """Returns a point from a u-value along a curve"""
#     rM = MeshFromCurve(obCrv, context)
#     ribbons = f_mesh.DetectRibbons(rM, fReport= fReport)
#     for ribbon in ribbons:
#         # could be improved, this will do a rotation for every ribbon
#         # if even one is a circle
#         if (ribbon[2]) == True:
#             # could be a better implementation
#             dupeCrv = obCrv.copy()
#             dupeCrv.data = obCrv.data.copy()
#             dupeCrv.data.extrude = 0
#             dupeCrv.data.bevel_depth = 0 
#             wM = MeshFromCurve(dupeCrv, context)
#             wires = f_mesh.DetectWireEdges(wM)
#             bpy.data.curves.remove(dupeCrv.data) #removes the object, too
#             ribbonsNew = []
#             for ribbon, wire in zip(ribbons, wires):
#                 if (ribbon[2] == True): #if it's a circle
#                     rNew = f_mesh.RotateRibbonToMatchWire(ribbon, rM, wire, wM)
#                 else:
#                     rNew = ribbon
#                 ribbonsNew.append( rNew )
#             ribbons = ribbonsNew
#             break
#     data = f_mesh.DataFromRibbon(rM, factorsList, obCrv.matrix_world, ribbons=ribbons, fReport=fReport)
#     bpy.data.meshes.remove(rM)
#     print ("time elapsed: ", time.time() - start)
#     #expects data...
#     # if ()


#     return data

def DetectRibbon(f, bm, skipMe):
    fFirst = f.index
    cont = True
    circle = False
    tEdge, bEdge = [],[]
    while (cont == True):
        skipMe.add(f.index)
        tEdge.append (f.loops[0].vert.index) # top-left
        bEdge.append (f.loops[3].vert.index) # bottom-left
        nEdge = bm.edges.get([f.loops[1].vert, f.loops[2].vert])
        nFaces = nEdge.link_faces
        if (len(nFaces) == 1): 
            cont = False
        else:
            for nFace in nFaces:
                if (nFace != f):
                    f = nFace
                    break
            if (f.index == fFirst):
                cont = False
                circle = True
        if (cont == False): # we've reached the end, get the last two:
            tEdge.append (f.loops[1].vert.index) # top-right
            bEdge.append (f.loops[2].vert.index) # bottom-right
            # this will create a loop for rings -- 
            #  "the first shall be the last and the last shall be first"
    return (tEdge,bEdge,circle)

def DetectRibbons(m, fReport = None):
    # Returns list of vertex indices belonging to ribbon mesh edges
    # NOTE: this assumes a mesh object with only ribbon meshes
    # ---DO NOT call this script with a mesh that isn't a ribbon!--- #
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(m)
    mIslands, mIsland = [], []
    skipMe = set()
    bm.faces.ensure_lookup_table()
    #first, get a list of mesh islands
    for f in bm.faces:
        if (f.index in skipMe):
            continue #already done here
        checkMe = [f]
        while (len(checkMe) > 0):
            facesFound = 0
            for f in checkMe:
                if (f.index in skipMe):
                    continue #already done here
                mIsland.append(f)
                skipMe.add(f.index)
                for e in f.edges:
                    checkMe += e.link_faces
            if (facesFound == 0):
                #this is the last iteration
                mIslands.append(mIsland)
                checkMe, mIsland = [], []
    ribbons = []
    skipMe = set() # to store ends already checked
    for mIsl in mIslands:
        ribbon = None
        first = float('inf')
        for f in mIsl:
            if (f.index in skipMe):
                continue #already done here
            if (f.index < first):
                first = f.index
            adjF = 0
            for e in f.edges:
                adjF+= (len(e.link_faces) - 1)
                # every face other than this one is added to the list
            if (adjF == 1):
                ribbon = (DetectRibbon(f, bm, skipMe) )
                break
        if (ribbon == None):
            ribbon = (DetectRibbon(bm.faces[first], bm, skipMe) )
        ribbons.append(ribbon)
    # print (ribbons)
    return ribbons

def data_from_ribbon_mesh(m, factorsList, mat, ribbons = None, fReport = None):
    #Note, factors list should be equal in length the the number of wires
    #Now working for multiple wires, ugly tho
    if (ribbons == None):
        ribbons = DetectRibbons(m, fReport=fReport)
        if (ribbons is None):
            if (fReport):
                fReport(type = {'ERROR'}, message="No ribbon to get data from.")
            else:  
                print ("No ribbon to get data from.")
            return None
    ret = []
    for factors, ribbon in zip(factorsList, ribbons):
        points  = []
        widths  = []
        normals = []
        ribbonData, totalLength = SetRibbonData(m, ribbon)

        for fac in factors:
            if (fac == 0):
                data = ribbonData[0]
                curFac = 0
            elif (fac == 1):
                data = ribbonData[-1]
                curFac = 0
            else:
                targetLength = totalLength * fac
                data = ribbonData[0]
                curLength = 0
                for ( (t, b), (tNext, bNext), length,) in ribbonData:
                    if (curLength >= targetLength):
                        break
                    curLength += length
                    data = ( (t, b), (tNext, bNext), length,)
                targetLengthAtEdge = (curLength - targetLength)
                if (targetLength == 0):
                    curFac = 0
                elif (targetLength == totalLength):
                    curFac = 1
                else:
                    try:
                        curFac = 1 - (targetLengthAtEdge/ data[2]) #length
                    except ZeroDivisionError:
                        curFac = 0
                        if (fReport):
                            fReport(type = {'WARNING'}, message="Division by Zero.")
                        else:  
                            prRed ("Division by Zero Error in evaluating data from curve.")
            t1 = m.vertices[data[0][0]]; b1 = m.vertices[data[0][1]]
            t2 = m.vertices[data[1][0]]; b2 = m.vertices[data[1][1]]
            #location
            loc1 = (t1.co).lerp(b1.co, 0.5)
            loc2 = (t2.co).lerp(b2.co, 0.5)
            #width
            w1 = (t1.co - b1.co).length/2
            w2 = (t2.co - b2.co).length/2 #radius, not diameter
            #normal
            n1 = (t1.normal).slerp(b1.normal, 0.5)
            n2 = (t1.normal).slerp(b2.normal, 0.5)
            if ((data[0][0] > data[1][0]) and (ribbon[2] == False)):
                curFac = 0
                #don't interpolate if at the end of a ribbon that isn't circular
            if ( 0 < curFac < 1):
                outPoint = loc1.lerp(loc2, curFac)
                outNorm  = n1.lerp(n2, curFac)
                outWidth = w1 + ( (w2-w1) * curFac)
            elif (curFac <= 0):
                outPoint = loc1.copy()
                outNorm = n1
                outWidth = w1
            elif (curFac >= 1):
                outPoint = loc2.copy()
                outNorm = n2
                outWidth = w2
            outPoint = mat @ outPoint
            outNorm.normalize()
            points.append ( outPoint.copy() ) #copy because this is an actual vertex location
            widths.append ( outWidth )
            normals.append( outNorm )
        ret.append( (points, widths, normals) )
    return ret # this is a list of tuples containing three lists

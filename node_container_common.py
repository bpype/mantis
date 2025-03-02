from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)
from .base_definitions import GraphError
# BE VERY CAREFUL
# the x_containers files import * from this file
# so all the top-level imports are carried over


#TODO: refactor the socket definitions so this becomes unnecessary.
def get_socket_value(node_socket):
    value = None
    if hasattr(node_socket, "default_value"): 
        value = node_socket.default_value
    if node_socket.bl_idname == 'MatrixSocket':
        value =  node_socket.TellValue()
    return value

def check_for_driver(node_container, input_name, index = None):
    prop = node_container.evaluate_input(input_name)
    if (index is not None):
        prop = prop[index]
    return (prop.__class__.__name__ == 'MantisDriver')

def trace_node_lines(node_container):
    """ Tells the depth of a node within the node tree. """
    node_lines = []
    if hasattr(node_container, "inputs"):
        for key, socket in node_container.inputs.items():
            # Recrusive search through the tree.
            #  * checc each relevant input socket in the node
            #  * for EACH input, find the node it's connected to
            #    * repeat from here until you get all the lines
            if ( ( key in ["Relationship", "Parent", "Input Relationship", "Target"])
                          and (socket.is_connected) ):
                # it is necesary to check the key because of Link nodes,
                #   which don't really traverse like normal.
                # TODO: see if I can refactor this to make it traverse
                other = socket.from_node
                if (other):
                    other_lines = trace_node_lines(other)
                    if not other_lines:
                        node_lines.append([other])
                    for line in other_lines:
                        node_lines.append( [other] + line )
    return node_lines


# TODO: modify this to work with multi-input nodes
def trace_single_line(node_container, input_name, link_index=0):
    # DO: refactor this for new link class
    """Traces a line to its input."""
    nodes = [node_container]
    # Trace a single line
    if (socket := node_container.inputs.get(input_name) ):
        while (socket.is_linked):
            link = socket.links[link_index]; link_index = 0
            if (socket := link.from_node.outputs.get(link.from_socket)):
                nodes.append(socket.node)
                if socket.can_traverse:
                    socket = socket.traverse_target
                else: # this is an output.
                    break
            else:
                break
    return nodes, socket


# this is same as the other, just flip from/to and in/out
def trace_single_line_up(node_container, output_name,):
    """I use this to get the xForm from a link node."""
    nodes = [node_container]
    if hasattr(node_container, "outputs"):
        # Trace a single line
        if (socket := node_container.outputs.get(output_name) ):
            while (socket.is_linked):
                # This is bad, but it's efficient for nodes that only expect
                #  one path along the given line
                link = socket.links[0] # TODO: find out if this is wise.
                other = link.to_node.inputs.get(link.to_socket)
                if (other):
                    socket = other
                    if socket.can_traverse:
                        socket = socket.traverse_target
                        nodes.append(socket.node)
                    else: # this is an input.
                        nodes.append(socket.node)
                        break
                else:
                    break
    return nodes, socket

def trace_all_lines_up(nc, output_name):
    copy_items = {}
    for item in dir(nc):
        if "__" not in item:
            copy_items[item]=getattr(nc, item)
    # we want to copy it, BUT:
    copy_items["outputs"]:{output_name:nc.outputs[output_name]}
    # override outputs with just the one we care about.
    
    check_me = type('', (object,), copy_items)
    return get_depth_lines(check_me)[1]





def num_hierarchy_connections(nc):
    num=0
    for out in nc.outputs:
        for link in out.links:
            if link.is_hierarchy: num+=1
    return num

def list_hierarchy_connections(nc):
    return len(nc.hierarchy_connections)-1
    hc=[]
    for out in nc.outputs:
        for link in out.links:
            if link.is_hierarchy: hc.append(link.to_node)
    return num

# what this is doing is giving a list of Output-Index that is the path to the given node, from a given root.
# HOW TO REWRITE...
# we simply do the same thing, but we look at the outputs, not the old hierarchy-connections
# we can do the same tree-search but we simply ignore an output if it is not hierarchy.
# the existing code isn't complicated, it's just hard to read. So this new code should be easier to read, too.

def get_depth_lines(root):
    from .base_definitions import GraphError
    path, nc_path = [0,], [root,]
    lines, nc_paths = {}, {}
    nc_len = len(root.hierarchy_connections)-1
    curheight=0
    while (path[0] <= nc_len):
        # this doesn't seem to make this any slower. It is good to check it.
        if nc_path[-1] in nc_path[:-1]:
            raise GraphError(wrapRed(f"Infinite loop detected while depth sorting for root {root}."))
        #
        nc_path.append(nc_path[-1].hierarchy_connections[path[-1]])
        if (not (node_lines  := lines.get(nc_path[-1].signature, None))):
            node_lines = lines[nc_path[-1].signature] = set()
        if (not (node_paths  := nc_paths.get(nc_path[-1].signature, None))):
            node_paths = nc_paths[nc_path[-1].signature] = set()
        node_lines.add(tuple(path)); node_paths.add(tuple(nc_path))
        if nc_path[-1].hierarchy_connections: # if there is at least one element
            path.append(0); curheight+=1
        else: # at this point, nc_path is one longer than path because path is a segment between two nodes
            # or more siimply, because nc_path has the root in it and path starts with the first node
            path[curheight] = path[curheight] + 1
            nc_path.pop() # so we go back and horizontal
            if ( path[-1] <= len(nc_path[-1].hierarchy_connections)-1 ):
                pass # and continue if we can
            elif curheight > 0: # otherwise we keep going back
                while(len(path) > 1):
                    path.pop(); curheight -= 1; path[curheight]+=1; nc_path.pop()
                    if ( (len(nc_path)>1) and path[-1] < len(nc_path[-1].hierarchy_connections) ):
                        break 
    return lines, nc_paths

# same but because the checks end up costing a fair amount of time, I don't want to use this one unless I need to.
def get_prepared_depth_lines(root,):
    # import pstats, io, cProfile
    # from pstats import SortKey
    # with cProfile.Profile() as pr:
        path, nc_path = [0,], [root,]
        lines, nc_paths = {}, {}
        nc_len = len(prepared_connections(root, ))-1
        curheight=0
        while (path[0] <= nc_len):
            if nc_path[-1] in nc_path[:-1]:
                raise GraphError(wrapRed(f"Infinite loop detected while depth sorting for root {root}."))
            nc_path.append(prepared_connections(nc_path[-1], )[path[-1]])
            if (not (node_lines  := lines.get(nc_path[-1].signature, None))):
                node_lines = lines[nc_path[-1].signature] = set()
            if (not (node_paths  := nc_paths.get(nc_path[-1].signature, None))):
                node_paths = nc_paths[nc_path[-1].signature] = set()
            node_lines.add(tuple(path)); node_paths.add(tuple(nc_path))
            if prepared_connections(nc_path[-1], ): # if there is at least one element
                path.append(0); curheight+=1
            else: # at this point, nc_path is one longer than path because path is a segment between two nodes
                # or more siimply, because nc_path has the root in it and path starts with the first node
                path[curheight] = path[curheight] + 1
                nc_path.pop() # so we go back and horizontal
                if path[-1] <= len(prepared_connections(nc_path[-1], ))-1:
                    pass # and continue if we can
                elif curheight > 0: # otherwise we keep going back
                    while(len(path) > 1):
                        path.pop(); curheight -= 1; path[curheight]+=1; nc_path.pop()
                        if (len(nc_path)>1) and path[-1] < len(prepared_connections(nc_path[-1], ) ):
                            break 
        # from the Python docs at https://docs.python.org/3/library/profile.html#module-cProfile
    # s = io.StringIO()
    # sortby = SortKey.TIME
    # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    # ps.print_stats()
    # print(s.getvalue())
        return lines, nc_paths


def prepared_connections(nc):
    if nc.prepared:
        return nc.hierarchy_connections
    else:
        ret = []
        for hc in nc.hierarchy_connections:
            if hc.prepared:
                ret.append(hc)
        return ret
        # return [hc for hc in nc.hierarchy_connections if hc.prepared]


def node_depth(lines):
    maxlen = 0
    for line in lines:
        if ( (l := len(line) ) > maxlen):
            maxlen = l
    return maxlen
    


#TODO rewrite this so it'll work with new nc_path thing
#  not a high priority bc this was debugging code for something that
#  works and has since ben refactored to work better
def printable_path(nc, path, no_wrap = False):
    string = ""; cur_nc = nc
    #DO: find out if the copy is necessary
    path = path.copy(); path.reverse()
    dummy = lambda a : a
    while path:
        wrap = dummy
        if not no_wrap:
            wrap=wrapWhite
            if (cur_nc.node_type == 'DRIVER'):
                wrap = wrapPurple
            elif (cur_nc.node_type == 'XFORM'):
                wrap = wrapOrange
            elif (cur_nc.node_type == 'LINK'):
                wrap = wrapGreen
        string += wrap(cur_nc.__repr__()) + " -> "
        try:
            cur_nc = get_from_path(cur_nc, [path.pop()] )
        except IndexError:
            string = string[:-4]
            return string
    string = string[:-4]
    return string
    # why is this not printing groups in brackets?


def get_parent(node_container, type = 'XFORM'):
    # type variable for selecting whether to get either 
    #   the parent xForm  or the inheritance node
    node_line, socket = trace_single_line(node_container, "Relationship")
    parent_nc = None
    for i in range(len(node_line)):
        # check each of the possible parent types.
        if ( (node_line[ i ].__class__.__name__ == 'LinkInherit') ):
            try: # it's the next one
                if (type == 'XFORM'):
                    return node_line[ i + 1 ]
                else: # type = 'LINK'
                    return node_line[ i ]
            except IndexError: # if there is no next one...
                return None # then there's no parent!
    return None
    # TODO!
    #
    # make this do shorthand parenting - if no parent, then use World
    #  if the parent node is skipped, use the previous node (an xForm)
    #  with default settings.
    # it is OK to generate a new, "fake" node container for this!

def get_target_and_subtarget(node_container, linkOb, input_name = "Target"):
    from bpy.types import PoseBone, Object, SplineIKConstraint, ArmatureModifier, HookModifier
    subtarget = ''; target = node_container.evaluate_input(input_name)
    if target:
        if not hasattr(target, "bGetObject"):
            prRed(f"No {input_name} target found for {linkOb.name} in {node_container} because there is no connected node, or node is wrong type")
            return 
        if (isinstance(target.bGetObject(), PoseBone)):
            subtarget = target.bGetObject().name
            target = target.bGetParentArmature()
        elif (isinstance(target.bGetObject(), Object) ):
            target = target.bGetObject()
        else:
            raise RuntimeError("Cannot interpret linkOb target!")
    
    if   (isinstance(linkOb, SplineIKConstraint)):
            if target and target.type not in ["CURVE"]:
                raise GraphError(wrapRed("Error: %s requires a Curve input, not %s" %
                                 (node_container, type(target))))
            linkOb.target = target# don't get a subtarget
    if (input_name == 'Pole Target'):
        linkOb.pole_target, linkOb.pole_subtarget = target, subtarget
    else:
        if hasattr(linkOb, "target"):
            linkOb.target = target
        if hasattr(linkOb, "object"):
            linkOb.object = target
        if hasattr(linkOb, "subtarget"):
            linkOb.subtarget = subtarget


def setup_custom_props(nc):
    from .utilities import get_node_prototype
    if nc.signature[0] == 'SCHEMA_AUTOGENERATED':
        from .base_definitions import custom_props_types
        if nc.__class__.__name__ not in custom_props_types:
            # prRed(f"Reminder: figure out how to deal with custom property setting for Schema Node {nc}")
            raise RuntimeError(wrapRed(f"Custom Properties not set up for node {nc}"))
        return
    else:
        np = get_node_prototype(nc.signature, nc.base_tree)
    if np:
        setup_custom_props_from_np(nc, np)
    else:
        prRed("Failed to setup custom properties for: nc")

def setup_custom_props_from_np(nc, np):
    for inp in np.inputs:
        if inp.identifier == "__extend__": continue
        if not (inp.name in nc.inputs.keys()) :
            socket = NodeSocket(is_input = True, name = inp.name, node = nc,)
            nc.inputs[inp.name] = socket
            nc.parameters[inp.name] = None
            for attr_name in ["min", "max", "soft_min", "soft_max", "description"]:
                try:
                    setattr(socket, attr_name, getattr(inp, attr_name))
                except AttributeError:
                    pass
    for out in np.outputs:
        if out.identifier == "__extend__": continue
        if not (out.name in nc.outputs.keys()) :
            nc.outputs[out.name] = NodeSocket(is_input = False, name = out.name, node = nc,)
            
def prepare_parameters(nc):
    # some nodes add new parameters at runtime, e.g. Drivers
    # so we need to take that stuff from the node_containers that have
    #  been executed prior to this node.
    for s_name, sock in nc.inputs.items():
        if not (sock.is_linked):
            continue
        if (sock.name  in sock.links[0].from_node.parameters.keys()):
            nc.parameters[s_name] = sock.links[0].from_node.parameters[sock.name]
    # should work, this is ugly.




# TODO: this should handle sub-properties better
def evaluate_sockets(nc, c, props_sockets):
    # this is neccesary because some things use dict properties for dynamic properties and setattr doesn't work
    def safe_setattr(ob, att_name, val):
        if ob.__class__.__name__ in ["NodesModifier"]:
            ob[att_name]=val
        elif c.__class__.__name__ in ["Key"]:
            if not val: val=0
            ob.key_blocks[att_name].value=val
        elif "]." in att_name:
            # it is of the form prop[int].prop2
            prop=att_name.split('[')[0]
            prop1=att_name.split('.')[1]
            index = int(att_name.split('[')[1][0])
            setattr(getattr(c, prop)[index], prop1, val)
        else:
            try:
                setattr(ob, att_name, val)
            except Exception as e:
                prRed(ob, att_name, val); raise e
    # HACK I think I should do this in __init__
    if not hasattr(nc, "drivers"):
        nc.drivers = {}
    # end HACK
    for prop, (sock, default) in props_sockets.items():
        # c = nc.bObject
        # annoyingly, sometimes the socket is an array
        index = None
        if isinstance(sock, tuple):
            index = sock[1]; sock = sock[0]
        if (check_for_driver(nc, sock, index)):
            sock = (sock, index)
            original_prop = prop
            # TODO: deduplicate this terrible hack
            if ("." in prop) and not c.__class__.__name__ in ["Key"]: # this is a property of a property...
                sub_props = [c]
                while ("." in prop):
                    split_prop = prop.split(".")
                    prop = split_prop[1]
                    sub_prop = (split_prop[0])
                    if ("[" in sub_prop):
                        sub_prop, index = sub_prop.split("[")
                        index = int(index[0])
                        sub_props.append(getattr(sub_props[-1], sub_prop)[index])
                    else:
                        sub_props.append(getattr(sub_props[-1], sub_prop))
                safe_setattr(sub_props[-1], prop, default)
            # this is really stupid
            else:
                safe_setattr(c, prop, default)
            if nc.node_type in ['LINK',]:
                printname  = wrapOrange(nc.GetxForm().bGetObject().name)
            elif nc.node_type in ['XFORM',]:
                printname  = wrapOrange(nc.bGetObject().name)
            else:
                printname = wrapOrange(nc)
            print("Adding driver %s to %s in %s" % (wrapPurple(original_prop), wrapWhite(nc.signature[-1]), printname))
            if c.__class__.__name__ in ["NodesModifier"]:
                nc.drivers[sock] = "[\""+original_prop+"\"]" # lol. It is a dict element not a "true" property
            elif c.__class__.__name__ in ["Key"]:
                nc.drivers[sock] = "key_blocks[\""+original_prop+"\"].value"
            else:
                nc.drivers[sock] = original_prop
        else: # here we can do error checking for the socket if needed
            if (index is not None):
                safe_setattr(c, prop, nc.evaluate_input(sock)[index])
            else:                    # 'mute' is better than 'enabled'
                # UGLY HACK          # because it is available in older
                if (prop == 'mute'): # Blenders.
                    safe_setattr(c, prop, not bool(nc.evaluate_input(sock)))
                elif (prop == 'hide'): # this will not cast it for me, annoying.
                    safe_setattr(c, prop, bool(nc.evaluate_input(sock)))
                else:
                    try:
                        # prRed(c.name, nc, prop, nc.evaluate_input(sock) )
                        # print( nc.evaluate_input(sock))
                    # value_eval = nc.evaluate_input(sock)
                    # just wanna see if we are dealing with some collection
                    # check hasattr in case it is one of those ["such-and-such"] props, and ignore those
                        if hasattr(c, prop) and (not isinstance(getattr(c, prop), str)) and hasattr(getattr(c, prop), "__getitem__"):
                            # prGreen("Doing the thing")
                            for val_index, value in enumerate(nc.evaluate_input(sock)):
                                # assume this will work, both because val should have the right number of elements, and because this should be the right data type.
                                from .drivers import MantisDriver
                                if isinstance(value, MantisDriver):
                                    getattr(c,prop)[val_index] =  default[val_index]
                                    print("Adding driver %s to %s in %s" % (wrapPurple(prop), wrapWhite(nc.signature[-1]), nc))
                                    try:
                                        nc.drivers[sock].append((prop, val_index))
                                    except:
                                        nc.drivers[sock] = [(prop, val_index)]
                                else:
                                    getattr(c,prop)[val_index] =  value
                        else:
                            # prOrange("Skipping the Thing", getattr(c, prop))
                            safe_setattr(c, prop, nc.evaluate_input(sock))
                    except Exception as e:
                        prRed(c, nc, prop, sock, nc.evaluate_input(sock))
                        raise e


def finish_driver(nc, driver_item, prop):
    # prWhite(nc, prop)
    index = driver_item[1]; driver_sock = driver_item[0]
    driver_trace = trace_single_line(nc, driver_sock)
    driver_provider, driver_socket = driver_trace[0][-1], driver_trace[1]
    if index is not None:
        driver = driver_provider.parameters[driver_socket.name][index].copy()
        # this is harmless and necessary for the weird ones where the property is a vector too
        driver["ind"] = index
    else:
        driver = driver_provider.parameters[driver_socket.name].copy()
    if driver:
        # todo: deduplicate this terrible hack
        c = None # no idea what this c and sub_prop thing is, HACK?
        if hasattr(nc, "bObject"):
            c = nc.bObject # STUPID                 # stupid and bad HACK here too
        if ("." in prop) and nc.__class__.__name__ != "DeformerMorphTargetDeform": # this is a property of a property...
            sub_props = [c]
            while ("." in prop):
                split_prop = prop.split(".")
                prop = split_prop[1]
                sub_prop = (split_prop[0])
                if ("[" in sub_prop):
                    sub_prop, index = sub_prop.split("[")
                    index = int(index[0])
                    sub_props.append(getattr(sub_props[-1], sub_prop)[index])
                else:
                    sub_props.append(getattr(sub_props[-1], sub_prop))
            driver["owner"] = sub_props[-1]
        elif nc.node_type in ['XFORM',] and nc.__class__.__name__ in ['xFormBone']:
            # TODO: I really shouldn't have to hardcode this. Look into better solutions.
            if prop in ['hide', 'show_wire']: # we need to get the bone, not the pose bone.
                bone_col = nc.bGetParentArmature().data.bones
            else:
                bone_col = nc.bGetParentArmature().pose.bones
            driver["owner"] = bone_col[nc.bObject] # we use "unsafe" brackets instead of get() because we want to see any errors that occur
        else:
            driver["owner"] = nc.bObject
        # prPurple("Successfully created driver for %s" % prop)
        driver["prop"] = prop
        return driver
        # prWhite(driver)
    else:
        prOrange("Provider", driver_provider)
        prGreen("socket", driver_socket)
        print (index)
        prPurple(driver_provider.parameters[driver_socket.name])
        prRed("Failed to create driver for %s" % prop)
        return None

def finish_drivers(nc):
    # gonna make this into a common function...
    drivers = []
    if not hasattr(nc, "drivers"):
        # prGreen(f"No Drivers to construct for {nc}")
        return # HACK
    for driver_item, prop in nc.drivers.items():
        if isinstance(prop, list):
            for sub_item in prop:
                drivers.append(finish_driver(nc, (driver_item, sub_item[1]), sub_item[0]))
        else:
            drivers.append(finish_driver(nc, driver_item, prop))
    from .drivers import CreateDrivers
    CreateDrivers(drivers)


from .base_definitions import from_name_filter, to_name_filter
def detect_hierarchy_link(from_node, from_socket, to_node, to_socket,):
    if to_node.node_type in ['DUMMY_SCHEMA', 'SCHEMA']:
        return False
    if (from_socket in from_name_filter) or (to_socket in to_name_filter):
        return False
    # if from_node.__class__.__name__ in ["UtilityCombineVector", "UtilityCombineThreeBool"]:
    #     return False
    return True

#Dummy classes for logic with node containers, they are not meant to do
#  each and every little thing the "real" Blender classes do.
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
    @property # this is a read-only property.
    def is_linked(self):
        return bool(self.links)
        
    def __init__(self, is_input = False,
                 node = None, name = None,
                 traverse_target = None):
        self.can_traverse = False # to/from the other side of the parent node
        self.traverse_target = None
        self.node = node
        self.name = name
        self.is_input = is_input
        self.links = []
        if (traverse_target):
            self.can_traverse = True
        
    def connect(self, node, socket, sort_id=0):
        if  (self.is_input):
            to_node   = self.node; from_node = node
            to_socket = self.name; from_socket = socket
        else:
            from_node   = self.node; to_node   = node
            from_socket = self.name; to_socket = socket
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
        self.links = [l for l in self.links if l.is_alive]
        
    @property
    def is_connected(self):
        return len(self.links)>0
    
    
    def __repr__(self):
        return self.node.__repr__() + "::" + self.name


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
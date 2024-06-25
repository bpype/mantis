

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


# uncomment to turn them off.
# def prRed(*args): return; print (*[wrapRed(arg) for arg in args])
# def prGreen(*args): return; print (*[wrapGreen(arg) for arg in args])
# def prPurple(*args): return; print (*[wrapPurple(arg) for arg in args])
# def prWhite(*args): return; print (*[wrapWhite(arg) for arg in args])
# def prOrange(*args): return; print (*[wrapOrange(arg) for arg in args])



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


# This has a lot of branches and is kinda slow.
def socket_seek(socket, trees):
    from bpy.types import NodeReroute, NodeGroupOutput
    if (hasattr( socket.node, "traverse")):
        if (socket.node.bl_idname == "MantisNodeGroup"):
            trees.append(socket.node)
            socket = socket.node.traverse(socket, "IN")
        else:
            socket = socket.node.traverse(socket)
    elif (isinstance(socket.node, NodeReroute)):
        socket = socket.node.outputs[0]
    elif (isinstance(socket.node, NodeGroupOutput)):
        group_node = trees.pop()
        if group_node:
            socket = group_node.traverse(socket, "OUT")
        else:
            raise RuntimeError("Error parsing Group Nodes")
    else:
        raise RuntimeError("Error: node tree cannot be navigated")
    return socket, trees

#This is a little slow.
def lines_from_socket(sock, tree_path = [None]):
    done = False
    sPath =[0,]
    lines = []
    while (not done):
        seek = sock
        trees = tree_path.copy() # make sure to copy, lists are not immutable
        for curheight, ind in enumerate(sPath):
            if not seek: #this will cause the loop to complete normally
                continue # which will return an error
            if (ind <= (len(seek.links) -1)):
                seek = seek.links[ind].to_socket
                nextseek, trees = socket_seek(seek, trees.copy())
                if (not nextseek): # The node has no no traverse function.
                    # note, kind of duplicated code, TODO,
                    lines.append(sPath[:curheight+1])
                    if (curheight > 0):
                        sPath[curheight] += 1
                    else:
                        done = True
                    break
                if (nextseek.is_linked): #otherwise this is a leaf
                    seek = nextseek
                    if (curheight == len(sPath)-1): #go up
                        sPath.append(0)
                elif not (nextseek.is_linked):
                    lines.append(sPath[:curheight+1])
                    sPath[curheight]+=1
                    # this makes sure we're progressing through the tree.
                    break
            else:
                if (curheight > 0):
                    sPath.pop() #go back...
                    sPath[curheight-1] += 1
                    
                else:
                    done = True
                break
        else:
            raise RuntimeError("There has been an error parsing the tree")
    return lines


# only using this once, should this even be a function?
def create_socket_lists(sock, tree_path, lines):
    out_lines = []
    for line in lines:
        s = sock
        trees = tree_path.copy()
        out_line = [(s, trees)]
        for i, ind in enumerate(line):
            if i < len(line):
                s_next = s.links[ind].to_socket
                s_final, trees = socket_seek(s_next, trees.copy())
                if s_final:
                    s = s_final
                else: # The node has no no traverse function.
                    # this needs special check, if it's the first node,
                    #  it's already in the tree.
                    if (i > 0):
                        out_line.append( (s, trees) )
                    out_line.append( (s_next, trees) )
                    break
            # nodes to skip...
            if (s.node.bl_idname in [
                                     "NodeReroute",
                                     "MantisNodeGroupOutput",
                                     "NodeGroupOutput",
                                     "MantisNodeGroupInput",
                                     "NodeGroupInput"
                                    ]):
                continue
            
            out_line.append( (s, trees) )
        out_lines.append(out_line)
    return out_lines

#NOTE: this may not work at all lol
# TODO BUG HACK rename and remove this before publishing
def find_root_nodes(tree, tree_path = [None]):
    root_nodes = []
    for node in tree.nodes:
        addMe = True
        for s in node.inputs:
            if (s.is_linked == True):
                addMe = False
                # for now, don't try to sovle this, it will need 
                #  a backwards search
                for link in s.links:
                    # we need to check if this is a "false" connection;
                    #  that is, a Group In from an unconnected Group
                    if (link.from_socket.node.bl_idname in ["NodeGroupInput", "MantisNodeGroupInput"]):
                        identifier = link.from_socket.identifier
                        for grp in tree_path[1:][::-1]:
                            for inp in grp.inputs:
                                if inp.identifier == identifier and not inp.is_linked:
                                    addMe=True
                                    break
                            else:
                                addMe=False
        if (hasattr(node, "node_tree")):
            # we use the node itself here for the node path, will use it for node signature later.
            root_nodes.extend( find_root_nodes(node.node_tree, tree_path+[node]) )
        
        if (node.bl_idname in [
                               "NodeReroute",
                               "MantisNodeGroupOutput",
                               "NodeGroupOutput",
                               "MantisNodeGroupInput",
                               "NodeGroupInput",
                               "NodeFrame",
                              ]):
            addMe = False
            continue
        
        if (addMe):
            root_nodes.append( (tree_path, node) )
    return root_nodes



def parse_node_tree(tree):
    root_nodes = find_root_nodes(tree)
    # this seems to produce garbage results. Check this!

    input_lines = []
    
    for path, node in root_nodes:
        # print (path, node)
        for s in node.outputs:
            socket_lists = create_socket_lists(s, path, lines_from_socket(s, path))
            for line in socket_lists:
                in_line = line.copy()
                input_lines.append(in_line)
    # NOT SURE if any of this stuff below is necesary at all
    return (input_lines) # let's find out if it is
    #
    
    # I think the unreachable code here is bad. TODO: figure out if there's
    #       any reason at all to revive this old code.
    #
    # I certainly *like* the idea of removing redundant data.
    #
    # note: it seems like the Execute Tree function is completing
    #     in 80% of the previous time after removing the below
    #     meanign that this was wasting 1/5 of the total time
    no_dupes_sigs = set()
    no_dupes_lines = set()
    for in_line in input_lines:
        sig = get_socket_signature(in_line[-1])
        sig = list(sig)
        sig.append(in_line[-1][0].name) # socket
        sig = tuple(sig)

        before = len(no_dupes_sigs)
        no_dupes_sigs.add(sig)
        after = len(no_dupes_sigs)
        # make a tuple of the node path, too.
        # in_line = tuple(in_line[0]), in_line[1]
        
        if (before < after): # new item
            no_dupes_lines.add(tuple_of_line(in_line))
    #MAYBE
    # maybe i can get a list of all nodes
    # including nodes in nodegroups and nested node groups
    # then I can assign a uuid to each one
    # and associate the uuids with the node lines
    # perhaps I should do that before running this function
    
    # for line in no_dupes_lines:
        # print (list(line))
    
    return (list(no_dupes_lines))

    # don't deal with lines no mo. Do stuff with line elements

# DO THIS!
# make lines_from_socket attach a tree path to each node-socket, instead of just a tree
# that way, if the tree-path is longer than the socket-path, the tree path won't be truncated.



# for use with node signatures

def tree_from_nc(sig, base_tree):
    if (sig[0] == 'MANTIS_AUTOGENERATED'):
        sig = sig[:-2] # cut off the input part of the signature.
    tree = base_tree
    for i, path_item in enumerate(sig):
        if (i == 0) or (i == len(sig) - 1):
            continue
        tree = tree.nodes.get(path_item).node_tree
    return tree
    
def get_node_prototype(sig, base_tree):
    return tree_from_nc(sig, base_tree).nodes.get( sig[-1] )

      
            
##################################################################################################
# misc
##################################################################################################

# This will not work with float properties. Use them directly.
# this is an extremely idiotic way to do this
# it's also slow!
# TODO fix this
#using isinstance is the most lizard-brained way to do this, utter idiocy.
def to_mathutils_value(socket):
    if (hasattr(socket, "default_value")):
        val = socket.default_value
        from mathutils import Matrix, Euler, Quaternion, Vector
        from bpy.types import (NodeSocketVector, NodeSocketVectorAcceleration,
                              NodeSocketVectorDirection, NodeSocketVectorEuler,
                              NodeSocketVectorTranslation, NodeSocketVectorVelocity,
                              NodeSocketVectorXYZ,)
        from . import socket_definitions
        if ((isinstance(socket, NodeSocketVector)) or
            (isinstance(socket, NodeSocketVectorAcceleration)) or
            (isinstance(socket, NodeSocketVectorDirection)) or
            (isinstance(socket, NodeSocketVectorTranslation)) or
            (isinstance(socket, NodeSocketVectorXYZ)) or
            (isinstance(socket, NodeSocketVectorVelocity)) or
            (isinstance(socket, socket_definitions.VectorSocket)) or
            (isinstance(socket, socket_definitions.VectorEulerSocket)) or
            (isinstance(socket, socket_definitions.VectorTranslationSocket)) or
            (isinstance(socket, socket_definitions.VectorScaleSocket)) or
            (isinstance(socket, socket_definitions.ParameterVectorSocket))):
            return (Vector(( val[0], val[1], val[2], )))
        if (isinstance(socket, NodeSocketVectorEuler)):
            return (Euler(( val[0], val[1], val[2])), 'XYZ',) #TODO make choice
        if (isinstance(socket, socket_definitions.MatrixSocket)):
            # return val #Blender makes it a Matrix for me <3
            # nevermind... BLENDER HAS BETRAYED ME
            return socket.TellValue()
        if (isinstance(socket,socket_definitions.QuaternionSocket)):
            return (Quaternion( (val[0], val[1], val[2], val[3],)) )
        if (isinstance(socket,socket_definitions.QuaternionSocketAA)):
            return (Quaternion( (val[1], val[2], val[3],), val[0], ) )
        if ((isinstance(socket, socket_definitions.FloatSocket)) or
            (isinstance(socket, socket_definitions.ParameterIntSocket)) or
            (isinstance(socket, socket_definitions.ParameterFloatSocket))):
            return val
        if (isinstance(socket, socket_definitions.BooleanThreeTupleSocket)):
            return (val[0], val[1], val[2]) # we'll send a tuple out
        # if ((isinstance(socket, socket_definitions.LayerMaskSocket)) or
        #     (isinstance(socket, socket_definitions.LayerMaskInputSocket))):
        #     return tuple(val) # should werk
    else:
        return None


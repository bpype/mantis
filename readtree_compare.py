from .utilities import prRed, prGreen, prPurple, prWhite, prOrange, \
                        wrapRed, wrapGreen, wrapPurple, wrapWhite, wrapOrange

# what in the cuss is this horrible abomination??
def class_for_mantis_prototype_node(prototype_node):
    """ This is a class which returns a class to instantiate for
        the given prototype node."""
    #from .node_container_classes import TellClasses
    from mantis import xForm_containers, link_containers, misc_containers, primitives_containers, deformer_containers
    classes = {}
    for module in [xForm_containers, link_containers, misc_containers, primitives_containers, deformer_containers]:
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
        # BAD need to fix the above, bl_idname is not consistent
    # Copy's
    elif prototype_node.bl_idname == 'LinkCopyLocation':
        return classes["LinkCopyLocation"] # also bad
    elif prototype_node.bl_idname == 'LinkCopyRotation':
        return classes["LinkCopyRotation"]
    elif prototype_node.bl_idname == 'LinkCopyScale':
        return classes["LinkCopyScale"]
    elif prototype_node.bl_idname == 'LinkCopyTransforms':
        return classes["LinkCopyTransforms"]
    # Limits
    elif prototype_node.bl_idname == 'LinkLimitLocation':
        return classes["LinkLimitLocation"]
    elif prototype_node.bl_idname == 'LinkLimitRotation':
        return classes["LinkLimitRotation"]
    elif prototype_node.bl_idname == 'LinkLimitScale':
        return classes["LinkLimitScale"]
    elif prototype_node.bl_idname == 'LinkLimitDistance':
        return classes["LinkLimitDistance"]
    # tracking
    elif prototype_node.bl_idname == 'LinkStretchTo':
        return classes["LinkStretchTo"]
    elif prototype_node.bl_idname == 'LinkDampedTrack':
        return classes["LinkDampedTrack"]
    elif prototype_node.bl_idname == 'LinkLockedTrack':
        return classes["LinkLockedTrack"]
    elif prototype_node.bl_idname == 'LinkTrackTo':
        return classes["LinkTrackTo"]
    # misc
    elif prototype_node.bl_idname == 'LinkInheritConstraint':
        return classes["LinkInheritConstraint"]
    # IK
    elif prototype_node.bl_idname == 'LinkInverseKinematics':
        return classes["LinkInverseKinematics"]
    elif prototype_node.bl_idname == 'LinkSplineIK':
        return classes["LinkSplineIK"]
    # utilities
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
    # geometry
    elif prototype_node.bl_idname == 'GeometryCirclePrimitive':
        return classes["CirclePrimitive"]
    # Deformers:
    elif prototype_node.bl_idname == 'DeformerArmature':
        return classes["DeformerArmature"]
        
    # every node before this point is not guarenteed to follow the pattern
    # but every node not checked above does follow the pattern.
    
    try:
        return classes[ prototype_node.bl_idname ]
    except KeyError:
        pass
    
    if prototype_node.bl_idname in [ 
                                    "NodeReroute",
                                    "NodeGroupInput",
                                    "NodeGroupOutput",
                                    "MantisNodeGroup",
                                    "NodeFrame",
                                   ]:
           return None
    
    prRed(prototype_node.bl_idname)
    raise RuntimeError("Failed to create node container for: %s" % prototype_node.bl_idname)
    return None

# This is really, really stupid HACK
def gen_nc_input_for_data(socket):
    # Class List #TODO deduplicate
    from mantis import xForm_containers, link_containers, misc_containers, primitives_containers, deformer_containers
    classes = {}
    for module in [xForm_containers, link_containers, misc_containers, primitives_containers, deformer_containers]:
        for cls in module.TellClasses():
            classes[cls.__name__] = cls
    #
    socket_class_map = {
                        "MatrixSocket"                      : classes["InputMatrix"],
                        "xFormSocket"                       : None,
                        "xFormMultiSocket"                  : None,
                        "RelationshipSocket"                : classes["xFormRoot"], # world in
                        "DeformerSocket"                    : classes["xFormRoot"], # world in
                        "GeometrySocket"                    : classes["InputExistingGeometryData"],
                        "EnableSocket"                      : classes["InputBoolean"],
                        "HideSocket"                        : classes["InputBoolean"],
                        #
                        "DriverSocket"                      : None,
                        "DriverVariableSocket"              : None, 
                        "FCurveSocket"                      : None, 
                        "KeyframeSocket"                    : None,
                        "LayerMaskInputSocket"              : classes["InputLayerMask"],
                        "LayerMaskSocket"                   : classes["InputLayerMask"],
                        #
                        "xFormParameterSocket"              : None,
                        "ParameterBoolSocket"               : classes["InputBoolean"],
                        "ParameterIntSocket"                : classes["InputFloat"],  #TODO: make an Int node for this
                        "ParameterFloatSocket"              : classes["InputFloat"],
                        "ParameterVectorSocket"             : classes["InputVector"],
                        "ParameterStringSocket"             : classes["InputString"],
                        #
                        "TransformSpaceSocket"              : classes["InputTransformSpace"],
                        "BooleanSocket"                     : classes["InputBoolean"],
                        "BooleanThreeTupleSocket"           : classes["InputBooleanThreeTuple"],
                        "RotationOrderSocket"               : classes["InputRotationOrder"],
                        "QuaternionSocket"                  : classes["InputQuaternion"],
                        "QuaternionSocketAA"                : classes["InputQuaternionAA"],
                        "IntSocket"                         : classes["InputFloat"],
                        "StringSocket"                      : classes["InputString"],
                        #
                        "BoolUpdateParentNode"              : classes["InputBoolean"],
                        "IKChainLengthSocket"               : classes["InputFloat"],
                        "EnumInheritScale"                  : classes["InputString"],
                        "EnumRotationMix"                   : classes["InputString"],
                        "EnumRotationMixCopyTransforms"     : classes["InputString"],
                        "EnumMaintainVolumeStretchTo"       : classes["InputString"],
                        "EnumRotationStretchTo"             : classes["InputString"],
                        "EnumTrackAxis"                     : classes["InputString"],
                        "EnumUpAxis"                        : classes["InputString"],
                        "EnumLockAxis"                      : classes["InputString"],
                        "EnumLimitMode"                     : classes["InputString"],
                        "EnumYScaleMode"                    : classes["InputString"],
                        "EnumXZScaleMode"                   : classes["InputString"],
                        # Deformers
                        "EnumSkinning"                      : classes["InputString"],
                        #
                        "FloatSocket"                       : classes["InputFloat"],
                        "FloatFactorSocket"                 : classes["InputFloat"],
                        "FloatPositiveSocket"               : classes["InputFloat"],
                        "FloatAngleSocket"                  : classes["InputFloat"],
                        "VectorSocket"                      : classes["InputVector"],
                        "VectorEulerSocket"                 : classes["InputVector"],
                        "VectorTranslationSocket"           : classes["InputVector"],
                        "VectorScaleSocket"                 : classes["InputVector"],
                        # Drivers             
                        "EnumDriverVariableType"            : classes["InputString"],
                        "EnumDriverVariableEvaluationSpace" : classes["InputString"],
                        "EnumDriverRotationMode"            : classes["InputString"],
                        "EnumDriverType"                    : classes["InputString"],
                       }
    return socket_class_map.get(socket.bl_idname, None)




class DummyLink:
    #gonna use this for faking links to keep the interface consistent
    def __init__(self, from_socket, to_socket, nc_from=None, nc_to=None, original_from=None):
        self.from_socket = from_socket
        self.to_socket = to_socket
        self.nc_from = nc_from
        self.nc_to = nc_to
        if (original_from):
            self.original_from = original_from
        else:
            self.original_from = self.from_socket
    def __repr__(self):
        return(self.nc_from.__repr__()+":"+self.from_socket.name + " -> " + self.nc_to.__repr__()+":"+self.to_socket.name)

# We'll treat this as a "dangling" link if either socket is unset...


# # May or may not use this for my Dummy Links to help me connect things
# #  I think I can avoid it tho
# class DummyNode:
    # def __init__(self, signature, base_tree, prototype):
        # self.signature = signature
        # self.base_tree = base_tree
        # self.prototype = prototype

# This really might be useful in sorting the tree, too.


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
    
def clear_reroutes(links):
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

def data_from_tree(base_tree, tree_path = [None], held_links = {}, all_nc = {}):
    # prGreen("Starting! Base Tree: %s, held nodes: %d, held links: %d, nc's: %d" % (base_tree.name, len(held_nodes), len(held_links), len(all_nc)))
    # prPurple(tree_path)
    nc_dict = {}
    tree_path_names = [tree.name for tree in tree_path if hasattr(tree, "name")]
    all_child_ng = []
    tree = base_tree
    if tree_path[-1]:
        tree = tree_path[-1].node_tree
    
    # Start by looking through the nodes and making nc's where possible
    #  store the groups, we'll pricess them soon.
    for np in tree.nodes:
        if (nc_cls := class_for_mantis_prototype_node(np)):
            nc = nc_cls( sig := tuple([None] + tree_path_names + [np.name]) , base_tree)
            nc_dict[sig] = nc; all_nc[sig] = nc
        if hasattr(np, "node_tree"):
            all_child_ng.append(np)

    # Then deal with the links in the current tree and the held_links.
    kept_links, incoming, outgoing = [], [], []
    all_links = clear_reroutes(list(tree.links))
    while(all_links):
        link = all_links.pop()
        to_cls = link.to_socket.node.bl_idname
        from_cls = link.from_socket.node.bl_idname
        if (from_cls in ["NodeGroupInput"]):
                incoming.append(link)
        elif (to_cls in ["NodeGroupOutput"]):
            nc_from = nc_dict.get( tuple([None]+tree_path_names+[link.from_socket.node.name]) )
            to_s = link.to_socket.identifier
            # Let's try and connect it now; go UP:
            nc_to, new_link = None, None
            
            if len(tree_path)==1:
                prRed("Warning: There is a GroupOutput node in the Base Tree.")
                kept_links.append(link)
                continue
            elif tree_path[-2] is None:
                up_tree=base_tree
            else:
                up_tree=tree_path[-2].node_tree
            
            for up_node in up_tree.nodes:
                for out in up_node.outputs:
                    if not hasattr(up_node, "node_tree"):
                        continue
                    if not out.is_linked:
                        continue
                    for up_link in out.links:
                        if up_link.from_socket.identifier == to_s:
                            new_link = DummyLink(from_socket=up_link.from_socket, to_socket=up_link.to_socket, nc_from=nc_from, nc_to=None)
                            link_sig = tuple([None]+tree_path_names[:-1]+[up_link.to_socket.node.name, link.from_socket.name])
                            held_links[link_sig] = new_link
            nc_from, nc_to = None, None # clear them
        elif (from_cls in ["MantisNodeGroup"]):
            outgoing.append(link)
        else:
            kept_links.append(link)
    # Make the connections:
    for link in kept_links:
        nc_from = nc_dict.get( tuple([None] + tree_path_names + [link.from_socket.node.name]) )
        nc_to = nc_dict.get( tuple([None] + tree_path_names + [link.to_socket.node.name]) )
        if (nc_from and nc_to):
            from_s, to_s = link.from_socket.name, link.to_socket.name
            connection = nc_from.outputs[from_s].connect(node=nc_to, socket=to_s)
    nc_from = None; nc_to = None #clear them, since we use the same variable names again
    
    # At this point we're also gonna deal with held links and held nodes
    hold_further = {}
    del_me = set() # I donno why but there can be dupes.
    for link_sig, held in held_links.items():
        found, connected = False, False
        nc_from, from_s = held.nc_from, held.original_from.name
        watch = (nc_from.signature[-1] == 'Parent') and (tree_path_names[-1] in ["right", "left"])
        for link in incoming:
            if watch:
                prWhite(link_sig)
            if ((link.from_socket.identifier != link_sig[-1]) or
                (link.from_socket.name != link_sig[-2])):
                continue # This ain't it
            if (link.from_socket.identifier == link_sig[-1]):
                if (link.to_socket.node.bl_idname in [ "MantisNodeGroup" ]):
                    del_me.add(link_sig)
                    link_sig = tuple(list(link_sig[:-2]) + [link.to_socket.name, link.to_socket.identifier])
                    hold_further[link_sig] = DummyLink(from_socket = held.from_socket, to_socket = link.to_socket, nc_from=nc_from, nc_to = None, original_from=held.original_from)
                    prGreen("Holding further %s" % held.original_from.name)
                    continue # just continue to hold it
                found = True
                # TO-Node:
                to_s = link.to_socket.name
                sig_to = tuple([None] + tree_path_names + [link.to_socket.node.name])
                nc_to = nc_dict.get( sig_to )
                if (nc_to and nc_from):
                    if watch:
                        prGreen("Connecting: %s%s -> %s%s" % (nc_from, from_s, nc_to, to_s) )
                    connection = nc_from.outputs[from_s].connect(node=nc_to, socket=to_s)
                    connected = True
                elif watch:
                    prRed("Not Connecting: %s%s -> %s%s" % (nc_from, from_s, nc_to, to_s) )
        if (connected) != found:
            print(wrapRed("Not Connected: ") ,link_sig, held)
    
    # it's fairly annoying that I can't do this while I go.
    # for k in del_me:
        # del held_links[k]
    for k,v in hold_further.items():
        held_links[k] = v
    
    
    for ng in  all_child_ng:
        for inp in ng.inputs:
            if not inp.is_linked:
                nc_cls = gen_nc_input_for_data(inp)
                if (nc_cls):
                    sig = ("MANTIS_AUTOGENERATED", *tree_path_names, inp.node.name, inp.identifier)
                    nc = nc_cls(sig, tree)
                    # HACK HACK HACK
                    for k, v in nc.outputs.items():
                        v.name = inp.name; break
                    from mantis.node_container_common import NodeSocket
                    nc.outputs[inp.name] = NodeSocket(name = inp.name, node=nc)
                    # del nc.outputs[k]; del nc.parameters[k]
                    nc.parameters[inp.name]=inp.default_value
                    # HACK HACK HACK
                    
                    nc_dict[sig] = nc; all_nc[sig] = nc
                    
                    dummy = DummyLink(from_socket = inp, to_socket = inp, nc_from=nc, nc_to=None)
                    link_sig =  tuple([None] + tree_path_names +[ng.name, inp.name, inp.identifier])
                    held_links[link_sig]=dummy
            else: # We need to hold the incoming connections
                for link in inp.links: #Usually there will only be 1
                    from_socket = link.from_socket
                    if (link.from_socket.node.bl_idname == "NodeGroupInput"):
                        # shouldn't there be a held link for this?
                        continue
                    
                    if (link.from_socket.node.bl_idname == "NodeReroute"):
                        from_socket = socket_seek(link, list(tree.links))
                    sig =  tuple( [None] + tree_path_names +[from_socket.node.name])
                    # print(sig)
                    nc_from = nc_dict.get(sig)
                    # This is kind of stupid
                    if from_socket.node.bl_idname in "NodeGroupInput":
                        nc_from = held_links.get( tuple([None] + tree_path_names + [link.from_socket.name, inp.identifier]) )
                        if not (nc_from):
                            prRed( [None] + tree_path_names + [link.from_socket.name, inp.identifier])
                            for signature, link in held_links.items():
                                print ( wrapGreen(signature), wrapWhite(link))
                        nc_from = nc_from.nc_from
                        
                    if (nc_from):
                        dummy = DummyLink(from_socket = from_socket, to_socket = inp, nc_from=nc_from, nc_to=None, original_from=from_socket )
                        # The link sig should take us back to the group node.
                        link_sig =  tuple( [None] + tree_path_names + [ng.name, inp.name, inp.identifier])
                        held_links[link_sig]=dummy
                        prGreen("Adding %s" % from_socket)
                    else:
                        prRed("no nc?")
                        prOrange(sig)
        # Recurse!
        # data_from_tree(base_tree, tree_path+[ng], grps, solved_trees, solved_tree_links, held_nodes, held_links, all_nc)
        
        
        data_from_tree(base_tree, tree_path+[ng], held_links, all_nc)
        
        for link_sig, held in held_links.items():
            from_cls = held.from_socket.node.bl_idname
            to_cls = held.to_socket.node.bl_idname
            if (from_cls in ["MantisNodeGroup"] and not
                    to_cls in ["MantisNodeGroup"]):
                nc_from = held.nc_from
                for link in outgoing:
                    if link.from_socket.node.name == nc_from.signature[-2]:
                        to_sig = tuple([None] + tree_path_names + [held.to_socket.node.name])
                        nc_to = nc_dict.get( to_sig )
                        if (nc_from and nc_to):
                            from_s, to_s = link_sig[-1], held.to_socket.name
                            connection = nc_from.outputs[from_s].connect(node=nc_to, socket=to_s)
            
        held_nodes = {}; held_links = {} # NO IDEA why I have to do this
            
            
    
    # return None, grps, all_links, solved_trees, solved_tree_links, all_nc
    return all_nc
            
            
from itertools import chain

def parse_tree(base_tree):
    all_nc =  data_from_tree(base_tree, tree_path = [None], held_links = {}, all_nc = {})
    all_nc = list(all_nc.values()).copy()
    kept_nc = {}
    while (all_nc):
        nc = all_nc.pop()
        # total_links=0
        # for sock in chain( nc.inputs.values(), nc.outputs.values()):
            # total_links+=len(sock.links)
        # if total_links > 0:
        nc.fill_parameters()
        # ugly, but it solves the problem easily:
        establish_node_connections(nc)
        kept_nc[nc.signature]=nc
    return kept_nc


from_name_filter = ["Driver", ]

to_name_filter = [
                   "Custom Object xForm Override",
                   "Custom Object",
                   "Deform Bones"
                 ]

def establish_node_connections(nc):
    # This is ugly bc it adds parameters to an object
    #  but it's kinda necesary to do it after the fact; and it
    #  wouldn't be ugly if I just initialized the parameter elsewhere
    connections, hierarchy_connections = [], []
    for socket in nc.outputs.values():
        for link in socket.links:
            connections.append(link.to_node)
            # this may catch custom properties... too bad.
            if link.from_socket in from_name_filter:
                continue
            if link.to_socket in to_name_filter:
                continue
            hierarchy_connections.append(link.to_node)
    nc.connected_to = connections
    nc.hierarchy_connections = hierarchy_connections


def sort_tree_into_layers(nodes, context):
    from time import time
    from mantis.node_container_common import (get_depth_lines,
      node_depth)
    from mantis.utilities import prGreen, prOrange, prRed, prPurple
    # All this function needs to do is sort out the hierarchy and
    #  get things working in order of their dependencies.
    
    prPurple ("Number of nodes: ", len(nodes))
    roots, drivers = [], []
    start = time()
    
    for n in nodes.values():
        if n.node_type == 'DRIVER': drivers.append(n)
        # ugly but necesary to ensure that drivers are always connected.
        if not (hasattr(n, 'inputs')) or ( len(n.inputs) == 0):
            roots.append(n)
        elif (hasattr(n, 'inputs')):
            none_connected = True
            for inp in n.inputs.values():
                if inp.is_linked: none_connected = False
            if none_connected: roots.append(n)
    
    layers, nodes_heights = {}, {}
    
    
    
    for root in roots:
            nodes_heights[root.signature] = 0
        
    #Possible improvement: unify roots if they represent the same data
    all_sorted_nodes = []
    for root in roots:
        
        # if len(root.hierarchy_connections) == 0:
            # if (len(root.connected_to) == 0):
                # prRed("No connections: ", root)
            # continue
        
        depth_lines = get_depth_lines(root)[0]
        
        for n in nodes.values():
            if n.signature not in (depth_lines.keys()):
                continue #belongs to a different root
            d = nodes_heights.get(n.signature, 0)
            if (new_d := node_depth(depth_lines[n.signature])) > d:
                d = new_d
            nodes_heights[n.signature] = d
                
    for k, v in nodes_heights.items():
        if (layer := layers.get(v, None)):
            layer.append(nodes[k]) # add it to the existing layer
        else: layers[v] = [nodes[k]] # or make a new layer with the node
        all_sorted_nodes.append(nodes[k]) # add it to the sorted list
    
    for n in nodes.values():
        if n not in all_sorted_nodes:
            for drv in drivers:
                if n in drv.connected_to:
                    depth = nodes_heights[drv.signature] + 1
                    nodes_heights[n.signature] = depth
                    # don't try to push downstream deps up bc this
                    #  is a driver and it will be done in the
                    #  finalize pass anyway
                    if (layer := layers.get(depth, None)):
                        layer.append(n)
                    else: layers[v] = [n]
                else:
                    prRed(n)
                    for inp in n.inputs.values():
                        print (len(inp.links))
                    raise RuntimeError(wrapRed("Failed to depth-sort nodes (because of a driver-combine node?)"))
    #
    prGreen("Sorting depth for %d nodes finished in %s seconds" %
               (len(nodes), time() - start))
    
    if (False): # True to print the layers
        for i in range(len(layers)):
            try:
                print(i, layers[i])
            except KeyError: # empty layer?
                print (i)
    return layers


def execute_tree(nodes, base_tree, context):
    import bpy
    from time import time
    from mantis.node_container_common import GraphError
    start_time  = time()
    
    # input_from_grp_nodes(parsed_tree, base_tree, nodes)
    # bpy.ops.wm.quit_blender()
    
    layers = sort_tree_into_layers(nodes, context)
    start_execution_time = time()
    
    #             Execute the first pass (xForm, Utility)              #
    for i in range(len(layers)):
        for node in layers[i]:
            if (node.node_type in ['XFORM', 'UTILITY']):
                try:
                    node.bExecute(context)
                except Exception as e:
                    prRed("Execution failed at %s" % node); raise e
    #                     Switch to Pose Mode                          #
    active = None
    switch_me = []
    for n in nodes.values():
        # if it is a armature, switch modes
        # total hack                   #kinda dumb
        if ((hasattr(n, "bGetObject")) and (n.__class__.__name__ == "xFormArmature" )):
            try:
                ob = n.bGetObject()
            except KeyError: # for bones
                ob = None
            # TODO this will be a problem if and when I add mesh/curve stuff
            if (hasattr(ob, 'mode') and ob.mode == 'EDIT'):
                switch_me.append(ob)
                active = ob # need to have an active ob, not None, to switch modes.
            # we override selected_objects to prevent anyone else from mode-switching
    # TODO it's possible but unlikely that the user will try to run a 
    #    graph with no armature nodes in it.
    if (active):
        bpy.ops.object.mode_set({'active_object':active, 'selected_objects':switch_me}, mode='POSE')
    
    #               Execute second pass (Link, Driver)                 #
    for i in range(len(layers)):
        for n in layers[i]:
            # Now do the Link & Driver nodes during the second pass.
            if (n.node_type in ['LINK', 'DRIVER']):
                try:
                    n.bExecute(context)   
                except GraphError:
                    pass                     
                except Exception as e:
                    print (n); raise e
                    
    #                          Finalize                                #
    for i in range(len(layers)):
        for node in layers[i]:
            if (hasattr(node, "bFinalize")):
                node.bFinalize(context)
    
    prGreen("Executed Tree in %s seconds" % (time() - start_execution_time))
    prGreen("Finished executing tree in %f seconds" % (time() - start_time))
    

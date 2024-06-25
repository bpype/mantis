from .utilities import prRed, prGreen, prPurple, prWhite, prOrange, \
                        wrapRed, wrapGreen, wrapPurple, wrapWhite, wrapOrange

# what in the cuss is this horrible abomination??
def class_for_mantis_prototype_node(prototype_node):
    """ This is a class which returns a class to instantiate for
        the given prototype node."""
    #from .node_container_classes import TellClasses
    from . import xForm_containers, link_containers, misc_containers, primitives_containers, deformer_containers
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
    elif prototype_node.bl_idname == 'LinkTransformation':
        return classes["LinkTransformation"]
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
    from . import xForm_containers, link_containers, misc_containers, primitives_containers, deformer_containers
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


def reroute_common(nc, nc_to, all_nc):
    # we need to do this: go  to the to-node
    # then reroute the link in the to_node all the way to the beginning
    # so that the number of links in "real" nodes is unchanged
    # then the links in the dummy nodes need to be deleted
    watch=False
    # if nc.signature[-1] == 'NodeGroupOutput': watch=True
    for inp_name, inp in nc.inputs.items():
        # assume each input socket only has one input for now
        if inp.is_connected:
            while (inp.links):
                in_link = inp.links.pop()
                from_nc = in_link.from_node
                from_socket = in_link.from_socket
                links = []
                from_links = from_nc.outputs[from_socket].links.copy()
                while(from_links):
                    from_link = from_links.pop()
                    if from_link == in_link:
                        continue # DELETE the dummy node link
                    links.append(from_link)
                from_nc.outputs[from_socket].links = links
                down = nc_to.outputs[inp_name]
                for downlink in down.links:
                    downlink.from_node = from_nc
                    downlink.from_socket = from_socket
                    from_nc.outputs[from_socket].links.append(downlink)
                    if hasattr(downlink.to_node, "reroute_links"):
                        # Recurse!
                        downlink.to_node.reroute_links(downlink.to_node, all_nc)
        


def reroute_links_grp(nc, all_nc):
    nc_to = all_nc.get( ( *nc.signature, "NodeGroupInput") )
    reroute_common(nc, nc_to, all_nc)

def reroute_links_grpout(nc, all_nc):
    nc_to = all_nc.get( ( *nc.signature[:-1],) )
    reroute_common(nc, nc_to, all_nc)


def data_from_tree(base_tree, tree_path = [None], dummy_nodes = {}, all_nc = {}):
    from .node_container_common import NodeSocket
    from .internal_containers import DummyNode
    nc_dict = {}
    tree_path_names = [tree.name for tree in tree_path if hasattr(tree, "name")]
    all_child_ng = []
    tree = base_tree
    if tree_path[-1]:
        tree = tree_path[-1].node_tree
    
    # Start by looking through the nodes and making nc's where possible
    #  store the groups, we'll process them soon.
    for np in tree.nodes:
        if (nc_cls := class_for_mantis_prototype_node(np)):
            nc = nc_cls( sig := (None, *tree_path_names, np.name) , base_tree)
            nc_dict[sig] = nc; all_nc[sig] = nc
        elif np.bl_idname in ["NodeGroupInput", "NodeGroupOutput"]: # make a Dummy Node
            # we only want ONE dummy in/out per tree_path, so use the bl_idname
            sig = (None, *tree_path_names, np.bl_idname)
            if nc_dict.get(sig):
                continue
            nc = DummyNode( signature=sig , base_tree=base_tree, prototype=np )
            nc_dict[sig] = nc; all_nc[sig] = nc#; dummy_nodes[sig] = nc
            # dummy_nodes[sig]=nc
            if np.bl_idname in ["NodeGroupOutput"]:
                nc.reroute_links = reroute_links_grpout
                dummy_nodes[sig]=nc
        elif np.bl_idname in  ["MantisNodeGroup"]:
            # if we do this here, no duplicate links.
            nc = DummyNode( signature= (sig := (None, *tree_path_names, np.name) ), base_tree=base_tree, prototype=np )
            nc_dict[sig] = nc; all_nc[sig] = nc; dummy_nodes[sig] = nc
            nc.reroute_links = reroute_links_grp
            all_child_ng.append(np)
        # else:
            # prRed(np.bl_idname)
    

    # Then deal with the links in the current tree and the held_nodes.
    kept_links = clear_reroutes(list(tree.links))
    
    for link in kept_links:
        from_name = link.from_socket.node.name
        to_name = link.to_socket.node.name
        if link.from_socket.node.bl_idname in ["NodeGroupInput", "NodeGroupOutput"]:
            from_name = link.from_socket.node.bl_idname
        if link.to_socket.node.bl_idname in ["NodeGroupInput", "NodeGroupOutput"]:
            to_name = link.to_socket.node.bl_idname
        if link.to_socket.node.bl_idname in ["MantisNodeGroup"]:
            continue
        
        nc_from = nc_dict.get( tuple([None] + tree_path_names + [from_name]) )
        nc_to = nc_dict.get( tuple([None] + tree_path_names + [to_name]) )
        
        if (nc_from and nc_to):
            from_s, to_s = link.from_socket.name, link.to_socket.name
            if nc_to.node_type == "DUMMY": to_s = link.to_socket.identifier
            if nc_from.node_type == "DUMMY": from_s = link.from_socket.identifier
            connection = nc_from.outputs[from_s].connect(node=nc_to, socket=to_s)
        else:
            raise RuntimeError(wrapRed("Link not connected: %s -> %s in tree %s" % (from_name, to_name, tree_path_names[-1])))
    nc_from = None; nc_to = None #clear them, since we use the same variable names again
    
    
    # Now, descend into the Node Group
    for ng in  all_child_ng:
        nc_to = nc_dict[(None, *tree_path_names, ng.name)]
        for inp in ng.inputs:
            # nc_to = nc_dict.get((None, *tree_path_names, ng.name))
            to_s = inp.identifier
            if not inp.is_linked:
                nc_cls = gen_nc_input_for_data(inp)
                print (inp)
                prRed(nc_cls)
                # at this point we also need to get the "Dummy Node" for
                #  this node group.
                if (nc_cls):
                    sig = ("MANTIS_AUTOGENERATED", *tree_path_names, ng.name, inp.name, inp.identifier)
                    nc_from = nc_cls(sig, base_tree)
                    # HACK HACK HACK
                    nc_from.inputs = {}
                    nc_from.outputs = {inp.name:NodeSocket(name = inp.name, node=nc_from)}
                    from .node_container_common import get_socket_value
                    nc_from.parameters = {inp.name:get_socket_value(inp)}
                    # HACK HACK HACK
                    nc_dict[sig] = nc_from; all_nc[sig] = nc_from
                    from_s = inp.name
                else:
                    prRed("No available auto-generated class for input %s:%s:%s" % (tree_path, ng.name, inp.name))
            else: # We need to handle the incoming connections
                for link in inp.links: #Usually there will only be 1
                    from_socket = link.from_socket
                    if (link.from_socket.node.bl_idname == "NodeReroute"):
                        from_socket = socket_seek(link, list(tree.links))
                    sig =  tuple( [None] + tree_path_names +[from_socket.node.name])
                    
                    from_s = from_socket.name
                    if (link.from_socket.node.bl_idname in ["NodeGroupInput"]):
                        sig =  tuple( [None] + tree_path_names +[from_socket.node.bl_idname])
                        from_s = from_socket.identifier
                    nc_from = nc_dict.get(sig)
            # this can be None. Why?
            prRed (sig)
            nc_from.outputs[from_s].connect(node=nc_to, socket=to_s)
            nc_from = None
        nc_to = None
        # Recurse!
        data_from_tree(base_tree, tree_path+[ng], dummy_nodes, all_nc)
    return dummy_nodes, all_nc


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
    if nc.node_type == 'DUMMY':
        nc.hierarchy_connections = []


def insert_lazy_parents(nc):
    from .link_containers import LinkInherit
    from .node_container_common import NodeLink
    inherit_nc = None
    if nc.inputs["Relationship"].is_connected:
        link = nc.inputs["Relationship"].links[0]
        from_nc = link.from_node
        if from_nc.__class__.__name__ == "xFormRoot":
            return
        if from_nc.node_type in ["XFORM"] and link.from_socket in ["xForm Out"]:
            inherit_nc = LinkInherit(("MANTIS_AUTOGENERATED", *nc.signature[1:], "LAZY_INHERIT"), nc.base_tree)
            for from_link in from_nc.outputs["xForm Out"].links:
                if from_link.to_node == nc and from_link.to_socket == "Relationship":
                    break # this is it
            from_link.to_node = inherit_nc; from_link.to_socket="Parent"
            
            links=[]
            while (nc.inputs["Relationship"].links):
                to_link = nc.inputs["Relationship"].links.pop()
                if to_link.from_node == from_nc and to_link.from_socket == "xForm Out":
                    continue # don't keep this one
                links.append(to_link)
            
            nc.inputs["Relationship"].links=links
            link=NodeLink(from_node=inherit_nc, from_socket="Inheritance", to_node=nc, to_socket="Relationship")
            inherit_nc.inputs["Parent"].links.append(from_link)
            
            inherit_nc.parameters = {
                                     "Parent":None,
                                     "Inherit Rotation":True,
                                     "Inherit Scale":'FULL',
                                     "Connected":False,
                                    }
            # because the from node may have already been done.
            establish_node_connections(from_nc)
            establish_node_connections(inherit_nc)
            # and the inherit node never was
    return inherit_nc


def parse_tree(base_tree, do_reroute=True):
    dummy_nodes, all_nc =  data_from_tree(base_tree, tree_path = [None], dummy_nodes = {}, all_nc = {})
    if do_reroute:
        for sig, dummy in dummy_nodes.items():
            if (hasattr(dummy, "reroute_links")):
                dummy.reroute_links(dummy, all_nc)
        
    
    all_nc = list(all_nc.values()).copy()
    kept_nc = {}
    while (all_nc):
        nc = all_nc.pop()
        nc.fill_parameters()
        if (nc.node_type in ['XFORM']) and ("Relationship" in nc.inputs.keys()):
            new_nc = insert_lazy_parents(nc)
            if new_nc:
                kept_nc[new_nc.signature]=new_nc
        establish_node_connections(nc)
        if nc.connected_to == 0:
            continue
        if nc.node_type == 'DUMMY' and do_reroute:
            continue
        kept_nc[nc.signature]=nc
    # return {}
    return kept_nc


from_name_filter = ["Driver", ]

to_name_filter = [
                   "Custom Object xForm Override",
                   "Custom Object",
                   "Deform Bones"
                 ]



def sort_tree_into_layers(nodes, context):
    from time import time
    from .node_container_common import (get_depth_lines,
      node_depth)
    # All this function needs to do is sort out the hierarchy and
    #  get things working in order of their dependencies.
    
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
    #Possible improvement: unify roots if they represent the same data
    all_sorted_nodes = []
    for root in roots:
        nodes_heights[root.signature] = 0
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
                    raise RuntimeError(wrapRed("Failed to depth-sort nodes (because of a driver-combine node?)"))
    #
    prGreen("Sorting depth for %d nodes finished in %s seconds" %
               (len(nodes), time() - start))
    
    keys = list(layers.keys())
    keys.sort()
    
    if (False): # True to print the layers
        for i in keys:
            # print_layer = [l_item for l_item in layers[i] if l_item.node_type in ["XFORM",]]# "LINK", "DRIVER"]]
            print_layer = [l_item for l_item in layers[i]]
            print(wrapGreen("%d: " % i), wrapWhite("%s" % print_layer))
    return layers


def execute_tree(nodes, base_tree, context):
    import bpy
    from time import time
    from .node_container_common import GraphError
    start_time  = time()
    original_active = context.view_layer.objects.active
    
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
                active = ob
                context.view_layer.objects.active = ob# need to have an active ob, not None, to switch modes.
            # we override selected_objects to prevent anyone else from mode-switching
    # TODO it's possible but unlikely that the user will try to run a 
    #    graph with no armature nodes in it.
    if (active):
        with context.temp_override(**{'active_object':active, 'selected_objects':switch_me}):
            bpy.ops.object.mode_set(mode='POSE')
    
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
    
    
    for n in nodes.values():
        # if it is a armature, switch modes
        # total hack                   #kinda dumb
        if ((hasattr(n, "bGetObject")) and (n.__class__.__name__ == "xFormArmature" )):
            try:
                ob = n.bGetObject()
            except KeyError: # for bones
                ob = None
            # TODO this will be a problem if and when I add mesh/curve stuff
            if (hasattr(ob, 'mode') and ob.mode == 'POSE'):
                switch_me.append(ob)
                active = ob
    if (active):
        with context.temp_override(**{'active_object':active, 'selected_objects':switch_me}):
            bpy.ops.object.mode_set(mode='OBJECT')
    
    prGreen("Executed Tree in %s seconds" % (time() - start_execution_time))
    prGreen("Finished executing tree in %f seconds" % (time() - start_time))
    if (original_active):
        context.view_layer.objects.active = original_active
        original_active.select_set(True)

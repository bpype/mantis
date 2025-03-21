# this is the I/O part of mantis. I eventually intend to make this a markup language. not right now tho lol

from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

from mathutils import  Vector

from .base_definitions import NODES_REMOVED, SOCKETS_REMOVED


# this works but it is really ugly and probably quite inneficient
# TODO: make hotkeys for export and import and reload from file
   # we need to give the tree a filepath attribute and update it on saving
   # then we need to use the filepath attribute to load from
   # finally we need to use a few operators to choose whether to open a menu or not
   # and we need a message to display on save/load so that the user knows it is happening

# TODO:
   # Additionally export MetaRig and Curve and other referenced data
   # Meshes can be exported as .obj and imported via GN

def TellClasses():
    return [ MantisExportNodeTreeSaveAs, MantisExportNodeTreeSave, MantisExportNodeTree, MantisImportNodeTree, MantisReloadNodeTree]

# https://stackoverflow.com/questions/42033142/is-there-an-easy-way-to-check-if-an-object-is-json-serializable-in-python - thanks!
def is_jsonable(x):
    import json
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


# https://stackoverflow.com/questions/295135/turn-a-stritree-into-a-valid-filename - thank you user "Sophie Gage"
def remove_special_characters(name):
    import re; return re.sub('[^\w_.)( -]', '', name)# re = regular expressions


def fix_custom_parameter(n, property_definition, ):
    if n.bl_idname in ['xFormNullNode', 'xFormBoneNode', 'xFormArmatureNode', 'xFormGeometryObjectNode',]:
        prop_name = property_definition["name"]
        prop_type = property_definition["bl_idname"]
        
        if prop_type in ['ParameterBoolSocket', 'ParameterIntSocket', 'ParameterFloatSocket', 'ParameterVectorSocket' ]:
            # is it good to make both of them?
            input = n.inputs.new( prop_type, prop_name)
            output = n.outputs.new( prop_type, prop_name)
            if property_definition["is_output"] == True:
                return output
            return input
    
    elif n.bl_idname in ['LinkArmature']:
        prop_name = property_definition["name"]
        prop_type = property_definition["bl_idname"]
        input = n.inputs.new( prop_type, prop_name)
        return input

    return None
    
    


def export_to_json(trees, path="", write_file=True, only_selected=False):
    # ignore these because they are either unrelated python stuff or useless or borked
    prop_ignore = [ "__dict__", "__doc__", "__module__", "__weakref__",# "name",
                    "bl_height_default", "bl_height_max", "bl_height_min",
                    "bl_icon", "bl_rna", "bl_static_type", "bl_description",
                    "bl_width_default", "bl_width_max", "bl_width_min",
                    "__annotations__", "original", "rna_type", "view_center",
                    "links", "nodes", "internal_links", "inputs", "outputs",
                    "__slots__", "dimensions", "type", "interface",
                    "library_weak_reference", "parsed_tree", "node_tree_updater",
                    "asset_data", "preview",  # blender asset stuff
                    "object_reference", # this one is here to hold on to widgets when appending
                    "color_tag" , # added in blender 4.4, not used by Mantis, readonly.
                    ] 
    # don't ignore: "bl_idname", "bl_label",
    # ignore the name, it's the dict - key for the node props
     # no that's stupid don't ignore the name good grief

    # I am doing this because these are interactions with other addons that cause problems and probably don't exist for any given user
    prop_ignore.extend(['keymesh'])

    export_data = {}
    for tree in trees:
        base_tree = False
        if tree is trees[-1]:
            base_tree = True

        tree_info, tree_in_out = {}, {}
        for propname  in dir(tree):
            # if getattr(tree, propname):
            #     pass
            if (propname in prop_ignore) or ( callable(getattr(tree, propname)) ):
                continue
            v = getattr(tree, propname)
            if isinstance(getattr(tree, propname), bpy.types.bpy_prop_array):
                v = tuple(getattr(tree, propname))
            if not is_jsonable( v  ):
                raise RuntimeError(f"Not JSON-able: {propname}, type: {type(v)}")
            tree_info[propname] = v
        tree_info["name"] = tree.name

        # if only_selected:
        #     # all in/out links, relative to the selection, should be marked and used to initialize tree properties
        #     pass
            
        
        if not only_selected: # we'll handle this later with the links
            for sock in tree.interface.items_tree:
                sock_data={}

                if sock.item_type == 'PANEL':
                    sock_data["name"] = sock.name
                    sock_data["item_type"] = sock.item_type
                    sock_data["description"] = sock.description
                    sock_data["default_closed"] = sock.default_closed
                    tree_in_out[sock.name] = sock_data

                # if it is a socket....
                else:
                    sock_parent = None
                    if sock.parent:
                        sock_parent = sock.parent.name
                    for propname  in dir(sock):
                        if (propname in prop_ignore) or ( callable(v) ):
                            continue
                        if (propname == "parent"):
                            sock_data[propname] = sock_parent
                            continue
                        v = getattr(sock, propname)
                        if isinstance(getattr(sock, propname), bpy.types.bpy_prop_array):
                            v = tuple(getattr(sock, propname))
                        if not is_jsonable( v ):
                            raise RuntimeError(f"{propname}, {type(v)}")
                        sock_data[propname] = v
                
                    tree_in_out[sock.identifier] = sock_data

        nodes = {}
        for n in tree.nodes:
            # if this is a node-group, force it to update its interface, because it may be messed up.
            # can remove this HACK when I have stronger guarentees about node-group's keeping the interface
            from .base_definitions import node_group_update
            if hasattr(n, "node_tree"):
                node_group_update(n, force=True)
            if only_selected and n.select == False:
                continue
            node_props, sockets = {}, {}
            for propname  in dir(n):
                v = getattr(n, propname)
                if propname in ['fake_fcurve_ob']:
                    v=v.name
                if (propname in prop_ignore) or ( callable(v) ):
                    continue
                if v.__class__.__name__ in ["Vector", "Color"]:
                    v = tuple(v)
                if isinstance(v, bpy.types.NodeTree):
                    v = v.name
                if isinstance(v, bpy.types.bpy_prop_array):
                    v = tuple(v)
                if propname == "parent" and v:
                    v = v.name
                if not is_jsonable(v):
                    raise RuntimeError(f"Could not export...  {n.name}, {propname}, {type(v)}")
                if v is None:
                    continue

                node_props[propname] = v

                # so we have to accumulate the parent location because the location is not absolute
                if propname == "location" and n.parent is not None:
                    location_acc = Vector((0,0))
                    parent = n.parent
                    while (parent):
                        location_acc += parent.location
                        parent = parent.parent
                    location_acc += getattr(n, propname)
                    node_props[propname] = tuple(location_acc)
                    # this works!

                    # n.parent = None
                
                # if propname == "location":
                #     print (v, n.location)
                # if parent:
                #     n.parent = parent
            # now we need to get the sockets...

            # WHY IS THIS FUNCTION DEFINED IN THIS SCOPE?
            def socket_data(s):
                socket = {}
                socket["name"] = s.name
                socket["bl_idname"] = s.bl_idname
                socket["is_output"] = s.is_output
                socket["is_multi_input"] = s.is_multi_input

                # if s.bl_idname == 'TransformSpaceSocket':
                #     prGreen(s.default_value)
                
                # here is where we'll handle a socket's special data
                if s.bl_idname == "EnumMetaBoneSocket":
                    socket["bone"] = s.bone
                if s.bl_idname in ["EnumMetaBoneSocket", "EnumMetaRigSocket", "EnumCurveSocket"]:
                    if sp := s.get("search_prop"): # may be None
                        socket["search_prop"] = sp.name # this is an object.
                #

                # v = s.get("default_value") # this doesn't seem to work, see below
                if hasattr(s, "default_value"):
                    v = s.default_value
                else:
                    v = None
                v_type = type(v)
                if v is None:
                    return socket # we don't need to store this.
                if not is_jsonable(v):
                    v = tuple(v)
                if not is_jsonable(v):
                    raise RuntimeError(f"Error serializing data in {s.node.name}::{s.name} for value of type {v_type}")
                socket["default_value"] = v
                # at this point we can get the custom parameter ui hints if we want
                if not s.is_output:
                    # try and get this data
                    if v := getattr(s,'min', None):
                        socket["min"] = v
                    if v := getattr(s,'max', None):
                        socket["max"] = v
                    if v := getattr(s,'soft_min', None):
                        socket["soft_min"] = v
                    if v := getattr(s,'soft_max', None):
                        socket["soft_max"] = v
                    if v := getattr(s,'description', None):
                        socket["description"] = v
                return socket
                #

            for i, s in enumerate(n.inputs):
                socket = socket_data(s)
                socket["index"]=i
                sockets[s.identifier] = socket
            for i, s in enumerate(n.outputs):
                socket = socket_data(s)
                socket["index"]=i
                sockets[s.identifier] = socket
            
            node_props["sockets"] = sockets
            nodes[n.name] = node_props
            
        
        links = []

        in_sockets = {}
        out_sockets = {}

        in_node = {"name":"MANTIS_AUTOGEN_GROUP_INPUT", "bl_idname":"NodeGroupInput", "sockets":in_sockets}
        out_node = {"name":"MANTIS_AUTOGEN_GROUP_OUTPUT", "bl_idname":"NodeGroupOutput", "sockets":out_sockets}


        add_input_node, add_output_node = False, False

        unique_sockets_from={}
        unique_sockets_to={}


        for l in tree.links:
            a, b = l.from_node.name, l.from_socket.identifier
            c, d = l.to_node.name, l.to_socket.identifier

            # get the indices of the sockets to be absolutely sure
            for e, outp in enumerate(l.from_node.outputs):
                # for some reason, 'is' does not return True no matter what...
                # so we are gonn compare the memory address directly, this is stupid
                if (outp.as_pointer() == l.from_socket.as_pointer()): break
            else:
                problem=l.from_node.name + "::" + l.from_socket.name
                raise RuntimeError(wrapRed(f"Error saving index of socket: {problem}"))
            for f, inp in enumerate(l.to_node.inputs):
                if (inp.as_pointer() == l.to_socket.as_pointer()): break
            else:
                problem = l.to_node.name + "::" + l.to_socket.name
                raise RuntimeError(wrapRed(f"Error saving index of socket: {problem}"))
            g, h = l.from_socket.name, l.to_socket.name

            # print (f"{a}:{b} --> {c}:{d})")
            # this data is good enough
            if base_tree:
                if (only_selected and l.from_node.select) and (not l.to_node.select):
                    # handle an output in the tree
                    add_output_node=True
                    if not (sock_name := unique_sockets_to.get(l.from_socket.node.name+l.from_socket.identifier)):
                        sock_name = l.to_socket.name; name_stub = sock_name
                        used_names = list(tree_in_out.keys()); i=0
                        while sock_name in used_names:
                            sock_name=name_stub+'.'+str(i).zfill(3); i+=1
                        unique_sockets_to[l.from_socket.node.name+l.from_socket.identifier]=sock_name

                    out_sock = out_sockets.get(sock_name)
                    if not out_sock:
                        out_sock = {}; out_sockets[sock_name] = out_sock
                        out_sock["index"]=len(out_sockets) # zero indexed, so zero length makes zero the first index and so on, this works
                    out_sock["name"] = sock_name
                    out_sock["identifier"] = sock_name
                    out_sock["bl_idname"] = l.to_socket.bl_idname
                    out_sock["is_output"] = False
                    out_sock["source"]=[l.to_socket.node.name,l.to_socket.identifier]
                    out_sock["is_multi_input"] = False # this is not something I can even set on tree interface items, and this code is not intended for making Schema
                    sock_data={}
                    sock_data["name"] = sock_name
                    sock_data["item_type"] = "SOCKET"
                    sock_data["default_closed"] = False
                    sock_data["socket_type"] = l.from_socket.bl_idname
                    sock_data["identifier"] = sock_name
                    sock_data["in_out"]="OUTPUT"
                    sock_data["index"]=out_sock["index"]
                    tree_in_out[sock_name] = sock_data

                    c=out_node["name"]
                    d=out_sock["identifier"]
                    f=out_sock["index"]
                    h=out_sock["name"]

                elif (only_selected and (not l.from_node.select)) and l.to_node.select:
                    add_input_node=True
                    # we need to get a unique name for this
                    # use the Tree IN/Out because we are dealing with Group in/out
                    if not (sock_name := unique_sockets_from.get(l.from_socket.node.name+l.from_socket.identifier)):
                        sock_name = l.from_socket.name; name_stub = sock_name
                        used_names = list(tree_in_out.keys()); i=0
                        while sock_name in used_names:
                            sock_name=name_stub+'.'+str(i).zfill(3); i+=1
                        unique_sockets_from[l.from_socket.node.name+l.from_socket.identifier]=sock_name

                    in_sock = in_sockets.get(sock_name)
                    if not in_sock:
                        in_sock = {}; in_sockets[sock_name] = in_sock
                        in_sock["index"]=len(in_sockets) # zero indexed, so zero length makes zero the first index and so on, this works
                        #
                        in_sock["name"] = sock_name
                        in_sock["identifier"] = sock_name
                        in_sock["bl_idname"] = l.from_socket.bl_idname
                        in_sock["is_output"] = True
                        in_sock["is_multi_input"] = False # this is not something I can even set on tree interface items, and this code is not intended for making Schema
                        in_sock["source"] = [l.from_socket.node.name,l.from_socket.identifier]
                        sock_data={}
                        sock_data["name"] = sock_name
                        sock_data["item_type"] = "SOCKET"
                        sock_data["default_closed"] = False
                        sock_data["socket_type"] = l.from_socket.bl_idname
                        sock_data["identifier"] = sock_name
                        sock_data["in_out"]="INPUT"
                        sock_data["index"]=in_sock["index"]

                        
                        tree_in_out[sock_name] = sock_data

                    a=in_node.get("name")
                    b=in_sock["identifier"]
                    e=in_sock["index"]
                    g=in_node.get("name")
                # parentheses matter here...
                elif (only_selected and not (l.from_node.select and l.to_node.select)):
                    continue
            elif only_selected and not (l.from_node.select and l.to_node.select):
                continue # pass if both links are not selected
            links.append( (a,b,c,d,e,f,g,h) ) # it's a tuple
        
        
        if add_input_node or add_output_node:
            all_nodes_bounding_box=[Vector((float("inf"),float("inf"))), Vector((-float("inf"),-float("inf")))]
            for n in nodes.values():
                if n["location"][0] < all_nodes_bounding_box[0].x:
                    all_nodes_bounding_box[0].x = n["location"][0]
                if n["location"][1] < all_nodes_bounding_box[0].y:
                    all_nodes_bounding_box[0].y = n["location"][1]
                #
                if n["location"][0] > all_nodes_bounding_box[1].x:
                    all_nodes_bounding_box[1].x = n["location"][0]
                if n["location"][1] > all_nodes_bounding_box[1].y:
                    all_nodes_bounding_box[1].y = n["location"][1]


        if add_input_node:
            in_node["location"] = Vector((all_nodes_bounding_box[0].x-400, all_nodes_bounding_box[0].lerp(all_nodes_bounding_box[1], 0.5).y))
            nodes["MANTIS_AUTOGEN_GROUP_INPUT"]=in_node
        if add_output_node:
            out_node["location"] = Vector((all_nodes_bounding_box[1].x+400, all_nodes_bounding_box[0].lerp(all_nodes_bounding_box[1], 0.5).y))
            nodes["MANTIS_AUTOGEN_GROUP_OUTPUT"]=out_node

        export_data[tree.name] = (tree_info, tree_in_out, nodes, links,) # f_curves)
    import json

    if not write_file:
        return export_data # gross to have a different type of return value... but I don't care

    with open(path, "w") as file:
        print(wrapWhite("Writing mantis tree data to: "), wrapGreen(file.name))
        file.write( json.dumps(export_data, indent = 4) )
    # I'm gonna do this in a totally naive way, because this should already be sorted properly
    #   for the sake of dependency satisfaction. So the current "tree" should be the "main" tree
    tree.filepath = path

    return {'FINISHED'}
    

def do_import_from_file(filepath, context):
    import json

    all_trees = [n_tree for n_tree in bpy.data.node_groups if n_tree.bl_idname in ["MantisTree", "SchemaTree"]]

    for tree in all_trees:
        tree.do_live_update = False

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        do_import(data,context)

        for tree in all_trees:
            tree.do_live_update = True

        tree = bpy.data.node_groups[list(data.keys())[-1]]
        try:
            context.space_data.node_tree = tree
        except AttributeError: # not hovering over the Node Editor
            pass
        return {'FINISHED'}
    # otherwise:
    # repeat this because we left the with, this is bad and ugly but I don't care
    for tree in all_trees:
        tree.do_live_update = True
    return {'CANCELLED'}

def do_import(data, context):
    trees = []
    tree_sock_id_maps = {}

    # First: init the interface of the node graph
    for tree_name, tree_data in data.items():
        tree_info = tree_data[0]
        tree_in_out = tree_data[1]

        # need to make a new tree; first, try to get it:
        tree = bpy.data.node_groups.get(tree_info["name"])
        if tree is None:
            tree = bpy.data.node_groups.new(tree_info["name"], tree_info["bl_idname"])
        tree.nodes.clear(); tree.links.clear(); tree.interface.clear()
        # this may be a bad bad thing to do without some kind of warning TODO TODO
        tree.is_executing = True
        tree.do_live_update = False
        trees.append(tree)
        
        tree_sock_id_map = {}
        tree_sock_id_maps[tree.name] = tree_sock_id_map
        
        interface_parent_me = {}

        # I need to guarantee that the interface items are in the right order.
        interface_sockets = [] # I'll just sort them afterwards so I hold them here.
        

        for s_name, s_props in tree_in_out.items():
            if s_props["item_type"] == 'SOCKET':
                if s_props["socket_type"] == "LayerMaskSocket":
                    continue
                if (socket_type := s_props["socket_type"]) == "NodeSocketColor":
                    socket_type = "VectorSocket"
                sock = tree.interface.new_socket(s_props["name"], in_out=s_props["in_out"], socket_type=socket_type)
                tree_sock_id_map[s_name] = sock.identifier
                interface_sockets.append( (sock, s_props['position']) )
                    # TODO: set whatever properties are needed (default, etc)
                if panel := s_props.get("parent"): # this get is just to maintain compatibility with an older form of this script... and it is harmless
                    interface_parent_me[sock] = (panel, s_props["position"])
            else: # it's a panel
                panel = tree.interface.new_panel(s_props["name"], description=s_props.get("description"), default_closed=s_props.get("default_closed"))
    
        for socket, (panel, index) in interface_parent_me.items():
            tree.interface.move_to_parent(
                                    socket,
                                    tree.interface.items_tree.get(panel),
                                    index,
                                    )
        
        # Go BACK through and set the index/position now that all items exist.
        interface_sockets.sort(key=lambda a : a[1])
        for (socket, position) in interface_sockets:
            print (socket.name, position)
            tree.interface.move(socket, position)
        
    # Now go and do nodes and links
    for tree_name, tree_data in data.items():
        print ("Importing sub-graph: %s with %s nodes" % (wrapGreen(tree_name), wrapPurple(len(tree_data[2]))) )

        tree_info = tree_data[0]
        nodes = tree_data[2]
        links = tree_data[3]
        
        parent_me = []

        tree = bpy.data.node_groups.get(tree_info["name"])

        tree.is_executing = True
        tree.do_live_update = False
        trees.append(tree)

        tree_sock_id_map=tree_sock_id_maps[tree.name]
        
        interface_parent_me = {}
        
#        from mantis.utilities import prRed, prWhite, prOrange, prGreen
        for name, propslist in nodes.items():
            bl_idname = propslist["bl_idname"]
            if bl_idname in NODES_REMOVED:
                prWhite(f"INFO: Ignoring import of node {name} of type {bl_idname}; it has been removed.")
                continue
            n = tree.nodes.new(bl_idname)
            if bl_idname in ["DeformerMorphTargetDeform"]:
                n.inputs.remove(n.inputs[-1]) # get rid of the wildcard

            if n.bl_idname in [ "SchemaArrayInput",
                                "SchemaArrayInputGet",
                                "SchemaArrayOutput",
                                "SchemaConstInput",
                                "SchemaConstOutput",
                                "SchemaOutgoingConnection",
                                "SchemaIncomingConnection",]:
                n.update()

            
            if sub_tree := propslist.get("node_tree"):
                n.node_tree = bpy.data.node_groups.get(sub_tree)
                from .base_definitions import node_group_update
                node_group_update(n, force = True)
            
            sockets_removed = []
            for i, (s_id, s_val) in enumerate(propslist["sockets"].items()):
                for socket_removed in SOCKETS_REMOVED:
                    if n.bl_idname == socket_removed[0] and s_id == socket_removed[1]:
                        prWhite(f"INFO: Ignoring import of socket {s_id}; it has been removed.")
                        sockets_removed.append(s_val["index"])
                        sockets_removed.sort()
                        continue
                try:
                    if s_val["is_output"]: # for some reason it thinks the index is a string?
                        # try:
                        if n.bl_idname == "MantisSchemaGroup":
                            socket = n.outputs.new(s_val["bl_idname"], s_val["name"], identifier=s_id)
                        else:
                            socket = n.outputs[int(s_val["index"])]
                    else:
                        for removed_index in sockets_removed:
                            if s_val["index"] > removed_index:
                                s_val["index"]-=1
                        if s_val["index"] >= len(n.inputs):
                            if n.bl_idname == "UtilityDriver":
                                with bpy.context.temp_override(**{'node':n}):
                                    bpy.ops.mantis.driver_node_add_variable()
                                socket = n.inputs[int(s_val["index"])]
                            elif n.bl_idname == "UtilityFCurve":
                                with bpy.context.temp_override(**{'node':n}):
                                    bpy.ops.mantis.fcurve_node_add_kf()
                                socket = n.inputs[int(s_val["index"])]
                            elif n.bl_idname == "MantisSchemaGroup":
                                socket = n.inputs.new(s_val["bl_idname"], s_val["name"], identifier=s_id, use_multi_input=s_val["is_multi_input"])
                                # for k,v in s_val.items():
                                #     print(f"{k}:{v}")
                                # print (s_id)
                                # raise NotImplementedError(s_val["is_multi_input"])
                            elif n.bl_idname in ["NodeGroupOutput"]:
                                # print (len(n.inputs), len(n.outputs))
                                pass
                            elif n.bl_idname == "LinkArmature":
                                with bpy.context.temp_override(**{'node':n}):
                                    bpy.ops.mantis.link_armature_node_add_target()
                                socket = n.inputs[int(s_val["index"])]
                            elif n.bl_idname == "DeformerMorphTargetDeform": # this one doesn't use an operator since I figure out how to do dynamic node stuff
                                socket = n.inputs.new(s_val["bl_idname"], s_val["name"], identifier=s_id)
                            else:
                                prWhite(n.name, s_val["name"], s_id)
                                for k,v in propslist["sockets"].items():
                                    print(k,v)
                                prRed(s_val["index"], len(n.inputs))
                                raise NotImplementedError(wrapRed(f"{n.bl_idname} needs to be handled in JSON load."))
                            # if n.bl_idname in ['']
                        else: # most of the time
                            socket = n.inputs[int(s_val["index"])]
                except IndexError:
                    socket = fix_custom_parameter(n, propslist["sockets"][s_id])
                    if socket is None:
                        is_output = "output" if {s_val["is_output"]} else "input"
                        prRed(s_val, type(s_val))
                        raise RuntimeError(is_output, n.name, s_val["name"], s_id, len(n.inputs))

                
#                if propslist["bl_idname"] == "UtilityMetaRig":#and i == 0:
#                    pass#prRed (i, s_id, s_val)
#                if propslist["bl_idname"] == "UtilityMetaRig":# and i > 0:
#                       prRed("Not Found: %s" % (s_id))
#                       prOrange(propslist["sockets"][s_id])
#                       socket = fix_custom_parameter(n, propslist["sockets"][s_id]
                for s_p, s_v in s_val.items():
                    if s_p not in ["default_value"]:
                        if s_p == "search_prop" and n.bl_idname == 'UtilityMetaRig':
                            socket.node.armature= s_v
                            socket.search_prop=bpy.data.objects.get(s_v)
                        if s_p == "search_prop" and n.bl_idname in ['UtilityMatrixFromCurve', 'UtilityMatricesFromCurve']:
                            socket.search_prop=bpy.data.objects.get(s_v)
                        elif s_p == "bone" and socket.bl_idname == 'EnumMetaBoneSocket':
                            socket.bone = s_v
                            socket.node.pose_bone = s_v
                        continue # not editable and NOT SAFE
                    #
                    if socket.bl_idname in ["BooleanThreeTupleSocket"]:
                        value = bool(s_v[0]), bool(s_v[1]), bool(s_v[2]),
                        s_v = value
                    try:
                        setattr(socket, s_p , s_v)
                    except TypeError as e:
                        prRed("Can't set socket due to type mismatch: ", socket, s_p, s_v)
                        # raise e
                    except ValueError as e:
                        prRed("Can't set socket due to type mismatch: ", socket, s_p, s_v)
                        # raise e
                    except AttributeError as e:
                        prWhite("Tried to write a read-only property, ignoring...")
                        prWhite(f"{socket.node.name}[{socket.name}].{s_p} is read only, cannot set value to {s_v}")
                        # raise e
                # not sure if this is true:
                    # this can find properties that aren't node in/out
                    # we should also be checking those above actually
                # TODO:
                # find out why "Bone hide" not being found
            for p, v in propslist.items():
                if p == "sockets": # it's the sockets dict
                    continue
                if p == "node_tree":
                    continue # we've already done this # v = bpy.data.node_groups.get(v)
                # will throw AttributeError if read-only
                # will throw TypeError if wrong type...
                if n.bl_idname == "NodeFrame" and p in ["width, height, location"]:
                    continue 
                if p == "parent" and v is not None:
                    parent_me.append( (n.name, v) )
                    v = None # for now) #TODO
                try:
                    setattr(n, p, v)
                except Exception as e:
                    print (p)
                    raise e
#        raise NotImplementedError

        
        
#        for k,v in tree_sock_id_map.items():
#            print (wrapGreen(k), "   ", wrapPurple(v))
        
        for l in links:

            id1 = l[1]
            id2 = l[3]
            #
            name1=l[6]
            name2=l[7]
            
            # prWhite(l[0], l[1], " --> ", l[2], l[3])
            
            # l has...
            # node 1
            # identifier 1
            # node 2
            # identifier 2
            
            # if the from/to socket or node has been removed, continue
            from_node = tree.nodes.get(l[0])
            if not from_node:
                prWhite(f"INFO: cannot create link {l[0]}:{l[1]} -->  {l[2]}:{l[3]}")
                continue
            if hasattr(from_node, "node_tree"): # now we have to map by name actually
                try:
                    id1 = from_node.outputs[l[4]].identifier
                except IndexError:
                    prRed ("Index incorrect")
                    id1 = None
            elif from_node.bl_idname in ["NodeGroupInput"]:
                id1 = tree_sock_id_map.get(l[1])
                if id1 is None:
                    prRed(l[1])
#                prOrange (l[1], id1)
            elif from_node.bl_idname in ["SchemaArrayInput", "SchemaConstInput", "SchemaIncomingConnection"]:
                # try the index instead
                id1 = from_node.outputs[l[4]].identifier
            

            for from_sock in from_node.outputs:
                if from_sock.identifier == id1: break
            else: # we can raise a runtime error here actually
                from_sock = None
                
                
            
            to_node = tree.nodes[l[2]]
            if hasattr(to_node, "node_tree"):
                try:
                    id2 = to_node.inputs[l[5]].identifier
                except IndexError:
                    prRed ("Index incorrect")
                    id2 = None
            elif to_node.bl_idname in ["NodeGroupOutput"]:
                id2 = tree_sock_id_map.get(l[3])
#                prPurple(to_node.name)
#                for inp in to_node.inputs:
#                    prPurple(inp.name, inp.identifier)
#                prOrange (l[3], id2)
            elif to_node.bl_idname in ["SchemaArrayOutput", "SchemaConstOutput", "SchemaOutgoingConnection"]:
                # try the index instead
                id2 = to_node.inputs[l[5]].identifier
                # try to get by name
                #id2 = to_node.inputs[name2]

            for to_sock in to_node.inputs:
                if to_sock.identifier == id2: break
            else:
                to_sock = None
            
            try:
                link = tree.links.new(from_sock, to_sock)
            except TypeError:
                if ((id1 is not None) and ("Layer Mask" in id1)) or ((id2 is not None) and ("Layer Mask" in id2)):
                    pass
                else:
                    prWhite(f"looking for... {name1}:{id1}, {name2}:{id2}")
                    prRed (f"Failed: {l[0]}:{l[1]} --> {l[2]}:{l[3]}")
                    prRed (f" got node: {from_node.name}, {to_node.name}")
                    prRed (f" got socket: {from_sock}, {to_sock}")

                    if from_sock is None:
                        prOrange ("Candidates...")
                        for out in from_node.outputs:
                            prOrange("   %s, id=%s" % (out.name, out.identifier))
                        for k, v in tree_sock_id_map.items():
                            print (wrapOrange(k), wrapPurple(v))
                    if to_sock is None:
                        prOrange ("Candidates...")
                        for inp in to_node.inputs:
                            prOrange("   %s, id=%s" % (inp.name, inp.identifier))
                        for k, v in tree_sock_id_map.items():
                            print (wrapOrange(k), wrapPurple(v))
                    raise RuntimeError
            
            # if at this point it doesn't work... we need to fix
            
        for name, p in parent_me:
            if (n := tree.nodes.get(name)) and (p := tree.nodes.get(p)):
                n.parent = p
            # otherwise the frame node is missing because it was not included in the data e.g. when grouping nodes.

        tree.is_executing = False
        tree.do_live_update = True
        
        # try:
        #     tree=context.space_data.path[0].node_tree
        #     tree.update_tree(context)
        # except: #update tree can cause all manner of errors
        #     pass





import bpy

from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

# Save As
class MantisExportNodeTreeSaveAs(Operator, ExportHelper):
    """Export a Mantis Node Tree by filename."""
    bl_idname = "mantis.export_save_as"
    bl_label = "Export Mantis Tree as ...(JSON)"

    # ExportHelper mix-in class uses this.
    filename_ext = ".rig"

    filter_glob: StringProperty(
        default="*.rig",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    @classmethod
    def poll(cls, context):
        return hasattr(context.space_data, 'path')

    def execute(self, context):
        # we need to get the dependent trees from self.tree...
        # there is no self.tree
        # how do I choose a tree?
        
        base_tree=context.space_data.path[-1].node_tree
        from .utilities import all_trees_in_tree
        trees = all_trees_in_tree(base_tree)[::-1]
        prGreen("Exporting node graph with dependencies...")
        for t in trees:
            prGreen ("Node graph: \"%s\"" % (t.name))
        return export_to_json(trees, self.filepath)

# Save
class MantisExportNodeTreeSave(Operator):
    """Save a Mantis Node Tree to disk."""
    bl_idname = "mantis.export_save"
    bl_label = "Export Mantis Tree (JSON)"

    @classmethod
    def poll(cls, context):
        return hasattr(context.space_data, 'path')

    def execute(self, context):
        
        base_tree=context.space_data.path[-1].node_tree
        from .utilities import all_trees_in_tree
        trees = all_trees_in_tree(base_tree)[::-1]
        prGreen("Exporting node graph with dependencies...")
        for t in trees:
            prGreen ("Node graph: \"%s\"" % (t.name))
        return export_to_json(trees, base_tree.filepath)

# Save Choose:
class MantisExportNodeTree(Operator):
    """Save a Mantis Node Tree to disk."""
    bl_idname = "mantis.export_save_choose"
    bl_label = "Export Mantis Tree (JSON)"

    @classmethod
    def poll(cls, context):
        return hasattr(context.space_data, 'path')

    def execute(self, context):
        base_tree=context.space_data.path[-1].node_tree
        if base_tree.filepath:
            prRed(base_tree.filepath)
            return bpy.ops.mantis.export_save()
        else:
            return bpy.ops.mantis.export_save_as('INVOKE_DEFAULT')




# here is what needs to be done...
#   - modify this to work with a sort of parsed-tree instead (sort of)
#        - this needs to treat each sub-graph on its own
#        - is this a problem? do I need to reconsider how I treat the graph data in mantis?
#        - I should learn functional programming / currying
#   - then the parsed-tree this builds must be executed as Blender nodes
#   - I think... this is not important right now. not yet.
#   -  KEEP IT SIMPLE, STUPID



class MantisImportNodeTree(Operator, ImportHelper):
    """Import a Mantis Node Tree."""
    bl_idname = "mantis.import_tree"
    bl_label = "Import Mantis Tree (JSON)"

    # ImportHelper mixin class uses this
    filename_ext = ".rig"

    filter_glob : StringProperty(
        default="*.rig",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )


    def execute(self, context):
        return do_import_from_file(self.filepath, context)


# this is useful:
# https://blender.stackexchange.com/questions/73286/how-to-call-a-confirmation-dialog-box

# class MantisReloadConfirmMenu(bpy.types.Panel):
#     bl_label = "Confirm?"
#     bl_idname = "OBJECT_MT_mantis_reload_confirm"

#     def draw(self, context):
#         layout = self.layout
#         layout.operator("mantis.reload_tree")

class MantisReloadNodeTree(Operator):
    # """Import a Mantis Node Tree."""
    # bl_idname = "mantis.reload_tree"
    # bl_label = "Import Mantis Tree"
    """Reload Mantis Tree"""
    bl_idname = "mantis.reload_tree"
    bl_label = "Confirm reload tree?"
    bl_options = {'REGISTER', 'INTERNAL'}


    @classmethod
    def poll(cls, context):
        if hasattr(context.space_data, 'path'):
            return True
        return False

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        base_tree=context.space_data.path[-1].node_tree
        if not base_tree.filepath:
            self.report({'ERROR'}, "Tree has not been saved - so it cannot be reloaded.")
            return {'CANCELLED'}
        self.report({'INFO'}, "reloading tree")
        return do_import_from_file(base_tree.filepath, context)

# todo:
#  - export metarig and option to import it
#  - same with controls
#  - it would be nice to have a library of these that can be imported alongside the mantis graph
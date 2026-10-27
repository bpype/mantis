
# If a $ character is in a value, it is an overlay request
# in the root tree, supply it immediately, otherwise tag this node
# once we finish pulling data from the tree we handle the overlay.
def handle_overlay_detect(node, socket_id, socket_idname, value) -> str:
    mContext = node.mContext
    root_tree = mContext.base_tree
    root_items_tree = root_tree.interface.items_tree
    # detect if it is in the root tree, if so, handle immediately
    out_value = value
    # what this recieves is determined by its idname
    socket_type = str
    match socket_idname:
        case "IntSocket" | "UnsignedIntSocket":
            socket_type = int
        case "FloatSocket" | "FloatPositiveSocket" | "FloatFactorSocket" | "FloatAngleSocket":
            socket_type = float
    # ONLY for root node trees, we can just directly fill this.
    if node.signature[0] is None and len(node.signature) == 2:
        for key, interface_item in root_items_tree.items():
            if interface_item.item_type != "SOCKET": continue
            if interface_item.in_out != "INPUT": continue
            # then what the interface provides is determined by its idname in turn
            # NOTE I'm not 100% sure checking the socket_type is the right thing to do here
            match interface_item.bl_socket_idname:
                case "IntSocket" | "BooleanSocket":
                    if socket_type in {int, float} and '$'+key == out_value:
                        # TODO this is the wrong way to do this, replace this with parser later
                        out_value = socket_type(interface_item.default_int)
                case "FloatSocket":
                    if socket_type in {int, float} and '$'+key == out_value:
                        out_value = socket_type(interface_item.default_float)
                case "StringSocket" | 'BoneCollectionSocket':
                    if socket_type == str:
                        out_value = socket_type(out_value.replace("$"+key, interface_item.default_string))

    else: # since it is not root, we have to tag it.
        mContext.tagged_for_overlay.append((node.signature, socket_id))
    return out_value


STRING_PADDING = 4
overlay_valid_socket_types = [
    "FloatSocket", "FloatPositiveSocket", "FloatFactorSocket",
    "FloatAngleSocket", "UnsignedIntSocket", "IntSocket", "StringSocket",
]
# Do not use these input names as overlay keys:
forbidden_key_names = ["",]
forbidden_in_key_name = ['$',]
def node_scan_overlays(node, socket_id,):
    from ..misc_nodes import SimpleInputNode
    from ..internal_nodes import AutoGenNode
    from ..utilities.utilities import get_ui_node
    from ..utilities.node_common import GraphError
    interface_nodes = node.mContext.interface_nodes
    if not isinstance(node, AutoGenNode):
        ui_node = get_ui_node(node.ui_signature, node.base_tree)
        # we'll assume that the overlay tag system checked if this is linked.
        # TODO this is probably redundant with the check above this
        # First let's check if it is a simple input node, by checking outputs that are marked "input"
        for socket in ui_node.outputs:
            # weird edge case for simple input nodes with unnamed sockets
            # the socket.identifier is not used by Mantis but it defaults to 'socket'\
            if socket.identifier == socket_id and socket.input == True: break
        else:
            for socket in ui_node.inputs:
                if socket.identifier == socket_id: break
            else:
                raise KeyError(f"Socket not found by ID {socket_id} in node {node.ui_signature}\n"
                            f"Candidates: {[socket.identifier for socket in ui_node.inputs]}")
        value = socket.default_value # get the ACTUAL UI value
        if hasattr(socket, 'overlay_text'): # TODO this is all wrong but for now
            value = "$"+socket.overlay_text # I am not implementing the Parser feature
    else: # since it doesn't have a UI node
        value = node.parameters[socket_id]
    
    overlay_data_type = str
    if isinstance(node, (AutoGenNode) ):
        overlay_data_type = type(node.parameters[list(node.outputs.values())[0].name])
    else: # we have the UI socket
        match socket.bl_idname:
            case "IntSocket" | "UnsignedIntSocket":
                overlay_data_type = int
            case "FloatSocket" | "FloatPositiveSocket" | "FloatFactorSocket" | "FloatAngleSocket":
                overlay_data_type = float
    
    if not isinstance(value, str): return
    # First step: get the interface nodes and the overlay keys
    # this should only check interfaces that are ancestors of this node
    my_interfaces = []
    for index in range(len(node.signature)-1):
        if index == 0: continue # root
        # we add one here because the node inside the schema references the schema's interface...
        current_schema_interface_index = node.generated_at_schema_index[index+1]
        if current_schema_interface_index < 0: # this indicates that it is not in a schema
            interface = interface_nodes.get(
                interface_signature := (None, *node.signature[1:index+1], "InputInterface"))
        else: # First we get the interface that enters the schema (index 0)
            interface = interface_nodes.get(
                interface_signature := (None, *node.signature[1:index+1],
                "InputInterface."+str( 0 ).zfill(4)))
            if interface and interface not in my_interfaces: my_interfaces.append(interface)
            if current_schema_interface_index == 0: continue # just did it
            # we need to get the schema of the current index
            interface = interface_nodes.get(
                interface_signature := (None, *node.signature[1:index+1],
                "InputInterface."+str(current_schema_interface_index).zfill(4)))
        if interface:
            my_interfaces.append( interface )
    # the my_interfaces list is sorted in REVERSE order of importance
    # Next, get all the overlay providers.
    name_to_id_map = {}
    name_to_type_map = {} # Just for printing reasonable error messages
    overlay_keys = set()
    root_overlay_values = {}
    # First, we'll get the base tree's default inputs
    for interface_item in node.mContext.base_tree.interface.items_tree:
        if interface_item.item_type != "SOCKET": continue
        if interface_item.in_out != "INPUT": continue
        base_value=None
        match interface_item.bl_socket_idname:
            case "IntSocket" | "BooleanSocket":
                # TODO parser for number types
                base_value = interface_item.default_int
            case "FloatSocket":
                base_value = interface_item.default_float
            case "StringSocket" | "BoneCollectionSocket":
                base_value = interface_item.default_string
        if base_value:
            root_overlay_values[interface_item.name] = base_value
        overlay_keys.add(interface_item.name)
        name_to_id_map[interface_item.name] = None # don't worry about it
        name_to_type_map[interface_item.name] = interface_item.bl_socket_idname
    # BUG? should this be my_interfaces ? why bother with interfaces this may not be a part of?
    for interface_node in interface_nodes.values():
        # problem: the interface node stores socket identifiers as keys
        # so in reality we need to get the group UI node and ask for its input names
        # if there is a duplicate name, too bad!
        group_ui_node = get_ui_node(interface_node.ui_signature[:-1], node.base_tree)
        for interface_item in group_ui_node.node_tree.interface.items_tree:
            if interface_item.item_type != 'SOCKET': continue
            if interface_item.in_out != 'INPUT': continue
            if interface_item.name in forbidden_key_names: continue
            for substr in forbidden_in_key_name:
                if substr in interface_item.name:
                    break
            else: # if we do not find a bad substr
                name_to_id_map[interface_item.name]=interface_item.identifier
                name_to_type_map[interface_item.name] = interface_item.bl_socket_idname
                overlay_keys.add(interface_item.name)
        # For schema interfaces, we also need to get the length and index.
        if 'Index' in interface.outputs:
            overlay_keys.add('Index'); overlay_keys.add('Length')
    if 'Index' in overlay_keys:
        name_to_id_map['Index']='Index'
        name_to_type_map['Index']= "IntSocket"
        name_to_id_map['Length']='Length'
        name_to_type_map['Length']= "IntSocket"
    # sort by reverse length so we find "CatsAndFrogs" before "Cats"
    overlay_keys = sorted(overlay_keys, key= lambda a :-1*len(a))
    # First I need to break it into substrings based on quotation marks
    from ..utilities.utilities import split_quoted_substrings_to_strings
    quoted_substrings = split_quoted_substrings_to_strings(value)
    overlay_tries = []
    for quoted_substring in  quoted_substrings:
        overlay_tries.extend(quoted_substring.split("$"))
    if overlay_data_type == str:
        result = overlay_tries[0] # the 0th element is always before the split character
    else: # TODO HACK later use the parser feature
        result = 0
    # the reason for the difference between overlay_try and key is because
    #  we don't actually know if the $text part has a key in it
    for overlay_try in overlay_tries[1:]:
        if not overlay_try: continue # some of these are empty
        overlay_resolved_value = "$" + overlay_try
        for key in overlay_keys:
            if key in overlay_try:
                overlay_resolved_value = "$" + key
                for interface in reversed(my_interfaces): # since this is reversed when we build it
                    actual_key = name_to_id_map.get(key)
                    socket = interface.inputs.get(actual_key)
                    if key in ['Index', 'Length']:
                        socket = interface.outputs.get(actual_key)
                    if socket:
                        overlay_value = None
                        try:
                            overlay_value = interface.evaluate_input(actual_key)
                        except KeyError:
                            if (socket_type := name_to_type_map.get(key) or 'NOT FOUND') in overlay_valid_socket_types:
                                raise GraphError(f"Error: Variable {key} is not supported because it has "
                                                 f"an invalid input in the node group: {interface.signature[:-1]}.")
                            raise GraphError( f"Error: Variable {key} is not supported because it is "
                                              f"type {socket_type}" )
                            # NOTE that the above can also be caused by any BUG occuring in node group update
                            # because it causes the interface to be invalid for the UI node that spawns the interface node.
                        if overlay_data_type == str:
                            if isinstance(overlay_value, (float, int)):
                                overlay_value = str(overlay_value).zfill(STRING_PADDING)
                            assert (isinstance(overlay_value, str)), f"Error: Variable {key} is not supported because it is type {type(overlay_value)}"
                            overlay_resolved_value = overlay_try.replace(key, overlay_value)
                        else:
                            overlay_resolved_value = overlay_value
                        break
                else: # we'll try the base tree
                    if base_tree_result := root_overlay_values.get(key):
                        if overlay_data_type == str and not isinstance(base_tree_result, str):
                            base_tree_result = str(base_tree_result).zfill(STRING_PADDING)
                        overlay_resolved_value = base_tree_result
                    else:
                        prOrange(f"WARN: no overlay value applied for {node.ui_signature} for key {key}")
                break # we found the key and are done here. One found Key per overlay-try
        result += overlay_resolved_value
    # Simple Input sockets with unnamed sockets assign this ID automatically
    # But Mantis uses the name instead. Usually the name and ID are the same.
    if socket_id == 'socket' and ui_node.outputs[0].name == "":
        socket_id = ''
    node.parameters[socket_id] = result
    return result # because sometimes I need to get the result, too


from ..utilities.utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

from ..base_definitions import OverlayApplyError, GraphError

# For now, this is not yet implemented. lol
def parser_handle_text(text):
    return '$' + text

def get_socket_idname_data_type(socket_idname):
    data_type = str
    match socket_idname:
        case "IntSocket" | "UnsignedIntSocket":
            data_type = int
        case "FloatSocket" | "FloatPositiveSocket" | "FloatFactorSocket" | "FloatAngleSocket":
            data_type = float
    return (data_type)

# If a $ character is in a value, it is an overlay request
# in the root tree, supply it immediately, otherwise tag this node
# once we finish pulling data from the tree we handle the overlay.
def handle_overlay_detect(node, socket_id, socket_idname, value) -> str:
    mContext = node.mContext
    if node.signature[0] is None and len(node.signature) == 2:
        value = fill_root_tree_overlays(mContext, socket_idname, value)
    else: # since it is not root, we have to tag it.
        mContext.tagged_for_overlay.append((node.signature, socket_id))
    return value

# The root tree doesn't have any interfaces to look up so we can fill it immediately
def fill_root_tree_overlays(mContext, socket_idname, value):
    root_tree = mContext.base_tree
    root_items_tree = root_tree.interface.items_tree
    socket_data_type = get_socket_idname_data_type(socket_idname)

    for key, interface_item in root_items_tree.items():
        if interface_item.item_type != "SOCKET": continue
        if interface_item.in_out != "INPUT": continue
        # then what the interface provides is determined by its idname in turn
        match interface_item.bl_socket_idname:
            case "IntSocket" | "BooleanSocket":
                if socket_data_type in {int, float} and '$'+key == value:
                    # TODO this is the wrong way to do this, replace this with parser later
                    value = socket_data_type(interface_item.default_int)
            case "FloatSocket":
                if socket_data_type in {int, float} and '$'+key == value:
                    value = socket_data_type(interface_item.default_float)
            case "StringSocket" | 'BoneCollectionSocket':
                if socket_data_type == str:
                    value = socket_data_type(value.replace("$"+key, interface_item.default_string))
    return value

def get_interfaces_for_node(mantis_node,):
    all_interface_nodes = mantis_node.mContext.input_interface_nodes
    my_interfaces = []
    for index in range(len(mantis_node.signature)-1):
        if index == 0: continue # the root isn't relevant unless I refactor to make an interface for it
        current_schema_interface_index = mantis_node.generated_at_schema_index[index+1]
        interfaces_from_schema = all_interface_nodes[ ( None, *mantis_node.signature[1:index+1] ) ]
        # we need to get ONLY the interfaces up to the current index, which is 0 for non-schema
        my_interfaces.extend( interfaces_from_schema[:current_schema_interface_index+1] ) # +1 (slice end is not inclusive)
    return my_interfaces

def get_base_tree_overlay_values(items_tree, name_to_type_map, overlay_keys, root_overlay_values):
    for interface_item in items_tree:
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
        name_to_type_map[interface_item.name] = interface_item.bl_socket_idname

def get_overlay_keys_types_ids(my_interfaces, overlay_keys, name_to_type_map, name_to_id_map):
    # We need to get all the relevant keys to search for, all the types for error messages
    # and all the IDs because interface nodes store stuff by ID, not by name
    # and if there is a duplicate name, it will shadow - too bad!
    for interface_node in my_interfaces:
        # fill in the overlay keys and name-to-type-map (used for errors)
        interface_items_tree = interface_node.get_tree_interface_items()
        for interface_item in interface_items_tree:
            if interface_item.item_type != 'SOCKET': continue
            if interface_item.in_out != 'INPUT': continue
            if interface_item.name in forbidden_key_names: continue
            for substr in forbidden_in_key_name:
                if substr in interface_item.name: break
            else: # if we do not find a bad substr
                name_to_id_map[interface_item.name]=interface_item.identifier
                name_to_type_map[interface_item.name] = interface_item.bl_socket_idname
                overlay_keys.add(interface_item.name)
        # For schema interfaces, we also need to get the length and index.
        if 'Index' in interface_node.outputs:
            overlay_keys.add('Index'); overlay_keys.add('Length')
    if 'Index' in overlay_keys:
        name_to_id_map['Index']='Index'; name_to_type_map['Index']= "IntSocket"
        name_to_id_map['Length']='Length'; name_to_type_map['Length']= "IntSocket"

STRING_PADDING = 4
overlay_valid_socket_types = [
    "FloatSocket", "FloatPositiveSocket", "FloatFactorSocket",
    "FloatAngleSocket", "UnsignedIntSocket", "IntSocket", "StringSocket",
]
# Do not use these input names as overlay keys:
forbidden_key_names = ["",]
forbidden_in_key_name = ['$',]
def node_scan_overlays(node, socket_id,):
    from ..internal_nodes import AutoGenNode
    overlay_data_type = str
    try:
        socket = node.inputs[socket_id]
    except KeyError:
        socket = node.outputs[socket_id]
    if socket_id == 'Schema Length':
        # this happens in schema solve init, the actual value lives in an autogen node...
        # it doesn't matter, we only need the overlay value and the intended type
        value = node.evaluate_input('Schema Length')
        overlay_data_type = int
    else:
        value = node.parameters[socket_id]
    if overlay_data_type == str: # It is still default, not set to int by the above
        if isinstance(node, (AutoGenNode) ):  # we need to check it for the general case
            overlay_data_type = type(node.parameters[list(node.outputs.values())[0].name])
        else: # we have the mantis socket which has a type field
            overlay_data_type = get_socket_idname_data_type(socket.socket_type)
    if not isinstance(value, str): return
    # First step: get the interface nodes and the overlay keys
    # this should only check interfaces that are ancestors of this node
    my_interfaces = get_interfaces_for_node(mantis_node=node)
    # the my_interfaces list is sorted in REVERSE order of importance
    # Next, get all the overlay providers.
    name_to_type_map, root_overlay_values, name_to_id_map = {}, {}, {}
    overlay_keys = set()
    # First, we'll get the base tree's default inputs
    items_tree = node.mContext.base_tree.interface.items_tree
    get_base_tree_overlay_values(items_tree, name_to_type_map, overlay_keys, root_overlay_values)
    get_overlay_keys_types_ids(my_interfaces, overlay_keys, name_to_type_map, name_to_id_map)
    # sort by reverse length so we find "CatsAndFrogs" before "Cats"
    overlay_keys = sorted(overlay_keys, key= lambda a :-1*len(a))
    # First I need to break it into substrings based on quotation marks
    from ..utilities.utilities import split_quoted_substrings_to_strings
    quoted_substrings = split_quoted_substrings_to_strings(value)
    overlay_tries = []
    for quoted_substring in quoted_substrings:
        overlay_tries.extend(quoted_substring.split("$"))
    if overlay_data_type == str: result = overlay_tries[0] # the 0th element is always before the split character
    else: result = 0# TODO HACK later use the parser feature
    # the reason for the difference between overlay_try and key is because
    #  we don't actually know if the $text part has a key in it yet!
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
        # this is where we can catch the errors if the type of the resolved value was wrong
        if type(overlay_resolved_value) != overlay_data_type:
            raise OverlayApplyError( f"Could not apply overlay variable to {node}::{socket_id}.")
        result += overlay_resolved_value
    node.parameters[socket_id] = result
    return result # because sometimes I need to get the result, too

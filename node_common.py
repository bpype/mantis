from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)
from .base_definitions import GraphError, NodeSocket, MantisNode
from collections.abc import Callable
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

# TODO: modify this to work with multi-input nodes
def trace_single_line(mantis_node, input_name, link_index=0):
    # DO: refactor this for new link class
    """Traces a line to its input."""
    nodes = [mantis_node]
    # Trace a single line
    if (socket := mantis_node.inputs.get(input_name) ):
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
def trace_single_line_up(mantis_node, output_name,):
    """I use this to get the xForm from a link node."""
    nodes = [mantis_node]
    if hasattr(mantis_node, "outputs"):
        # Trace a single line
        if (socket := mantis_node.outputs.get(output_name) ):
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

def trace_line_up_branching(mantis_node : MantisNode, output_name : str,
        break_condition : Callable = lambda mantis_node : False):
    """ Returns all leaf nodes at the ends of branching lines from an output."""
    leaf_nodes = []
    if hasattr(mantis_node, "outputs"):
        # Trace a single line
        if (socket := mantis_node.outputs.get(output_name) ):
            check_sockets={socket}
            while (check_sockets):
                # This is bad, but it's efficient for nodes that only expect
                #  one path along the given line
                socket = check_sockets.pop()
                for link in socket.links:
                    other = link.to_node.inputs.get(link.to_socket)
                    if (other):
                        socket = other
                        if break_condition(socket.node):
                            leaf_nodes.append(socket.node)
                        elif socket.is_input and socket.can_traverse:
                            check_sockets.add(socket.traverse_target)
                        else: # this is an input.
                            leaf_nodes.append(socket.node)
    return leaf_nodes

# this function exists to walk back to the first ancestor node of XFORM or LINK without
#  breaking the traverse behaviour which I still need for various reasons.
def get_parent_xForm_info(mantis_node, socket_name = 'Relationship'):
    from .mantis_dataclasses import xForm_info
    # we re-implement the trace logic here for performance.
    # because this kind of connection has traversal (for Links to find their children), we must
    # simply seek back to the first available xForm or Link and get its xForm info.\
    parent_node = None
    if (socket := mantis_node.inputs.get(socket_name) ):
        while (socket.is_linked):
            link = socket.links[0]
            if (socket := link.from_node.outputs.get(link.from_socket)):
                if socket.node.node_type in ['LINK', 'XFORM']:
                    parent_node = socket.node; break
                if socket.can_traverse:
                    socket = socket.traverse_target
                else: # this is an output.
                    break
            else:
                break
    parent_xForm_info = None
    if parent_node:
        if parent_node.node_type == 'XFORM':
            parent_xForm_info = parent_node.parameters['xForm Out']
        else:
            if 'Output Relationship' in parent_node.parameters.keys():
                parent_xForm_info = parent_node.parameters['Output Relationship']
            else: # TODO refactor Inherit Node to have the same output as the other link nodes.
                parent_xForm_info = parent_node.parameters['Inheritance']
    if parent_xForm_info is None: parent_xForm_info = xForm_info() # default to empty
    return parent_xForm_info

def setup_custom_property_inputs_outputs(mantis_node):
    from .utilities import get_ui_node
    if mantis_node.signature[0] == 'SCHEMA_AUTOGENERATED':
        from .base_definitions import custom_props_types
        if mantis_node.__class__.__name__ not in custom_props_types:
            # prRed(f"Reminder: figure out how to deal with custom property setting for Schema Node {mantis_node}")
            raise RuntimeError(wrapRed(f"Custom Properties not allowed for class {mantis_node.__class__.__name__}"))
        return
    else:
        ui_node = get_ui_node(mantis_node.signature, mantis_node.base_tree)
    if ui_node:
        setup_custom_props_from_np(mantis_node, ui_node)
    else:
        prRed("Failed to setup custom properties for: mantis_node")

def setup_custom_props_from_np(mantis_node, ui_node):
    for inp in ui_node.inputs:
        if inp.identifier == "__extend__": continue
        if not (inp.name in mantis_node.inputs.keys()) :
            socket = NodeSocket(is_input = True, name = inp.name, node = mantis_node,)
            mantis_node.inputs[inp.name] = socket
            mantis_node.parameters[inp.name] = None
            for attr_name in ["min", "max", "soft_min", "soft_max", "description"]:
                try:
                    setattr(socket, attr_name, getattr(inp, attr_name))
                except AttributeError:
                    pass
    for out in ui_node.outputs:
        if out.identifier == "__extend__": continue
        if not (out.name in mantis_node.outputs.keys()) :
            mantis_node.outputs[out.name] = NodeSocket(is_input = False, name = out.name, node = mantis_node,)
            
def prepare_parameters(mantis_node):
    # some nodes add new parameters at runtime, e.g. Drivers
    # so we need to take that stuff from the mantis_nodes that have
    #  been executed prior to this node.
    for s_name, sock in mantis_node.inputs.items():
        if not (sock.is_linked):
            continue
        if (sock.name  in sock.links[0].from_node.parameters.keys()):
            mantis_node.parameters[s_name] = sock.links[0].from_node.parameters[sock.name]
    # should work, this is ugly.

def check_for_driver(mantis_node, input_name, index = None):
    prop = mantis_node.evaluate_input(input_name)
    if (index is not None):
        prop = prop[index]
    return (prop.__class__.__name__ == 'MantisDriver')

# TODO: this should handle sub-properties better
def evaluate_sockets(mantis_node, b_object, props_sockets,):
    # this is neccesary because some things use dict properties for dynamic properties and setattr doesn't work
    def safe_setattr(ob, att_name, val):
        if ob.__class__.__name__ in ["NodesModifier"]:
            ob[att_name]=val
        elif b_object.__class__.__name__ in ["Key"]:
            if not val: val=0
            ob.key_blocks[att_name].value=val
        elif "]." in att_name:
            # it is of the form prop[int].prop2
            prop=att_name.split('[')[0]
            prop1=att_name.split('.')[1]
            index = int(att_name.split('[')[1][0])
            setattr(getattr(b_object, prop)[index], prop1, val)
        else:
            try:
                setattr(ob, att_name, val)
            except Exception as e:
                prRed(ob, att_name, val); raise e
    for prop, (sock, default) in props_sockets.items():
        # annoyingly, sometimes the socket is an array
        index = None
        if isinstance(sock, tuple):
            index = sock[1]; sock = sock[0]
        if (check_for_driver(mantis_node, sock, index)):
            sock = (sock, index)
            original_prop = prop
            # TODO: deduplicate this terrible hack
            if ("." in prop) and not b_object.__class__.__name__ in ["Key"]: # this is a property of a property...
                sub_props = [b_object]
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
                safe_setattr(b_object, prop, default)
            if mantis_node.node_type in ['LINK',]:
                printname  = wrapOrange(b_object.id_data.name)
            elif mantis_node.node_type in ['XFORM',]:
                printname  = wrapOrange(mantis_node.bGetObject().name)
            else:
                printname = wrapOrange(mantis_node)
            print("Adding driver %s to %s in %s" % (wrapPurple(original_prop), wrapWhite(mantis_node.signature[-1]), printname))
            if b_object.__class__.__name__ in ["NodesModifier"]:
                mantis_node.drivers[sock] = "[\""+original_prop+"\"]" # lol. It is a dict element not a "true" property
            elif b_object.__class__.__name__ in ["Key"]:
                mantis_node.drivers[sock] = "key_blocks[\""+original_prop+"\"].value"
            else:
                mantis_node.drivers[sock] = original_prop
        else: # here we can do error checking for the socket if needed
            if (index is not None):
                safe_setattr(b_object, prop, mantis_node.evaluate_input(sock)[index])
            else:                    # 'mute' is better than 'enabled'
                # UGLY HACK          # because it is available in older
                if (prop == 'mute'): # Blenders.
                    safe_setattr(b_object, prop, not bool(mantis_node.evaluate_input(sock)))
                elif (prop == 'hide'): # this will not cast it for me, annoying.
                    safe_setattr(b_object, prop, bool(mantis_node.evaluate_input(sock)))
                else:
                    try:
                        # prRed(b_object.name, mantis_node, prop, mantis_node.evaluate_input(sock) )
                        # print( mantis_node.evaluate_input(sock))
                    # value_eval = mantis_node.evaluate_input(sock)
                    # just wanna see if we are dealing with some collection
                    # check hasattr in case it is one of those ["such-and-such"] props, and ignore those
                        if hasattr(b_object, prop) and (not isinstance(getattr(b_object, prop), str)) and hasattr(getattr(b_object, prop), "__getitem__"):
                            # prGreen("Doing the thing")
                            for val_index, value in enumerate(mantis_node.evaluate_input(sock)):
                                # assume this will work, both because val should have the right number of elements, and because this should be the right data type.
                                from .drivers import MantisDriver
                                if isinstance(value, MantisDriver):
                                    getattr(b_object,prop)[val_index] =  default[val_index]
                                    print("Adding driver %s to %s in %s" % (wrapPurple(prop), wrapWhite(mantis_node.signature[-1]), mantis_node))
                                    try:
                                        mantis_node.drivers[sock].append((prop, val_index))
                                    except:
                                        mantis_node.drivers[sock] = [(prop, val_index)]
                                else:
                                    getattr(b_object,prop)[val_index] =  value
                        else:
                            # prOrange("Skipping the Thing", getattr(b_object, prop))
                            safe_setattr(b_object, prop, mantis_node.evaluate_input(sock))
                    except Exception as e:
                        prRed(b_object, mantis_node, prop, sock, mantis_node.evaluate_input(sock))
                        raise e

def finish_driver(mantis_node, b_object, driver_item, prop):
    # prWhite(mantis_node, prop)
    index = driver_item[1]; driver_sock = driver_item[0]
    driver_trace = trace_single_line(mantis_node, driver_sock)
    driver_provider, driver_socket = driver_trace[0][-1], driver_trace[1]
    if index is not None:
        driver = driver_provider.parameters[driver_socket.name][index].copy()
        # this is harmless and necessary for the weird ones where the property is a vector too
        driver["ind"] = index
    else:
        driver = driver_provider.parameters[driver_socket.name].copy()
    if driver:
        if ("." in prop) and mantis_node.__class__.__name__ != "DeformerMorphTargetDeform": # this is a property of a property...
            sub_props = [b_object]
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
        elif mantis_node.node_type in ['XFORM',] and mantis_node.__class__.__name__ in ['xFormBone']:
            # TODO: I really shouldn't have to hardcode this. Look into better solutions.
            if prop in ['hide', 'show_wire']: # we need to get the bone, not the pose bone.
                bone_col = mantis_node.bGetParentArmature().data.bones
            else:
                bone_col = mantis_node.bGetParentArmature().pose.bones
            driver["owner"] = bone_col[b_object] # we use "unsafe" brackets instead of get() because we want to see any errors that occur
        # HACK having special cases here is indicitave of a deeper problem that should be refactored
        elif mantis_node.__class__.__name__ in ['xFormCurvePin'] and \
                      prop in ['offset_factor', 'forward_axis', 'up_axis']:
                driver["owner"] = b_object.constraints['Curve Pin']
        else:
            driver["owner"] = b_object
        driver["prop"] = prop
        return driver
    else:
        prOrange("Provider", driver_provider)
        prGreen("socket", driver_socket)
        print (index)
        prPurple(driver_provider.parameters[driver_socket.name])
        prRed("Failed to create driver for %s" % prop)
        return None

def finish_drivers(mantis_node):
    drivers = []
    if not hasattr(mantis_node, "drivers"):
        return # HACK
    for driver_item, prop in mantis_node.drivers.items():
        b_objects = [mantis_node.bObject]
        if mantis_node.node_type == 'LINK':
            b_objects = mantis_node.bObject # this is already a list
        for b_object in b_objects:
            if isinstance(prop, list):
                for sub_item in prop:
                        drivers.append(finish_driver(mantis_node, b_object, (driver_item, sub_item[1]), sub_item[0]))
                else:
                    drivers.append(finish_driver(mantis_node, b_object, (driver_item, sub_item[1]), sub_item[0]))
            else:
                drivers.append(finish_driver(mantis_node, b_object, driver_item, prop))
    from .drivers import CreateDrivers
    CreateDrivers(drivers)

from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)
from ..base_definitions import GraphError, NodeSocket, MantisNode
from collections.abc import Callable
# BE VERY CAREFUL
# the x_containers files import * from this file
# so all the top-level imports are carried over

from bpy.app import version as bpy_version


# Utility to print links nicely for end user.
def print_link_list(links):
    ret_str = ""
    for link in links:
        ret_str+= link.__repr__() + '\n'
    return ret_str

# I've moved this to a separate function because the trace functions
# are kind of hard to understand and the cycle check breaks the flow
# of the code. 
def detect_cycle_in_trace(link, link_circle):
    if link.is_hierarchy:
        if link in link_circle:
            raise GraphError( "There is a cycle in the following links:\n" +
                                print_link_list(link_circle))
        link_circle.append(link)

# NOTE this is a dupe of trace_single_line, and it must be used
#      at any time before the tree is parsed (to check for cycles)
#      I don't want or need to pay the performance cost to check this everywhere
def trace_single_line_safe(mantis_node, input_name, link_index=0):
    # DO: refactor this for new link class
    """Traces a line to its input."""
    nodes = [mantis_node]
    # a test for cyclic connections
    link_circle = []
    # Trace a single line
    if (socket := mantis_node.inputs.get(input_name) ):
        while (socket.is_linked):
            link = socket.links[link_index]; link_index = 0
            # should throw an error if it is in the set
            if detect_cycle_in_trace(link, link_circle):
                return
            if (socket := link.from_node.outputs.get(link.from_socket)):
                nodes.append(socket.node)
                if socket.can_traverse:
                    socket = socket.traverse_target
                else: # this is an output.
                    break
            else:
                break
    return nodes, socket


def trace_single_line(mantis_node, input_name, link_index=0):
    # DO: refactor this for new link class
    """Traces a line to its input."""
    nodes = [mantis_node]
    # a test for cyclic connections
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


# For this, we basically just evaluate the driver once and use the result
def find_driven_default_value(mantis_node, socket_name):
    from ..misc_nodes import UtilityDriver, UtilitySwitch
    from .utilities import get_ui_node
    xf_inputs_values_var_names = []

    node_line, _last_socket = trace_single_line(mantis_node, socket_name)
    driver_node = None
    driver_type = 'SUM'
    keys = [ (0, 0), (1, 1) ]
    for driver_node in node_line:
        if driver_node.node_type == 'DRIVER': break
    else: # it's not being driven
        return mantis_node.evaluate_input(socket_name)
    
    if isinstance(driver_node, UtilityDriver):
        driver_type = driver_node.evaluate_input("Driver Type")
        # then get the variables
        for i, input in enumerate(driver_node.inputs):
            # unicode for 'a'
            var_name = chr(i - 2 + 96)
            if i == 0 : continue # the Driver Type doesn't interest us
            elif i ==1 : continue # for now. we do need the fCurve
            else:
                if not input.is_linked: continue # nothing to do here
            var_node    = input.links[0].from_node
            # NOTE: this var_node will not be prepared on time unless we sort the graph by depth
            #       and it doesn't seem to be possible to do that without breaking drivers... so
            # HACK it's safe to do this, but VERY ugly and bad.
            if not var_node.prepared:
                var_node.bPrepare()
            # end HACK
            var_data    = var_node.parameters["Driver Variable"]
            var_type    = var_data['type']
            var_channel = var_data['channel']
            prop_name = None; value = None 
            xf1 = var_node.GetxForm(index=1)
            match var_type:
                case "SINGLE_PROP":
                    prop_name = var_node.evaluate_input("Property")
                    # we'll get the property value in the next step
                case "TRANSFORMS":
                    matrix1 = xf1.evaluate_input['Matrix']
                    # Mantis ensures that these are identity at creation time
                    if "LOC" in var_channel or "ROT" in var_channel:
                            value = 0
                    else: # Scale, defaults to 1
                            value = 1
                case "ROTATION_DIFF":
                    xf2 = var_node.GetxForm(index=2)
                    matrix1 = xf1.evaluate_input['Matrix']
                    matrix2 = xf2.evaluate_input['Matrix']
                    value = matrix1.to_quaternion().rotation_difference(matrix2.to_quaternion()).angle
                case "LOC_DIFF":
                    xf2 = var_node.GetxForm(index=2)
                    matrix1 = xf1.evaluate_input['Matrix']
                    matrix2 = xf2.evaluate_input['Matrix']
                    value = (matrix1.to_translation() - matrix2.to_translation()).length
                case "CONTEXT_PROP":
                    raise NotImplementedError("Mantis Does not yet support Context Property")
                    pass
            xf_inputs_values_var_names.append((xf1, prop_name, value, var_name))

        # Now we'll get the keyframe points and sort them, too!
        if driver_node.inputs['fCurve'].is_linked:
            fCurve_node = driver_node.inputs['fCurve'].links[0].from_node
        extrapolation_mode = 'CONSTANT'
        keys = []
        if fCurve_node:
            extrapolation_mode = fCurve_node.evaluate_input("Extrapolation Mode")
            for l in fCurve_node.inputs['Keyframes'].links:
                key_node = l.from_node
                if key_node:
                    keys.append( (key_node.evaluate_input("Frame"),  key_node.evaluate_input("Value")) )
        keys = sorted( keys, key = lambda a : a[0]) # sort by the frame

    elif isinstance(driver_node, UtilitySwitch):
        # Reimplementing the GetxForm from the switch here
        # because it is faster to inline this and store the trace result
        trace = trace_single_line(driver_node, "Parameter" )
        for node in trace[0]:
            if node.node_type == 'XFORM':
                xf = node                    # reuse trace HERE
                prop_name = trace[1].name    # saves us from tracing again.
                xf_inputs_values_var_names.append(( xf, prop_name, None, "a")); break
        else:
            raise RuntimeError(f"ERROR: Cannot Set the default of the driven value {socket_name} \n"
                                f"in node {mantis_node}")
    # We're gonna assume the xForm is sorting these right
    # but we'll check the name if it is cheap
    default_values = {}
    for xf, prop_name, value, var_name in xf_inputs_values_var_names:
        i=0
        for output in xf.outputs:
            if 'xForm Out' == output.name: continue
            if output.name == prop_name: break
            i+=1
        node_line, _last_socket = trace_single_line(xf, "Custom Properties", i)
        custom_prop_node = node_line[-1]
        if value:
            default_values[var_name] = value; continue
        if prop_name:
            if custom_prop_node.evaluate_input("Name") == prop_name:
                custom_prop_type = custom_prop_node.evaluate_input("Type")
                default_prop_name = ""
                match custom_prop_type:
                    case "BOOL":
                        default_prop_name = 'Default (Bool)'
                    case "FLOAT":
                        default_prop_name = 'Default (Float)'
                    case "INT":
                        default_prop_name = 'Default (Int)'
                    case _:
                        raise RuntimeError(f"ERROR: Cannot Set the default of the driven value {socket_name} \n"
                                           f"in node {mantis_node}"
                                           f"Reason: Custom Property {prop_name} is not a valid type." )
                default_values[var_name] = float(custom_prop_node.evaluate_input(default_prop_name))
            else:
                raise RuntimeError(f"ERROR: failed to get proeprty {prop_name} for node {xf}, \n"
                                   f"cannot Set the default of the driven value {socket_name} \n"
                                   f"in node {mantis_node}"
                                    "Reason: Cannot Find Custom Property Node")
    frame = 0.0
    if default_values:
        match driver_type:
            case "AVERAGE":
                frame = sum(default_values.values())/len(default_values)
            case "SUM":
                frame = sum(default_values.values())
            case "MIN":
                frame = min(default_values.values())
            case "MAX":
                frame = max(default_values.values())
            case "SCRIPTED":
                raise NotImplementedError (f"ERROR: Cannot Set the default of the driven value {socket_name} \n"
                                        f"in node {mantis_node} \n"
                                            "Reason: Driver Expressions are not yet implemented.")
    # Now we apply the fCurve
    # For now, We'll assume LINEAR keys TODO: come back to this during Pose update!
    if len(keys) >= 2:
        previous_frame = None
        next_frame = None
        previous_value = None
        next_value = None
        for key in keys:
            if key[0] <= frame: previous_frame, previous_value = key
            if key[0] >= frame: next_frame, next_value = key
            if previous_frame is not None and next_frame is not None: break
        else: # if our frame is out-of-bounds we need a slope to extrapolate on.
            if previous_frame and not next_frame:
                next_frame, next_value = previous_frame, previous_value
                if extrapolation_mode == 'LINEAR':
                    previous_frame, previous_value = keys[-2] # we need the second last key to extrapolate
            elif next_frame and not previous_frame:
                previous_frame, previous_value = next_frame, next_value
                if extrapolation_mode == 'LINEAR':
                    next_frame, next_value = keys[1] # we need the second key to extrapolate
            else:   
                raise RuntimeError (f"ERROR: Cannot Set the default of the driven value {socket_name} \n"
                                    f"in node {mantis_node} \n"
                                    "Reason: Cannot place value on driver fCurve.")
        if previous_frame == next_frame: # the frame is exactly on a key
            return previous_value
        # this is just a simple lerp because we are assuming the keys are linear for now
        result = previous_value + ((frame - previous_frame) / (next_frame - previous_frame)) * (next_value - previous_value)
    elif len(keys) ==1:
        result = key[1] # flat curve, take the value of the only key
    else:
        raise RuntimeError (f"ERROR: Cannot Set the default of the driven value {socket_name} \n"
                            f"in node {mantis_node} \n"
                             "Reason: Invalid fCurve has 0 keyframes")
    return result
        
# this function exists to walk back to the first ancestor node of XFORM or LINK without
#  breaking the traverse behaviour which I still need for various reasons.
def get_parent_xForm_info(mantis_node, socket_name = 'Relationship'):
    from ..mantis_dataclasses import xForm_info
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
        from ..base_definitions import custom_props_types
        if mantis_node.__class__.__name__ not in custom_props_types:
            raise RuntimeError(wrapRed(f"Custom Properties not allowed for class {mantis_node.__class__.__name__}"))
        return
    else:
        ui_node = get_ui_node(mantis_node.ui_signature, mantis_node.base_tree)
    if ui_node:
        setup_custom_props_from_np(mantis_node, ui_node)
    else:
        prRed(f"Failed to setup custom properties for: {mantis_node.ui_signature}")

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

def check_for_driver(mantis_node, input_name, value_index = None, array_index = 0):
    prop = mantis_node.evaluate_input(input_name, array_index)
    if (value_index is not None):
        try:
            prop = prop[value_index]
        except KeyError: # We'll try to use the driver for all three channels.
            pass
        # TODO an Index or Key error here should have a reasonable error message
    return (prop.__class__.__name__ == 'MantisDriver')

# this is neccesary because some things use dict properties for dynamic properties and setattr doesn't work
def safe_setattr(ob, att_name, val):
    ob_class_name = ob.__class__.__name__
    match ob_class_name:
        case "NodesModifier":
            ob[att_name]=val
        case "Key":
            ob.key_blocks[att_name].value=val
        case _:
            setattr(ob, att_name, val)

# do: make this function end in a single setattr
def evaluate_sockets(mantis_node, b_objects, props_sockets,):
    # TODO: I think it is wasteful to run this once per b_object for e.g. Link nodes.
    #       Should be able to get the results once and pass 'em along. Probably only saves
    #       a handful of fn calls in a big graph. Not worth doing a big refactor right now
    # Because Mantis Nodes are sometimes a composition of different Blender objects,
    # We have to set properties on different Blender Objects and the easiest way
    # is to send the object in directly instead of trying to find e.g. nested properties
    for property_group, b_object in b_objects.items():
        ob_class_name = b_object.__class__.__name__
        for filler_item in props_sockets.values():
            filler_property_group = filler_item.property_group or "DEFAULT"
            prop = filler_item.property_name
            if filler_property_group != property_group: continue
            if b_object is None: continue

            input_name = filler_item.socket_name
            default = ( filler_item.default_value, )
            value_index = filler_item.value_index
            array_index = filler_item.array_index
            combo = filler_item.combo_property
            vector = filler_item.vector_property

            # Check for a driver -- this is inlined from check_for_driver()
            evaluated_value = mantis_node.evaluate_input(input_name, array_index)
            driver = evaluated_value
            drivers_exist = (evaluated_value.__class__.__name__ == 'MantisDriver', )
            single_driver_input = drivers_exist[0]

            if combo and vector: # we map an element of the socket's vector to a single scalar property
                evaluated_value = evaluated_value[value_index]
                drivers_exist = (evaluated_value.__class__.__name__ == 'MantisDriver', )
            if vector and not combo: # then we map a vector to a vector and have to check for drivers per-element
                default = filler_item.default_value
                # the evaluated value could either be a vector of scalar values (or scalar drivers) OR one driver
                if single_driver_input: # we have alredy checked for single-driver, so this is a vector otherwise
                    drivers_exist = tuple( True for _unused in range(len(default)) )
                else:
                    drivers_exist = tuple( val.__class__.__name__ == 'MantisDriver' for val in evaluated_value )
            assign_this_value = evaluated_value # Usually we just assign the value right away
            if single_driver_input and vector: # in this pernicious case, we need to lift
                assign_this_value = list(default) # the evaluated value from scalar to vector
            # We had to pack everything into this weird iterable format so we can handle
            # all 4 cases, (scalar, vector, scalar combo, vector combo) in one place
            # this isn't perfectly optimal but I expect it to cost a few milliseconds at most
            # and while it is kind of confusing it is nice to keep all this in one code path
            if any(drivers_exist):
                if vector and not combo and isinstance(assign_this_value, tuple):
                    assign_this_value = list(assign_this_value) # because we have to mutate it
                for i, (default_value, driver_exists) in enumerate(zip(default, drivers_exist)):
                    if driver_exists: # we need to pack data for the driver
                        if filler_item.is_animatable == False:
                            raise RuntimeError(f"Driver is not allowed for input \"{input_name}\" in node \"{mantis_node}\".")
                        # NOTE at this point we can inject the driver's default resulting value
                        #      and we have to do so in Curve Pin where it has a special case
                        #      In the future I may implement this HERE in general
                        printname = wrapOrange(mantis_node)

                        if vector and not combo: assign_this_value[i] = default_value
                        else: assign_this_value = default_value

                        if mantis_node.node_type == 'LINK': printname  = wrapOrange(b_object.id_data.name)
                        elif mantis_node.node_type == 'XFORM': printname  = wrapOrange(mantis_node.bGetObject().name)
                        print(f"Adding driver to property: {wrapPurple(prop)} in {printname} in node: {wrapWhite(mantis_node.ui_signature[1:])}")
                        # NOW we can set up the driver.
                        # TODO: Maybe can prefill this in the socket template or cache the result per-socket
                        driver_properties = {} # use this dict to pack this data without mutating the driver itself
                        driver_properties["path_from_id"] = b_object.path_from_id(prop,)
                        driver_properties['owner'] = b_object # it is the CALLER's responsibility to send the right object!!
                        # we need a special case here for Bones :/
                        # TODO: refactor so I don't need this
                        if mantis_node.__class__.__name__ == 'xFormBone':
                            from ..xForm_socket_templates import attributes_shared_by_bone_and_pose_bone
                            if prop in attributes_shared_by_bone_and_pose_bone:
                                driver_properties['owner'] = b_objects['pose_bone']
                                driver_properties["path_from_id"] = b_objects['pose_bone'].path_from_id(prop,)
                        if (vector and not combo):
                            driver_properties['ind'] = i
                        if vector and single_driver_input:
                            driver_properties['ind'] = -1 # the driver will be added to all 3 channels
                        # TODO: I would like the socket filler to handle the special cases here.
                        #       even if it means I have to pack another operator in the filler.
                        resolved_prop_name = prop
                        match ob_class_name:
                            case "NodesModifier": # It is a dict element.
                                resolved_prop_name = "[\""+prop+"\"]"
                            case "Key": # that is, the outer data block that owns shape keys, not a key-frame.
                                resolved_prop_name = "key_blocks[\""+prop+"\"].value"
                        driver_properties["prop"] = resolved_prop_name
                        driver_index = value_index if vector and not single_driver_input else None
                        if driver_index: driver = driver[driver_index]
                        mantis_node.drivers.append( (driver, driver_properties) )

            # We wait until now to skip this because it is important to do the
            #   is_animatable check above and give the user a meaningful error
            if prop is None: continue
            # Some socket values need to be transformed, so we can use the operator to do that.
            if filler_item.property_value_operator:
                assign_this_value = filler_item.property_value_operator(mantis_node, evaluated_value)
            # at this point there is ONE filler per property and we just have to assign the value
            if ob_class_name not in {'NodesModifier', 'Key'}:
                setattr(b_object, prop, assign_this_value)
            elif ob_class_name == "NodesModifier":
                b_object[prop] = assign_this_value
            else: # ob_class_name == "Key":
                b_object.key_blocks[prop].value = assign_this_value

def finish_drivers(mantis_node):
    drivers = []
    for driver, driver_properties in mantis_node.drivers:
        drivers_from_socket = (driver,)
        if isinstance(driver, (tuple, list)):
            drivers_from_socket = driver # this is a collection e.g. from a Vector Combine
        for driver in drivers_from_socket:
            driver_copy = driver.copy() # it is safe to copy it here because it is guarenteed to be filled out.
            driver_copy.update(driver_properties)
            drivers.append(driver_copy)
    from .drivers import CreateDrivers
    CreateDrivers(drivers)
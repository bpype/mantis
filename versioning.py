#Versioning Tasks
# this will be the new versioning system, and will deprecate the old SOCKETS_ADDED and such

from bpy.types import Node, NodeSocket
from bpy.app import version as bpy_version

from .utilities.utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,
                              get_socket_maps, do_relink, )


# CHECKLIST FOR DUMMIES:
# Did you make sure to turn off and re-enable tree updates?
# Did you restore connections to the node socket after changing things?
# Did you test FUNCTIONALITY in your test rigs instead of just checking if the tree
#    would generate? CHANGED FUNCTIONALITY IS STILL A BUG!!
# Did you make sure to toggle the is_updating flag for ANY node that is touched by
#    the edits you are doing to the current node (example: removing a socket causes
#    linked group and schema nodes to update)
# (add more whenever a weird or difficult to debug problem occurs)
# Did you check the update script on a tree that doesn't need it?

def version_upgrade_very_old(*args, **kwargs):
    node = kwargs['node']
    current_major_version = node.id_data.mantis_version[0]
    current_minor_version = node.id_data.mantis_version[1]
    if  current_major_version > 0: return# major version must be 0
    if current_minor_version > 11: return# minor version must be 12 or less

    # this is the old node update, very inneficient and strange and badly organized
    NODES_REMOVED=["xFormRootNode"]
                    # Node bl_idname, # Socket Name
    SOCKETS_REMOVED=[("UtilityDriverVariable", "Transform Channel"),
                    ("xFormRootNode","World Out"),
                    ("UtilitySwitch","xForm"),
                    ("LinkDrivenParameter", "Enable")]
                    # Node Class           #Prior bl_idname  # prior name # new bl_idname #       new name,          # Multi
    SOCKETS_RENAMED=[ ("LinkDrivenParameter", "DriverSocket",   "Driver",     "FloatSocket",        "Value",              False),
                    ("DeformerHook",        "IntSocket",      "Index",      "UnsignedIntSocket",  "Point Index",        False),
                    ("SchemaConstOutput",   "IntSocket",      "Expose when N==",      "UnsignedIntSocket",  "Expose at Index", False),]

                    # NODE CLASS NAME             IN_OUT    SOCKET TYPE     SOCKET NAME     INDEX   MULTI     DEFAULT
    SOCKETS_ADDED=[("DeformerMorphTargetDeform", 'INPUT', 'BooleanSocket', "Use Shape Key", 1,      False,    False),
                ("DeformerMorphTargetDeform", 'INPUT', 'BooleanSocket', "Use Offset",    2,      False,    True),
                ("UtilityFCurve",             'INPUT',  "eFCrvExtrapolationMode", "Extrapolation Mode", 0, False, 'CONSTANT'),
                ("LinkCopyScale",             'INPUT',  "BooleanSocket", "Additive",     3,      False,    False),
                ("DeformerHook",              'INPUT',  "FloatFactorSocket", "Influence",3,      False,    1.0),
                ("DeformerHook",              'INPUT',  "UnsignedIntSocket", "Spline Index", 2,  False,    0),
                ("DeformerHook",              'INPUT',  "BooleanSocket", "Auto-Bezier",  5,      False,    True),
                ("UtilityCompare",            'INPUT',  "EnumCompareOperation", "Comparison", 0, False,    'EQUAL'),
                ("UtilityMatrixFromCurve",    'INPUT',  "UnsignedIntSocket", "Spline Index",  1, False,    0),
                ("UtilityMatricesFromCurve",  'INPUT',  "UnsignedIntSocket", "Spline Index",  1, False,    0),
                ("UtilityPointFromCurve",     'INPUT',  "UnsignedIntSocket", "Spline Index",  1, False,    0),
                ("LinkCopyScale",             'INPUT',  "FloatFactorSocket", "Power",    5,      False,    1.0),
                ]

    rename_jobs = []
    node_tree = kwargs['node_tree']
    try:
        if node.bl_idname in NODES_REMOVED:
            print(f"INFO: removing node {node.name} of type {node.bl_idname} because it has been deprecated.")
            node.inputs.remove(socket)
            return
        for i, socket in enumerate(node.inputs.values()):
            if (node.bl_idname, socket.identifier) in SOCKETS_REMOVED:
                print(f"INFO: removing socket {socket.identifier} of node {node.name} of type {node.bl_idname} because it has been deprecated.")
                node.inputs.remove(socket)
            for old_class, old_bl_idname, old_name, new_bl_idname, new_name, multi in SOCKETS_RENAMED:
                if (node.bl_idname == old_class and socket.bl_idname == old_bl_idname and socket.name == old_name):
                    rename_jobs.append((socket, i, new_bl_idname, new_name, multi))
        for i, socket in enumerate(node.outputs.values()):
            if (node.bl_idname, socket.identifier) in SOCKETS_REMOVED:
                print(f"INFO: removing socket {socket.identifier} of node {node.name} of type {node.bl_idname} because it has been deprecated.")
                node.outputs.remove(socket)
            for old_class, old_bl_idname, old_name, new_bl_idname, new_name, multi in SOCKETS_RENAMED:
                if (node.bl_idname == old_class and socket.bl_idname == old_bl_idname and socket.name == old_name):
                    rename_jobs.append((socket, i, new_bl_idname, new_name, multi))

        for bl_idname, in_out, socket_type, socket_name, index, use_multi_input, default_val in SOCKETS_ADDED:
            if node.bl_idname != bl_idname:
                continue
            if in_out == 'INPUT' and node.inputs.get(socket_name) is None:
                print(f"INFO: adding socket \"{socket_name}\" of type {socket_type} to node {node.name} of type {node.bl_idname}.")
                s = node.inputs.new(socket_type, socket_name, use_multi_input=use_multi_input)
                try:
                    s.default_value = default_val
                except AttributeError:
                    pass # the socket is read-only
                node.inputs.move(len(node.inputs)-1, index)
        socket_map = None
        if rename_jobs:
            socket_maps = get_socket_maps(node)
        for socket, socket_index, new_bl_idname, new_name, multi in rename_jobs:
            old_id = socket.identifier
            print (f"Renaming socket {socket.identifier} to {new_name} in node {node.name}")
            if socket.is_output:
                index = 1
                in_out = "OUTPUT"
                node.outputs.remove(socket)
                s = node.outputs.new(new_bl_idname, new_name, identifier=new_name, use_multi_input=multi)
                node.outputs.move(len(node.outputs)-1, socket_index)
                socket_map = socket_maps[1]
            else:
                index = 0
                in_out = "INPUT"
                node.inputs.remove(socket)
                s = node.inputs.new(new_bl_idname, new_name, identifier=new_name, use_multi_input=multi)
                node.inputs.move(len(node.inputs)-1, socket_index)
                socket_map = socket_maps[0]
            socket_map[new_name] = socket_map[old_id]
            if new_name != old_id: del socket_map[old_id] # sometimes rename just changes the socket type or multi
            do_relink(node, s, socket_map)
    except Exception as e:
        prRed(f"Error updating version in node: {node.id_data.name}::{node.name}; see error:")
        print(e)

def version_upgrade_bone_0_12_0_from_older(*args, **kwargs):
    # we need to check if it has an array collection input and a color input
    # then we need to solve each task
    node = kwargs['node']
    live_updates = node.id_data.do_live_update
    node.id_data.do_live_update = False

    current_major_version = node.id_data.mantis_version[0]
    current_minor_version = node.id_data.mantis_version[1]
    if  current_major_version > 0: # major version must be 0
        return
    if current_minor_version >= 12: # minor version must be 11 or less
        return
    # sub version doesn't matter since any subversion of 11 should trigger this task
    collection_input_is_array = False
    try:
        collection_input_is_array = node.inputs['Bone Collection'].is_multi_input
    except KeyError: # I suppose this happens in very, very old trees
        pass         # but it is extremely unlikely
    toggle_updating = []
    was_updating = {}
    try:
        if not collection_input_is_array: # it must be made into an array!
            prPurple(f"Updating \"Bone Collection\" Socket in {node.name}")
            from .utilities.utilities import get_socket_maps
            socket_maps = get_socket_maps(node)
            socket_map = socket_maps[0]
            for i, socket in enumerate(node.inputs):
                if socket.name == 'Bone Collection': break
            # Always guard socket removal in case of connection to e.g. schema
            for socket_name, links in socket_map.items():
                if isinstance(links, list):
                    for link in links:
                        if hasattr(link, 'node') and hasattr(link.node, 'is_updating'):
                            toggle_updating.append(link.node)
                            was_updating[link.node.name] = link.node.is_updating
                            link.node.is_updating = True
            node.inputs.remove(socket)
            s = node.inputs.new('BoneCollectionSocket', 'Bone Collection',
                                identifier='Bone Collection', use_multi_input=True)
            node.inputs.move(len(node.inputs)-1, i)
            do_relink(node, s, socket_map, in_out='INPUT')
        if node.inputs.get('Color') is None:
            prPurple(f"Adding \"Color\" Socket to {node.name}")
            s = node.inputs.new('ColorSetSocket', 'Color',)
            node.inputs.move(len(node.inputs)-1, 22)
    except Exception as e:
        prRed(f"Error updating version in node: {node.id_data.name}::{node.name}; see error:")
        print(e)
    finally:
        # Now we have to clean up by removing the unneeded sockets and repositioning.
        for other_node in toggle_updating:
            other_node.is_updating = was_updating[other_node.name]
        node.id_data.do_live_update = live_updates

def up_0_12_1_add_inherit_color(*args, **kwargs):
    # add an inherit color input.
    node = kwargs['node']
    current_major_version = node.id_data.mantis_version[0]
    current_minor_version = node.id_data.mantis_version[1]
    current_sub_version = node.id_data.mantis_version[2]
    if  current_major_version > 0: return# major version must be 0
    if current_minor_version > 12: return# minor version must be 12 or less
    if current_minor_version == 12 and current_sub_version > 9: return # sub version must be 8 or less
    # I am having it do 8 or less because there was a bug in this function prior to 9
    # sub version doesn't matter since any subversion of 11 should trigger this task
    prPurple(f"Adding \"Inherit Color\" socket to {node.name}")
    try:
        inh_color = node.inputs.get('Inherit Color')
        if inh_color and inh_color.bl_idname != 'BooleanSocket':
            node.inputs.remove(inh_color)
            inh_color = None
        if inh_color is None:
            s = node.inputs.new('BooleanSocket', 'Inherit Color',)
            node.inputs.move(len(node.inputs)-1, 23)
            s.default_value=True
    except Exception as e:
        prRed(f"Error updating version in node: {node.id_data.name}::{node.name}; see error:")
        print(e)

def up_0_12_13_add_widget_scale(*args, **kwargs):
    node = kwargs['node']
    current_major_version = node.id_data.mantis_version[0]
    current_minor_version = node.id_data.mantis_version[1]
    current_sub_version = node.id_data.mantis_version[2]
    if  current_major_version > 0: return# major version must be 0
    if current_minor_version > 12: return# minor version must be 12 or less
    if current_minor_version == 12 and current_sub_version > 12: return
    # sub version must be 12 or less
    prPurple(f"Adding \"Scale\" socket to {node.name}")
    try:
        scale = node.inputs.get('Scale')
        if scale is None:
            s = node.inputs.new('VectorScaleSocket', 'Scale',)
            s.default_value=[1.0,1.0,1.0]
            node.inputs.move(len(node.inputs)-1, 1)
    except Exception as e:
        prRed(f"Error updating version in node: {node.id_data.name}::{node.name}; see error:")
        print(e)

def up_0_12_25_replace_floor_offset_type(*args, **kwargs):
    node = kwargs['node']
    current_major_version = node.id_data.mantis_version[0]
    current_minor_version = node.id_data.mantis_version[1]
    current_sub_version = node.id_data.mantis_version[2]
    if  current_major_version > 0: return# major version must be 0
    if current_minor_version > 12: return# minor version must be 12 or less
    if current_minor_version == 12 and current_sub_version > 24: return 
    socket_maps = get_socket_maps(node)
    prPurple(f"Fixing \"Offset\" socket in {node.name}")
    try:
        offset = node.inputs["Offset"]
        node.inputs.remove(offset)
        s = node.inputs.new('FloatSocket', 'Offset',)
        node.inputs.move(len(node.inputs)-1, 2)
        do_relink(node, s, socket_maps[0])
    except Exception as e:
        prRed(f"Error updating version in node: {node.id_data.name}::{node.name}; see error:")
        print(e)

def get_absolute_location(node): # using this for version compatibility
    location = node.location.copy() # FUTURE: deprecate old blenders and use absolute_location
    while(node.parent):
        node = node.parent
        location+= node.location
    return location

def up_0_13_0_new_custom_prop_node(*args, **kwargs):
    tree, node = kwargs['node_tree'], kwargs['node']
    current_major_version = tree.mantis_version[0]
    if  current_major_version > 0: return# major version must be 0
    current_minor_version = tree.mantis_version[1]
    if current_minor_version >= 13: return# minor version must be 12 or less
    remove_me, prop_nodes = [], []
    from .xForm_nodes_ui import xFormBoneNode
    socket_map_in, socket_map_out = get_socket_maps(node)
    if isinstance(node, xFormBoneNode):
        for custom_input in reversed(list(node.inputs)):
            if 'Parameter' not in custom_input.bl_idname:
                continue
            custom_prop_node = tree.nodes.new('UtilityCustomProperty')
            prop_type = None
            if custom_input.bl_idname == 'ParameterBoolSocket':
                prop_type = 'BOOL'
                custom_prop_node.inputs['Default (Bool)'].default_value = getattr(custom_input, "default_value")
            elif custom_input.bl_idname == 'ParameterIntSocket':
                prop_type = 'INT'
                custom_prop_node.inputs['Default (Int)'].default_value = int( getattr(custom_input, "default_value") )
                custom_prop_node.inputs['Min (Int)'].default_value = int( getattr(custom_input, "min") )
                custom_prop_node.inputs['Max (Int)'].default_value = int( getattr(custom_input, "max") )
                custom_prop_node.inputs['Soft Min (Int)'].default_value = int( getattr(custom_input, "soft_min") )
                custom_prop_node.inputs['Soft Max (Int)'].default_value = int( getattr(custom_input, "soft_max") )
            elif custom_input.bl_idname == 'ParameterFloatSocket':
                prop_type = 'FLOAT'
                custom_prop_node.inputs['Default (Float)'].default_value = getattr(custom_input, "default_value")
                custom_prop_node.inputs['Min (Float)'].default_value = getattr(custom_input, "min")
                custom_prop_node.inputs['Max (Float)'].default_value = getattr(custom_input, "max")
                custom_prop_node.inputs['Soft Min (Float)'].default_value = getattr(custom_input, "soft_min")
                custom_prop_node.inputs['Soft Max (Float)'].default_value = getattr(custom_input, "soft_max")
            elif custom_input.bl_idname == 'ParameterVectorSocket':
                prop_type = 'VECTOR'
                custom_prop_node.inputs['Default (Vector)'].default_value = getattr(custom_input, "default_value")
                try:
                    custom_prop_node.inputs['Min (Float)'].default_value = getattr(custom_input, "min")
                    custom_prop_node.inputs['Max (Float)'].default_value = getattr(custom_input, "max")
                    custom_prop_node.inputs['Soft Min (Float)'].default_value = getattr(custom_input, "soft_min")
                    custom_prop_node.inputs['Soft Max (Float)'].default_value = getattr(custom_input, "soft_max")
                except AttributeError: # I don't know if I just never implemented these or if it is version specific
                    pass # anyways this isn't critical and should not trigger even a warning
            elif custom_input.bl_idname == 'ParameterStringSocket':
                prop_type = 'STRING'
                custom_prop_node.inputs['Default (String)'].default_value = getattr(custom_input, "default_value")
            custom_prop_node.inputs['Name'].default_value = custom_input.name
            custom_prop_node.inputs['Type'].default_value = prop_type
            prop_nodes.append(custom_prop_node)
            remove_me.append(custom_input)
            # now we need to relink things, because the custom property socket could have had an
            # input supplying the default value
            relink_value = socket_map_in.get(custom_input.identifier, None)
            if isinstance(relink_value, list): # this indicates it is a list of links
                # CRITICALLY, we need to force display update before doing this.
                custom_prop_node.display_update({}, None) # parsed_tree and context, not needed
                input_socket = None
                match prop_type:
                    case 'BOOL':
                        input_socket = "Default (Bool)"
                    case 'INT':
                        input_socket = "Default (Int)"
                    case 'FLOAT':
                        input_socket = "Default (Float)"
                    case 'VECTOR':
                        input_socket = "Default (Vector)"
                    case 'STRING':
                        input_socket = "Default (String)"
                    case _: # Should never never happen
                        raise RuntimeError("Unexpected Code Path Reached, this is a bug.")
                do_relink(custom_prop_node, custom_prop_node.inputs[input_socket],
                          {input_socket:relink_value})
        while remove_me:
            custom_input = remove_me.pop()
            node.inputs.remove(custom_input)
        new_input = node.inputs.new("CustomPropSocket", "Custom Properties", use_multi_input=True)
        from mathutils import Vector
        for i, prop_node in enumerate(prop_nodes):
            tree.links.new(input=prop_node.outputs[0], output=new_input)
            prop_node.location = get_absolute_location(node)
            prop_node.location = prop_node.location - Vector((180, -260*i))
            prop_node.select = False # it is annoying to select them all by default
    else: # just need to add the socket.
        new_input = node.inputs.new("CustomPropSocket", "Custom Properties", use_multi_input=True)

def schema_enable_custom_interface_types(*args, **kwargs):
    tree = kwargs['tree']
    current_major_version = tree.mantis_version[0]
    current_minor_version = tree.mantis_version[1]
    current_sub_version = tree.mantis_version[2]
    if  current_major_version > 0: return# major version must be 0
    if current_minor_version >= 13: return# minor version must be 12 or less
    # we need to set the new interface values on the schema interface stuff
    prGreen(f"Updating Schema tree {tree.name} to support new, improved UI!")
    tree.do_live_update = False
    for n in tree.nodes:
        if hasattr(n, "is_updating"):
            n.is_updating = True
    try:
        for item in tree.interface.items_tree:
            if item.item_type == 'PANEL':
                continue
            parent_name = 'Constant'
            if item.parent:
                parent_name=item.parent.name
            if hasattr(item, "is_array"):
                # if is_array exists we're in the custom interface class
                # so we'll assume the other attributes exist
                if parent_name == 'Array':
                    item.is_array = True
                if parent_name == 'Connection':
                    item.is_array = False
                    item.is_connection=True
                    item.connected_to=item.name
                    # since heretofore it has been a requirement that the names match
    except Exception as e:
        prRed(f"Error updating version in tree: {tree.name}; see error:")
        print(e)
    finally:
        for n in tree.nodes:
            if hasattr(n, "is_updating"):
                n.is_updating = False
        tree.do_live_update = True

def update_fcurve_and_armature_node_to_multi_socket(*args, **kwargs):
    from .base_definitions import SchemaUINode
    node = kwargs['node']
    live_updates = node.id_data.do_live_update
    node.id_data.do_live_update = False
    # First we have to get the socket maps and re-init the sockets
    convert_keys = {'UtilityFCurve' : [ 'Keyframe', ],
                    'LinkArmature'  : [ 'Target', 'Weight', ], }
    my_convert_keys = convert_keys[node.bl_idname]
    sockets_in, _sockets_out = get_socket_maps(node,)
    # NOTE IMPORTANT BUG INFO
    # I was using node.inputs.clear() here before unguarded...
    # this caused connected Schema nodes to update and mutate the socket map
    # which, in turn, connected the new socket to the wildcard and extended the schema
    # resulting in trees that fail to run. This was particularly bad because it was
    # so hard to debug (due to spooky action at a distance mutation)
    # So we have to mark the connected nodes as "updating" before we modify the tree.
    # TODO: should I just mark all nodes as updating during versioning?
    toggle_updating = []
    was_updating = {}
    for socket_name, links in sockets_in.items():
        if isinstance(links, list):
            for link in links:
                if hasattr(link, 'node') and hasattr(link.node, 'is_updating'):
                    toggle_updating.append(link.node)
                    was_updating[link.node.name] = link.node.is_updating
                    link.node.is_updating = True
    node.inputs.clear() # this is VERY DANGEROUS without the above
    add_me_sockets = [st for st in node.socket_templates if st.is_input == True]
    node.init_sockets(add_me_sockets)
    try:
        new_sockets_in = {}
        for convert_key in my_convert_keys:
            for socket_name, links in sockets_in.items():
                if links is None: continue
                if convert_key+'.' in socket_name:
                    if new_sockets_in.get(convert_key+'s'):
                                                    # has to be in this order to come back alright.
                                                    # assuming, that is, that the keys are sorted. they should be.
                        new_sockets_in[convert_key+'s'] = sockets_in[socket_name] + new_sockets_in[convert_key+'s']
                    else:
                        new_sockets_in[convert_key+'s'] = sockets_in[socket_name]
            if new_sockets_in:
                do_relink(node, node.inputs[convert_key+'s'], new_sockets_in, in_out="INPUT",)
        for socket_name, links in sockets_in.items():
            proceed = True
            for convert_key in my_convert_keys:
                if convert_key in socket_name:
                    proceed = False
            if proceed:
                do_relink(node, node.inputs[socket_name], sockets_in, in_out='INPUT')
    finally:
        # Now we have to clean up by removing the unneeded sockets and repositioning.
        for other_node in toggle_updating:
            other_node.is_updating = was_updating[other_node.name]
        node.id_data.do_live_update = live_updates

# These BBone Scale-In, Scale-Out properties had the wrong defaults
# now that they are implemented properly, 
# since they were not implemented before, we'll do all of them at once.
# Normally it is wrong to set things directly like this, but they didn't
# do anything before. Oh well.
def fix_bbone_default_scale_in_and_out(*args, **kwargs):
    tree = kwargs['tree']
    current_major_version = tree.mantis_version[0]
    current_minor_version = tree.mantis_version[1]
    current_sub_version = tree.mantis_version[2]
    if  current_major_version > 0: return# major version must be 0
    if current_minor_version >= 13: return# minor version must be 12 or less
    if current_minor_version == 13 and current_sub_version >= 5: return# sub version must be 4 or less
    prPurple(f"Fixing BBone Settings for {tree.name}")
    live_updates = tree.do_live_update
    bones = []
    for node in tree.nodes:
        if hasattr(node, 'is_updating'):
            node.is_updating = True
        if node.bl_idname == 'xFormBoneNode':
            bones.append(node)
    try:
        for bone_node in bones:
            bone_node.inputs['BBone Scale-In'].default_value = (1,1,1)
            bone_node.inputs['BBone Scale-Out'].default_value = (1,1,1)
    finally:
        for node in tree.nodes:
            if hasattr(node, 'is_updating'):
                node.is_updating = False

# versioning tasks that involve Blender versions rather than Mantis versions:
error_description_4_5_0_LTS = 'There is a bug in Blender 4.5.0 LTS, that is why these sockets are blue.'\
                             ' This will be fixed in future Blender versions.'
def cleanup_4_5_0_LTS_interface_workaround(*args, **kwargs):
    # this is a function for cleaning up the workaround up above
    tree = kwargs['tree']
    if bpy_version == (4,5,0): return
    if not hasattr(tree, "interface_helper"): return
    import json
    try:
        interface_helper = json.loads(tree.interface_helper)
    except:
        return # this should mean it was never a problem to begin with.
    prPurple(f"Restoring Tree Interface for {tree.name}.")
    for interface_item in tree.interface.items_tree:
        if interface_item.item_type == 'PANEL': continue
        # now we need to restore the socket types, which are in the interface helper
        # keep the interface stuff around, I'll use it for marking arrays in the future
        int_info = interface_helper[interface_item.identifier]
        socket_type = int_info['bl_socket_idname']
        interface_item.socket_type = socket_type
        if interface_item.description == error_description_4_5_0_LTS:
            interface_item.description = ''

versioning_tasks = [
    # node bl_idname    task                required keyword arguments
    (['ALL'], version_upgrade_very_old, ['node_tree', 'node'],),
    (['xFormBoneNode'], version_upgrade_bone_0_12_0_from_older, ['node'],),
    (['xFormBoneNode'], up_0_12_1_add_inherit_color, ['node'],),
    (['MantisTree', 'SchemaTree'], cleanup_4_5_0_LTS_interface_workaround, ['tree']),
    (['InputWidget'], up_0_12_13_add_widget_scale, ['node']),
    (['LinkFloor'], up_0_12_25_replace_floor_offset_type, ['node']),
    (['XFORM'], up_0_13_0_new_custom_prop_node, ['node', 'node_tree']),
    (['SchemaTree'], schema_enable_custom_interface_types, ['tree']),
    (['UtilityFCurve', 'LinkArmature'],
           update_fcurve_and_armature_node_to_multi_socket, ['node']),
    (['MantisTree', 'SchemaTree'], fix_bbone_default_scale_in_and_out, ['tree']),
]


# WORKAROUNDS for bugs should go here:
# 4.5.0 LTS valid socket types bug:
def workaround_4_5_0_interface_update(tree, name, in_out, sock_type, parent_name, do_parent=False):
    # TODO: dedupe this code from i_o.py
    prRed("There is a bug in Blender 4.5.0 regarding node-group interface sockets. Working around it.")
    sock = tree.interface.new_socket(name=name, in_out=in_out, socket_type="NodeSocketGeometry")
    import json
    interface_helper = {} # initialize it if it is empty
    if tree.interface_helper: # may be empty, check here
        interface_helper = json.loads(tree.interface_helper)
    error_message = error_description_4_5_0_LTS
    interface_helper[sock.identifier] = {
            'name'             : sock.name,
            'identifier'       : sock.identifier,
            'in_out'           : sock.in_out,
            'socket_type'      : sock_type,
            'bl_socket_idname' : sock_type,
            'mantis_socket_category' : parent_name,
            'description' : error_message,
        }
    sock.description = error_message # this tells the user why the socket looks weird.
    tree.interface_helper = json.dumps(interface_helper)
    if do_parent and (parent := tree.interface.items_tree.get(parent_name)):
        tree.interface.move_to_parent(
                                sock,
                                parent,
                                0, # what to do here?
                                )
    return sock

def socket_add_workaround_for_4_5_0_LTS(item, socket_collection, multi):
    import json
    tree = item.id_data
    interface_helper = json.loads(tree.interface_helper)
    socket_info = interface_helper.get(item.identifier)
    if not socket_info: raise RuntimeError(f"There has been an error adding the socket {item.name}")
    s = socket_collection.new(
        type=socket_info['bl_socket_idname'],
        name=item.name, # in case the user has changed it
        identifier=item.identifier,
        use_multi_input=multi, )
    return s

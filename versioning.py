#Versioning Tasks
# this will be the new versioning system, and will deprecate the old SOCKETS_ADDED and such

from bpy.types import Node, NodeSocket
from .utilities import prRed, prGreen, prPurple

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
            from .utilities import get_socket_maps
            socket_maps = get_socket_maps(node)
        for socket, socket_index, new_bl_idname, new_name, multi in rename_jobs:
            old_id = socket.identifier
            print (f"Renaming socket {socket.identifier} to {new_name} in node {node.name}")
            from .utilities import do_relink
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
        for bl_idname, task in versioning_node_tasks:
            if node.bl_idname in bl_idname: task(node)
    except Exception as e:
        prRed(f"Error updating version in node: {node.id_data.name}::{node.name}; see error:")
        print(e)


def version_upgrade_bone_0_12_0_from_older(*args, **kwargs):
    # we need to check if it has an array collection input and a color input
    # then we need to solve each task
    node = kwargs['node']
    current_major_version = node.id_data.mantis_version[0]
    current_minor_version = node.id_data.mantis_version[1]
    if  current_major_version > 0: # major version must be 0
        return
    if current_minor_version >= 12: # minor version must be 11 or less
        return
    # sub version doesn't matter since any subversion of 11 should trigger this task
    try:
        collection_input_is_array = node.inputs['Bone Collection'].is_multi_input
        if not collection_input_is_array: # it must be made into an array!
            prPurple(f"Updating \"Bone Collection\" Socket in {node.name}")
            from .utilities import get_socket_maps
            socket_maps = get_socket_maps(node)
            socket_map = socket_maps[0]
            for i, socket in enumerate(node.inputs):
                if socket.name == 'Bone Collection': break
            old_id = socket.identifier
            # it is an input
            node.inputs.remove(socket)
            s = node.inputs.new('BoneCollectionSocket', 'Bone Collection',
                                identifier='Bone Collection', use_multi_input=True)
            node.inputs.move(len(node.inputs)-1, i)
            socket_map_from_old_socket = socket_map[old_id]
            # there seems to be an error in do_relink
            # gonna do it directly instead
            if isinstance(socket_map_from_old_socket, list):
                for map_info in socket_map_from_old_socket:
                    if isinstance(map_info, Node ):
                        l = node.id_data.links.new(input=map_info.outputs[0], output=s)
                    elif isinstance(map_info, NodeSocket):
                        l = node.id_data.links.new(input=map_info, output=s)
            else:
                s.default_value = socket_map_from_old_socket
        if node.inputs.get('Color') is None:
            prPurple(f"Adding \"Color\" Socket to {node.name}")
            s = node.inputs.new('ColorSetSocket', 'Color',)
            node.inputs.move(len(node.inputs)-1, 22)
    except Exception as e:
        prRed(f"Error updating version in node: {node.id_data.name}::{node.name}; see error:")
        print(e)


def up_0_12_1_add_inherit_color(*args, **kwargs):
    # add an inherit color input.
    node = kwargs['node']
    current_major_version = node.id_data.mantis_version[0]
    current_minor_version = node.id_data.mantis_version[1]
    current_sub_version = node.id_data.mantis_version[2]
    if  current_major_version > 0: return# major version must be 0
    if current_minor_version > 12: return# minor version must be 12 or less
    if current_minor_version == 12 and current_sub_version < 1: return # sub version must be 0
    # sub version doesn't matter since any subversion of 11 should trigger this task
    prPurple(f"Adding \"Inherit Color\" socket to {node.name}")
    try:
        inh_color = node.inputs.get('Inherit Color')
        if inh_color.bl_idname != 'BooleanSocket':
            node.inputs.remove(inh_color)
            inh_color = None
        if inh_color is None:
            s = node.inputs.new('BooleanSocket', 'Inherit Color',)
            node.inputs.move(len(node.inputs)-1, 23)
            s.default_value=True
    except Exception as e:
        prRed(f"Error updating version in node: {node.id_data.name}::{node.name}; see error:")
        print(e)



versioning_tasks = [
    # node bl_idname    task                required keyword arguments 
    (['ALL'], version_upgrade_very_old, ['node_tree', 'node'],),
    (['xFormBoneNode'], version_upgrade_bone_0_12_0_from_older, ['node'],),
    (['xFormBoneNode'], up_0_12_1_add_inherit_color, ['node'],),
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
    error_message= 'There is a bug in Blender 4.5.0 LTS, that is why these sockets are blue.'\
                    ' This will be fixed in future Blender versions.'
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
        prRed(parent.name)

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

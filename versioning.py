#Versioning Tasks
# this will be the new versioning system, and will deprecate the old SOCKETS_ADDED and such

from bpy.types import Node, NodeSocket
from .utilities import prRed, prGreen


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
            s = node.inputs.new('ColorSetSocket', 'Color',)
            node.inputs.move(len(node.inputs)-1, 22)
    except Exception as e:
        prRed(f"Error updating version in node: {node.id_data.name}::{node.name}; see error:")
        print(e)


versioning_tasks = [
    # node bl_idname    task                required keyword arguments 
    (['xFormBoneNode'], version_upgrade_bone_0_12_0_from_older, ['node'],),
]
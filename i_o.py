# this is the I/O part of mantis. I eventually intend to make this a markup language. not right now tho lol

from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

from mathutils import Vector, Matrix

NODES_REMOVED=["xFormRootNode"]
                 # Node bl_idname, # Socket Name
SOCKETS_REMOVED=[("UtilityDriverVariable", "Transform Channel"),
                 ("xFormRootNode","World Out"),
                 ("UtilitySwitch","xForm"),
                 ("LinkDrivenParameter", "Enable")]
                  # Node Class           #Prior bl_idname  # prior name # new bl_idname #       new name,          # Multi

# Debugging values.
print_read_only_warning = False
print_link_failure = False

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
                # more blender properties...
                "bl_use_group_interface", "default_group_node_width", "id_type",
                # blender runtime stuff
                "animation_data", "description", "grease_pencil", "is_editable",
                "is_embedded_data", "is_evaluated", "is_library_indirect", "is_missing",
                "is_runtime_data", "library", "name_full", "override_library",
                "session_uid", "tag", "use_extra_user", "use_fake_user", "users",
                # some Mantis stuff I don't need to save
                "do_live_update", "is_executing", "is_exporting", "hash", "filepath",
                "prevent_next_exec", "execution_id", "num_links", "tree_valid",
                "interface_helper",
                # node stuff
                "mantis_node_class_name", "color", "height", "initialized", "select",
                "show_options", "show_preview", "show_texture", "use_custom_color",
                "warning_propagation",
                # these are in Bone
                "socket_count", "display_bb_settings", "display_def_settings",
                "display_ik_settings", "display_vp_settings",
                ] 
# don't ignore: "bl_idname", "bl_label",
# ignore the name, it's the dict - key for the node props
    # no that's stupid don't ignore the name good grief

# I am doing this because these are interactions with other addons that cause problems and probably don't exist for any given user
prop_ignore.extend(['keymesh'])

# trees
prop_ignore_tree = prop_ignore.copy()
prop_ignore_tree.extend(["bl_label", "name"])

prop_ignore_interface = prop_ignore.copy()
                                # Geometry Nodes stuff that Mantis doesn't use
prop_ignore_interface.extend( [ "attribute_domain",
                                "default_attribute_name",
                                "default_input",
                                "force_non_field",
                                "hide_in_modifier",
                                "hide_value",
                                # no idea what this is, also don't care
                                "is_inspect_output",
                                "is_panel_toggle",
                                "layer_selection_field",
                                "structure_type",  ] )



from bpy.app import version

if version >= (4,5,0):
    SOCKETS_REMOVED.append( ("LinkSplineIK", "Use Original Scale"))

add_inputs_bl_idnames = [
    "UtilityDriver", "UtilityFCurve", "DeformerMorphTargetDeform",
    "LinkArmature",
    "xFormBoneNode"
    # for custom properties, right?
    # For a long time this wasn't in here and I guess there weren't problems
    # I really don't know if adding it here is right...
    ]

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
    return [ MantisExportNodeTreeSaveAs,
            MantisExportNodeTreeSave,
            MantisExportNodeTree,
            MantisImportNodeTree,
            MantisImportNodeTreeNoMenu,
            MantisReloadNodeTree]

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

# def scan_tree_for_objects(base_tree, current_tree):
#     # goal: find all referenced armature and curve objects
#     # return [set(armatures), set(curves)]
#     armatures = set()
#     curves    = set()
#     for node in base_tree.parsed_tree.values():
#         from .utilities import get_node_prototype
#         if node.ui_signature is None:
#             continue
#         ui_node = get_node_prototype(node.ui_signature, node.base_tree)
#         if ui_node is None or ui_node.id_data != current_tree:
#             continue
#         if hasattr(node, "bGetObject"):
#             ob = node.bGetObject()
#             print(node, ob)
#             if ob is None:
#                 continue
#             if not hasattr(node, "type"):
#                 continue
#             if ob.type == 'ARMATURE':
#                 armatures.add(ob)
#             if ob.type == 'CURVE':
#                 curves.add(ob)
#     return (armatures, curves)

# Currently this isn't very robust and doesn't seek backwards
# to see if a dependency is created by node connections.
# TODO it remains to be seen if that is even a desirable behaviour.
def scan_tree_for_objects(base_tree, current_tree):
    # this should work 
    armatures, curves    = set(), set()
    if current_tree == base_tree:
        scan_tree_dependencies(base_tree, curves, armatures,)
    return (curves, armatures )

def scan_tree_dependencies(base_tree, curves:set, armatures:set, ):
    from .utilities import check_and_add_root
    from collections import deque
    from bpy import context, data
    xForm_pass = deque()
    if base_tree.tree_valid:
        nodes = base_tree.parsed_tree
    else:
        base_tree.update_tree(context=context)
        nodes = base_tree
    for nc in nodes.values():
        nc.reset_execution()
        check_and_add_root(nc, xForm_pass)
    from .readtree import sort_execution
    from .utilities import get_node_prototype
    sorted_nodes, execution_failed = sort_execution(nodes, xForm_pass)
    if execution_failed:
        prRed("Error reading dependencies from tree, skipping")
        return curves, armatures
    for n in sorted_nodes:
        if n.ui_signature is None:
            continue # doesn't matter
        ui_node = get_node_prototype(n.ui_signature, n.base_tree)
        if not ui_node:
            continue
        # we need to see if it is receiving a Curve
        # so check the ui_node if it is a socket that takes an object
        for s in ui_node.inputs:
            if s.bl_idname in 'EnumCurveSocket':
                curve_name = n.evaluate_input(s.name)
                prRed(curve_name)
                if curve := data.objects.get(curve_name):
                    curves.add(curve)
                else:
                    raise NotImplementedError(curve_name)
        match ui_node.bl_idname:
            case "UtilityMetaRig":
                armature_name = n.evaluate_input("Meta-Armature")
                prWhite(armature_name)
                if armature := data.objects.get(armature_name):
                    armatures.add(armature)
            case "InputExistingGeometryObjectNode":
                object_name = n.evaluate_input("Name")
                prWhite(object_name)
                if object := data.objects.get(object_name):
                    if object.type == "ARMATURE":
                        armatures.add(object)
                    elif object.type == "CURVE":
                        curves.add(object)
            # Usually we don't want an object that is generated by the tree
            # case "xFormArmatureNode":
            #     armature_name = n.evaluate_input("Name")
            #     prWhite(armature_name)
            #     if armature := data.objects.get(armature_name):
            #         armatures.add(armature)
            case "xFormGeometryObjectNode":
                object_name = n.evaluate_input("Name")
                prWhite(object_name)
                if object := data.objects.get(object_name):
                    if object.type == "ARMATURE":
                        armatures.add(object)
                    elif object.type == "CURVE":
                        curves.add(object)
    return (curves, armatures )

# TODO move these dataclasses into a new file
from dataclasses import dataclass, field, asdict
# some basic classes to define curve point types
@dataclass
class crv_pnt_data():
     co                 : tuple[float, float, float] = field(default=(0,0,0,))
     handle_left        : tuple[float, float, float] = field(default=(0,0,0,))
     handle_right       : tuple[float, float, float] = field(default=(0,0,0,))
     handle_left_type   : str = field(default="ALIGNED")
     handle_right_type  : str = field(default="ALIGNED")
     radius             : float = field(default=0.0)
     tilt               : float = field(default=0.0)
     w                  : float = field(default=0.0)

@dataclass
class spline_data():
    type                  : str = field(default='POLY')
    points                : list[dict] = field(default_factory=[])
    order_u               : int = field(default=4)
    radius_interpolation  : str = field(default="LINEAR")
    tilt_interpolation    : str = field(default="LINEAR")
    resolution_u          : int = field(default=12)
    use_bezier_u          : bool = field(default=False)
    use_cyclic_u          : bool = field(default=False)
    use_endpoint_u        : bool = field(default=False)
    index                 : int = field(default=0)
    object_name           : str = field(default='Curve')

def get_curve_for_pack(object):
    splines = []
    for i, spline in enumerate(object.data.splines):
        points = []
        if spline.type == 'BEZIER':
            for point in spline.bezier_points:
                export_pnt = crv_pnt_data(
                        co                = tuple(point.co),
                        radius            = point.radius,
                        tilt              = point.tilt,
                        handle_left       = tuple(point.handle_left),
                        handle_right      = tuple(point.handle_right),
                        handle_left_type  = point.handle_left_type,
                        handle_right_type = point.handle_right_type,
                )
                points.append(asdict(export_pnt))
        else:
            for point in spline.points:
                export_pnt = crv_pnt_data(
                        co     = point.co[:3], # exclude the w value
                        radius = point.radius,
                        tilt   = point.tilt,
                        w      = point.co[3],
                )
                points.append(asdict(export_pnt))
        export_spl = spline_data(
                type                  = spline.type,
                points                = points,
                order_u               = spline.order_u,
                radius_interpolation  = spline.radius_interpolation,
                tilt_interpolation    = spline.tilt_interpolation,
                resolution_u          = spline.resolution_u,
                use_bezier_u          = spline.use_bezier_u,
                use_cyclic_u          = spline.use_cyclic_u,
                use_endpoint_u        = spline.use_endpoint_u,
                index                 = i,
                object_name           = object.name,)
        splines.append(asdict(export_spl))
    return splines

def matrix_as_tuple(matrix):
    return ( matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
             matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3], 
             matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3],
             matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3], )

@dataclass
class metabone_data:
    object_name           : str = field(default='')
    name                  : str = field(default=''),
    type                  : str = field(default='BONE'),
    matrix                : tuple[float] = field(default=()),
    parent                : str = field(default=''),
    length                : float = field(default=-1.0),
    children              : list[str] = field(default_factory=[]), 
# keep it really simple for now. I'll add BBone and envelope later on
# when I make them accessible from the meta-rig

def get_armature_for_pack(object):
    metarig_data = {}
    armature_children = []
    for bone in object.data.bones:
        parent_name = ''
        if bone.parent is None:
            armature_children.append(bone.name)
        else:
            parent_name=bone.parent.name
        children=[]
        for c in bone.children:
            children.append(c.name)
        bone_data = metabone_data( object_name = object.name,
            name=bone.name, type='BONE',
            matrix=matrix_as_tuple(bone.matrix_local),
            parent=parent_name, length = bone.length, children = children,
        )
        metarig_data[bone.name]=asdict(bone_data)
    armature_data = metabone_data( object_name = object.name,
        name=object.name, type='ARMATURE',
        matrix=matrix_as_tuple(object.matrix_world),
        parent="", # NOTE that this is not always a fair assumption!
        length = -1.0, children = armature_children,)
    metarig_data[object.name] = asdict(armature_data)
    metarig_data["MANTIS_RESERVED"] = asdict(armature_data) # just in case a bone is named the same as the armature
    return metarig_data

def get_socket_data(socket, ignore_if_default=False):
    # TODO: don't get stuff in the socket templates
    # PROBLEM: I don't have easy access to this from the ui class (or mantis class)
    socket_data = {}
    socket_data["name"] = socket.name
    socket_data["bl_idname"] = socket.bl_idname
    socket_data["is_output"] = socket.is_output
    socket_data["is_multi_input"] = socket.is_multi_input
    
    # here is where we'll handle a socket_data'socket special data
    if socket.bl_idname == "EnumMetaBoneSocket":
        socket_data["bone"] = socket.bone
    if socket.bl_idname in ["EnumMetaBoneSocket", "EnumMetaRigSocket", "EnumCurveSocket"]:
        if sp := socket.get("search_prop"): # may be None
            socket_data["search_prop"] = sp.name # this is an object.
    #
    if hasattr(socket, "default_value"):
        value = socket.default_value
    else:
        value = None
        return socket_data # we don't need to store any more.
    if not is_jsonable(value): # FIRST try and make a tuple out of it because JSON doesn't like mutables
        value = tuple(value)
    if not is_jsonable(value): # now see if it worked and crash out if it didn't
        raise RuntimeError(f"Error serializing data in {socket.node.name}::{socket.name} for value of type {type(value)}")
    socket_data["default_value"] = value
    # TODO TODO implement "ignore if default" feature here
    # at this point we can get the custom parameter ui hints if we want
    if not socket.is_output:
        # try and get this data
        if value := getattr(socket,'min', None):
            socket_data["min"] = value
        if value := getattr(socket,'max', None):
            socket_data["max"] = value
        if value := getattr(socket,'soft_min', None):
            socket_data["soft_min"] = value
        if value := getattr(socket,'soft_max', None):
            socket_data["soft_max"] = value
        if value := getattr(socket,'description', None):
            socket_data["description"] = value
    return socket_data
    #
def get_node_data(ui_node):
    # if this is a node-group, force it to update its interface, because it may be messed up.
    # can remove this HACK when I have stronger guarentees about node-group's keeping the interface
    from .base_definitions import node_group_update
    if hasattr(ui_node, "node_tree"):
        ui_node.is_updating = True
        try: # HERE BE DANGER
            node_group_update(ui_node, force=True)
        finally: # ensure this line is run even if there is an error
            ui_node.is_updating = False
    node_props, inputs, outputs = {}, {}, {}
    for propname  in dir(ui_node):
        value = getattr(ui_node, propname)
        if propname in ['fake_fcurve_ob']:
            value=value.name
        if (propname in prop_ignore) or ( callable(value) ):
            continue
        if value.__class__.__name__ in ["Vector", "Color"]:
            value = tuple(value)
        if isinstance(value, bpy.types.NodeTree):
            value = value.name
        if isinstance(value, bpy.types.bpy_prop_array):
            value = tuple(value)
        if propname == "parent" and value:
            value = value.name
        if not is_jsonable(value):
            raise RuntimeError(f"Could not export...  {ui_node.name}, {propname}, {type(value)}")
        if value is None:
            continue
        node_props[propname] = value
        # so we have to accumulate the parent location because the location is not absolute
        if propname == "location" and ui_node.parent is not None:
            location_acc = Vector((0,0))
            parent = ui_node.parent
            while (parent):
                location_acc += parent.location
                parent = parent.parent
            location_acc += getattr(ui_node, propname)
            node_props[propname] = tuple(location_acc)
            # this works!
    if ui_node.bl_idname in ['RerouteNode']:
        return node_props # we don't need to get the socket information.
    for i, ui_socket in enumerate(ui_node.inputs):
        socket = get_socket_data(ui_socket)
        socket["index"]=i
        inputs[ui_socket.identifier] = socket
    for i, ui_socket in enumerate(ui_node.outputs):
        socket = get_socket_data(ui_socket)
        socket["index"]=i
        outputs[ui_socket.identifier] = socket
    node_props["inputs"] = inputs
    node_props["outputs"] = outputs
    return node_props

def get_tree_data(tree):
    tree_info = {}
    for propname  in dir(tree):
        # if getattr(tree, propname):
        #     pass
        if (propname in prop_ignore_tree) or ( callable(getattr(tree, propname)) ):
            continue
        v = getattr(tree, propname)
        if isinstance(getattr(tree, propname), bpy.types.bpy_prop_array):
            v = tuple(getattr(tree, propname))
        if not is_jsonable( v  ):
            raise RuntimeError(f"Not JSON-able: {propname}, type: {type(v)}")
        tree_info[propname] = v
    tree_info["name"]=tree.name
    return tree_info

def get_interface_data(tree, tree_in_out):
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
            # we need to get the socket class from the bl_idname
            bl_socket_idname = sock.bl_socket_idname
            # try and import it
            from . import socket_definitions
            # WANT an attribute error if this fails.
            socket_class = getattr(socket_definitions, bl_socket_idname)
            sock_parent = None
            if sock.parent:
                sock_parent = sock.parent.name
            for propname  in dir(sock):
                if propname in prop_ignore_interface:
                    continue
                if (propname == "parent"):
                    sock_data[propname] = sock_parent
                    continue
                v = getattr(sock, propname)
                if (propname in prop_ignore) or ( callable(v) ):
                    continue
                if isinstance(getattr(sock, propname), bpy.types.bpy_prop_array):
                    v = tuple(getattr(sock, propname))
                if not is_jsonable( v ):
                    raise RuntimeError(f"{propname}, {type(v)}")
                sock_data[propname] = v
            # this is a property. pain.
            sock_data["socket_type"] = socket_class.interface_type.fget(socket_class)
            tree_in_out[sock.identifier] = sock_data
            

def export_to_json(trees, base_tree=None, path="", write_file=True, only_selected=False, ):
    export_data = {}
    for tree in trees:
        current_tree_is_base_tree = False
        if tree is trees[-1]:
            current_tree_is_base_tree = True
        
        tree_info, tree_in_out = {}, {}
        tree_info = get_tree_data(tree)
        curves, metarig_data = {}, {}

        embed_metarigs=True
        if base_tree and embed_metarigs:
            curves_in_tree, metarigs_in_tree = scan_tree_for_objects(base_tree, tree)
            for crv in curves_in_tree:
                curves[crv.name] = get_curve_for_pack(crv)
            for mr in metarigs_in_tree:
                metarig_data[mr.name] = get_armature_for_pack(mr)

        # if only_selected:
        #     # all in/out links, relative to the selection, should be marked and used to initialize tree properties

        if not only_selected: # we'll handle this later with the links
            for sock in tree.interface.items_tree:
                get_interface_data(tree, tree_in_out) # it concerns me that this one modifies
                #  the collection instead of getting the data and returning it. TODO refactor this

        nodes = {}
        for node in tree.nodes:
            if only_selected and node.select == False:
                continue
            nodes[node.name] = get_node_data(node)
            
        links = []
        in_sockets, out_sockets = {}, {}
        unique_sockets_from, unique_sockets_to = {}, {}

        in_node = {"name":"MANTIS_AUTOGEN_GROUP_INPUT", "bl_idname":"NodeGroupInput", "inputs":in_sockets}
        out_node = {"name":"MANTIS_AUTOGEN_GROUP_OUTPUT", "bl_idname":"NodeGroupOutput", "outputs":out_sockets}
        add_input_node, add_output_node = False, False

        for link in tree.links:
            from_node_name, from_socket_id = link.from_node.name, link.from_socket.identifier
            to_node_name, to_socket_id = link.to_node.name, link.to_socket.identifier
            from_socket_name, to_socket_name = link.from_socket.name, link.to_socket.name

            # get the indices of the sockets to be absolutely sure
            for from_outoput_index, outp in enumerate(link.from_node.outputs):
                # for some reason, 'is' does not return True no matter what...
                # so we are gonn compare the memory address directly, this is stupid
                if (outp.as_pointer() == link.from_socket.as_pointer()): break
            else:
                problem=link.from_node.name + "::" + link.from_socket.name
                raise RuntimeError(wrapRed(f"Error saving index of socket: {problem}"))
            for to_input_index, inp in enumerate(link.to_node.inputs):
                if (inp.as_pointer() == link.to_socket.as_pointer()): break
            else:
                problem = link.to_node.name + "::" + link.to_socket.name
                raise RuntimeError(wrapRed(f"Error saving index of socket: {problem}"))
            
            if current_tree_is_base_tree:
                if (only_selected and link.from_node.select) and (not link.to_node.select):
                    # handle an output in the tree
                    add_output_node=True
                    if not (sock_name := unique_sockets_to.get(link.from_socket.node.name+link.from_socket.identifier)):
                        sock_name = link.to_socket.name; name_stub = sock_name
                        used_names = list(tree_in_out.keys()); i=0
                        while sock_name in used_names:
                            sock_name=name_stub+'.'+str(i).zfill(3); i+=1
                        unique_sockets_to[link.from_socket.node.name+link.from_socket.identifier]=sock_name

                    out_sock = out_sockets.get(sock_name)
                    if not out_sock:
                        out_sock = {}; out_sockets[sock_name] = out_sock
                        out_sock["index"]=len(out_sockets) # zero indexed, so zero length makes zero the first index and so on, this works
                    # what in the bad word is happening here?
                    # why?
                    # why no de-duplication?
                    # what was I thinking?
                    # TODO REFACTOR THIS SOON
                    out_sock["name"] = sock_name
                    out_sock["identifier"] = sock_name
                    out_sock["bl_idname"] = link.to_socket.bl_idname
                    out_sock["is_output"] = False
                    out_sock["source"]=[link.to_socket.node.name,link.to_socket.identifier]
                    out_sock["is_multi_input"] = False # this is not something I can even set on tree interface items, and this code is not intended for making Schema
                    sock_data={}
                    sock_data["name"] = sock_name
                    sock_data["item_type"] = "SOCKET"
                    sock_data["default_closed"] = False
                        # record the actual bl_idname and the proper interface type.
                    sock_data["socket_type"] = link.from_socket.interface_type
                    sock_data["bl_socket_idname"] = link.from_socket.bl_idname
                    sock_data["identifier"] = sock_name
                    sock_data["in_out"]="OUTPUT"
                    sock_data["index"]=out_sock["index"]
                    tree_in_out[sock_name] = sock_data

                    to_node_name=out_node["name"]
                    to_socket_id=out_sock["identifier"]
                    to_input_index=out_sock["index"]
                    to_socket_name=out_sock["name"]

                elif (only_selected and (not link.from_node.select)) and link.to_node.select:
                    add_input_node=True
                    # we need to get a unique name for this
                    # use the Tree IN/Out because we are dealing with Group in/out
                    if not (sock_name := unique_sockets_from.get(link.from_socket.node.name+link.from_socket.identifier)):
                        sock_name = link.from_socket.name; name_stub = sock_name
                        used_names = list(tree_in_out.keys()); i=0
                        while sock_name in used_names:
                            sock_name=name_stub+'.'+str(i).zfill(3); i+=1
                        unique_sockets_from[link.from_socket.node.name+link.from_socket.identifier]=sock_name

                    in_sock = in_sockets.get(sock_name)
                    if not in_sock:
                        in_sock = {}; in_sockets[sock_name] = in_sock
                        in_sock["index"]=len(in_sockets) # zero indexed, so zero length makes zero the first index and so on, this works
                        #
                        in_sock["name"] = sock_name
                        in_sock["identifier"] = sock_name
                        in_sock["bl_idname"] = link.from_socket.bl_idname
                        in_sock["is_output"] = True
                        in_sock["is_multi_input"] = False # this is not something I can even set on tree interface items, and this code is not intended for making Schema
                        in_sock["source"] = [link.from_socket.node.name,link.from_socket.identifier]
                        sock_data={}
                        sock_data["name"] = sock_name
                        sock_data["item_type"] = "SOCKET"
                        sock_data["default_closed"] = False
                        # record the actual bl_idname and the proper interface type.
                        sock_data["socket_type"] = link.from_socket.interface_type
                        sock_data["bl_socket_idname"] = link.from_socket.bl_idname
                        sock_data["identifier"] = sock_name
                        sock_data["in_out"]="INPUT"
                        sock_data["index"]=in_sock["index"]

                        
                        tree_in_out[sock_name] = sock_data

                    from_node_name=in_node.get("name")
                    from_socket_id=in_sock["identifier"]
                    from_outoput_index=in_sock["index"]
                    from_socket_name=in_node.get("name")
                # parentheses matter here...
                elif (only_selected and not (link.from_node.select and link.to_node.select)):
                    continue
            elif only_selected and not (link.from_node.select and link.to_node.select):
                continue # pass if both links are not selected
            links.append( (from_node_name,
                           from_socket_id,
                           to_node_name,
                           to_socket_id,
                           from_outoput_index,
                           to_input_index,
                           from_socket_name,
                           to_socket_name) ) # it's a tuple
        
        
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

        export_data[tree.name] = (tree_info, tree_in_out, nodes, links, curves, metarig_data,) # f_curves)
    
    return export_data

def write_json_data(data, path):
    import json
    with open(path, "w") as file:
        print(wrapWhite("Writing mantis tree data to: "), wrapGreen(file.name))
        file.write( json.dumps(data, indent = 4) )
        
def get_link_sockets(link, tree, tree_socket_id_map):
    from_node_name = link[0]
    from_socket_id = link[1]
    to_node_name = link[2]
    to_socket_id = link[3]
    from_output_index = link[4]
    to_input_index = link[5]
    from_socket_name = link[6]
    to_socket_name = link[7]

    # TODO: make this a loop and swap out the in/out stuff
    # this is OK but I want to avoid code-duplication, which this almost is.
    from_node = tree.nodes.get(from_node_name)
    # first try and get by name. we'll use this if the ID and the name do not match.
    # from_sock = from_node.outputs.get(from_socket_name)

    id1 = from_socket_id
    if hasattr(from_node, "node_tree") or \
        from_node.bl_idname in ["SchemaArrayInput",
                                "SchemaArrayInputGet",
                                "SchemaArrayInputAll",
                                "SchemaConstInput",
                                "SchemaIncomingConnection", ]: # now we have to map by something else
                try:
                    id1 = from_node.outputs[from_socket_name].identifier
                except KeyError: # we'll try index if nothing else works
                    try:
                        id1 = from_node.outputs[from_output_index].identifier
                    except IndexError as e:
                        prRed("failed to create link: "
                            f"{from_node_name}:{from_socket_id} --> {to_node_name}:{to_socket_id}")
                        return (None, None)
    elif from_node.bl_idname in ["NodeGroupInput"]:
        id1 = tree_socket_id_map.get(from_socket_id)
    for from_sock in from_node.outputs:
        if from_sock.identifier == id1: break
    else: 
        from_sock = None

    id2 = to_socket_id
    to_node = tree.nodes[to_node_name]
    if hasattr(to_node, "node_tree") or \
        to_node.bl_idname in ["SchemaArrayOutput",
                              "SchemaConstOutput",
                              "SchemaOutgoingConnection", ]: # now we have to map by something else
                try:
                    id2 = to_node.inputs[to_socket_name].identifier
                except KeyError: # we'll try index if nothing else works
                    try:  # nesting try/except is ugly but it is right...
                        id2 = to_node.inputs[to_input_index].identifier
                    except IndexError as e:
                        prRed("failed to create link: "
                            f"{from_node_name}:{from_socket_id} --> {to_node_name}:{to_socket_id}")
                    return (None, None)
    elif to_node.bl_idname in ["NodeGroupOutput"]:
        id2 = tree_socket_id_map.get(to_socket_id)

    for to_sock in to_node.inputs:
        if to_sock.identifier == id2: break
    else:
        to_sock = None
    return from_sock, to_sock

def setup_sockets(node, propslist, in_out="inputs"):
        sockets_removed = []
        for i, (s_id, s_val) in enumerate(propslist[in_out].items()):
            if node.bl_idname in ['NodeReroute']:
                break # Reroute Nodes do not have anything I can set or modify.
            for socket_removed in SOCKETS_REMOVED:
                if node.bl_idname == socket_removed[0] and s_id == socket_removed[1]:
                    prWhite(f"INFO: Ignoring import of socket {s_id}; it has been removed.")
                    sockets_removed.append(s_val["index"])
                    sockets_removed.sort()
                    continue
            if s_val["is_output"]:
                if node.bl_idname in "MantisSchemaGroup":
                    node.is_updating = True
                    try:
                        socket = node.outputs.new(s_val["bl_idname"], s_val["name"], identifier=s_id)
                    finally:
                        node.is_updating=False
                elif s_val["index"] >= len(node.outputs):
                    if node.bl_idname in add_inputs_bl_idnames:
                        socket = node.outputs.new(s_val["bl_idname"], s_val["name"], identifier=s_id, )
                else: # first try to get by ID AND name. ID's switch around a bit so we need both to match.
                    for socket in node.outputs:
                        if socket.identifier == s_id and socket.name == s_val['name']:
                            break
                        # this often fails for group outputs and such
                        # because the socket ID may not be the same when it is re-generated
                    else: # otherwise try to get the index
                        # IT IS NOT CLEAR but this is what throws the index error below BAD
                        # try to get by name
                        socket = node.outputs.get(s_val['name'])
                        if not socket:
                            try:
                                socket = node.outputs[int(s_val["index"])]
                            except IndexError as e:
                                print (node.id_data.name)
                                print (propslist['name'])
                                print (s_id, s_val['name'], s_val['index'])
                                raise e

                    if socket.name != s_val["name"]:
                        right_name = s_val['name']
                        prRed( "There has been an error getting a socket while importing data."
                                f"found name: {socket.name}; should have found: {right_name}.")
            else:
                for removed_index in sockets_removed:
                    if s_val["index"] > removed_index:
                        s_val["index"]-=1
                if s_val["index"] >= len(node.inputs):
                    if node.bl_idname in add_inputs_bl_idnames:
                        socket = node.inputs.new(s_val["bl_idname"], s_val["name"], identifier=s_id, use_multi_input=s_val["is_multi_input"])
                    elif node.bl_idname in ["MantisSchemaGroup"]:
                        node.is_updating = True
                        try:
                            socket = node.inputs.new(s_val["bl_idname"], s_val["name"], identifier=s_id, use_multi_input=s_val["is_multi_input"])
                        finally:
                            node.is_updating=False
                    elif node.bl_idname in ["NodeGroupOutput"]:
                        pass # this is dealt with separately
                    else:
                        prWhite("Not found: ", propslist['name'], s_val["name"], s_id)
                        prRed("Index: ", s_val["index"], "Number of inputs", len(node.inputs))
                        for thing1, thing2 in zip(propslist[in_out].keys(), getattr(node, in_out).keys()):
                            print (thing1, thing2)
                        raise NotImplementedError(wrapRed(f"{node.bl_idname} in {node.id_data.name} needs to be handled in JSON load."))
                else: # first try to get by ID AND name. ID's switch around a bit so we need both to match.
                    for socket in node.inputs:
                        if socket.identifier == s_id and socket.name == s_val['name']:
                            break
                        # failing to find the socket by ID is less common for inputs than outputs.
                        # it usually isn't a problem.
                    else: # otherwise try to get the index
                        # IT IS NOT CLEAR but this is what throws the index error below BAD
                        socket = node.inputs.get(s_val["name"])
                        if not socket:
                            socket = node.inputs[int(s_val["index"])]
                        # finally we need to check that the name matches.
                    if socket.name != s_val["name"]:
                        right_name = s_val['name']
                        prRed( "There has been an error getting a socket while importing data."
                                f"found name: {socket.name}; should have found: {right_name}.")
            # set the value
            for s_p, s_v in s_val.items():
                if s_p not in ["default_value"]:
                    if s_p == "search_prop" and node.bl_idname == 'UtilityMetaRig':
                        socket.node.armature= s_v
                        socket.search_prop=bpy.data.objects.get(s_v)
                    if s_p == "search_prop" and node.bl_idname in ['UtilityMatrixFromCurve', 'UtilityMatricesFromCurve']:
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
                    prRed("Can't set socket due to type mismatch: ", node.name, socket.name, s_p, s_v)
                    # raise e
                except ValueError as e:
                    prRed("Can't set socket due to type mismatch: ", node.name,  socket.name, s_p, s_v)
                    # raise e
                except AttributeError as e:
                    if print_read_only_warning == True:
                        prWhite("Tried to write a read-only property, ignoring...")
                        prWhite(f"{socket.node.name}[{socket.name}].{s_p} is read only, cannot set value to {s_v}")


def do_import_from_file(filepath, context):
    import json

    all_trees = [n_tree for n_tree in bpy.data.node_groups if n_tree.bl_idname in ["MantisTree", "SchemaTree"]]

    for tree in all_trees:
        tree.is_exporting = True
        tree.do_live_update = False
    
    def do_cleanup(tree):
        tree.is_exporting = False
        tree.do_live_update = True
        tree.prevent_next_exec = True

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        do_import(data,context, search_multi_files=True, filepath=filepath)

        for tree in all_trees:
            do_cleanup(tree)

        tree = bpy.data.node_groups[list(data.keys())[-1]]
        try:
            context.space_data.node_tree = tree
        except AttributeError: # not hovering over the Node Editor
            pass
        return {'FINISHED'}
    # otherwise:
    # repeat this because we left the with, this is bad and ugly but I don't care
    for tree in all_trees:
            do_cleanup(tree)
    return {'CANCELLED'}

# TODO figure out the right way to dedupe this stuff (see above)
# I need this function for recursing through multi-file components
# but I am using the with statement in the above function...
# it should be easy to refactor but I don't know 100% for sure
# the behaviour will be identical or if that matters.
def get_graph_data_from_json(filepath) -> dict:
    import json
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def do_import(data, context, search_multi_files=False, filepath=''):
    trees = []
    tree_sock_id_maps = {}

    # First: init the interface of the node graph
    for tree_name, tree_data in data.items():
        tree_info = tree_data[0]
        tree_in_out = tree_data[1]


        # TODO: IMPORT THIS DATA HERE!!!
        try:
            curves = tree_data[4]
            armatures = tree_data[5]
        except IndexError: # shouldn't happen but maybe someone has an old file
            curves = {}
            armatures = {}
        
        for curve_name, curve_data in curves.items():
            from .utilities import import_curve_data_to_object, import_metarig_data
            import_curve_data_to_object(curve_name, curve_data)
            for armature_name, armature_data in armatures.items():
                import_metarig_data(armature_data)
        


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
        default_position=0 # We'll use this if the position attribute is not set when e.g. making groups.
        

        for s_name, s_props in tree_in_out.items():
            if s_props["item_type"] == 'SOCKET':
                if s_props["socket_type"] == "LayerMaskSocket":
                    continue
                if (socket_type := s_props["socket_type"]) == "NodeSocketColor":
                    socket_type = "VectorSocket"
                if bpy.app.version != (4,5,0):
                    sock = tree.interface.new_socket(s_props["name"], in_out=s_props["in_out"], socket_type=socket_type)
                else: # blender 4.5.0 LTS, have to workaround a bug!
                    from .versioning import workaround_4_5_0_interface_update
                    sock = workaround_4_5_0_interface_update(tree=tree, name=s_props["name"], in_out=s_props["in_out"],
                                                            sock_type=socket_type, parent_name=s_props.get("parent", ''))

                tree_sock_id_map[s_name] = sock.identifier
                if not (socket_position := s_props.get('position')):
                    socket_position=default_position; default_position+=1
                interface_sockets.append( (sock, socket_position) )
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
        
        # BUG this was screwing up the order of things
        # so I want to fix it and re-enable it
        if True:
            # Go BACK through and set the index/position now that all items exist.
            interface_sockets.sort(key=lambda a : a[1])
            for (socket, position) in interface_sockets:
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
                                "SchemaArrayInputAll",
                                "SchemaArrayOutput",
                                "SchemaConstInput",
                                "SchemaConstOutput",
                                "SchemaOutgoingConnection",
                                "SchemaIncomingConnection",]:
                n.update()

            
            if sub_tree := propslist.get("node_tree"):
                # now that I am doing multi-file exports, this is tricky
                # we need to see if the tree exists and if not, recurse
                # and import that tree before continuing.
                grp_tree = bpy.data.node_groups.get(sub_tree)
                if grp_tree is None: # for multi-file component this is intentional
                    if search_multi_files: # we'll get the filename and recurse
                        from bpy.path import native_pathsep, clean_name
                        from os import path as os_path
                        native_filepath = native_pathsep(filepath)
                        directory = os_path.split(native_filepath)[0]
                        subtree_filepath = os_path.join(directory, clean_name(sub_tree)+'.rig')
                        subtree_data = get_graph_data_from_json(subtree_filepath)
                        do_import(subtree_data, context,
                                  search_multi_files=True,
                                  filepath=subtree_filepath)
                        #now get the grp_tree lol
                        grp_tree = bpy.data.node_groups[sub_tree]
                    else: # otherwise it is an error
                        raise RuntimeError(f"Tree {sub_tree} not available to import.")

                n.node_tree = grp_tree
                from .base_definitions import node_group_update
                n.is_updating = True
                try:
                    node_group_update(n, force = True)
                finally:
                    n.is_updating=False
            # set up sockets
            setup_sockets(n, propslist, in_out="inputs")
            setup_sockets(n, propslist, in_out="outputs")
            for p, v in propslist.items():
                if p in ["node_tree",
                         "sockets",
                         "inputs",
                         "outputs",
                         "warning_propagation", 
                         "socket_idname"]:
                    continue
                # will throw AttributeError if read-only
                # will throw TypeError if wrong type...
                if n.bl_idname == "NodeFrame" and p in ["width, height, location"]:
                    continue 
                if version  < (4,4,0) and p == 'location_absolute':
                    continue
                if p == "parent" and v is not None:
                    parent_me.append( (n.name, v) )
                    v = None # for now) #TODO
                try:
                    setattr(n, p, v)
                except Exception as e:
                    prRed (p)
                    raise e
                

        for l in links:
            from_socket_name = l[6]
            to_socket_name = l[7]
            name1=l[0]
            name2=l[2]
            from_sock, to_sock = get_link_sockets(l, tree, tree_sock_id_map)
            try:
                link = tree.links.new(from_sock, to_sock)
            except TypeError:
                prPurple (from_sock)
                prOrange (to_sock)
                if print_link_failure:
                    from_node_name = link[0]; from_socket_id = link[1]
                    to_node_name = link[2]; to_socket_id = link[3]
                    prWhite(f"looking for... {from_node_name}:{from_socket_id}, {to_node_name}:{to_socket_id}")
                    prRed (f"Failed: {l[0]}:{l[1]} --> {l[2]}:{l[3]}")
                    prRed (f" got node: {from_node_name}, {to_node_name}")
                    prRed (f" got socket: {from_sock}, {to_sock}")
                    raise RuntimeError
                else:
                    prRed(f"Failed to add link in {tree.name}: {name1}:{from_socket_name}, {name2}:{to_socket_name}")
            
            # if at this point it doesn't work... we need to fix
        for name, p in parent_me:
            if (n := tree.nodes.get(name)) and (p := tree.nodes.get(p)):
                n.parent = p
            # otherwise the frame node is missing because it was not included in the data e.g. when grouping nodes.
        
        tree.is_executing = False
        tree.do_live_update = True
        

def export_multi_file(trees : list,  base_tree, filepath : str, base_name :str) -> None:
    for t in trees:
        # this should name them the name of the tree...
        from bpy.path import native_pathsep, clean_name
        from os import path as os_path
        from os import mkdir
        native_filepath = native_pathsep(filepath)
        directory = os_path.split(native_filepath)[0]
        export_data = export_to_json([t], base_tree, os_path.join(directory,
                        clean_name(t.name)+'.rig'))
        write_json_data(export_data, os_path.join(directory,
                        clean_name(t.name)+'.rig'))
        

import bpy

from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

# Save As
class MantisExportNodeTreeSaveAs(Operator, ExportHelper):
    """Export a Mantis Node Tree by filename."""
    bl_idname = "mantis.export_save_as"
    bl_label = "Export Mantis Tree as ...(.rig)"

    # ExportHelper mix-in class uses this.
    filename_ext = ".rig"

    filter_glob: StringProperty(
        default="*.rig",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    export_trees_together : BoolProperty(
        default=False,
        name="Pack All Sub-Trees",
        description="Pack all Sub-trees into one file?")


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
        base_tree.is_exporting = True
        if self.export_trees_together:
            export_data = export_to_json(trees, base_tree, self.filepath)
            write_json_data(export_data, self.filepath)
        else:
            export_multi_file(trees, base_tree, self.filepath, base_tree.name)
        base_tree.is_exporting = False
        base_tree.prevent_next_exec = True
        # set the properties on the base tree for re-exporting with alt-s
        base_tree.filepath = self.filepath
        base_tree.export_all_subtrees_together = self.export_trees_together
        return {'FINISHED'}

# Save
class MantisExportNodeTreeSave(Operator):
    """Save a Mantis Node Tree to disk."""
    bl_idname = "mantis.export_save"
    bl_label = "Export Mantis Tree (.rig)"

    @classmethod
    def poll(cls, context):
        return hasattr(context.space_data, 'path')

    def execute(self, context):
        base_tree=context.space_data.path[-1].node_tree
        filepath = base_tree.filepath
        from .utilities import all_trees_in_tree
        trees = all_trees_in_tree(base_tree)[::-1]
        prGreen("Exporting node graph with dependencies...")
        for t in trees:
            prGreen ("Node graph: \"%s\"" % (t.name))
        base_tree.is_exporting = True
        if base_tree.export_all_subtrees_together:
            export_data = export_to_json(trees, base_tree, filepath)
            write_json_data(export_data, filepath)
        else:
            export_multi_file(trees, base_tree,  filepath, base_tree.name)
        base_tree.is_exporting = False
        base_tree.prevent_next_exec = True
        return {'FINISHED'}

# Save Choose:
class MantisExportNodeTree(Operator):
    """Save a Mantis Node Tree to disk."""
    bl_idname = "mantis.export_save_choose"
    bl_label = "Export Mantis Tree (.rig)"

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
    bl_label = "Import Mantis Tree (.rig)"

    # ImportHelper mixin class uses this
    filename_ext = ".rig"

    filter_glob : StringProperty(
        default="*.rig",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return do_import_from_file(self.filepath, context)



class MantisImportNodeTreeNoMenu(Operator):
    """Import a Mantis Node Tree."""
    bl_idname = "mantis.import_tree_no_menu"
    bl_label = "Import Mantis Tree (.rig)"

    filepath : StringProperty()

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
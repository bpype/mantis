import bpy
from bpy.types import Operator
from mathutils import Vector

from .utilities.utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

def mantis_tree_poll_op(context):
    space = context.space_data
    if hasattr(space, "node_tree"):
        if (space.node_tree):
            return (space.tree_type in ["MantisTree", "SchemaTree"])
    return False

def any_tree_poll(context):
    space = context.space_data
    if hasattr(space, "node_tree"):
        return True
    return False

def tag_mantis_node_for_update(context, node):
    if any_tree_poll(context):
        from .base_definitions import get_signature_from_edited_tree
        node_tree = context.space_data.path[0].node_tree
        mantis_node = node_tree.parsed_tree.get(
                    get_signature_from_edited_tree(node, context))
        if mantis_node is None:
            node_tree.hash = ''
        else:
            mantis_node.reset_execution_recursive() # tag this as a change.
#########################################################################3

class MantisGroupNodes(Operator):
    """Create node-group from selected nodes"""
    bl_idname = "mantis.group_nodes"
    bl_label = "Group Nodes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return mantis_tree_poll_op(context)

    def execute(self, context):
        base_tree=context.space_data.path[-1].node_tree
        try:
            for path_item in context.space_data.path:
                path_item.node_tree.is_exporting = True

            from .utilities.i_o import export_to_json, do_import
            from random import random
            grp_name = "".join([chr(int(random()*30)+35) for i in range(20)])
            trees=[base_tree]
            selected_nodes=export_to_json(trees, base_tree=None, write_file=False, only_selected=True)
            # this snippet of confusing indirection edits the name of the base tree in the JSON data
            selected_nodes[base_tree.name][0]["name"]=grp_name
            do_import(selected_nodes, context)

            affected_links_in = []
            affected_links_out = []

            for l in base_tree.links:
                if l.from_node.select and not l.to_node.select: affected_links_out.append(l)
                if not l.from_node.select and l.to_node.select: affected_links_in.append(l)
            delete_me = []
            all_nodes_bounding_box=[Vector((float("inf"),float("inf"))), Vector((-float("inf"),-float("inf")))]
            for n in base_tree.nodes:
                if n.select:
                    node_loc = (0,0,0)
                    if bpy.app.version <= (4, 4):
                        node_loc = n.location
                        parent = n.parent
                        while (parent): # accumulate parent offset
                            node_loc += parent.location
                            parent = parent.parent
                    else: # there is a new location_absolute property in 4.4
                        node_loc = n.location_absolute
                    if node_loc.x < all_nodes_bounding_box[0].x:
                        all_nodes_bounding_box[0].x = node_loc.x
                    if node_loc.y < all_nodes_bounding_box[0].y:
                        all_nodes_bounding_box[0].y = node_loc.y
                    #
                    if node_loc.x > all_nodes_bounding_box[1].x:
                        all_nodes_bounding_box[1].x = node_loc.x
                    if node_loc.y > all_nodes_bounding_box[1].y:
                        all_nodes_bounding_box[1].y = node_loc.y
                    delete_me.append(n)
            grp_node = base_tree.nodes.new('MantisNodeGroup')
            grp_node.node_tree = bpy.data.node_groups[grp_name]
            bb_center = all_nodes_bounding_box[0].lerp(all_nodes_bounding_box[1],0.5)
            for n in grp_node.node_tree.nodes:
                n.location -= bb_center

            grp_node.location = Vector((all_nodes_bounding_box[0].x+200, all_nodes_bounding_box[0].lerp(all_nodes_bounding_box[1], 0.5).y))
            from .base_definitions import node_group_update
            grp_node.is_updating=True
            try:
                node_group_update(grp_node, force=True)
            finally:
                grp_node.is_updating=False

            # for each node in the JSON
            for n in selected_nodes[base_tree.name][2].values():
                for socket_collection in ['inputs', 'outputs']:
                    for s in n[socket_collection].values(): # for each socket in the node
                        if source := s.get("source"):
                            prGreen (s["name"], source[0], source[1])
                            base_tree_node=base_tree.nodes.get(source[0])
                            if s["is_output"]:
                                for output in base_tree_node.outputs:
                                    if output.identifier == source[1]:
                                        break
                                else:
                                    raise RuntimeError(wrapRed("Socket not found when grouping"))
                                base_tree.links.new(input=output, output=grp_node.inputs[s["name"]])
                            else:
                                for s_input in base_tree_node.inputs:
                                    if s_input.identifier == source[1]:
                                        break
                                else:
                                    raise RuntimeError(wrapRed("Socket not found when grouping"))
                                base_tree.links.new(input=grp_node.outputs[s["name"]], output=s_input)

            for n in delete_me: base_tree.nodes.remove(n)
            base_tree.nodes.active = grp_node
        finally: # MAKE SURE to turn it back to not exporting
            for path_item in context.space_data.path:
                path_item.node_tree.is_exporting = False

        grp_node.node_tree.name = "Group_Node.000"
        return {'FINISHED'}

class MantisEditGroup(Operator):
    """Edit the group referenced by the active node (or exit the current node-group)"""
    bl_idname = "mantis.edit_group"
    bl_label = "Edit Group"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            mantis_tree_poll_op(context)
        )

    def execute(self, context):
        space = context.space_data
        path = space.path
        node = path[len(path)-1].node_tree.nodes.active
        base_tree = path[0].node_tree
        live_update_start_state=base_tree.do_live_update
        base_tree.do_live_update = False
        base_tree.is_executing = True
        try:
            if hasattr(node, "node_tree"):
                if (node.node_tree):
                    path.append(node.node_tree, node=node)
                    path[0].node_tree.display_update(context)
                    return {"FINISHED"}
            elif len(path) > 1:
                path.pop()
                # get the active node in the current path
                active = path[len(path)-1].node_tree.nodes.active
                from .base_definitions import node_group_update
                active.is_updating = True
                try:
                    node_group_update(active, force = True)
                finally:
                    active.is_updating = False
                # call update to force the node group to check if its tree has changed
                # now we need to loop through the tree and update all node groups of this type.
                from .utilities.utilities import get_all_nodes_of_type
                for g in get_all_nodes_of_type(base_tree, "MantisNodeGroup") + \
                         get_all_nodes_of_type(base_tree, "MantisSchemaGroup"):
                    if g.node_tree == active.node_tree:
                        g.is_updating = True
                        active.is_updating = True
                        try:
                            node_group_update(g, force = True)
                        finally:
                            g.is_updating = False
                            active.is_updating = False
                base_tree.display_update(context)
                base_tree.is_executing = True
                # base_tree.is_executing = True # because it seems display_update unsets this.
        finally:
            base_tree.do_live_update = live_update_start_state
            base_tree.is_executing = False
            # HACK
            base_tree.handler_flip = True # HACK
            # HACK
            # I have no idea why but the operator finishing causes the exeuction handler to fire
            # I have no control over this since it happens after the execution returns...
            # so I have to do this ridiculous hack with a Boolean flip bit.
            return {"FINISHED"}

class MantisNewNodeTree(Operator):
    """Add a new Mantis tree."""
    bl_idname = "mantis.new_node_tree"
    bl_label = "New Node Group"
    bl_options = {'REGISTER', 'UNDO'}

    tree_invoked : bpy.props.StringProperty(options ={'HIDDEN'})
    node_invoked : bpy.props.StringProperty(options ={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return (
            mantis_tree_poll_op(context) and \
                context.node.bl_idname in ["MantisNodeGroup", "MantisSchemaGroup"]
        )


    @classmethod
    def poll(cls, context):
        return True #(hasattr(context, 'active_node') )

    def invoke(self, context, event):
        self.tree_invoked = context.node.id_data.name
        self.node_invoked = context.node.name
        return self.execute(context)

    def execute(self, context):
        node = bpy.data.node_groups[self.tree_invoked].nodes[self.node_invoked]
        if node.bl_idname == "MantisSchemaGroup":
            if (node.node_tree):
                print('a')
                return {"CANCELLED"}
            else:
                from bpy import data
                print('b')
                node.node_tree = data.node_groups.new(name='Schema Group', type='SchemaTree')
                return {'FINISHED'}
        elif node.bl_idname == "MantisNodeGroup":
            if (node.node_tree):
                print('c')
                return {"CANCELLED"}
            else:
                from bpy import data
                print('d')
                node.node_tree = data.node_groups.new(name='Mantis Group', type='MantisTree')
                return {'FINISHED'}
        else:
            return {"CANCELLED"}

class InvalidateNodeTree(Operator):
    """Invalidates this node tree, forcing it to read all data again."""
    bl_idname = "mantis.invalidate_node_tree"
    bl_label = "Clear Node Tree Cache"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (mantis_tree_poll_op(context))

    def execute(self, context):
        print("Clearing Active Node Tree cache")
        tree=context.space_data.path[0].node_tree
        tree.execution_id=''; tree.hash=''
        return {"FINISHED"}

class ExecuteNodeTree(Operator):
    """Execute this node tree"""
    bl_idname = "mantis.execute_node_tree"
    bl_label = "Execute Node Tree"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (mantis_tree_poll_op(context))

    def execute(self, context):
        from time import time
        from .utilities.utilities import wrapGreen

        tree=context.space_data.path[0].node_tree

        import cProfile
        from os import environ
        start_time = time()
        do_profile=False
        if environ.get("DOPROFILE"):
            do_profile=True
        pass_error = True
        if environ.get("DOERROR"):
            pass_error=False
        if do_profile:
            import pstats, io
            from pstats import SortKey
            with cProfile.Profile() as pr:
                tree.update_tree(context, error_popups = pass_error)
                tree.execute_tree(context, error_popups = pass_error, profile=True)
                # from the Python docs at https://docs.python.org/3/library/profile.html#module-cProfile
                s = io.StringIO()
                sortby = SortKey.TIME
                # sortby = SortKey.CUMULATIVE
                ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats(sortby)
                ps.print_stats(20) # print the top 20
                print(s.getvalue())

        else:
            tree.update_tree(context, error_popups = pass_error)
            tree.execute_tree(context, error_popups = pass_error)
        prGreen("Finished executing tree in %f seconds" % (time() - start_time))
        return {"FINISHED"}

class SelectNodesOfType(Operator):
    """Selects all nodes of same type as active node."""
    bl_idname = "mantis.select_nodes_of_type"
    bl_label = "Select Nodes of Same Type as Active"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (any_tree_poll(context))

    def execute(self, context):
        active_node = context.active_node
        tree = active_node.id_data
        if not hasattr(active_node, "node_tree"):
            for node in tree.nodes:
                node.select = (active_node.bl_idname == node.bl_idname)
        else:
            for node in tree.nodes:
                node.select = (active_node.bl_idname == node.bl_idname) and (active_node.node_tree == node.node_tree)

        return {"FINISHED"}

def get_parent_tree_interface_enum(operator, context):
    ret = []; i = -1
    tree = bpy.data.node_groups[operator.tree_invoked]
    for sock in tree.interface.items_tree:
        if sock.item_type == 'PANEL': continue
        if sock.in_out == "OUTPUT": continue
        ret.append( (sock.identifier, sock.name, "Socket from Node Group Input", i := i + 1), )
    return ret

def get_node_inputs_enum(operator, context):
    ret = []; i = -1
    n = bpy.data.node_groups[operator.tree_invoked].nodes[operator.node_invoked]
    for inp in n.inputs:
        ret.append( (inp.identifier, inp.name, "Socket of node to connect to.", i := i + 1), )
    return ret

class ConnectNodeToInput(Operator):
    """Connects a Node Group Input socket to specified socket of active node and all selected same-type nodes."""
    bl_idname = "mantis.connect_nodes_to_input"
    bl_label = "Connect Socket to Input for Selected Nodes"
    bl_options = {'REGISTER', 'UNDO'}

    group_output : bpy.props.EnumProperty(
        items=get_parent_tree_interface_enum,
        name="Node Group Input Socket",
        description="Select which socket from the Node Group Input to connect to this node",)
    node_input : bpy.props.EnumProperty(
        items=get_node_inputs_enum,
        name="Node Input Socket",
        description="Select which of this node's sockets to recieve the connection",)
    tree_invoked : bpy.props.StringProperty(options ={'HIDDEN'})
    world_invoked : bpy.props.StringProperty(options ={'HIDDEN'})
    material_invoked : bpy.props.StringProperty(options ={'HIDDEN'})
    node_invoked : bpy.props.StringProperty(options ={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        is_tree = (any_tree_poll(context))
        is_material = False
        if hasattr(context, 'space_data') and context.space_data.type == 'NODE_EDITOR':
            is_material = context.space_data.node_tree.bl_idname == 'ShaderNodeTree'
        return is_tree and not is_material # doesn't work for Material right now TODO

    def invoke(self, context, event):
        self.material_invoked=''; self.world_invoked=''
        self.tree_invoked = context.active_node.id_data.name
        if context.space_data.node_tree.bl_idname == 'ShaderNodeTree':
            if context.space_data.shader_type == 'WORLD':
                self.world_invoked = context.space_data.id.name
            elif context.space_data.shader_type == 'OBJECT':
                self.material_invoked = context.space_data.id.name
            else:
                return {'CANCELLED'} # what is the LINESTYLE menu? TODO
        self.node_invoked = context.active_node.name
        # we use active_node here ^ because we are comparing the active node to the selection.
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        if context.space_data.node_tree.bl_idname == 'ShaderNodeTree':
            if context.space_data.shader_type == 'WORLD':
                t = bpy.data.worlds[self.material_invoked].node_tree
            elif context.space_data.shader_type == 'OBJECT':
                t = bpy.data.materials[self.material_invoked].node_tree
        else:
            t = bpy.data.node_groups.get(self.tree_invoked)
        if hasattr(t, "is_executing"): # for Mantis trees, but this function should just work anywhere.
            t.is_executing = True
        n = t.nodes[self.node_invoked]
        for node in t.nodes:
            if n.bl_idname == node.bl_idname and node.select:
                # the bl_idname is the same so they both have node_tree
                if hasattr(n, "node_tree") and n.node_tree != node.node_tree: continue
                # TODO: maybe I should try and find a nearby input node and reuse it
                # doing these identifier lookups again and again is slow, whatever. faster than doing it by hand
                for connect_to_me in node.inputs:
                    if connect_to_me.identifier == self.node_input: break
                if connect_to_me.is_linked: connect_to_me = None
                if connect_to_me: # only make the node if the socket is there and free
                    inp = t.nodes.new("NodeGroupInput")
                    connect_me = None
                    for s in inp.outputs:
                        if s.identifier != self.group_output: s.hide = True
                        else: connect_me = s
                        inp.location = node.location
                        inp.location.x-=200
                    if connect_me is None:
                        continue # I don't know how this happens.
                    # TODO: this bit doesn't work in shader trees for some reason, fix it
                    t.links.new(input=connect_me, output=connect_to_me)

        if hasattr(t, "is_executing"):
            t.is_executing = False
        return {"FINISHED"}

class QueryNodeSockets(Operator):
    """Utility Operator for querying the data in a socket"""
    bl_idname = "mantis.query_sockets"
    bl_label = "Query Node Sockets"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (mantis_tree_poll_op(context))

    def execute(self, context):
        active_node = context.active_node
        tree = active_node.id_data
        for node in tree.nodes:
            if not node.select: continue
        return {"FINISHED"}

class FoceUpdateGroup(Operator):
    """Developer Tool to force a group update"""
    bl_idname = "mantis.force_update_group"
    bl_label = "Force Mantis Group Update"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (mantis_tree_poll_op(context))

    def execute(self, context):
        active_node = context.active_node
        from .base_definitions import node_group_update
        try:
            active_node.is_updating = True
            node_group_update(active_node, force=True)
        finally:
            active_node.is_updating = False
        return {"FINISHED"}

class ForceDisplayUpdate(Operator):
    """Utility Operator for querying the data in a socket"""
    bl_idname = "mantis.force_display_update"
    bl_label = "Force Mantis Display Update"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (mantis_tree_poll_op(context))

    def execute(self, context):
        base_tree = bpy.context.space_data.path[0].node_tree
        base_tree.display_update(context)
        return {"FINISHED"}

class CleanUpNodeGraph(bpy.types.Operator):
    """Clean Up Node Graph"""
    bl_idname = "mantis.nodes_cleanup"
    bl_label = "Clean Up Node Graph"
    bl_options = {'REGISTER', 'UNDO'}

    # num_iterations=bpy.props.IntProperty(default=8)


    @classmethod
    def poll(cls, context):
        return hasattr(context, 'active_node')

    def execute(self, context):
        base_tree=context.space_data.path[-1].node_tree
        from .utilities.utilities import SugiyamaGraph
        SugiyamaGraph(base_tree, 12)
        return {'FINISHED'}

class MantisMuteNode(Operator):
    """Mantis Test Operator"""
    bl_idname = "mantis.mute_node"
    bl_label = "Mute Node"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (mantis_tree_poll_op(context))

    def execute(self, context):
        path = context.space_data.path
        node = path[len(path)-1].node_tree.nodes.active
        node.mute = not node.mute
        # There should only be one of these
        if (enable := node.inputs.get("Enable")):
                # annoyingly, 'mute' and 'enable' are opposites
                enable.default_value = not node.mute
        # this one is for Deformers
        elif (enable := node.inputs.get("Enable in Viewport")):
                # annoyingly, 'mute' and 'enable' are opposites
                enable.default_value = not node.mute
        elif (hide := node.inputs.get("Hide")):
                hide.default_value = node.mute
        elif (hide := node.inputs.get("Hide in Viewport")):
                hide.default_value = node.mute
        return {"FINISHED"}

class DriverAddDriverVariableInput(bpy.types.Operator):
    """Add a Driver Variable input to the Driver node"""
    bl_idname = "mantis.driver_node_add_variable"
    bl_label = "Add Driver Variable"
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (hasattr(context, 'active_node') )

    def execute(self, context):           # unicode for 'a'
        i = len (context.node.inputs) - 2 + 96
        context.node.inputs.new("DriverVariableSocket", chr(i))
        return {'FINISHED'}

class DriverRemoveDriverVariableInput(bpy.types.Operator):
    """Remove a DriverVariable input from the active Driver node"""
    bl_idname = "mantis.driver_node_remove_variable"
    bl_label = "Remove Driver Variable"
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (hasattr(context, 'active_node') )

    def execute(self, context):
        n = context.node
        n.inputs.remove(n.inputs[-1])
        return {'FINISHED'}

class CollectionAddNewOutput(bpy.types.Operator):
    """Add a new Collection output to the Driver node"""
    bl_idname = "mantis.collection_add_new"
    bl_label = "+ Child"
    bl_options = {'REGISTER', 'UNDO'}

    collection_name : bpy.props.StringProperty(default='Collection')
    tree_invoked : bpy.props.StringProperty(options ={'HIDDEN'})
    node_invoked : bpy.props.StringProperty(options ={'HIDDEN'})
    socket_invoked : bpy.props.StringProperty(options ={'HIDDEN'}) # set by caller

    @classmethod
    def poll(cls, context):
        return True #(hasattr(context, 'active_node') )
    # DUPLICATED CODE HERE, DUMMY
    def invoke(self, context, event):
        self.tree_invoked = context.node.id_data.name
        self.node_invoked = context.node.name
        t = context.node.id_data
        t.nodes.active = context.node
        context.node.select = True
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        if not self.collection_name:
            return {'CANCELLED'}
        n = bpy.data.node_groups[self.tree_invoked].nodes[self.node_invoked]
        # we need to know which socket it is called from...
        s = None
        for socket in n.outputs:
            if socket.identifier == self.socket_invoked:
                s=socket; break
        parent_path = ''
        if s is not None and s.collection_path:
                parent_path = s.collection_path + '>'
        outer_dict = n.read_declarations_from_json()
        current_data = outer_dict
        if parent_path:
            for name_elem in parent_path.split('>'):
                if name_elem == '': continue # HACK around being a bad programmer
                current_data = current_data[name_elem]
        current_data[self.collection_name] = {}
        n.push_declarations_to_json(outer_dict)
        n.update_interface()
        return {'FINISHED'}

# TODO: should this prune the children, too?
class CollectionRemoveOutput(bpy.types.Operator):
    """Remove a Collection output to the Driver node"""
    bl_idname = "mantis.collection_remove"
    bl_label = "X"
    bl_options = {'REGISTER', 'UNDO'}

    tree_invoked : bpy.props.StringProperty(options ={'HIDDEN'})
    node_invoked : bpy.props.StringProperty(options ={'HIDDEN'})
    socket_invoked : bpy.props.StringProperty(options ={'HIDDEN'}) # set by caller

    @classmethod
    def poll(cls, context):
        return True #(hasattr(context, 'active_node') )
    # DUPLICATED CODE HERE, DUMMY
    def invoke(self, context, event):
        self.tree_invoked = context.node.id_data.name
        self.node_invoked = context.node.name
        t = context.node.id_data
        t.nodes.active = context.node
        context.node.select = True
        return self.execute(context)

    def execute(self, context):
        n = bpy.data.node_groups[self.tree_invoked].nodes[self.node_invoked]
        s = None
        for socket in n.outputs:
            if socket.identifier == self.socket_invoked:
                s=socket; break
        if not s:
            return {'CANCELLED'}
        parent_path = ''
        if s is not None and s.collection_path:
                parent_path = s.collection_path + '>'
        outer_dict = n.read_declarations_from_json()
        current_data = outer_dict
        print(parent_path)
        if parent_path:
            for name_elem in parent_path.split('>')[:-2]: # just skip the last one
                print(name_elem)
                if name_elem == '': continue # HACK around being a bad programmer
                current_data = current_data[name_elem]
        del current_data[s.name]
        n.push_declarations_to_json(outer_dict)
        n.update_interface()
        return {'FINISHED'}

def get_socket_enum(operator, context):
    valid_types = []; i = -1
    from .socket_definitions import TellClasses, MantisSocket
    for cls in TellClasses():
        if cls.is_valid_interface_type:
            valid_types.append( (cls.bl_idname, cls.bl_label, "Socket Type", i := i + 1), )
    return valid_types

class B4_4_0_Workaround_NodeTree_Interface_Update(Operator):
    """Selects all nodes of same type as active node."""
    bl_idname = "mantis.node_tree_interface_update_4_4_0_workaround"
    bl_label = "Add Socket to Node Tree"
    bl_options = {'REGISTER', 'UNDO'}

    socket_name : bpy.props.StringProperty()
    output : bpy.props.BoolProperty()
    socket_type  : bpy.props.EnumProperty(
        name="Socket Type",
        description="Socket Type",
        items=get_socket_enum,
        default=0,)

    tree_invoked : bpy.props.StringProperty(options ={'HIDDEN'})
    @classmethod
    def poll(cls, context):
        return (any_tree_poll(context))

    def invoke(self, context, event):
        self.tree_invoked = context.active_node.id_data.name
        # we use active_node here ^ because we are comparing the active node to the selection.
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        tree = bpy.data.node_groups[self.tree_invoked]
        in_out = 'OUTPUT' if self.output else 'INPUT'
        tree.interface.new_socket(self.socket_name, in_out=in_out, socket_type=self.socket_type)
        # try to prevent the next execution
        # because updating the interface triggers a depsgraph update.
        # this doesn't actually work though...TODO
        if tree.bl_idname == "MantisTree":
            tree.prevent_next_exec=True
        return {"FINISHED"}

class ConvertBezierCurveToNURBS(Operator):
    """Converts all bezier splines of curve to NURBS."""
    bl_idname = "mantis.convert_bezcrv_to_nurbs"
    bl_label = "Convert Bezier Curve to NURBS"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None) and (context.active_object.type=='CURVE')

    def execute(self, context):
        from .utilities.utilities import nurbs_copy_bez_spline
        curve = context.active_object
        bez=[]
        for spl in curve.data.splines:
            if spl.type=='BEZIER':
                bez.append(spl)
        for bez_spline in bez:
            new_spline=nurbs_copy_bez_spline(curve, bez_spline)

            curve.data.splines.remove(bez_spline)
        return {"FINISHED"}

def get_component_library_items(self, context):
    import json
    from .preferences import get_bl_addon_object
    bl_mantis_addon = get_bl_addon_object()
    return_value = [('NONE', 'None', 'None', 'ERROR', 0)]
    component_name_and_path={}
    if bl_mantis_addon:
        widgets_path = bl_mantis_addon.preferences.ComponentsLibraryFolder
        import os
        for path_root, dirs, files, in os.walk(widgets_path):
            for file in files:
                if file.endswith('.rig'):
                    filepath = os.path.join(path_root, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                        for tree_name in json_data.keys():
                            component_name_and_path[tree_name] = os.path.join(path_root, file)
    if component_name_and_path.keys():
        return_value=[]
        for i, (name, path) in enumerate(component_name_and_path.items()):
            return_value.append( ((path+"|"+name).upper(), name, path + ': ' + name, 'NODE_TREE', i) )
    return return_value

class ImportFromComponentLibrary(Operator):
    """Import a Mantis Component from your Component Library."""
    bl_idname = "mantis.import_from_component_library"
    bl_label = "Import From Component Library"
    bl_options = {'REGISTER', 'UNDO'}
    default_value  : bpy.props.EnumProperty(
            items=get_component_library_items,
            name="Component",
            description="Which Component to Import",
            default = 0,
        )

    @classmethod
    def poll(cls, context):
        return True # probably not best to do a True for this LOL

    def execute(self, context):
        return {"FINISHED"}

from os import environ
if environ.get("DOERROR"): # this should only be available to devs
    class TestMantisVersioning(Operator):
        """Utility Operator for testing Mantis Versioning"""
        bl_idname = "mantis.test_versioning"
        bl_label = "Test Mantis Versioning"
        bl_options = {'REGISTER', 'UNDO'}

        tree_invoked : bpy.props.StringProperty(options ={'HIDDEN'})
        node_invoked : bpy.props.StringProperty(options ={'HIDDEN'})

        @classmethod
        def poll(cls, context):
            return (mantis_tree_poll_op(context))
        
        def invoke(self, context, event):
            self.tree_invoked = bpy.context.space_data.path[-1].node_tree.name
            self.node_invoked = bpy.context.space_data.path[-1].node_tree.nodes.active.name
            return self.execute(context)

        def execute(self, context):
            tree = bpy.data.node_groups[self.tree_invoked]
            node = tree.nodes[self.node_invoked]
            from .versioning import up_0_13_0_new_custom_prop_node
            print ("testing...")
            up_0_13_0_new_custom_prop_node(node=node, tree=tree)
            return {"FINISHED"}

# this has to be down here for some reason. what a pain
classes = [
        MantisGroupNodes,
        MantisEditGroup,
        MantisNewNodeTree,
        InvalidateNodeTree,
        ExecuteNodeTree,
        # CreateMetaGroup,
        QueryNodeSockets,
        FoceUpdateGroup,
        ForceDisplayUpdate,
        CleanUpNodeGraph,
        MantisMuteNode,
        SelectNodesOfType,
        ConnectNodeToInput,
        # Driver
        DriverAddDriverVariableInput,
        DriverRemoveDriverVariableInput,
        # managing collections
        CollectionAddNewOutput,
        CollectionRemoveOutput,
        # rigging utilities
        ConvertBezierCurveToNURBS,
        # component library
        ImportFromComponentLibrary,
        ]
if (bpy.app.version >= (4, 4, 0)):
    classes.append(B4_4_0_Workaround_NodeTree_Interface_Update)
if environ.get("DOERROR"):
    classes.append(TestMantisVersioning)

def TellClasses():
    return classes

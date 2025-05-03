import bpy
from bpy.types import Operator
from mathutils import Vector

from .utilities import (prRed, prGreen, prPurple, prWhite,
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

            from .i_o import export_to_json, do_import
            from random import random
            grp_name = "".join([chr(int(random()*30)+35) for i in range(20)])
            trees=[base_tree]
            selected_nodes=export_to_json(trees, write_file=False, only_selected=True)
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
                for s in n["sockets"].values(): # for each socket in the node
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
                from .utilities import get_all_nodes_of_type
                for g in get_all_nodes_of_type(base_tree, "MantisNodeGroup"):
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
            base_tree.do_live_update = True
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
        from .utilities import wrapGreen
        
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
                tree.execute_tree(context, error_popups = pass_error)
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
    node_invoked : bpy.props.StringProperty(options ={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return (any_tree_poll(context))

    def invoke(self, context, event):
        self.tree_invoked = context.active_node.id_data.name
        self.node_invoked = context.active_node.name
        # we use active_node here ^ because we are comparing the active node to the selection.
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        t = bpy.data.node_groups[self.tree_invoked]
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
        from .utilities import SugiyamaGraph
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
        if (hide := node.inputs.get("Hide")):
                hide.default_value = node.mute
        return {"FINISHED"}

ePropertyType =(
        ('BOOL'  , "Boolean", "Boolean", 0),
        ('INT'   , "Integer", "Integer", 1),
        ('FLOAT' , "Float"  , "Float"  , 2),
        ('VECTOR', "Vector" , "Vector" , 3),
        ('STRING', "String" , "String" , 4),
        #('ENUM'  , "Enum"   , "Enum"   , 5),
    )
    

from .base_definitions import xFormNode


class AddCustomProperty(bpy.types.Operator):
    """Add Custom Property to xForm Node"""
    bl_idname = "mantis.add_custom_property"
    bl_label = "Add Custom Property"
    bl_options = {'REGISTER', 'UNDO'}


    prop_type : bpy.props.EnumProperty(
        items=ePropertyType,
        name="New Property Type",
        description="Type of data for new Property",
        default = 'BOOL',)
    prop_name  : bpy.props.StringProperty(default='Prop')
    
    min:bpy.props.FloatProperty(default = 0)
    max:bpy.props.FloatProperty(default = 1)
    soft_min:bpy.props.FloatProperty(default = 0)
    soft_max:bpy.props.FloatProperty(default = 1)
    description:bpy.props.StringProperty(default = "")
    
    tree_invoked : bpy.props.StringProperty(options ={'HIDDEN'})
    node_invoked : bpy.props.StringProperty(options ={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return True #( hasattr(context, 'node') ) 

    def invoke(self, context, event):
        self.tree_invoked = context.node.id_data.name
        self.node_invoked = context.node.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
    def execute(self, context):
        n = bpy.data.node_groups[self.tree_invoked].nodes[self.node_invoked]
        # For whatever reason, context.node doesn't exist anymore
        #   (probably because I use a window to execute)
        # so as a sort of dumb workaround I am saving it to a hidden
        #  property of the operator... it works but Blender complains.
        socktype = ''
        if not (self.prop_name):
            self.report({'ERROR_INVALID_INPUT'}, "Must name the property.")
            return {'CANCELLED'}
        if self.prop_type == 'BOOL':
            socktype = 'ParameterBoolSocket'
        if self.prop_type == 'INT':
            socktype = 'ParameterIntSocket'
        if self.prop_type == 'FLOAT':
            socktype = 'ParameterFloatSocket'
        if self.prop_type == 'VECTOR':
            socktype = 'ParameterVectorSocket'
        if self.prop_type == 'STRING':
            socktype = 'ParameterStringSocket'
        #if self.prop_type == 'ENUM':
        #    sock_type = 'ParameterStringSocket'
        if (s := n.inputs.get(self.prop_name)):
            try:
                number = int(self.prop_name[-3:])
                # see if it has a number
                number+=1
                self.prop_name = self.prop_name[:-3] + str(number).zfill(3)
            except ValueError:
                self.prop_name+='.001'
                # WRONG # HACK # TODO # BUG #
        new_prop = n.inputs.new( socktype, self.prop_name)
        if self.prop_type in ['INT','FLOAT']:
            new_prop.min = self.min
            new_prop.max = self.max
            new_prop.soft_min = self.soft_min
            new_prop.soft_max = self.soft_max
        new_prop.description = self.description
        # now do the output
        n.outputs.new( socktype, self.prop_name)
        
        return {'FINISHED'}

def main_get_existing_custom_properties(operator, context):
    ret = []; i = -1
    n = bpy.data.node_groups[operator.tree_invoked].nodes[operator.node_invoked]
    for inp in n.inputs:
        if 'Parameter' in inp.bl_idname:
            ret.append( (inp.identifier, inp.name, "Custom Property to Modify", i := i + 1), )
    return ret
            

class EditCustomProperty(bpy.types.Operator):
    """Edit Custom Property"""
    bl_idname = "mantis.edit_custom_property"
    bl_label = "Edit Custom Property"
    bl_options = {'REGISTER', 'UNDO'}

    def get_existing_custom_properties(self, context):
        return main_get_existing_custom_properties(self, context)

    prop_edit : bpy.props.EnumProperty(
        items=get_existing_custom_properties,
        name="Property to Edit?",
        description="Select which property to edit",)
    prop_type : bpy.props.EnumProperty(
        items=ePropertyType,
        name="New Property Type",
        description="Type of data for new Property",
        default = 'BOOL',)
    prop_name  : bpy.props.StringProperty(default='Prop')
    min:bpy.props.FloatProperty(default = 0)
    max:bpy.props.FloatProperty(default = 1)
    soft_min:bpy.props.FloatProperty(default = 0)
    soft_max:bpy.props.FloatProperty(default = 1)
    description:bpy.props.StringProperty(default = "") # TODO: use getters to fill these automatically
    
    tree_invoked : bpy.props.StringProperty(options ={'HIDDEN'})
    node_invoked : bpy.props.StringProperty(options ={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return True #( hasattr(context, 'node') ) 

    def invoke(self, context, event):
        self.tree_invoked = context.node.id_data.name
        self.node_invoked = context.node.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
    def execute(self, context):
        n = bpy.data.node_groups[self.tree_invoked].nodes[self.node_invoked]
        prop = n.inputs.get( self.prop_edit )
        if prop:
            prop.name = self.prop_name
            if (s := n.inputs.get(self.prop_edit)):
                if self.prop_type in ['INT','FLOAT']:
                    prop.min = self.min
                    prop.max = self.max
                    prop.soft_min = self.soft_min
                    prop.soft_max = self.soft_max
                prop.description = self.description
            return {'FINISHED'}
        else:
            self.report({'ERROR_INVALID_INPUT'}, "Cannot edit a property that does not exist.")



class RemoveCustomProperty(bpy.types.Operator):
    """Remove a Custom Property from an xForm Node"""
    bl_idname = "mantis.remove_custom_property"
    bl_label = "Remove Custom Property"
    bl_options = {'REGISTER', 'UNDO'}

    def get_existing_custom_properties(self, context):
        return main_get_existing_custom_properties(self, context)
    
    prop_remove : bpy.props.EnumProperty(
        items=get_existing_custom_properties,
        name="Property to remove?",
        description="Select which property to remove",)
    tree_invoked : bpy.props.StringProperty(options ={'HIDDEN'})
    node_invoked : bpy.props.StringProperty(options ={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return True #(hasattr(context, 'active_node') )

    def invoke(self, context, event):
        self.tree_invoked = context.node.id_data.name
        self.node_invoked = context.node.name
        t = context.node.id_data
        # HACK the props dialog makes this necesary
        #  because context.node only exists during the event that
        #  was created by clicking on the node.
        t.nodes.active = context.node # HACK
        context.node.select = True # HACK
        # I need this bc of the callback for the enum property.
        #  for whatever reason I can't use tree_invoked there
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
    def execute(self, context):
        n = bpy.data.node_groups[self.tree_invoked].nodes[self.node_invoked]
        # For whatever reason, context.node doesn't exist anymore
        #   (probably because I use a window to execute)
        # so as a sort of dumb workaround I am saving it to a hidden
        #  property of the operator... it works.
        for i, inp in enumerate(n.inputs):
            if inp.identifier == self.prop_remove:
                break
        else:
            self.report({'ERROR'}, "Input not found")
            return {'CANCELLED'}
        # it's possible that the output property's identifier isn't the
        #   exact same... but I don' care. Shouldn't ever happen. TODO
        for j, out in enumerate(n.outputs):
            if out.identifier == self.prop_remove:
                break
        else:
            self.report({'ERROR'}, "Output not found")
            raise RuntimeError("This should not happen!")
        n.inputs.remove ( n.inputs [i] )
        n.outputs.remove( n.outputs[j] )
        return {'FINISHED'}



# SIMPLE node operators...
# May rewrite these in a more generic way later
class FcurveAddKeyframeInput(bpy.types.Operator):
    """Add a keyframe input to the fCurve node"""
    bl_idname = "mantis.fcurve_node_add_kf"
    bl_label = "Add Keyframe"
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (hasattr(context, 'active_node') )

    def execute(self, context):
        num_keys = len( context.node.inputs)-1
        context.node.inputs.new("KeyframeSocket", "Keyframe."+str(num_keys).zfill(3))
        return {'FINISHED'}

class FcurveRemoveKeyframeInput(bpy.types.Operator):
    """Remove a keyframe input from the fCurve node"""
    bl_idname = "mantis.fcurve_node_remove_kf"
    bl_label = "Remove Keyframe"
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}
        
    @classmethod
    def poll(cls, context):
        return (hasattr(context, 'active_node') )

    def execute(self, context):
        n = context.node
        n.inputs.remove(n.inputs[-1])
        return {'FINISHED'}

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
        
class LinkArmatureAddTargetInput(bpy.types.Operator):
    """Add a Driver Variable input to the Driver node"""
    bl_idname = "mantis.link_armature_node_add_target"
    bl_label = "Add Target"
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return hasattr(context, 'node')

    def execute(self, context):           # unicode for 'a'
        num_targets = len( list(context.node.inputs)[6:])//2
        context.node.inputs.new("xFormSocket", "Target."+str(num_targets).zfill(3))
        context.node.inputs.new("FloatFactorSocket", "Weight."+str(num_targets).zfill(3))
        return {'FINISHED'}


class LinkArmatureRemoveTargetInput(bpy.types.Operator):
    """Remove a DriverVariable input from the active Driver node"""
    bl_idname = "mantis.link_armature_node_remove_target"
    bl_label = "Remove Target"
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}
        
    @classmethod
    def poll(cls, context):
        return hasattr(context, 'node')

    def execute(self, context):
        n = context.node
        n.inputs.remove(n.inputs[-1]); n.inputs.remove(n.inputs[-1])
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
        from .utilities import nurbs_copy_bez_spline
        curve = context.active_object
        bez=[]
        for spl in curve.data.splines:
            if spl.type=='BEZIER':
                bez.append(spl)
        for bez_spline in bez:
            new_spline=nurbs_copy_bez_spline(curve, bez_spline)
            
            curve.data.splines.remove(bez_spline)
        return {"FINISHED"}


# this has to be down here for some reason. what a pain
classes = [
        MantisGroupNodes,
        MantisEditGroup,
        MantisNewNodeTree,
        ExecuteNodeTree,
        # CreateMetaGroup,
        QueryNodeSockets,
        ForceDisplayUpdate,
        CleanUpNodeGraph,
        MantisMuteNode,
        SelectNodesOfType,
        ConnectNodeToInput,
        # xForm
        AddCustomProperty,
        EditCustomProperty,
        RemoveCustomProperty,
        # EditFCurveNode,
        FcurveAddKeyframeInput,
        FcurveRemoveKeyframeInput,
        # Driver
        DriverAddDriverVariableInput,
        DriverRemoveDriverVariableInput,
        # Armature Link Node
        LinkArmatureAddTargetInput,
        LinkArmatureRemoveTargetInput,
        # rigging utilities
        ConvertBezierCurveToNURBS,
        ]
if (bpy.app.version >= (4, 4, 0)):
    classes.append(B4_4_0_Workaround_NodeTree_Interface_Update)

def TellClasses():
    return classes
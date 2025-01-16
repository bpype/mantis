import bpy
from bpy.types import Operator
from mathutils import Vector

from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

def TellClasses():
    return [
        MantisGroupNodes,
        MantisEditGroup,
        ExecuteNodeTree,
        # CreateMetaGroup,
        QueryNodeSockets,
        ForceDisplayUpdate,
        CleanUpNodeGraph,
        MantisMuteNode,
        MantisVisualizeOutput,
        TestOperator,
        # xForm
        AddCustomProperty,
        EditCustomProperty,
        RemoveCustomProperty,
        # Fcurve
        # EditFCurveNode,
        FcurveAddKeyframeInput,
        FcurveRemoveKeyframeInput,
        # Driver
        DriverAddDriverVariableInput,
        DriverRemoveDriverVariableInput,
        # Armature Link Node
        LinkArmatureAddTargetInput,
        LinkArmatureRemoveTargetInput,]
        # ExportNodeTreeToJSON,]

def mantis_tree_poll_op(context):
    # return True
    space = context.space_data
    if hasattr(space, "node_tree"):
        if (space.node_tree):
            return (space.tree_type == "MantisTree")
    return False


def get_override(active=None, edit=False, selected=[], type='VIEW_3D'):
    #no clue what this does... taken from sorcar
    override = bpy.context.copy()
    if (type == 'VIEW_3D'):
        override["active_object"] = active
        if (edit):
            override["edit_object"] = active
        if (active not in selected):
            selected.append(active)
        override["selected_object"] = selected
    flag = False
    for window in bpy.data.window_managers[0].windows:
        for area in window.screen.areas:
            if area.type == type:
                override["area"] = area
                override["region"] = [i for i in area.regions if i.type == 'WINDOW'][0]
                flag = True
                break
        if (flag):
            break
    return override

def ChooseNodeGroupNode(treetype):
    #I don't need this anymore... but I'm leaving it here
    #  because this is a useful thing to separate
    #  in case I add multiple tree types in the future
    if (treetype == "MantisTree"):
        return "MantisNodeGroup"
    # if (treetype == "LinkTree"):
    #     return "linkGroupNode"

#########################################################################3

class MantisGroupNodes(Operator):
    """Create node-group from selected nodes"""
    bl_idname = "mantis.group_nodes"
    bl_label = "Group Nodes"

    @classmethod
    def poll(cls, context):
        return mantis_tree_poll_op(context)

    def execute(self, context):
        base_tree=context.space_data.path[-1].node_tree
        base_tree.is_exporting = True

        from .i_o import export_to_json, do_import
        from random import random
        grp_name = "".join([chr(int(random()*30)+35) for i in range(20)])
        trees=[base_tree]
        selected_nodes=export_to_json(trees, write_file=False, only_selected=True)
        selected_nodes[base_tree.name][0]["name"]=grp_name
        # this is for debugging the result of the export
        # for k,v in selected_nodes[base_tree.name][2].items():
        #     prPurple(k)
        #     for k1, v1 in v["sockets"].items():
        #         prRed("    ", k1, v1["name"])
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
                if n.location.x < all_nodes_bounding_box[0].x:
                    all_nodes_bounding_box[0].x = n.location.x
                if n.location.y < all_nodes_bounding_box[0].y:
                    all_nodes_bounding_box[0].y = n.location.y
                #
                if n.location.x > all_nodes_bounding_box[1].x:
                    all_nodes_bounding_box[1].x = n.location.x
                if n.location.y > all_nodes_bounding_box[1].y:
                    all_nodes_bounding_box[1].y = n.location.y
                delete_me.append(n)
        grp_node = base_tree.nodes.new('MantisNodeGroup')
        grp_node.node_tree = bpy.data.node_groups[grp_name]
        bb_center = all_nodes_bounding_box[0].lerp(all_nodes_bounding_box[1],0.5)
        for n in grp_node.node_tree.nodes:
            n.location -= bb_center

        grp_node.location = Vector((all_nodes_bounding_box[0].x+200, all_nodes_bounding_box[0].lerp(all_nodes_bounding_box[1], 0.5).y))

        # for l in selected_nodes[base_tree.name][3]:
        #     if source := l.get("source"):
        #         n_from = base_tree.nodes.get(source[0])
        #         # s_from = n_from.

        for n in selected_nodes[base_tree.name][2].values():
            for s in n["sockets"].values():
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

        base_tree.is_exporting = False
        grp_node.node_tree.name = "Group_Node.000"
        return {'FINISHED'}

class MantisEditGroup(Operator):
    """Edit the group referenced by the active node (or exit the current node-group)"""
    bl_idname = "mantis.edit_group"
    bl_label = "Edit Group"

    @classmethod
    def poll(cls, context):
        return (
            mantis_tree_poll_op(context)
        )

    def execute(self, context):
        space = context.space_data
        path = space.path
        node = path[len(path)-1].node_tree.nodes.active

        if hasattr(node, "node_tree"):
            if (node.node_tree):
                path.append(node.node_tree, node=node)
                path[0].node_tree.display_update(context)
                return {"FINISHED"}
        elif len(path) > 1:
            path.pop()
            path[0].node_tree.display_update(context)
            # get the active node in the current path
            path[len(path)-1].node_tree.nodes.active.update() # call update to force the node group to check if its tree has changed
        return {"CANCELLED"}

class ExecuteNodeTree(Operator):
    """Execute this node tree"""
    bl_idname = "mantis.execute_node_tree"
    bl_label = "Execute Node Tree"

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
        print (environ.get("DOPROFILE"))
        if environ.get("DOPROFILE"):
            do_profile=True
        if do_profile:
            # cProfile.runctx("tree.update_tree(context)", None, locals())
            # cProfile.runctx("tree.execute_tree(context)", None, locals())
            # import hunter
            # hunter.trace(stdlib=False, action=hunter.CallPrinter(force_colors=False))
            # tree.update_tree(context)
            # tree.execute_tree(context)
            # return {"FINISHED"}
            import pstats, io
            from pstats import SortKey
            with cProfile.Profile() as pr:
                tree.update_tree(context)
                tree.execute_tree(context)
                # from the Python docs at https://docs.python.org/3/library/profile.html#module-cProfile
                s = io.StringIO()
                sortby = SortKey.TIME
                # sortby = SortKey.CUMULATIVE
                ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats(sortby)
                ps.print_stats(20) # print the top 20
                print(s.getvalue())

        else:
            tree.update_tree(context)
            tree.execute_tree(context)
        prGreen("Finished executing tree in %f seconds" % (time() - start_time))
        return {"FINISHED"}

# class CreateMetaGroup(Operator):
    # """Create Meta Rig group node"""
    # bl_idname = "mantis.create_meta_group"
    # bl_label = "Create Meta Rig group node"

    # @classmethod
    # def poll(cls, context):
        # return (mantis_tree_poll_op(context))

    # def execute(self, context):
        # space = context.space_data
        # path = space.path
        # node_tree = space.path[len(path)-1].node_tree
        # # selected_nodes = [i for i in node_tree.nodes if i.select]
        # ob = bpy.context.active_object
        # matrices_build = []
        # if (ob):
            # if (ob.type == 'ARMATURE'):
                # for pb in ob.pose.bones:
                    # matrices_build.append((pb.name, pb.matrix, pb.length))
        # xloc = -400
        # yloc = 400
        # loops = 0
        # node_group = bpy.data.node_groups.new(ob.name, space.tree_type) 
        # group_node = node_tree.nodes.new("MantisNodeGroup")
        # group_output = node_group.nodes.new("NodeGroupOutput")
        # path.append(node_group, node=group_node)
        # group_node.node_tree = node_group
        # gTree = group_node.node_tree
        # for name, m, length in matrices_build:
            # n = gTree.nodes.new("MetaRigMatrixNode")
            # n.first_row = m[0]
            # n.second_row = m[1]
            # n.third_row = m[2]
            # n.fourth_row = [m[3][0], m[3][1], m[3][2], length]
            # print (n.fourth_row[3])
            # n.name = name
            # n.label = name
            # n.location = (xloc + loops*250, yloc)
            # if (yloc > -800):
                # yloc-=55
            # else:
                # loops+=1
                # yloc = 400
            # node_group.links.new(n.outputs["Matrix"], group_output.inputs[''])
            # node_group.outputs["Matrix"].name = name
        # return {"FINISHED"}


class QueryNodeSockets(Operator):
    """Utility Operator for querying the data in a socket"""
    bl_idname = "mantis.query_sockets"
    bl_label = "Query Node Sockets"

    @classmethod
    def poll(cls, context):
        return (mantis_tree_poll_op(context))

    def execute(self, context):
        node = context.active_node
        print ("Node type: ", node.bl_idname)
        
        # This is useful. Todo: reimplement this eventually.
        
        return {"FINISHED"}


class ForceDisplayUpdate(Operator):
    """Utility Operator for querying the data in a socket"""
    bl_idname = "mantis.force_display_update"
    bl_label = "Force Mantis Display Update"

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


class MantisVisualizeOutput(Operator):
    """Mantis Visualize Output Operator"""
    bl_idname = "mantis.visualize_output"
    bl_label = "Visualize Output"

    @classmethod
    def poll(cls, context):
        return (mantis_tree_poll_op(context))

    def execute(self, context):
        from time import time
        from .utilities import wrapGreen, prGreen
        
        tree=context.space_data.path[0].node_tree
        tree.update_tree(context)
        # tree.execute_tree(context)
        prGreen(f"Visualize Tree: {tree.name}")
        nodes = tree.parsed_tree
        from .readtree import visualize_tree
        visualize_tree(nodes, tree, context)
        return {"FINISHED"}


class TestOperator(Operator):
    """Mantis Test Operator"""
    bl_idname = "mantis.test_operator"
    bl_label = "Mantis Test Operator"

    @classmethod
    def poll(cls, context):
        return (mantis_tree_poll_op(context))

    def execute(self, context):
        path = context.space_data.path
        base_tree = path[0].node_tree
        tree = path[len(path)-1].node_tree
        node = tree.nodes.active
        node.display_update(base_tree.parsed_tree, context)
        # from .base_definitions import get_signature_from_edited_tree
        # if nc := base_tree.parsed_tree.get(get_signature_from_edited_tree(node, context)):
        #     from .utilities import get_all_dependencies
        #     deps = get_all_dependencies(nc)
        #     self.report({'INFO'}, f"Number of Node Dependencies: {len(deps)}")
        #     # for n in deps:
        #     #     prGreen(n)
        # else:
        #     # prRed("No NC found in parsed tree.")
        #     self.report({'ERROR_INVALID_CONTEXT'}, "No data for node.")
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
    
    node_invoked : bpy.props.PointerProperty(type=bpy.types.Node, 
                options ={'HIDDEN'}) # note this seems to affect all
                                     # subsequent properties

    @classmethod
    def poll(cls, context):
        return True #( hasattr(context, 'node') ) 

    def invoke(self, context, event):
        self.node_invoked = context.node
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
    def execute(self, context):
        n = self.node_invoked
        # For whatever reason, context.node doesn't exist anymore
        #   (probably because I use a window to execute)
        # so as a sort of dumb workaround I am saving it to a hidden
        #  property of the operator... it works.
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

#DOESN'T WORK YET
class EditCustomProperty(bpy.types.Operator):
    """Edit Custom Property"""
    bl_idname = "mantis.edit_custom_property"
    bl_label = "Edit Custom Property"


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
    
    node_invoked : bpy.props.PointerProperty(type=bpy.types.Node, 
                options ={'HIDDEN'}) # note this seems to affect all
                                     # subsequent properties

    @classmethod
    def poll(cls, context):
        return True #( hasattr(context, 'node') ) 

    def invoke(self, context, event):
        self.node_invoked = context.node
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
    def execute(self, context):
        n = self.node_invoked
        prop = n.inputs.get( self.prop_name )
        if (s := n.inputs.get(self.prop_name)):
            if self.prop_type in ['INT','FLOAT']:
                new_prop.min = self.min
                new_prop.max = self.max
                new_prop.soft_min = self.soft_min
                new_prop.soft_max = self.soft_max
            new_prop.description = self.description
        
        return {'FINISHED'}



class RemoveCustomProperty(bpy.types.Operator):
    """Remove a Custom Property from an xForm Node"""
    bl_idname = "mantis.remove_custom_property"
    bl_label = "Remove Custom Property"

    def get_existing_custom_properties(self, context):
        ret = []; i = -1
        n = context.active_node
        for inp in n.inputs:
            if 'Parameter' in inp.bl_idname:
                ret.append( (inp.identifier, inp.name, "Parameter to remove", i := i + 1), )
        if ret:
            return ret
        return None
                

    prop_remove : bpy.props.EnumProperty(
        items=get_existing_custom_properties,
        name="Property to remove?",
        description="Select which property to remove",)
    node_invoked : bpy.props.PointerProperty(type=bpy.types.Node, 
                options ={'HIDDEN'}) # note this seems to affect all
                                     # subsequent properties

    @classmethod
    def poll(cls, context):
        return True #(hasattr(context, 'active_node') )

    def invoke(self, context, event):
        print (context.node)
        self.node_invoked = context.node
        t = context.node.id_data
        # HACK the props dialog makes this necesary
        #  because context.node only exists during the event that
        #  was created by clicking on the node.
        t.nodes.active = context.node # HACK
        context.node.select = True # HACK
        # I need this bc of the callback for the enum property.
        #  for whatever reason I can't use node_invoked there
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
    def execute(self, context):
        n = self.node_invoked
        # For whatever reason, context.node doesn't exist anymore
        #   (probably because I use a window to execute)
        # so as a sort of dumb workaround I am saving it to a hidden
        #  property of the operator... it works.
        for i, inp in enumerate(n.inputs):
            if inp.identifier == self.prop_remove:
                break
        else:
            self.report({'ERROR'}, "Input not found")
            raise RuntimeError("This should not happen!")
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


# TODO: not a priority
#  This one will remove the old socket and add a new one
#  and it'll put it back in place and reconnect the links
#   It's OK to just ask the user to do this manually for now
#
 # class EditCustomProperty(bpy.types.Operator):
    # """Edit Custom Property in xForm Node"""
    # bl_idname = "mantis.edit_custom_property"
    # bl_label = "Edit Custom Property"


    # prop_type : bpy.props.EnumProperty(
        # items=ePropertyType,
        # name="New Property Type",
        # description="Type of data for new Property",
        # default = 'BOOL',)
    # prop_name  : bpy.props.StringProperty(default='Prop')
    
    # min:bpy.props.FloatProperty(default = 0)
    # max:bpy.props.FloatProperty(default = 1)
    # soft_min:bpy.props.FloatProperty(default = 0)
    # soft_max:bpy.props.FloatProperty(default = 1)
    # description:bpy.props.StringProperty(default = "")
    
    # node_invoked : bpy.props.PointerProperty(type=bpy.types.Node, 
                # options ={'HIDDEN'}) # note this seems to affect all
                                     # # subsequent properties

    # @classmethod
    # def poll(cls, context):
        # return True #( hasattr(context, 'node') ) 

    # def invoke(self, context, event):
        # print (context.node)
        # self.node_invoked = context.node
        # print(dir(self))
        # wm = context.window_manager
        # return wm.invoke_props_dialog(self)
        
    # def execute(self, context):
        # n = self.node_invoked
        # # For whatever reason, context.node doesn't exist anymore
        # #   (probably because I use a window to execute)
        # # so as a sort of dumb workaround I am saving it to a hidden
        # #  property of the operator... it works.
        # socktype = ''
        # if not (self.prop_name):
            # self.report({'ERROR_INVALID_INPUT'}, "Must name the property.")
            # return {'CANCELLED'}
        # if self.prop_type == 'BOOL':
            # socktype = 'ParameterBoolSocket'
        # if self.prop_type == 'INT':
            # socktype = 'ParameterIntSocket'
        # if self.prop_type == 'FLOAT':
            # socktype = 'ParameterFloatSocket'
        # if self.prop_type == 'VECTOR':
            # socktype = 'ParameterVectorSocket'
        # if self.prop_type == 'STRING':
            # socktype = 'ParameterStringSocket'
        # #if self.prop_type == 'ENUM':
        # #    sock_type = 'ParameterStringSocket'
        # if (s := n.inputs.get(self.prop_name)):
            # try:
                # number = int(self.prop_name[-3:])
                # # see if it has a number
                # number+=1
                # self.prop_name = self.prop_name[:-3] + str(number).zfill(3)
            # except ValueError:
                # self.prop_name+='.001'
        # new_prop = n.inputs.new( socktype, self.prop_name)
        # if self.prop_type in ['INT','FLOAT']:
            # new_prop.min = self.min
            # new_prop.max = self.max
            # new_prop.soft_min = self.soft_min
            # new_prop.soft_max = self.soft_max
        # new_prop.description = self.description
            
            
        # return {'FINISHED'}

class EditFCurveNode(bpy.types.Operator):
    """Edit the fCurve owned by fCurve node"""
    bl_idname = "mantis.edit_fcurve_node"
    bl_label = "Edit fCurve"
    bl_options = {'INTERNAL'}
    
    my_window : bpy.props.StringProperty(default = "-1")
    node_invoked : bpy.props.PointerProperty(type=bpy.types.Node, 
                options ={'HIDDEN'}) # note this seems to affect all
                                     # subsequent properties
    fake_fcurve_ob: bpy.props.PointerProperty(
                type=bpy.types.Object, 
                options ={'HIDDEN'},)
    prev_active: bpy.props.PointerProperty(
                type=bpy.types.Object, 
                options ={'HIDDEN'},)
    

    @classmethod
    def poll(cls, context):
        return True #(hasattr(context, 'active_node') )

    def modal(self, context, event):
        for w in context.window_manager.windows:
            if str(w.as_pointer()) == self.my_window:
                break
        else:
            context.scene.collection.objects.unlink( self.fake_fcurve_ob )
            context.view_layer.objects.active = self.prev_active
            self.prev_active.select_set(True)
            # at this point I will push the fcurve to nodes
            #  or some kind of internal data
            return {'FINISHED'}
        # I can't currently think of anything I need to do with w
        return {'PASS_THROUGH'}
        
        
    def invoke(self, context, event):
        self.node_invoked = context.node
        self.fake_fcurve_ob = self.node_invoked.fake_fcurve_ob
        context.scene.collection.objects.link( self.fake_fcurve_ob )
        self.prev_active = context.view_layer.objects.active
        context.view_layer.objects.active = self.fake_fcurve_ob
        self.fake_fcurve_ob.select_set(True)
        context.window_manager.modal_handler_add(self)
        # this is added to the active window.
        if (self.my_window == "-1"):
            prev_windows = set()
            for w in context.window_manager.windows:
                prev_windows.add(w.as_pointer())
            bpy.ops.wm.window_new()
            for w in context.window_manager.windows:
                w_int = w.as_pointer()
                if (w_int not in prev_windows):
                    self.my_window = str(w_int)
                    break
            else:
                print ("cancelled")
                return {'CANCELLED'}
            # set up properties for w
            # w.height = 256 # READ
            # w.width = 400  # ONLY
            w.screen.areas[0].type = 'GRAPH_EDITOR'
            w.screen.areas[0].spaces[0].auto_snap = 'NONE'
            
        return {'RUNNING_MODAL'}


# SIMPLE node operators...
# May rewrite these in a more generic way later
class FcurveAddKeyframeInput(bpy.types.Operator):
    """Add a keyframe input to the fCurve node"""
    bl_idname = "mantis.fcurve_node_add_kf"
    bl_label = "Add Keyframe"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return (hasattr(context, 'active_node') )

    def execute(self, context):
        num_keys = len( context.node.inputs)
        context.node.inputs.new("KeyframeSocket", "Keyframe."+str(num_keys).zfill(3))
        return {'FINISHED'}

class FcurveRemoveKeyframeInput(bpy.types.Operator):
    """Remove a keyframe input from the fCurve node"""
    bl_idname = "mantis.fcurve_node_remove_kf"
    bl_label = "Remove Keyframe"
    bl_options = {'INTERNAL'}
        
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
    bl_options = {'INTERNAL'}
    
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
    bl_options = {'INTERNAL'}
        
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
    bl_options = {'INTERNAL'}
    
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
    bl_options = {'INTERNAL'}
        
    @classmethod
    def poll(cls, context):
        return hasattr(context, 'node')

    def execute(self, context):
        n = context.node
        n.inputs.remove(n.inputs[-1]); n.inputs.remove(n.inputs[-1])
        return {'FINISHED'}



# class ExportNodeTreeToJSON(Operator):
#     """Export this node tree as a JSON file"""
#     bl_idname = "mantis.export_node_tree_json"
#     bl_label = "Export Mantis Tree to JSON"

#     @classmethod
#     def poll(cls, context):
#         return (mantis_tree_poll_op(context))

#     def execute(self, context):
#         from .i_o import export_to_json
#         import bpy

#         tree = context.space_data.path[0].node_tree
#         # tree.update_tree(context)
#         trees = {tree}
#         check_trees=[tree]
#         while check_trees:
#             check = check_trees.pop()
#             for n in check.nodes:
#                 if hasattr(n, "node_tree"):
#                     if n.node_tree not in trees:
#                         check_trees.append(n.node_tree)
#                         trees.add(n.node_tree)
        


#         def remove_special_characters(stritree):
#             # https://stackoverflow.com/questions/295135/turn-a-stritree-into-a-valid-filename
#             # thank you user "Sophie Gage"
#             import re # regular expressions
#             return re.sub('[^\w_.)( -]', '', stritree)

#         path = bpy.path.abspath('//')+remove_special_characters(tree.name)+".json"
#         export_to_json(trees, path)
#         return {"FINISHED"}
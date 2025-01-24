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
        LinkArmatureRemoveTargetInput,]
        # ExportNodeTreeToJSON,]

def mantis_tree_poll_op(context):
    space = context.space_data
    if hasattr(space, "node_tree"):
        if (space.node_tree):
            return (space.tree_type in ["MantisTree", "SchemaTree"])
    return False


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
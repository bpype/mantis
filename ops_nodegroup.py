import bpy
from bpy.types import Operator
from mathutils import Vector

def TellClasses():
    return [
        MantisGroupNodes,
        MantisEditGroup,
        ExecuteNodeTree,
        # CreateMetaGroup,
        QueryNodeSockets,
        CleanUpNodeGraph,
        MantisMuteNode,
        TestOperator,
        # xForm
        AddCustomProperty,
        RemoveCustomProperty,
        # Fcurve
        EditFCurveNode,
        FcurveAddKeyframeInput,
        FcurveRemoveKeyframeInput,
        # Driver
        DriverAddDriverVariableInput,
        DriverRemoveDriverVariableInput,
        # Armature Link Node
        LinkArmatureAddTargetInput,
        LinkArmatureRemoveTargetInput,]

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


# source is https://github.com/aachman98/Sorcar/blob/master/operators/ScGroupNodes.py
# checc here: https://github.com/nortikin/sverchok/blob/9002fd4af9ec8603e86f86ed7e567a4ed0d2e07c/core/node_group.py#L568

    def execute(self, context):
        # Get space, path, current nodetree, selected nodes and a newly created group
        space = context.space_data
        path = space.path
        node_tree = space.path[len(path)-1].node_tree
        node_group = bpy.data.node_groups.new(ChooseNodeGroupNode(space.tree_type), space.tree_type)
        selected_nodes = [i for i in node_tree.nodes if i.select]
        nodes_len = len(selected_nodes)

        # Store all links (internal/external) for the selected nodes to be created as group inputs/outputs
        links_external_in = []
        links_external_out = []
        for n in selected_nodes:
            for i in n.inputs:
                if (i.is_linked):
                    l = i.links[0]
                    if (not l.from_node in selected_nodes):
                        if (not l in links_external_in):
                            links_external_in.append(l)
            for o in n.outputs:
                if (o.is_linked):
                    for l in o.links:
                        if (not l.to_node in selected_nodes):
                            if (not l in links_external_out):
                                links_external_out.append(l)

        # Calculate the required locations for placement of grouped node and input/output nodes
        loc_x_in = 0
        loc_x_out = 0
        loc_avg = Vector((0, 0))
        for n in selected_nodes:
            loc_avg += n.location/nodes_len
            if (n.location[0] < loc_x_in):
                loc_x_in = n.location[0]
            if (n.location[0] > loc_x_out):
                loc_x_out = n.location[0]
        
        # Create and relocate group input & output nodes in the newly created group
        group_input = node_group.nodes.new("NodeGroupInput")
        group_output = node_group.nodes.new("NodeGroupOutput")
        group_input.location = Vector((loc_x_in-200, loc_avg[1]))
        group_output.location = Vector((loc_x_out+200, loc_avg[1]))
        
        # Copy the selected nodes from current nodetree
        if (nodes_len > 0):
            bpy.ops.node.clipboard_copy(get_override(type='NODE_EDITOR'))
        
        # Create a grouped node with correct location and assign newly created group
        group_node = node_tree.nodes.new(ChooseNodeGroupNode(space.tree_type))
        node_tree.nodes.active = group_node
        group_node.location = loc_avg
        group_node.node_tree = node_group
        
        # Add overlay to node editor for the newly created group
        path.append(node_group, node=group_node)
        
        # Paste the copied nodes to newly created group
        if (nodes_len > 0):
            bpy.ops.node.clipboard_paste(get_override(type='NODE_EDITOR'))

        # Create group input/output links in the newly created group
        o = group_input.outputs
        for link in links_external_in:
            # node_group.links.new(o.get(link.from_socket.name, o[len(o)-1]), node_group.nodes[link.to_node.name].inputs[link.to_socket.name])
            node_group.links.new(group_input.outputs[''], node_group.nodes[link.to_node.name].inputs[link.to_socket.name])
        i = group_output.inputs
        for link in links_external_out:
            # node_group.links.new(node_group.nodes[link.from_node.name].outputs[link.from_socket.name], i.get(link.to_socket.name, i[len(i)-1]))
            node_group.links.new(node_group.nodes[link.from_node.name].outputs[link.from_socket.name], group_output.inputs[''])
        
        # Add new links to grouped node from original external links
        for i in range(0, len(links_external_in)):
            link = links_external_in[i]
            node_tree.links.new(link.from_node.outputs[link.from_socket.name], group_node.inputs[i])
        for i in range(0, len(links_external_out)):
            link = links_external_out[i]
            node_tree.links.new(group_node.outputs[i], link.to_node.inputs[link.to_socket.name])
        
        # Remove redundant selected nodes
        for n in selected_nodes:
            node_tree.nodes.remove(n)

        return {"FINISHED"}

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
        return {"CANCELLED"}

class ExecuteNodeTree(Operator):
    """Execute this node tree"""
    bl_idname = "mantis.execute_node_tree"
    bl_label = "Execute Node Tree"

    @classmethod
    def poll(cls, context):
        return (mantis_tree_poll_op(context))

    def execute(self, context):
        from .utilities import parse_node_tree, print_lines
        from time import time
        from .utilities import wrapGreen
        
        tree=context.space_data.path[0].node_tree
        
        import cProfile
        from os import environ
        do_profile=False
        print (environ.get("DOPROFILE"))
        if environ.get("DOPROFILE"):
            do_profile=True
        if do_profile:
            cProfile.runctx("tree.update_tree(context)", None, locals())
            cProfile.runctx("tree.execute_tree(context)", None, locals())
        else:
            tree.update_tree(context)
            tree.execute_tree(context)
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


class CleanUpNodeGraph(bpy.types.Operator):
    """Clean Up Node Graph"""
    bl_idname = "mantis.nodes_cleanup"
    bl_label = "Clean Up Node Graph"

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'active_node')

    def execute(self, context):
        
        base_tree=context.space_data.path[-1].node_tree
        
        from mantis.grandalf.graphs import Vertex, Edge, Graph, graph_core
        
        class defaultview(object):
            w,h = 1,1
            xz = (0,0)
        
        verts = {}
        for n in base_tree.nodes:
            has_links=False
            for inp in n.inputs:
                if inp.is_linked:
                    has_links=True
                    break
            for out in n.outputs:
                if out.is_linked:
                    has_links=True
                    break
            if not has_links:
                continue
                
            v = Vertex(n.name)
            v.view = defaultview()
            v.view.xy = n.location
            v.view.h = n.height*3
            v.view.w = n.width*3
            verts[n.name] = v
            
        edges = []
        for link in base_tree.links:
            weight = 1 # maybe this is useful
            edges.append(Edge(verts[link.from_node.name], verts[link.to_node.name], weight) )
        graph = Graph(verts.values(), edges)
        

        
        from mantis.grandalf.layouts import SugiyamaLayout
        
        
        sug = SugiyamaLayout(graph.C[0]) # no idea what .C[0] is
        
        roots=[]
        for node in base_tree.nodes:
            
            has_links=False
            for inp in node.inputs:
                if inp.is_linked:
                    has_links=True
                    break
            for out in node.outputs:
                if out.is_linked:
                    has_links=True
                    break
            if not has_links:
                continue
                
            if len(node.inputs)==0:
                roots.append(verts[node.name])
            else:
                for inp in node.inputs:
                    if inp.is_linked==True:
                        break
                else:
                    roots.append(verts[node.name])
        
        sug.init_all(roots=roots,)
        sug.draw(8)
        for v in graph.C[0].sV:
            for n in base_tree.nodes:
                if n.name == v.data:
                    n.location.x = v.view.xy[1]
                    n.location.y = v.view.xy[0]
        
        
        
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


class TestOperator(Operator):
    """Mantis Test Operator"""
    bl_idname = "mantis.test_operator"
    bl_label = "Mantis Test Operator"

    @classmethod
    def poll(cls, context):
        return (mantis_tree_poll_op(context))

    def execute(self, context):
        path = context.space_data.path
        node = path[len(path)-1].node_tree.nodes.active
        print("Inputs:")
        for sock in node.inputs:
            print(sock.identifier)
        print("Outputs:")
        for sock in node.outputs:
            print(sock.identifier)
        print ("\n")
        # if (not node):
        #     return {"FINISHED"}
        # for out in node.outputs:
        #     utilities.lines_from_socket(out)
        
        # import bpy
        # c = bpy.context
        # print (c.space_data.path)
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
                # WRONG
        new_prop = n.inputs.new( socktype, self.prop_name)
        if self.prop_type in ['INT','FLOAT']:
            new_prop.min = self.min
            new_prop.max = self.max
            new_prop.soft_min = self.soft_min
            new_prop.soft_max = self.soft_max
        new_prop.description = self.description
        # now do the output
        n.outputs.new( socktype, self.prop_name)
        
        if (False):
            print (new_prop.is_property_set("default_value"))
            ui_data = new_prop.id_properties_ui("default_value")
            ui_data.update(
                description=new_prop.description,
                default=0,) # for now
            #if a number
            for num_type in ['Float', 'Int', 'Bool']:
                if num_type in new_prop.bl_idname:
                    ui_data.update(
                        min = new_prop.min,
                        max = new_prop.max,
                        soft_min = new_prop.soft_min,
                        soft_max = new_prop.soft_max,)
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
        context.node.inputs.new("KeyframeSocket", "Keyframe")
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
        context.node.inputs.new("FloatSocket", "Weight."+str(num_targets).zfill(3))
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

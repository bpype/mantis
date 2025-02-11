from .node_container_common import *
from .xForm_containers import xFormGeometryObject
from .misc_containers import InputExistingGeometryObject
from bpy.types import Node
from .base_definitions import MantisNode

from .utilities import (prRed, prGreen, prPurple, prWhite, prOrange,
                        wrapRed, wrapGreen, wrapPurple, wrapWhite,
                        wrapOrange,)

def TellClasses():
             
    return [ 
             DeformerArmature,
             DeformerHook,
             DeformerMorphTarget,
             DeformerMorphTargetDeform,
           ]


def trace_xForm_back(nc, socket):
    from .xForm_containers import xFormGeometryObject
    from .misc_containers import InputExistingGeometryObject
    from bpy.types import Object
    if (trace := trace_single_line(nc, socket)[0] ) :
        for i in range(len(trace)): # have to look in reverse, actually
            if ( isinstance(trace[ i ], xFormGeometryObject ) ) or ( isinstance(trace[ i ], InputExistingGeometryObject ) ):
                return trace[ i ].bGetObject()
        raise GraphError(wrapRed(f"No other object found for {nc}."))

def default_evaluate_input(nc, input_name):
    # duped from link_containers... should be common?
    # should catch 'Target', 'Pole Target' and ArmatureConstraint targets, too
    if ('Target' in input_name) and input_name != "Target Space":
        socket = nc.inputs.get(input_name)
        if socket.is_linked:
            return socket.links[0].from_node
        return None
        
    else:
        return evaluate_input(nc, input_name)


# semi-duplicated from link_containers
def GetxForm(nc):
    trace = trace_single_line_up(nc, "Deformer")
    for node in trace[0]:
        if (node.__class__ in [xFormGeometryObject, InputExistingGeometryObject]):
            return node
    raise GraphError("%s is not connected to a downstream xForm" % nc)

class DeformerArmature:
    '''A node representing an armature deformer'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
          "Input Relationship"     : NodeSocket(is_input = True, name = "Input Relationship", node = self,),
          "Armature Object"        : NodeSocket(is_input = True, name = "Armature Object", node = self,),
          "Blend Vertex Group"     : NodeSocket(is_input = True, name = "Blend Vertex Group", node = self),
          "Invert Vertex Group"    : NodeSocket(is_input = True, name = "Invert Vertex Group", node = self),
          "Preserve Volume"        : NodeSocket(is_input = True, name = "Preserve Volume", node = self),
          "Use Multi Modifier"     : NodeSocket(is_input = True, name = "Use Multi Modifier", node = self),
          "Use Envelopes"          : NodeSocket(is_input = True, name = "Use Envelopes", node = self),
          "Use Vertex Groups"      : NodeSocket(is_input = True, name = "Use Vertex Groups", node = self),
          "Skinning Method"        : NodeSocket(is_input = True, name = "Skinning Method", node = self),
          "Deformer"               : NodeSocket(is_input = True, name = "Deformer", node = self),
          "Copy Skin Weights From" : NodeSocket(is_input = True, name = "Copy Skin Weights From", node = self),
        }
        self.outputs = {
          "Deformer" : NodeSocket(is_input = False, name = "Deformer", node=self), }
        self.parameters = {
          "Name"                   : None,
          "Armature Object"        : None,
          "Blend Vertex Group"     : None,
          "Invert Vertex Group"    : None,
          "Preserve Volume"        : None,
          "Use Multi Modifier"     : None,
          "Use Envelopes"          : None,
          "Use Vertex Groups"      : None,
          "Skinning Method"        : None,
          "Deformer"               : None,
          "Copy Skin Weights From" : None,
        }
        # now set up the traverse target...
        self.inputs["Deformer"].set_traverse_target(self.outputs["Deformer"])
        self.outputs["Deformer"].set_traverse_target(self.inputs["Deformer"])
        self.node_type = "LINK"
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies, self.dependencies = [], []
        self.prepared = True
        self.executed = False

    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)

    def GetxForm(self, socket="Deformer"):
        if socket == "Deformer":
            return GetxForm(self)
        else:
            trace_xForm_back(self, socket)
    
    # DUPLICATED FROM xForm_containers::xFormBone 
    # DEDUP HACK HACK HACK HACK HACK
    def bGetParentArmature(self):
        from .xForm_containers import xFormArmature
        from .misc_containers import InputExistingGeometryObject
        from bpy.types import Object
        if (trace := trace_single_line(self, "Armature Object")[0] ) :
            for i in range(len(trace)):
                # have to look in reverse, actually
                if ( isinstance(trace[ i ], xFormArmature ) ):
                    return trace[ i ].bGetObject()
                elif ( isinstance(trace[i], InputExistingGeometryObject)):
                    if (ob := trace[i].bGetObject()).type == "ARMATURE":
                        return ob
        raise RuntimeError(f"Cannot find armature for node {self}")
        return None
        #should do the trick...

    def bExecute(self, bContext = None,):
        self.executed = True
    
    def initialize_vgroups(self,):
        ob = self.GetxForm().bGetObject()
        armOb = self.bGetParentArmature()
        for b in armOb.data.bones:
            if b.use_deform == False:
                continue
            vg = ob.vertex_groups.get(b.name)
            if not vg:
                vg = ob.vertex_groups.new(name=b.name)
                num_verts = len(ob.data.vertices)
                vg.add(range(num_verts), 0, 'REPLACE')
    
    def copy_weights(self):
        # we'll use modifiers for this, maybe use GN for it in the future tho
        import bpy
        ob = self.GetxForm().bGetObject()
        try:
            copy_from = self.GetxForm(socket="Copy Skin Weights From")
        except GraphError:
            copy_from = None
            prRed(f"No object found for copying weights in {self}, continuing anyway.")
        m = ob.modifiers.new(type="DATA_TRANSFER", name="Mantis_temp_data_transfer")
        m.object = None; m.use_vert_data = True
        m.data_types_verts = {'VGROUP_WEIGHTS'}
        m.vert_mapping = 'POLYINTERP_NEAREST'
        m.layers_vgroup_select_src = 'ALL'
        m.layers_vgroup_select_dst = 'NAME'
        m.object = copy_from
        # m.use_object_transform = False # testing reveals that this is undesirable - since the objects may not have their transforms applied.
        ob.modifiers.move(len(ob.modifiers)-1, 0)

        # ob.data = ob.data.copy()
        if False: #MAYBE the mouse needs to be in the 3D viewport, no idea how to set this in an override
            # TODO: figure out how to apply this, context is incorrect because armature is still in pose mode
            original_active = bpy.context.active_object
            original_mode = original_active.mode
            bpy.ops.object.mode_set(mode='OBJECT')
            with bpy.context.temp_override(**{'active_object':ob, 'selected_objects':[ob, copy_from]}):
                # bpy.ops.object.datalayout_transfer(modifier=m.name) # note: this operator is used by the modifier or stand-alone in the UI
                # the poll for this operator is defined in blender/source/blender/editors/object/object_data_transfer.cc
                # and blender/source/blender/editors/object/object_modifier.cc
                # bpy.ops.object.modifier_apply(modifier=m.name, single_user=True)
                bpy.ops.object.datalayout_transfer(data_type='VGROUP_WEIGHTS')
                bpy.ops.object.data_transfer(data_type='VGROUP_WEIGHTS')
            bpy.ops.object.mode_set(mode=original_mode)
         
    def bFinalize(self, bContext=None):
        prGreen("Executing Armature Deform Node")
        mod_name = self.evaluate_input("Name")
        d = self.GetxForm().bGetObject().modifiers.new(mod_name, type='ARMATURE')
        if d is None:
            raise RuntimeError(f"Modifier was not created in node {self} -- the object is invalid.")
        self.bObject = d
        d.object = self.bGetParentArmature()
        props_sockets = {
        'vertex_group'               : ("Blend Vertex Group", ""),
        'invert_vertex_group'        : ("Invert Vertex Group", ""),
        'use_deform_preserve_volume' : ("Preserve Volume", False),
        'use_multi_modifier'         : ("Use Multi Modifier", False),
        'use_bone_envelopes'         : ("Use Envelopes", False),
        'use_vertex_groups'          : ("Use Vertex Groups", False),
        }
        evaluate_sockets(self, d, props_sockets)
        #
        if (skin_method := self.evaluate_input("Skinning Method")) == "AUTOMATIC_HEAT":
            # This is bad and leads to somewhat unpredictable
            #  behaviour, e.g. what object will be selected? What mode?
            # also bpy.ops is ugly and prone to error when used in
            #  scripts. I don't intend to use bpy.ops when I can avoid it.
            import bpy
            self.initialize_vgroups()
            bContext.view_layer.depsgraph.update()
            ob = self.GetxForm().bGetObject()
            armOb = self.bGetParentArmature()
            deform_bones = []
            for pb in armOb.pose.bones:
                if pb.bone.use_deform == True:
                    deform_bones.append(pb)
            
            context_override = {
                                  'active_object':ob,
                                  'selected_objects':[ob, armOb],
                                  'active_pose_bone':deform_bones[0],
                                  'selected_pose_bones':deform_bones,}
            #
            with bContext.temp_override(**{'active_object':armOb}):
                bpy.ops.object.mode_set(mode='POSE')
                bpy.ops.pose.select_all(action='SELECT')
            with bContext.temp_override(**context_override):
                bpy.ops.paint.weight_paint_toggle()
                bpy.ops.paint.weight_from_bones(type='AUTOMATIC')
                bpy.ops.paint.weight_paint_toggle()
                #
            with bContext.temp_override(**{'active_object':armOb}):
                bpy.ops.object.mode_set(mode='POSE')
                bpy.ops.pose.select_all(action='DESELECT') 
                bpy.ops.object.mode_set(mode='OBJECT')
            # TODO: modify Blender to make this available as a Python API function.
        elif skin_method == "EXISTING_GROUPS":
            pass
        elif skin_method == "COPY_FROM_OBJECT":
            self.initialize_vgroups()
            self.copy_weights()


class DeformerHook:
    '''A node representing a hook deformer'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
          "Hook Target"    : NodeSocket(is_input = True, name = "Hook Target", node = self,),
          "Index"          : NodeSocket(is_input = True, name = "Index", node = self),
          "Deformer"       : NodeSocket(is_input = True, name = "Deformer", node = self),
        }
        self.outputs = {
          "Deformer" : NodeSocket(is_input = False, name = "Deformer", node=self), }
        self.parameters = {
          "Hook Target"     : None,
          "Index"           : None,
          "Deformer"        : None,
          "Name"            : None,
        }
        # now set up the traverse target...
        self.inputs["Deformer"].set_traverse_target(self.outputs["Deformer"])
        self.outputs["Deformer"].set_traverse_target(self.inputs["Deformer"])
        self.node_type = "LINK"
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies, self.dependencies = [], []
        self.prepared = True
        self.executed = False

    def evaluate_input(self, input_name):
        return default_evaluate_input(self, input_name)

    def GetxForm(self, socket="Deformer"):
        if socket == "Deformer":
            return GetxForm(self)
        else:
            trace_xForm_back(self, socket)
            
    def bExecute(self, bContext = None,):
        self.executed = True

    def bFinalize(self, bContext=None):
        from bpy.types import Bone, PoseBone, Object
        prGreen(f"Executing Hook Deform Node: {self}")
        mod_name = self.evaluate_input("Name")
        target_node = self.evaluate_input('Hook Target')
        target = target_node.bGetObject(); subtarget = ""
        if isinstance(target, Bone) or isinstance(target, PoseBone):
            subtarget = target.name; target = target.id_data
        ob=self.GetxForm().bGetObject()
        reuse = False
        for m in ob.modifiers:
            if  m.type == 'HOOK' and m.object == target and m.subtarget == subtarget:
                d = m; reuse = True; break
        else:
            d = ob.modifiers.new(mod_name, type='HOOK')
            if d is None:
                raise RuntimeError(f"Modifier was not created in node {self} -- the object is invalid.")
        get_target_and_subtarget(self, d, input_name="Hook Target")
        vertices_used=[]
        if reuse: # Get the verts in the list... filter out all the unneeded 0's
            vertices_used = list(d.vertex_indices)
            include_0 = 0 in vertices_used
            vertices_used = list(filter(lambda a : a != 0, vertices_used))
            if include_0: vertices_used.append(0)
        # now we add the selected vertex to the list, too
        vertices_used.append(self.evaluate_input("Index"))
        d.vertex_indices_set(vertices_used)
        # todo: this should be able to take many indices in the future.


class DeformerMorphTarget:
    '''A node representing an armature deformer'''
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
          "Relative to"  : NodeSocket(is_input = True, name = "Relative To", node = self,),
          "Object"       : NodeSocket(is_input = True, name = "Object", node = self,),
          "Deformer"     : NodeSocket(is_input = True, name = "Deformer", node = self),
          "Vertex Group" : NodeSocket(is_input = True, name = "Vertex Group", node = self),
        }
        self.outputs = {
          "Deformer" : NodeSocket(is_input = False, name = "Deformer", node=self),
          "Morph Target" : NodeSocket(is_input = False, name = "Morph Target", node=self), }
        self.parameters = {
          "Name"               : None,
          "Relative to"        : None,
          "Object"             : None,
          "Morph Target"       : None,
          "Deformer"           : None,
          "Vertex Group"       : None,
        }
        # now set up the traverse target...
        self.inputs["Deformer"].set_traverse_target(self.outputs["Deformer"])
        self.outputs["Deformer"].set_traverse_target(self.inputs["Deformer"])
        self.node_type = "LINK"
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies, self.dependencies = [], []
        self.prepared = True
        self.executed = False
    
    def GetxForm(self, trace_input="Object"):
        trace = trace_single_line(self, trace_input)
        for node in trace[0]:
            if (node.__class__ in [xFormGeometryObject, InputExistingGeometryObject]):
                return node
        raise GraphError("%s is not connected to an upstream xForm" % self)


    def bExecute(self, bContext = None,):
        prGreen("Executing Morph Target Node")

        ob = None; relative = None
        # do NOT check if the object exists here. Just let the next node deal with that.
        try:
            ob = self.GetxForm().bGetObject().name 
        except Exception as e: # this will and should throw an error if it fails
            ob = self.GetxForm().evaluate_input("Name")
        if self.inputs["Relative to"].is_linked:
            try:
                relative = self.GetxForm("Relative to").bGetObject().name
            except Exception as e: # same here
                prRed(f"Execution failed at {self}: no relative object found for morph target, despite link existing.")
                raise e

        vg = self.evaluate_input("Vertex Group") if self.evaluate_input("Vertex Group") else "" # just make sure it is a string
        
        mt={"object":ob, "vertex_group":vg, "relative_shape":relative}

        self.parameters["Morph Target"] = mt
        self.parameters["Name"] = ob # this is redundant but it's OK since accessing the mt is tedious
        self.executed = True



class DeformerMorphTargetDeform:
    '''A node representing an armature deformer'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
          "Deformer"            : NodeSocket(is_input = True, name = "Deformer", node = self),
          "Use Shape Key"       : NodeSocket(is_input = True, name = "Use Shape Key", node = self),
        }
        self.outputs = {
          "Deformer" : NodeSocket(is_input = False, name = "Deformer", node=self), }
        self.parameters = {
          "Name"                : None,
          "Deformer"            : None,
          "Deformer"            : None,
          "Use Shape Key"       : None,}
        # now set up the traverse target...
        self.inputs["Deformer"].set_traverse_target(self.outputs["Deformer"])
        self.outputs["Deformer"].set_traverse_target(self.inputs["Deformer"])
        self.node_type = "LINK"
        self.hierarchy_connections, self.connections = [], []
        self.hierarchy_dependencies, self.dependencies = [], []
        self.prepared = True
        self.executed = True
        self.bObject = None
        setup_custom_props(self)

    def GetxForm(self):
        return GetxForm(self)
    
    # bpy.data.node_groups["Morph Deform.045"].nodes["Named Attribute.020"].data_type = 'FLOAT_VECTOR'
    # bpy.context.object.add_rest_position_attribute = True


    def gen_morph_target_modifier(self, context):
        # first let's see if this is a no-op
        targets = []
        for k,v in self.inputs.items():
            if "Target" in k:
                targets.append(v)
        if not targets:
            return # nothing to do here.
        
        mod_name = self.evaluate_input("Name")
        self_ob = self.GetxForm().bGetObject()
        m = self_ob.modifiers.new(mod_name, type='NODES')
        self.bObject = m
        # at this point we make the node tree
        self_ob.add_rest_position_attribute = True
        from bpy import data
        ng = data.node_groups.new(mod_name, "GeometryNodeTree")
        m.node_group = ng
        ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
        inp = ng.nodes.new("NodeGroupInput")
        out = ng.nodes.new("NodeGroupOutput")
        # TODO CLEANUP here
        if (position := ng.nodes.get("Position")) is None: position = ng.nodes.new("GeometryNodeInputPosition")
        if (index := ng.nodes.get("Index")) is None: index = ng.nodes.new("GeometryNodeInputIndex")
        rest_position = ng.nodes.new("GeometryNodeInputNamedAttribute")
        rest_position.inputs["Name"].default_value="rest_position"
        rest_position.data_type = 'FLOAT_VECTOR'
        # rest_position = position
        add_these = []

        props_sockets={}
        object_map = {}

        for i, t in enumerate(targets):
            mt_node = t.links[0].from_node
            mt_ob = mt_node.GetxForm().bGetObject()
            if mt_ob is None: # create it
                mt_ob = data.objects.new(mt_node.evaluate_input("Name"), data.meshes.new_from_object(self_ob))
                context.collection.objects.link(mt_ob)
                prOrange(f"WARN: no object found for f{mt_node}; creating duplicate of current object ")
            mt_name = mt_ob.name
            vg = mt_node.parameters["Morph Target"]["vertex_group"]
            if vg: mt_name = mt_name+"."+vg
            try:
                ob_relative = t.links[0].from_node.inputs["Relative to"].links[0].from_node.bGetObject()
            except IndexError:
                ob_relative = None
            
            ng.interface.new_socket(mt_name, in_out = "INPUT", socket_type="NodeSocketObject")
            ng.interface.new_socket(mt_name+" Value", in_out = "INPUT", socket_type="NodeSocketFloat")
            ob_node = ng.nodes.new("GeometryNodeObjectInfo")
            sample_index = ng.nodes.new("GeometryNodeSampleIndex"); sample_index.data_type = 'FLOAT_VECTOR'
            subtract = ng.nodes.new("ShaderNodeVectorMath"); subtract.operation="SUBTRACT"
            scale1 = ng.nodes.new("ShaderNodeVectorMath"); scale1.operation="SCALE"
            

            ng.links.new(input=inp.outputs[mt_name], output=ob_node.inputs["Object"])
            ng.links.new(input=index.outputs["Index"], output=sample_index.inputs["Index"])
            ng.links.new(input=position.outputs["Position"], output=sample_index.inputs["Value"])
            ng.links.new(input=sample_index.outputs["Value"], output=subtract.inputs[0])
            ng.links.new(input=ob_node.outputs["Geometry"], output=sample_index.inputs["Geometry"])

            if ob_relative: # TODO: this should also be exposed as an input
                ob_node1 = ng.nodes.new("GeometryNodeObjectInfo"); ob_node1.inputs["Object"].default_value = ob_relative
                sample_index1 = ng.nodes.new("GeometryNodeSampleIndex"); sample_index1.data_type = 'FLOAT_VECTOR'
                ng.links.new(input=index.outputs["Index"], output=sample_index1.inputs["Index"])
                ng.links.new(input=position.outputs["Position"], output=sample_index1.inputs["Value"])
                ng.links.new(input=ob_node1.outputs["Geometry"], output=sample_index1.inputs["Geometry"])
                ng.links.new(input=sample_index1.outputs["Value"], output=subtract.inputs[1])
            else:
                # ng.links.new(input=rest_position.outputs["Attribute"], output=subtract.inputs[1])                
                ng.links.new(input=rest_position.outputs[0], output=subtract.inputs[1])

            ng.links.new(input=subtract.outputs["Vector"], output=scale1.inputs[0])

            # TODO: this should be exposed as a node tree input
            if vg:= mt_node.evaluate_input("Vertex Group"): # works
                vg_att = ng.nodes.new("GeometryNodeInputNamedAttribute"); vg_att.inputs["Name"].default_value=vg
                multiply = ng.nodes.new("ShaderNodeMath"); multiply.operation = "MULTIPLY"
                ng.links.new(input=vg_att.outputs["Attribute"], output=multiply.inputs[1])
                ng.links.new(input=inp.outputs[mt_name+" Value"], output=multiply.inputs[0])
                ng.links.new(input=multiply.outputs[0], output=scale1.inputs["Scale"])
            else:
                ng.links.new(input=inp.outputs[mt_name+" Value"], output=scale1.inputs["Scale"])
            add_these.append(scale1)
            object_map["Socket_"+str((i+1)*2)]=mt_node.GetxForm().bGetObject()
            props_sockets["Socket_"+str((i+1)*2+1)]= ("Value."+str(i).zfill(3), 1.0)
        
        set_position = ng.nodes.new("GeometryNodeSetPosition")
        bake = ng.nodes.new("GeometryNodeBake")
        ng.links.new(inp.outputs["Geometry"], output=set_position.inputs["Geometry"])
        ng.links.new(set_position.outputs["Geometry"], output=bake.inputs[0])
        ng.links.new(bake.outputs[0], output=out.inputs[0])

        
        # prev_node = ng.nodes.new("ShaderNodeVectorMath"); prev_node.operation="SUBTRACT"
        # ng.links.new(position.outputs[0], output=prev_node.inputs[0])
        # ng.links.new(rest_position.outputs[0], output=prev_node.inputs[1])
        prev_node = ng.nodes.new("FunctionNodeInputVector")
        for i, node in enumerate(add_these):
            add = ng.nodes.new("ShaderNodeVectorMath"); add.operation="ADD"
            ng.links.new(prev_node.outputs[0], output=add.inputs[0])
            ng.links.new(node.outputs[0], output=add.inputs[1])
            prev_node = add
        ng.links.new(add.outputs[0], output=set_position.inputs["Offset"])
        
        from .utilities import SugiyamaGraph
        SugiyamaGraph(ng, 12)


        evaluate_sockets(self, m, props_sockets)
        for socket, ob in object_map.items():
            m[socket]=ob
        finish_drivers(self)

    def gen_shape_key(self, context): # TODO: make this a feature of the node definition that appears only when there are no prior deformers - and shows a warning!
        # TODO: the below works well, but it is quite slow. It does not seem to have better performence. Its only advantage is export to FBX.
        # there are a number of things I need to fix here
        #   - reuse shape keys if possible
        #   - figure out how to make this a lot faster
        #   - edit the xForm stuff to delete drivers from shape key ID's, since they belong to the Key, not the Object.
        # first check if we need to do anythign
        targets = []
        for k,v in self.inputs.items():
            if "Target" in k:
                targets.append(v)
        if not targets:
            return # nothing to do here
        from time import time
        start_time = time()
        from bpy import data
        xf = self.GetxForm()
        ob = xf.bGetObject()
        dg = context.view_layer.depsgraph
        dg.update()
        if xf.has_shape_keys == False:
            m = data.meshes.new_from_object(ob, preserve_all_data_layers=True, depsgraph=dg)
            ob.data = m
            ob.add_rest_position_attribute = True
            ob.shape_key_clear()
            ob.shape_key_add(name='Basis', from_mix=False)
        else:
            m = ob.data
        xf.has_shape_keys = True
        
        # using the built-in shapekey feature is actually a lot harder in terms of programming because I need...
            # min/max, as it is just not a feature of the GN version
            # to carry info from the morph target node regarding relative shapes and vertex groups and all that
            # the drivers may be more difficult to apply, too.
            # hafta make new geometry for the object and add shape keys and all that
            # the benefit to all this being exporting to game engines via .fbx

        # first make a basis shape key
        keys={}
        props_sockets={}
        for i, t in enumerate(targets):
            mt_node = t.links[0].from_node; sk_ob = mt_node.GetxForm().bGetObject()
            if sk_ob is None:
                sk_ob = data.objects.new(mt_node.evaluate_input("Name"), data.meshes.new_from_object(ob))
                context.collection.objects.link(sk_ob)
                prOrange(f"WARN: no object found for f{mt_node}; creating duplicate of current object ")
            sk_ob = dg.id_eval_get(sk_ob)
            mt_name = sk_ob.name
            vg = mt_node.parameters["Morph Target"]["vertex_group"]
            if vg: mt_name = mt_name+"."+vg
            
            sk = ob.shape_key_add(name=mt_name, from_mix=False)
            # the shapekey data is absolute point data for each vertex, in order, very simple

            # SERIOUSLY IMPORTANT:
               # use the current position of the vertex AFTER SHAPE KEYS AND DEFORMERS
               # easiest way to do it is to eval the depsgraph
               # TODO: try and get it without depsgraph update, since that may be (very) slow
            sk_m = sk_ob.data#data.meshes.new_from_object(sk_ob, preserve_all_data_layers=True, depsgraph=dg)
            for j in range(len(m.vertices)):
                sk.data[j].co = sk_m.vertices[j].co # assume they match
            # data.meshes.remove(sk_m)
            sk.vertex_group = vg
            sk.slider_min = -10
            sk.slider_max = 10
            keys[mt_name]=sk
            props_sockets[mt_name]= ("Value."+str(i).zfill(3), 1.0)
        for i, t in enumerate(targets):
            mt_node = t.links[0].from_node; sk_ob = mt_node.GetxForm().bGetObject()
            if sk_ob is None: continue
            if rel := mt_node.parameters["Morph Target"]["relative_shape"]:
                sk = keys.get(mt_name)
                sk.relative_key = keys.get(rel)
        
        self.bObject = sk.id_data
        evaluate_sockets(self, sk.id_data, props_sockets)
        finish_drivers(self)
        prWhite(f"Initializing morph target took {time() -start_time} seconds")
        

    def bFinalize(self, bContext=None):
        prGreen(f"Executing Morph Deform node {self}")
        # if there is a not a prior deformer then there should be an option to use plain 'ol shape keys
        # GN is always desirable as an option though because it can be baked & many other reasons
        use_shape_keys = self.evaluate_input("Use Shape Key")
        if use_shape_keys: # check and see if we can.
            if self.inputs.get("Deformer"): # I guess this isn't available in some node group contexts... bad. FIXME
                if (links := self.inputs["Deformer"].links):
                    if not links[0].from_node.parameters.get("Use Shape Key"):
                        use_shape_keys = False
                    elif links[0].from_node.parameters.get("Use Shape Key") == False:
                        use_shape_keys = False
        self.parameters["Use Shape Key"] = use_shape_keys
        if use_shape_keys:
            self.gen_shape_key(bContext)
        else:
            self.gen_morph_target_modifier(bContext)


        
        
            

        

for c in TellClasses():
    setup_container(c)
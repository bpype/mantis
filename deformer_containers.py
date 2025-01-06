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
             DeformerMorphTarget,
             DeformerMorphTargetDeform,
           ]



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
            from .xForm_containers import xFormGeometryObject
            from .misc_containers import InputExistingGeometryObject
            from bpy.types import Object
            if (trace := trace_single_line(self, socket)[0] ) :
                for i in range(len(trace)): # have to look in reverse, actually
                    if ( isinstance(trace[ i ], xFormGeometryObject ) ) or ( isinstance(trace[ i ], InputExistingGeometryObject ) ):
                        return trace[ i ].bGetObject()
                raise GraphError(wrapRed(f"No other object found for {self}."))
    
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
        m.use_object_transform = False
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
        try:
            d = self.GetxForm().bGetObject().modifiers[mod_name]
        except KeyError:
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
            # This is reatarded and leads to somewhat unpredictable
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
        name = ''

        ob = None; relative = None
        try:
            ob = self.GetxForm().bGetObject().name 
        except Exception as e: # this will and should throw an error if it fails
            prRed(f"Execution failed at {self}: no object found for morph target.")
            raise e
        if self.inputs["Relative to"].is_linked:
            try:
                relative = self.GetxForm("Relative to").bGetObject().name
            except Exception as e: # same here
                prRed(f"Execution failed at {self}: no relative object found for morph target, despite link existing.")
                raise e

        vg = self.evaluate_input("Vertex Group") if self.evaluate_input("Vertex Group") else "" # just make sure it is a string
        
        mt={"object":ob, "vertex_group":vg, "relative_shape":relative}

        self.parameters["Morph Target"] = mt
        self.executed = True



class DeformerMorphTargetDeform:
    '''A node representing an armature deformer'''

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
          "Deformer"            : NodeSocket(is_input = True, name = "Deformer", node = self),
        }
        self.outputs = {
          "Deformer" : NodeSocket(is_input = False, name = "Deformer", node=self), }
        self.parameters = {
          "Name"                : None,
          "Deformer"            : None,}
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
    

    def gen_morph_target_modifier(self):
        mod_name = self.evaluate_input("Name")
        # self.GetxForm().bGetObject().add_rest_position_attribute = True # this ended up being unnecessary
        try:
            m = self.GetxForm().bGetObject().modifiers[mod_name]
        except KeyError:
            m = self.GetxForm().bGetObject().modifiers.new(mod_name, type='NODES')
        self.bObject = m
        # at this point we make the node tre
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
        # if (rest_position := ng.nodes.get("Rest Position")) is None: rest_position = ng.nodes.new("GeometryNodeInputNamedAttribute"); rest_position.name = "Rest Position"
        # rest_position.data_type = "FLOAT_VECTOR"; rest_position.inputs["Name"].default_value = "rest_position"
        rest_position = position
        add_these = []

        props_sockets={}
        object_map = {}

        targets = []
        for k,v in self.inputs.items():
            if "Target" in k:
                targets.append(v)
        for i, t in enumerate(targets):
            mt_node = t.links[0].from_node
            # mt_name = "Morph Target."+str(i).zfill(3)
            mt_name = mt_node.GetxForm().bGetObject().name
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
            # if (rest_position := ng.nodes.get("Rest Position")) is None: rest_position = ng.nodes.new("GeometryNodeInputNamedAttribute"); rest_position.name = "Rest Position"
            # rest_position.data_type = "FLOAT_VECTOR"; rest_position.inputs["Name"].default_value = "rest_position"
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
                ng.links.new(input=rest_position.outputs["Position"], output=subtract.inputs[1])

            # IMPORTANT TODO (?):
               # relative objects can be recursive! Need to go back and back and back as long as we have relative objects!
               # in reality I am not sure haha

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
        ng.links.new(inp.outputs["Geometry"], output=set_position.inputs["Geometry"])
        ng.links.new(set_position.outputs["Geometry"], output=out.inputs["Geometry"])

        
        prev_node = rest_position
        for i, node in enumerate(add_these):
            add = ng.nodes.new("ShaderNodeVectorMath"); add.operation="ADD"
            ng.links.new(prev_node.outputs[0], output=add.inputs[0])
            ng.links.new(node.outputs[0], output=add.inputs[1])
            prev_node = add
        ng.links.new(add.outputs[0], output=set_position.inputs["Position"])
        
        from .utilities import SugiyamaGraph
        SugiyamaGraph(ng, 12)


        # for k,v in props_sockets.items():
        #     print(wrapWhite(k), wrapOrange(v))
        evaluate_sockets(self, m, props_sockets)
        for socket, ob in object_map.items():
            m[socket]=ob
        finish_drivers(self)

    def gen_shape_key(self): # TODO: make this a feature of the node definition that appears only when there are no prior deformers - and shows a warning!
        self.gen_morph_target_modifier()
        return
        # TODO: the below works well, but it is quite slow. It does not seem to have better performence. Its only advantage is export to FBX.
        # there are a number of things I need to fix here
        #   - reuse shape keys if possible
        #   - figure out how to make this a lot faster
        #   - edit the xForm stuff to delete drivers from shape key ID's, since they belong to the Key, not the Object.
        from time import time
        start_time = time()
        from bpy import data
        ob = self.GetxForm().bGetObject()
        m = data.meshes.new_from_object(ob, preserve_all_data_layers=True)
        ob.data = m
        ob.add_rest_position_attribute = True
        ob.shape_key_clear()

        targets = []
        for k,v in self.inputs.items():
            if "Target" in k:
                targets.append(v)
        for i, t in enumerate(targets):
            mt_node = t.links[0].from_node
            mt_name = "Morph Target."+str(i).zfill(3)
        
        # using the built-in shapekey feature is actually a lot harder in terms of programming because I need...
            # min/max, as it is just not a feature of the GN version
            # to carry info from the morph target node regarding relative shapes and vertex groups and all that
            # the drivers may be more difficult to apply, too.
            # hafta make new geometry for the object and add shape keys and all that
            # the benefit to all this being maybe better performence and exporting to game engines via .fbx

        #
        # first make a basis shape key
        ob.shape_key_add(name='Basis', from_mix=False)
        keys={}
        props_sockets={}
        for i, t in enumerate(targets):
            mt_node = t.links[0].from_node
            # mt_name = "Morph Target."+str(i).zfill(3)
            sk_ob = mt_node.GetxForm().bGetObject()
            mt_name = sk_ob.name
            vg = mt_node.parameters["Morph Target"]["vertex_group"]
            if vg: mt_name = mt_name+"."+vg
            
            sk = ob.shape_key_add(name=mt_name, from_mix=False)
            # the shapekey data is absolute point data for each vertex, in order, very simple
            for j in range(len(m.vertices)):
                sk.data[j].co = sk_ob.data.vertices[j].co # assume they match
            sk.vertex_group = vg
            sk.slider_min = -10
            sk.slider_max = 10
            keys[mt_name]=sk
            props_sockets[mt_name]= ("Value."+str(i).zfill(3), 1.0)
        for i, t in enumerate(targets):
            mt_node = t.links[0].from_node
            # mt_name = "Morph Target."+str(i).zfill(3)
            sk_ob = mt_node.GetxForm().bGetObject()
            mt_name = sk_ob.name
            vg = mt_node.parameters["Morph Target"]["vertex_group"]
            if vg: mt_name = mt_name+"."+vg
            if rel := mt_node.parameters["Morph Target"]["relative_shape"]:
                sk = keys.get(mt_name)
                sk.relative_key = keys.get(rel)
        
        # for k,v in props_sockets.items():
        #     print(wrapWhite(k), wrapOrange(v), wrapRed(self.evaluate_input(v)))
        self.bObject = sk.id_data
        evaluate_sockets(self, sk.id_data, props_sockets)
        finish_drivers(self)
            
        
        prWhite(f"Initializing morph target took {time() -start_time} seconds")
        
        
        
            

            

        # then we need to get all the data from the morph targets, pull all the relative shapes first and add them, vertex groups and properties
        # next we add all the shape keys that are left, and their vertex groups
        # set the slider ranges to -10 and 10
        # then set up the drivers
        

    def bFinalize(self, bContext=None):
        # let's find out if there is a prior deformer.
        # if not, then there should be an option to use plain 'ol shape keys
        # GN is always desirable as an option though because it can be baked.
        if self.inputs["Deformer"].is_linked:
            self.gen_morph_target_modifier()
        else:
            # for now we'll just do it this way.
            self.gen_shape_key()


        
        
            

        

for c in TellClasses():
    setup_container(c)
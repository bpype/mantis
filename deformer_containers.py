from .node_container_common import *
from .xForm_containers import xFormGeometryObject, xFormObjectInstance
from .misc_nodes import InputExistingGeometryObject
from .base_definitions import MantisNode, MantisSocketTemplate
from .utilities import (prRed, prGreen, prPurple, prWhite, prOrange,
                        wrapRed, wrapGreen, wrapPurple, wrapWhite,
                        wrapOrange,)

from .deformer_socket_templates import *

from bpy.types import NodeTree

def TellClasses():
             
    return [ 
             DeformerArmature,
             DeformerHook,
             DeformerMorphTarget,
             DeformerMorphTargetDeform,
             DeformerSurfaceDeform,
             DeformerMeshDeform,
             DeformerLatticeDeform,
             DeformerSmoothCorrectiveDeform,
           ]

# object instance probably can't use the deformer but it doesn't hurt to try.
deformable_types= (xFormGeometryObject, InputExistingGeometryObject, xFormObjectInstance)

def trace_xForm_back(nc, socket):
    if (trace := trace_single_line(nc, socket)[0] ) :
        for i in range(len(trace)): # have to look in reverse, actually
            if ( isinstance(trace[ i ], deformable_types ) ):
                return trace[ i ].bGetObject()
        raise GraphError(wrapRed(f"No other object found for {nc}."))

class MantisDeformerNode(MantisNode):
    def __init__(self, signature : tuple,
                 base_tree : NodeTree,
                 socket_templates : list[MantisSocketTemplate]=[]):
        super().__init__(signature, base_tree, socket_templates)
        self.node_type = 'LINK'
        self.prepared = True
        self.bObject=[]
    # we need evaluate_input to have the same behaviour as links.
    def evaluate_input(self, input_name, index=0):
        if (input_name in ['Target', 'Object', 'Hook Target']):
            socket = self.inputs.get(input_name)
            if socket.is_linked:
                return socket.links[0].from_node
            return None
            
        else:
            return super().evaluate_input(input_name, index)
    
    def GetxForm(nc, output_name="Deformer"):
        break_condition= lambda node : node.__class__ in deformable_types
        xforms = trace_line_up_branching(nc, output_name, break_condition)
        return_me=[]
        for xf in xforms:
            if xf.node_type != 'XFORM':
                continue
            if xf in return_me:
                continue
            return_me.append(xf)
        return return_me
    

    
    def reset_execution(self):
        super().reset_execution()
        self.bObject=[]; self.prepared=True

class DeformerArmature(MantisDeformerNode):
    '''A node representing an armature deformer'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Input Relationship",
            "Armature Object",
            "Blend Vertex Group",
            "Invert Vertex Group",
            "Preserve Volume",
            "Use Multi Modifier",
            "Use Envelopes",
            "Use Vertex Groups",
            "Skinning Method",
            "Deformer",
            "Copy Skin Weights From"
        ]
        outputs = [
          "Deformer"
        ]
        self.outputs.init_sockets(outputs)
        self.inputs.init_sockets(inputs)
        self.init_parameters(additional_parameters={"Name":None})
        self.set_traverse([("Deformer", "Deformer")])
        self.node_type = "LINK"
        self.prepared = True


    def GetxForm(self, socket="Deformer"):
        if socket == "Deformer":
            return super().GetxForm()
        else:
            trace_xForm_back(self, socket)
    
    # DUPLICATED FROM xForm_containers::xFormBone 
    # DEDUP HACK HACK HACK HACK HACK
    def bGetParentArmature(self):
        from .xForm_containers import xFormArmature
        from .misc_nodes import InputExistingGeometryObject
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
    
    def initialize_vgroups(self, xf):
        ob = xf.bGetObject()
        armOb = self.bGetParentArmature()
        for b in armOb.data.bones:
            if b.use_deform == False:
                continue
            vg = ob.vertex_groups.get(b.name)
            if not vg:
                vg = ob.vertex_groups.new(name=b.name)
                if ob.type == 'MESH':
                    num_verts = len(ob.data.vertices)
                elif ob.type == 'LATTICE':
                    num_verts = len(ob.data.points)
                vg.add(range(num_verts), 0, 'REPLACE')
    
    def copy_weights(self, xf):
        # we'll use modifiers for this, maybe use GN for it in the future tho
        import bpy
        ob = xf.bGetObject()
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
         
    def do_automatic_skinning_mesh(self, ob, xf, bContext):
        # This is bad and leads to somewhat unpredictable
        #  behaviour, e.g. what object will be selected? What mode?
        # also bpy.ops is ugly and prone to error when used in
        #  scripts. I don't intend to use bpy.ops when I can avoid it.
        import bpy
        self.initialize_vgroups(xf)
        armOb = self.bGetParentArmature()
        armOb.data.pose_position = 'REST'
        bContext.view_layer.depsgraph.update()
        deform_bones = []
        for pb in armOb.pose.bones:
            if pb.bone.use_deform == True:
                deform_bones.append(pb)
        if not deform_bones:
            prPurple("Warning: No deform bones in armature. Cancelling.")
            return
        context_override = {
                            'active_object':ob,
                            'selected_objects':[ob, armOb],
                            'active_pose_bone':deform_bones[0],
                            'selected_pose_bones':deform_bones,}
        for b in armOb.data.bones:
            b.select = True
        with bContext.temp_override(**context_override):
            bpy.ops.paint.weight_paint_toggle()
            bpy.ops.paint.weight_from_bones(type='AUTOMATIC')
            bpy.ops.paint.weight_paint_toggle()
        for b in armOb.data.bones:
            b.select = False
        armOb.data.pose_position = 'POSE'
        # TODO: modify Blender to make this available as a Python API function.

    def do_automatic_skinning_lattice(self, ob, xf, bContext):
        # Temporarily, I am making a very simple and ugly automatic skinning algo for lattice points
        import bpy
        from mathutils.geometry import intersect_point_line
        self.initialize_vgroups(xf)
        armOb = self.bGetParentArmature()
        armOb.data.pose_position = 'REST'
        bContext.view_layer.depsgraph.update()
        deform_bones = []
        for pb in armOb.pose.bones:
            if pb.bone.use_deform == True: deform_bones.append(pb)
        # How this works:
        #   - Calculates the weights based on proximity and angle
        #   - we'll make a vector of the point and the nearest point on the bone
        #   - dot (point_displacement, bone_y_axis) to get the angle
        #   - weight the bone's value by this dot product and distance
        #   - distance should prevail when both bones are within the angle
        mat = ob.matrix_world; mat_arm = armOb.matrix_world
        for p_index, p in enumerate(ob.data.points):
            loc = mat @ p.co_deform # co_deform is the position in edit mode
            pt_distance, pt_dot = {}, {}
            for b in deform_bones:
                bone_vec = ((mat_arm @ b.tail) - (mat_arm @ b.head)).normalized()
                nearest_point_on_bone, factor = intersect_point_line(
                    loc, mat_arm @ b.head, mat_arm @ b.tail) # 0 is point, 1 is factor
                if factor > 1.0: nearest_point_on_bone = mat_arm @ b.tail
                if factor < 0.0: nearest_point_on_bone = mat_arm @ b.head
                point_vec = nearest_point_on_bone - loc
                distance = point_vec.length_squared # no need to sqrt, this is faster and
                # the quadratic falloff is better than linear falloff.
                dot = 1-abs(point_vec.normalized().dot(bone_vec))
                # we want to weight zero at 1.0 so that it favors points in its "envelope"
                pt_distance[b.name]=distance; pt_dot[b.name] = dot
            # now we can assign weights
            distance_pairs = [(k,v) for k,v in pt_distance.items()]
            distance_pairs.sort(key = lambda a : a[1])
            i=0; max_distance = 0.0; near_enough_bones = []
            while (i < 4): # TODO: limit-total should be exposed to the user.
                if i+1 > len(distance_pairs): break # in case there are fewer than 4 deform bones
                near_enough_bones.append(distance_pairs[i][0])
                if distance_pairs[i][1] > max_distance: max_distance = distance_pairs[i][1]
                i+=1
            max_pre_normalized_weight = 0.0
            weights = {}
            if max_distance == 0.0:  max_distance = 1.0
            for b_name in near_enough_bones:
                w = 1.0
                if pt_distance[b_name] > 0:
                    w*= 1/(pt_distance[b_name]/max_distance) # weight by inverse-distance
                w*= pt_dot[b_name]**4 # NOTE: **4 is arbitrary but feels good to me.
                if w > max_pre_normalized_weight: max_pre_normalized_weight = w
                weights[b_name] = w
            if max_pre_normalized_weight == 0.0: max_pre_normalized_weight = 1.0
            for b_name in near_enough_bones:
                vg = ob.vertex_groups.get(b_name)
                vg.add([p_index], weights[b_name]/max_pre_normalized_weight, 'REPLACE')
        armOb.data.pose_position = 'POSE'
    

    def bFinalize(self, bContext=None):
        prGreen("Executing Armature Deform Node")
        mod_name = self.evaluate_input("Name")
        for xf in self.GetxForm():
            ob = xf.bGetObject()
            d = ob.modifiers.new(mod_name, type='ARMATURE')
            if d is None:
                raise RuntimeError(f"Modifier was not created in node {self} -- the object is invalid.")
            self.bObject.append(d)
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
                match ob.type:
                    case "MESH":
                        self.do_automatic_skinning_mesh(ob, xf, bContext)
                    case "LATTICE":
                        self.do_automatic_skinning_lattice(ob, xf, bContext)
            elif skin_method == "COPY_FROM_OBJECT":
                self.initialize_vgroups(xf)
                self.copy_weights(xf)
            # elif skin_method == "EXISTING_GROUPS":
            #     pass


class DeformerHook(MantisDeformerNode):
    '''A node representing a hook deformer'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, HookSockets)
        # now set up the traverse target...
        self.init_parameters(additional_parameters={"Name":None})
        self.set_traverse([("Deformer", "Deformer")])
        self.prepared = True

    def driver_for_radius(self, object, hook, index, influence, bezier=True):
        """ Creates a driver to control the radius of a curve point with the hook."""
        from bpy.types import Bone, PoseBone
        var_template = {"owner":hook,
                        "name":"a",
                        "type":"TRANSFORMS",
                        "space":'WORLD_SPACE',
                        "channel":'SCALE_X',}
        var1_template = {"owner":hook.id_data,
                        "name":"b",
                        "type":"TRANSFORMS",
                        "space":'WORLD_SPACE',
                        "channel":'SCALE_X',}
        keys_template = [{"co":(0,0),
                          "interpolation": "LINEAR",
                          "type":"KEYFRAME",},
                         {"co":(1,influence),
                          "interpolation": "LINEAR",
                          "type":"KEYFRAME",},]
        if bezier:
            owner=object.data.splines[0].bezier_points
        else:
            owner=object.data.splines[0].points
        driver = {
            "owner":owner[index],
            "prop":"radius",
            "ind":-1,
            "extrapolation":"LINEAR",
            "type":"AVERAGE",
            "vars":[],
            "keys":keys_template,
        }
        if isinstance(hook, (Bone, PoseBone)):
            driver['type']='SCRIPTED'
            driver['expression']="(((1/b)*a)+((1/b_001)*a_001)+((1/b_002)*a_002))/3"
        from .drivers import CreateDrivers
        axes='XYZ'
        for i in range(3):
            var = var_template.copy()
            var["channel"]="SCALE_"+axes[i]
            driver["vars"].append(var)
            if isinstance(hook, (Bone, PoseBone)):
                var1=var1_template.copy()
                var1['channel']="SCALE_"+axes[i]
                driver['vars'].append(var1)
        CreateDrivers([driver])
            
    def bExecute(self, bContext = None,):
        self.executed = True

    def bFinalize(self, bContext=None):
        from bpy.types import Bone, PoseBone, Object
        prGreen(f"Executing Hook Deform Node: {self}")
        mod_name = self.evaluate_input("Name")
        affect_radius = self.evaluate_input("Affect Curve Radius")
        auto_bezier = self.evaluate_input("Auto-Bezier")
        target_node = self.evaluate_input('Hook Target')
        target = target_node.bGetObject(); subtarget = ""
        props_sockets = self.gen_property_socket_map()
        if isinstance(target, Bone) or isinstance(target, PoseBone):
            subtarget = target.name; target = target.id_data
        for xf in self.GetxForm():
            ob=xf.bGetObject()
            if ob.type == 'CURVE':
                spline_index = self.evaluate_input("Spline Index")
                from .utilities import get_extracted_spline_object
                ob = get_extracted_spline_object(ob, spline_index, self.mContext)
            
            reuse = False
            for m in ob.modifiers:
                if  m.type == 'HOOK' and m.object == target and m.subtarget == subtarget:
                    if self.evaluate_input("Influence") != m.strength:
                        continue # make a new modifier so they can have different strengths
                    if ob.animation_data: # this can be None
                        drivers = ob.animation_data.drivers
                        for k in props_sockets.keys():
                            if driver := drivers.find(k):
                                # TODO: I should check to see if the drivers are the same...
                                break # continue searching for an equivalent modifier
                        else: # There was no driver - use this one.
                            d = m; reuse = True; break
                    else: # use this one, there can't be drivers without animation_data.
                        d = m; reuse = True; break
            else:
                d = ob.modifiers.new(mod_name, type='HOOK')
                if d is None:
                    raise RuntimeError(f"Modifier was not created in node {self} -- the object is invalid.")
            self.bObject.append(d)
            self.get_target_and_subtarget(d, input_name="Hook Target")
            vertices_used=[]
            if reuse: # Get the verts in the list... filter out all the unneeded 0's
                vertices_used = list(d.vertex_indices)
                include_0 = 0 in vertices_used
                vertices_used = list(filter(lambda a : a != 0, vertices_used))
                if include_0: vertices_used.append(0)
            # now we add the selected vertex to the list, too
            vertex = self.evaluate_input("Point Index")
            if ob.type == 'CURVE' and ob.data.splines[0].type == 'BEZIER' and auto_bezier:
                if affect_radius:
                    self.driver_for_radius(ob, target_node.bGetObject(), vertex, d.strength)
                vertex*=3
                vertices_used.extend([vertex, vertex+1, vertex+2])
            else:
                vertices_used.append(vertex)
            # if we have a curve and it is NOT using auto-bezier for the verts..
            if ob.type == 'CURVE' and ob.data.splines[0].type == 'BEZIER' and affect_radius and not auto_bezier:
                print (f"WARN: {self}: \"Affect Radius\" may not behave as expected"
                        " when used on Bezier curves without Auto-Bezier")
                #bezier point starts at 1, and then every third vert, so 4, 7, 10...
                if vertex%3==1:
                    self.driver_for_radius(ob, target_node.bGetObject(), vertex, d.strength)
            if ob.type == 'CURVE' and ob.data.splines[0].type != 'BEZIER' and \
                        affect_radius:
                self.driver_for_radius(ob, target_node.bGetObject(), vertex, d.strength, bezier=False)
                
            d.vertex_indices_set(vertices_used)
            evaluate_sockets(self, d, props_sockets)
        finish_drivers(self)
        # todo: this node should be able to take many indices in the future.
        # Also: I have a Geometry Nodes implementation of this I can use... maybe...


class DeformerMorphTarget(MantisDeformerNode):
    '''A node representing an armature deformer'''
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Relative to",
            "Object",
            "Deformer",
            "Vertex Group",
        ]
        outputs = [
          "Deformer",
          "Morph Target",
        ]
        # now set up the traverse target...
        self.outputs.init_sockets(outputs)
        self.inputs.init_sockets(inputs)
        self.init_parameters(additional_parameters={"Name":None})
        self.set_traverse([("Deformer", "Deformer")])
        self.node_type = "LINK"
        self.prepared = True
    
    def GetxForm(self, trace_input="Object"):
        trace = trace_single_line(self, trace_input)
        for node in trace[0]:
            if (isinstance(node, deformable_types)):
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



class DeformerMorphTargetDeform(MantisDeformerNode):
    '''A node representing an armature deformer'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Deformer",
            "Use Shape Key",
            "Use Offset",
        ]
        outputs = [
          "Deformer",
        ]
        self.outputs.init_sockets(outputs)
        self.inputs.init_sockets(inputs)
        self.init_parameters(additional_parameters={"Name":None})
        self.set_traverse([("Deformer", "Deformer")])
        self.node_type = "LINK"
        self.prepared = True
        self.executed = True
        setup_custom_props(self)
    
    # bpy.data.node_groups["Morph Deform.045"].nodes["Named Attribute.020"].data_type = 'FLOAT_VECTOR'
    # bpy.context.object.add_rest_position_attribute = True

    def reset_execution(self):
        return super().reset_execution()
        self.executed=True

    def gen_morph_target_modifier(self, xf, context):
        # first let's see if this is a no-op
        targets = []
        for k,v in self.inputs.items():
            if "Target" in k:
                targets.append(v)
        if not targets:
            return # nothing to do here.
        
        # at this point we make the node tree
        from .geometry_node_graphgen import gen_morph_target_nodes
        m, props_sockets = gen_morph_target_nodes(
                            self.evaluate_input("Name"),
                            xf.bGetObject(),
                            targets,
                            context,
                            use_offset=self.evaluate_input("Use Offset"))
        self.bObject.append(m)
        evaluate_sockets(self, m, props_sockets)
        finish_drivers(self)

    def gen_shape_key_lattice(self, xf, context):
        # first check if we need to do anything
        targets = []
        for k,v in self.inputs.items():
            if "Target" in k:
                targets.append(v)
        if not targets:
            return # nothing to do here
        # TODO: deduplicate the code above here
        from time import time
        start_time = time()
        from bpy import data
        ob = xf.bGetObject()
        dg = context.view_layer.depsgraph
        dg.update()
        if xf.has_shape_keys == False:
            lat = ob.data.copy()
            ob.data = lat
            ob.add_rest_position_attribute = True
            ob.shape_key_clear()
            ob.shape_key_add(name='Basis', from_mix=False)
        else:
            lat = ob.data
        xf.has_shape_keys = True
        
        # first make a basis shape key
        keys, props_sockets, ={}, {}
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
        
        self.bObject.append(sk.id_data)
        evaluate_sockets(self, sk.id_data, props_sockets)
        finish_drivers(self)
        prWhite(f"Initializing morph target took {time() -start_time} seconds")


        

    def gen_shape_key(self, xf, context):
        # TODO: make this a feature of the node definition that appears only when there are no prior deformers - and shows a warning!
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
        ob = xf.bGetObject()
        dg = context.view_layer.depsgraph
        dg.update()
        if xf.has_shape_keys == False:
            match ob.type:
                case 'MESH':
                    ob_data = data.meshes.new_from_object(ob, preserve_all_data_layers=True, depsgraph=dg)
                case 'LATTICE':
                    ob_data = ob.data.copy()
            ob.data = ob_data
            ob.add_rest_position_attribute = True
            ob.shape_key_clear()
            ob.shape_key_add(name='Basis', from_mix=False)
        else:
            ob_data = ob.data
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
            match ob.type:
                case 'MESH':
                    for j in range(len(ob_data.vertices)):
                        sk.data[j].co = sk_m.vertices[j].co # assume they match
                case 'LATTICE':
                    for j in range(len(ob.data.points)):
                        sk.data[j].co = sk_m.points[j].co_deform
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
        
        self.bObject.append(sk.id_data)
        evaluate_sockets(self, sk.id_data, props_sockets)
        finish_drivers(self)
        prWhite(f"Initializing morph target took {time() -start_time} seconds")

    def bFinalize(self, bContext=None):
        prGreen(f"Executing Morph Deform node {self}")
        use_shape_keys = self.evaluate_input("Use Shape Key")
        # if there is a not a prior deformer then there should be an option to use plain 'ol shape keys
        # GN is always desirable as an option though because it can be baked & many other reasons
        if use_shape_keys: # check and see if we can.
            if self.inputs.get("Deformer"): # I guess this isn't available in some node group contexts... bad. FIXME
                if (links := self.inputs["Deformer"].links):
                    if not links[0].from_node.parameters.get("Use Shape Key"):
                        use_shape_keys = False
                    elif links[0].from_node.parameters.get("Use Shape Key") == False:
                        use_shape_keys = False
        self.parameters["Use Shape Key"] = use_shape_keys
        for xf in self.GetxForm():
            # Lattice objects do not support geometry nodes at this time.
            ob = xf.bGetObject()
            if ob and ob.type == 'LATTICE':
                if not use_shape_keys:
                    raise NotImplementedError("Blender does not support Geometry Nodes for Lattices. "
                                              "Enable 'Shape Key' and execute again.")
                self.gen_shape_key(xf, bContext)
            elif use_shape_keys:
                self.gen_shape_key(xf, bContext)
            else:
                self.gen_morph_target_modifier(xf, bContext)



class DeformerSurfaceDeform(MantisDeformerNode):
    '''A node representing an surface deform modifier'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, SurfaceDeformSockets)
        # now set up the traverse target...
        self.init_parameters(additional_parameters={"Name":None})
        self.set_traverse([("Deformer", "Deformer")])
        self.prepared = True

    def GetxForm(self, socket="Deformer"):
        if socket == "Deformer":
            return super().GetxForm()
        else:
            trace_xForm_back(self, socket)
    
    def bExecute(self, bContext = None,):
        self.executed = True
         
    def bFinalize(self, bContext=None):
        prGreen("Executing Surface Deform Node")
        mod_name = self.evaluate_input("Name")
        for xf in self.GetxForm():
            ob = xf.bGetObject()
            d = ob.modifiers.new(mod_name, type='SURFACE_DEFORM')
            if d is None:
                raise RuntimeError(f"Modifier was not created in node {self} -- the object is invalid.")
            self.bObject.append(d)
            self.get_target_and_subtarget(d, input_name="Target")
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, d, props_sockets)

    def bModifierApply(self, bContext=None):
        for d in self.bObject:
            from bpy import ops
            from .utilities import bind_modifier_operator
            bind_modifier_operator(d, ops.object.surfacedeform_bind)


class DeformerMeshDeform(MantisDeformerNode):
    '''A node representing a mesh deform modifier'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, MeshDeformSockets)
        # now set up the traverse target...
        self.init_parameters(additional_parameters={"Name":None})
        self.set_traverse([("Deformer", "Deformer")])
        self.prepared = True

    def GetxForm(self, socket="Deformer"):
        if socket == "Deformer":
            return super().GetxForm()
        else:
            trace_xForm_back(self, socket)
    
    def bExecute(self, bContext = None,):
        self.executed = True
         
    def bFinalize(self, bContext=None):
        prGreen("Executing Mesh Deform Node")
        mod_name = self.evaluate_input("Name")
        for xf in self.GetxForm():
            ob = xf.bGetObject()
            d = ob.modifiers.new(mod_name, type='MESH_DEFORM')
            if d is None:
                raise RuntimeError(f"Modifier was not created in node {self} -- the object is invalid.")
            self.bObject.append(d)
            self.get_target_and_subtarget(d, input_name="Object")
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, d, props_sockets)

    def bModifierApply(self, bContext=None):
        for d in self.bObject:
            from bpy import ops
            from .utilities import bind_modifier_operator
            bind_modifier_operator(d, ops.object.meshdeform_bind)

    # todo: add influence parameter and set it up with vertex group and geometry nodes
    # todo: make cage object display as wireframe if it is not being used for something else
    #          or add the option in the Geometry Object node


class DeformerLatticeDeform(MantisDeformerNode):
    '''A node representing a lattice deform modifier'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, LatticeDeformSockets)
        # now set up the traverse target...
        self.init_parameters(additional_parameters={"Name":None})
        self.set_traverse([("Deformer", "Deformer")])
        self.prepared = True

    def GetxForm(self, socket="Deformer"):
        if socket == "Deformer":
            return super().GetxForm()
        else:
            trace_xForm_back(self, socket)
    
    def bExecute(self, bContext = None,):
        self.executed = True
         
    def bFinalize(self, bContext=None):
        prGreen("Executing Lattice Deform Node")
        mod_name = self.evaluate_input("Name")
        for xf in self.GetxForm():
            ob = xf.bGetObject()
            d = ob.modifiers.new(mod_name, type='LATTICE')
            if d is None:
                raise RuntimeError(f"Modifier was not created in node {self} -- the object is invalid.")
            self.bObject.append(d)
            self.get_target_and_subtarget(d, input_name="Object")
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, d, props_sockets)

class DeformerSmoothCorrectiveDeform(MantisDeformerNode):
    '''A node representing a corrective smooth deform modifier'''

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, SmoothDeformSockets)
        # now set up the traverse target...
        self.init_parameters(additional_parameters={"Name":None})
        self.set_traverse([("Deformer", "Deformer")])
        self.prepared = True

    def GetxForm(self, socket="Deformer"):
        if socket == "Deformer":
            return super().GetxForm()
        else:
            trace_xForm_back(self, socket)
    
    def bExecute(self, bContext = None,):
        self.executed = True
         
    def bFinalize(self, bContext=None):
        prGreen("Executing Smooth Deform Node")
        mod_name = self.evaluate_input("Name")
        for xf in self.GetxForm():
            ob = xf.bGetObject()
            d = ob.modifiers.new(mod_name, type='CORRECTIVE_SMOOTH')
            if d is None:
                raise RuntimeError(f"Modifier was not created in node {self} -- the object is invalid.")
            self.bObject.append(d)
            # self.get_target_and_subtarget(d, input_name="Object")
            props_sockets = self.gen_property_socket_map()
            evaluate_sockets(self, d, props_sockets)
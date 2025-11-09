from bpy.types import Operator
import bpy
from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)

def mantis_poll_op(context):
    space = context.space_data
    if hasattr(space, "node_tree"):
        if (space.node_tree):
            return (space.tree_type == "MantisTree")
    return False

def create_inheritance_node(pb, parent_name, bone_inherit_node, node_tree):
    from bpy.types import PoseBone
    parent_node = node_tree.nodes.new("linkInherit")
    parent_bone_node = node_tree.nodes.get(parent_name)
    if not parent_bone_node:
        raise RuntimeError("Can't Find parent node!!")
    parent_node.location = parent_bone_node.location; parent_node.location.x+=200
    node_tree.links.new(parent_bone_node.outputs["xForm Out"], parent_node.inputs['Parent'])
    if isinstance(pb, PoseBone):
        parent_node.inputs["Connected"].default_value        = pb.bone.use_connect
        parent_node.inputs["Inherit Scale"].default_value    = pb.bone.inherit_scale
        parent_node.inputs["Inherit Rotation"].default_value = pb.bone.use_inherit_rotation
    else:
        parent_node.inputs["Connected"].default_value        = False
        parent_node.inputs["Inherit Scale"].default_value    = "FULL"
        parent_node.inputs["Inherit Rotation"].default_value = True
    if (bone_inherit_node.get(parent_bone_node.name)):
        bone_inherit_node[parent_bone_node.name].append(parent_node)
    else:
        bone_inherit_node[parent_bone_node.name] = [parent_node]
    return parent_node

def get_pretty_name(name):
    if   name == "bbone_curveinx": return "BBone X Curve-In"
    elif name == "bbone_curveinz": return "BBone Z Curve-In"
    elif name == "bbone_curveoutx": return "BBone X Curve-Out"
    elif name == "bbone_curveoutz": return "BBone Z Curve-Out"
    elif name == "BBone HQ Deformation":
        raise NotImplementedError(wrapRed("I wasn't expecting this property to be driven lol why would you even want to do that"))

    elif name == "bbone_handle_type_start": return "BBone Start Handle Type"
    elif name == "bbone_handle_type_end": return "BBone End Handle Type"
    elif name == "bbone_x": return "BBone X Size"
    elif name == "bbone_z": return "BBone Z Size"
    elif name == "bbone_rollin": return "BBone Roll-In"
    elif name == "bbone_rollout": return "BBone Roll-Out"
    elif name == "bbone_scalein": return "BBone Scale-In"
    elif name == "bbone_scaleout": return "BBone Scale-Out"

    pretty = name.replace("_", " ")
    words = pretty.split(" "); pretty = ''
    for word in words:
        pretty+=(word.capitalize()); pretty+=' '
    return pretty [:-1] #omit the last trailing space


constraint_link_map={
    'COPY_LOCATION'     : "LinkCopyLocation",
    'COPY_ROTATION'     : "LinkCopyRotation",
    'COPY_SCALE'        : "LinkCopyScale",
    'COPY_TRANSFORMS'   : "LinkCopyTransforms",
    'LIMIT_DISTANCE'    : "LinkLimitDistance",
    'LIMIT_LOCATION'    : "LinkLimitLocation",
    'LIMIT_ROTATION'    : "LinkLimitRotation",
    'LIMIT_SCALE'       : "LinkLimitScale",
    'DAMPED_TRACK'      : "LinkDampedTrack",
    'LOCKED_TRACK'      : "LinkLockedTrack",
    'STRETCH_TO'        : "LinkStretchTo",
    'TRACK_TO'          : "LinkTrackTo",
    'CHILD_OF'          : "LinkInheritConstraint",
    'IK'                : "LinkInverseKinematics",
    'ARMATURE'          : "LinkArmature",
    'SPLINE_IK'         : "LinkSplineIK",
    'TRANSFORM'         : "LinkTransformation",
    'FLOOR'             : "LinkFloor",
    'SHRINKWRAP'        : "LinkShrinkWrap",
    'GEOMETRY_ATTRIBUTE': "LinkGeometryAttribute"
    }

def create_relationship_node_for_constraint(node_tree, c):
    if cls_name := constraint_link_map.get(c.type):
        return node_tree.nodes.new(cls_name)
    else:
        prRed ("Not yet implemented: %s" % c.type)
        return None

def fill_parameters(node, c, context):
    # just try the basic parameters...

    node.mute = not c.enabled
    if c.mute == True and c.enabled == True:
        node.mute = c.mute
        # this is obviously stupid, but it's the new API as of, IIRC, 2.80

    try:
        owner_space = c.owner_space
        if c.owner_space == 'CUSTOM':
            pass
            #raise NotImplementedError("Custom Space is a TODO")
        if ( input := node.inputs.get("Owner Space") ):
            input.default_value = owner_space
    except AttributeError:
        pass

    try:
        target_space = c.target_space
        if c.target_space == 'CUSTOM':
            pass
            #raise NotImplementedError("Custom Space is a TODO")
        if ( input := node.inputs.get("Target Space") ):
            input.default_value = target_space
    except AttributeError:
        pass

    try:
        use_x, use_y, use_z = c.use_x, c.use_y, c.use_z
        if ( input := node.inputs.get("Axes") ):
            input.default_value[0] = use_x
            input.default_value[1] = use_y
            input.default_value[2] = use_z
    except AttributeError:
        pass
    try:
        invert_x, invert_y, invert_z = c.invert_x, c.invert_y, c.invert_z
        if ( input := node.inputs.get("Invert") ):
            input.default_value[0] = invert_x
            input.default_value[1] = invert_y
            input.default_value[2] = invert_z
    except AttributeError:
        pass

    try:
        influence = c.influence
        if ( input := node.inputs.get("Influence") ):
            input.default_value = influence
    except AttributeError:
        pass

    # gonna dispense with the try/except from here on
    match c.type:
        case 'COPY_LOCATION':
            node.inputs["Head/Tail"].default_value = c.head_tail
            node.inputs["UseBBone"].default_value  = c.use_bbone_shape
        case 'COPY_ROTATION':
            node.inputs["RotationOrder"].default_value = c.euler_order
            # ofset (legacy) is not supported TODO BUG
            if (mix_mode := c.mix_mode) == 'OFFSET':
                mix_mode = 'AFTER' # TODO there should be a message here. IIRC rigify rigs use this
            node.inputs["Rotation Mix"].default_value  = mix_mode
        case'COPY_SCALE':
            node.inputs["Additive"].default_value = c.use_make_uniform
            node.inputs["Power"].default_value = c.power
            node.inputs["Average"].default_value  = c.use_make_uniform
            node.inputs["Offset"].default_value  = c.use_offset
        case'COPY_TRANSFORMS':
            node.inputs["Head/Tail"].default_value = c.head_tail
            node.inputs["UseBBone"].default_value  = c.use_bbone_shape
            node.inputs["Mix"].default_value  = c.mix_mode
        case 'LIMIT_LOCATION' | 'LIMIT_ROTATION' | 'LIMIT_SCALE':
            try:
                node.inputs["Use Max X"].default_value = c.use_max_x
                node.inputs["Use Max Y"].default_value = c.use_max_y
                node.inputs["Use Max Z"].default_value = c.use_max_z
                #
                node.inputs["Use Min X"].default_value = c.use_min_x
                node.inputs["Use Min Y"].default_value = c.use_min_y
                node.inputs["Use Min Z"].default_value = c.use_min_z
            except AttributeError: # rotation
                node.inputs["Use X"].default_value = c.use_limit_x
                node.inputs["Use Y"].default_value = c.use_limit_y
                node.inputs["Use Z"].default_value = c.use_limit_z
            node.inputs["Max X"].default_value = c.max_x
            node.inputs["Max Y"].default_value = c.max_y
            node.inputs["Max Z"].default_value = c.max_z
            #
            node.inputs["Min X"].default_value = c.min_x
            node.inputs["Min Y"].default_value = c.min_y
            node.inputs["Min Z"].default_value = c.min_z
        case 'DAMPED_TRACK':
            node.inputs["Head/Tail"].default_value   = c.head_tail
            node.inputs["UseBBone"].default_value    = c.use_bbone_shape
            node.inputs["Track Axis"].default_value  = c.track_axis
        case 'LOCKED_TRACK':
            node.inputs["Head/Tail"].default_value   = c.head_tail
            node.inputs["UseBBone"].default_value    = c.use_bbone_shape
            node.inputs["Track Axis"].default_value  = c.track_axis
            node.inputs["Lock Axis"].default_value   = c.lock_axis
        case 'STRETCH_TO':
            node.inputs["Head/Tail"].default_value = c.head_tail
            node.inputs["UseBBone"].default_value  = c.use_bbone_shape
            node.inputs["Volume Variation"].default_value = c.bulge
            node.inputs["Use Volume Min"].default_value = c.use_bulge_min
            node.inputs["Volume Min"].default_value = c.bulge_min
            node.inputs["Use Volume Max"].default_value = c.use_bulge_max
            node.inputs["Volume Max"].default_value = c.bulge_max
            node.inputs["Smooth"].default_value = c.bulge_smooth
            node.inputs["Maintain Volume"].default_value = c.volume
            node.inputs["Rotation"].default_value        = c.keep_axis
        case 'IK':
            node.inputs["Chain Length"].default_value = c.chain_count
            node.inputs["Use Tail"].default_value = c.use_tail
            node.inputs["Stretch"].default_value = c.use_stretch
            # this isn't quite right lol
            node.inputs["Position"].default_value = c.weight
            node.inputs["Rotation"].default_value = c.orient_weight
            if not (c.use_location):
                node.inputs["Position"].default_value = 0
            if not (c.use_rotation):
                node.inputs["Rotation"].default_value = 0
        case 'ARMATURE':
            node.inputs["Preserve Volume"].default_value = c.use_deform_preserve_volume
            node.inputs["Use Envelopes"].default_value = c.use_bone_envelopes
            node.inputs["Use Current Location"].default_value = c.use_current_location
            for i in range(len(c.targets)):
                with context.temp_override(node=node):
                    bpy.ops.mantis.link_armature_node_add_target()
                    node.inputs["Weight."+str(i).zfill(3)].default_value = c.targets[i].weight
        case 'SPLINE_IK':
            node.inputs["Chain Length"].default_value = c.chain_count
            node.inputs["Even Divisions"].default_value = c.use_even_divisions
            node.inputs["Chain Offset"].default_value = c.use_chain_offset
            node.inputs["Use Curve Radius"].default_value = c.use_curve_radius
            node.inputs["Y Scale Mode"].default_value = c.y_scale_mode
            node.inputs["XZ Scale Mode"].default_value = c.xz_scale_mode
        case 'TRANSFORM':
            # I can't be arsed to do all this work..
            from .link_nodes import transformation_props_sockets as props
            for prop, (sock_name, _unused) in props.items():
                if "from" in prop:
                    if prop in ["map_from"] or "to" in prop:
                       pass
                    elif c.map_from == 'LOCATION':
                        if "scale" in prop:
                            continue
                        if "rot" in prop:
                            continue
                    elif c.map_from == 'ROTATION':
                        if "rot" not in prop:
                            continue
                    elif c.map_from == 'SCALE':
                        if "scale" not in prop:
                            continue
                if "to" in prop:
                    if prop in ["map_to"] or "from" in prop:
                       pass
                    elif c.map_from == 'LOCATION':
                        if "scale" in prop:
                            continue
                        if "rot" in prop:
                            continue
                    elif c.map_from == 'ROTATION':
                        if "rot" not in prop:
                            continue
                    elif c.map_from == 'SCALE':
                        if "scale" not in prop:
                            continue
                node.inputs[sock_name].default_value = getattr(c, prop)
                if prop in "mute":
                    node.inputs[sock_name].default_value = not getattr(c, prop)
        case _:
            print (f"Not yet implemented: {c.type}")





def walk_edit_bone(armOb, bone):
    # this is a simplified version of the node-tree walking code
    bonePath, bones, lines, seek = [0,], set(), [], bone
    while (True):
        curheight = len(bonePath)-1; ind = bonePath[-1]
        if (curheight == 0) and (ind > len(bone.children)-1):
            break
        if (curheight > 0):
            parent = seek.parent
            if (ind > len(seek.children)-1 ):
                bonePath[curheight-1]+=1
                del bonePath[curheight]
                seek = parent
                continue
                # should work...
        seek = get_bone_from_path(bone, bonePath)

        if (seek.name not in bones):
            lines.append(bonePath.copy())
        bones.add(seek.name)

        if (seek.children):
            bonePath.append(0)
        else:
            bonePath[curheight] = bonePath[curheight] + 1
            seek = seek.parent
    return lines


def get_bone_from_path(root_bone, path):
    # this function assumes the path is valid
    path = path.copy(); bone = root_bone
    while(path):
        bone = bone.children[path.pop(0)]
    return bone

# THIS IS BAD AND DUMB
def setup_custom_properties(bone_node, pb):
    for k, v in pb.items():
        socktype, prop_type = '', type(v)
        if   prop_type == bool:
            socktype = 'ParameterBoolSocket'
        elif prop_type == int:
            socktype = 'ParameterIntSocket'
        elif prop_type == float:
            socktype = 'ParameterFloatSocket'
        elif prop_type == bpy.props.FloatVectorProperty:
            socktype = 'ParameterVectorSocket'
        elif prop_type == str:
            socktype = 'ParameterStringSocket'
        else:
            prRed(f"Cannot create property {k} of type {prop_type} in {bone_node}")
            continue # it's a PointerProp or something
        new_prop = bone_node.inputs.new( socktype, k)
        bone_node.outputs.new( socktype, k)
        # set its value and limits and such
        # the ui_data is where this is stored. Feels hacky.
        ui_data = pb.id_properties_ui(k).as_dict()
        new_prop.default_value = ui_data['default']

        for attr_name in ['min', 'max', 'soft_min', 'soft_max', 'description']:
            if prop_type == str and attr_name != "description":
                continue # the first four are not available for string prop.
            try:
                attr_val = ui_data[attr_name]
                # there is a weird conversion error for unset min/max
                # because it defaults to exactly the value of long or something?
                if not isinstance(attr_val, str): # this doesn't work??
                    if attr_val >= 2147483647.0: attr_val = 2147483646.0
                    if attr_val <= -2147483648.0: attr_val = -2147483647.0
                setattr(new_prop, attr_name, attr_val)
            except KeyError:
                # TODO: find out why this happens and quit using exceptions
                prRed(f"prop {k} has no attribute {attr_name} (in {bone_node})")

def setup_ik_settings(bone_node, pb):
    # Set Up IK settings:
    stiffness = [pb.ik_stiffness_x, pb.ik_stiffness_y, pb.ik_stiffness_z]
    lock = [pb.lock_ik_x, pb.lock_ik_y, pb.lock_ik_z]
    limit = [pb.use_ik_limit_x, pb.use_ik_limit_y, pb.use_ik_limit_z]
    bone_node.inputs["IK Stretch"].default_value = pb.ik_stretch
    bone_node.inputs["Lock IK"].default_value = lock
    bone_node.inputs["IK Stiffness"].default_value = stiffness
    bone_node.inputs["Limit IK"].default_value = limit
    bone_node.inputs["X Min"].default_value = pb.ik_min_x
    bone_node.inputs["X Max"].default_value = pb.ik_max_x
    bone_node.inputs["Y Min"].default_value = pb.ik_min_y
    bone_node.inputs["Y Max"].default_value = pb.ik_max_y
    bone_node.inputs["Z Min"].default_value = pb.ik_min_z
    bone_node.inputs["Z Max"].default_value = pb.ik_max_z

def setup_vp_settings(bone_node, pb, do_after, node_tree):
    # bone_node.inputs["Hide"].default_value = pb.bone.hide
    bone_node.inputs["Custom Object Scale"].default_value = pb.custom_shape_scale_xyz
    bone_node.inputs["Custom Object Translation"].default_value = pb.custom_shape_translation
    bone_node.inputs["Custom Object Rotation"].default_value = pb.custom_shape_rotation_euler
    bone_node.inputs["Custom Object Scale to Bone Length"].default_value = pb.use_custom_shape_bone_size
    bone_node.inputs["Custom Object Wireframe"].default_value = pb.bone.show_wire
    # bone_node.inputs["Layer Mask"].default_value = pb.bone.layers

    collection_membership = ''
    for col in pb.bone.collections:
        # TODO: implement this!
        pass
    bone_node.inputs["Bone Collection"].default_value = collection_membership



    if (shape_ob := pb.custom_shape):
        shape_n = None
        for n in node_tree.nodes:
            if n.name == shape_ob.name:
                shape_n = n
                break
        else: # we make it now
            shape_n = node_tree.nodes.new("InputExistingGeometryObject")
            shape_n.name = shape_ob.name
            shape_n.label = shape_ob.name
            shape_n.inputs["Name"].default_value = shape_ob.name
        node_tree.links.new(shape_n.outputs["Object"], bone_node.inputs['Custom Object'])

    if (shape_xform_ob := pb.custom_shape_transform): # not implemented just yet
        shape_xform_n = None
        for n in node_tree.nodes:
            if n.name == shape_xform_ob.name:
                shape_xform_n = n
                node_tree.links.new(shape_xform_n.outputs["xForm"], bone_node.inputs['Custom Object xForm Override'])
                break
        else: # make it a task
            do_after.add( ("Custom Object xForm Override", bone_node.name , shape_xform_ob.name ) )
    # all the above should be in a function.


def setup_df_settings(bone_node, pb):
        bone_node.inputs["Deform"].default_value = pb.bone.use_deform
        # TODO: get the rest of these working
        # eb.envelope_distance     = self.evaluate_input("Envelope Distance")
        # eb.envelope_weight       = self.evaluate_input("Envelope Weight")
        # eb.use_envelope_multiply = self.evaluate_input("Envelope Multiply")
        # eb.head_radius           = self.evaluate_input("Envelope Head Radius")
        # eb.tail_radius           = self.evaluate_input("Envelope Tail Radius")

def create_driver(in_node_name, out_node_name, armOb, finished_drivers, switches, driver_vars, fcurves, drivers, node_tree, context):
    # TODO: CLEAN this ABOMINATION
    # print ("DRIVER: ", in_node_name, out_node_name)
    in_node  = node_tree.nodes[ in_node_name]
    out_node = node_tree.nodes[out_node_name]
    for fc in armOb.animation_data.drivers:
        if (in_node.label not in fc.data_path) or ( "[\""+out_node.label+"\"]" not in fc.data_path):
#                        print ("node not in name?: %s" % fc.data_path)
            continue
        if fc.data_path in finished_drivers:
            continue
        finished_drivers.add(fc.data_path)
        # print ("Creating driver.... %s" % fc.data_path)
        keys = []
        for k in fc.keyframe_points:
            key = {}
            for prop in dir(k):
                if ("__" in prop) or ("bl_" in prop): continue
                #it's __name__ or bl_rna or something
                key[prop] = getattr(k, prop)
            keys.append(key)
        switch, inverted = False, False
        if (fc.evaluate(0) == 0) and (fc.evaluate(1) == 1):
            switch = True
        elif (fc.evaluate(0) == 1) and (fc.evaluate(1) == 0):
            switch = True; inverted = True
        if (fc.driver.type == 'SCRIPTED'):
            #print (fc.driver.expression)
            if not (len(fc.driver.variables) == 1 and fc.driver.expression == fc.driver.variables[0].name):
                switch = False
        if (switch):
            # OK, let's prepare before making the node
            #  we want to reuse existing nodes if possible.
            target_string = fc.driver.variables[0].targets[0].data_path
            if target_string == "":
                for var in fc.driver.variables:
                    print (var)
                    print (var.name)
                    print (var.targets)
            bone = target_string.split("pose.bones[\"")[1]
            bone = bone.split("\"]")[0]
            bone_node = node_tree.nodes.get(bone)
            if not (bone_node):
                raise RuntimeError("excpected to find....", bone)


            p_string = fc.driver.variables[0].targets[0].data_path
            p_string = p_string.split("[\"")[-1]; p_string = p_string.split("\"]")[0]
            #switch_node.inputs["Parameter"].default_value = p_string
            #switch_node.inputs["Parameter Index"].default_value = fc.array_index
            #switch_node.inputs["Invert Switch"].default_value = inverted
            parameter = fc.data_path

            # Try to find an existing node.
            fail = False
            switch_node = None
            for n in switches:
                # if n.inputs[0].is_linked:
                #     if n.inputs[0].links[0].from_node != bone_node:
                #         fail = True
                if n.inputs[0].is_linked:
                    if n.inputs[0].links[0].from_node != bone_node:
                        fail = True
                    if n.inputs[0].links[0].from_socket != bone_node.outputs.get(p_string):
                        fail = True
                else:
                    if n.inputs[0].default_value != p_string:
                        fail = True
                if n.inputs[1].default_value != fc.array_index:
                    fail = True
                if n.inputs[2].default_value != inverted:
                    fail = True
                if not fail:
                    switch_node = n
                    break # found it!
            else:
                # make and connect the switch node
                switch_node = node_tree.nodes.new("UtilitySwitch"); switches.append(switch_node)
                # node_tree.links.new(bone_node.outputs["xForm Out"], switch_node.inputs[0])
                try:
                    node_tree.links.new(bone_node.outputs[p_string], switch_node.inputs[0])
                except KeyError:
                    prRed("this is such bad code lol fix this", p_string)
                switch_node.inputs[1].default_value = fc.array_index
                switch_node.inputs[2].default_value = inverted
                #print ("   Inverted?  ", inverted, (fc.evaluate(0) == 1) and (fc.evaluate(1) == 0), switch_node.inputs[3].default_value)
                if not inverted:
                    pass # TODO find out why there is a warning here?
                    # print ("    --> Check this node: %s" % switch_node.name)
            # this may be a custom property or a normal property...
            # this should lead to a constraint
            if len(parameter.split("[\"") ) == 3:
                property = parameter.split(".")[-1]
                if (property == 'mute'): # this is mapped to the 'Enable' socket...
                    prop_in = out_node.inputs.get('Enable')
                else:
                    prop_in = out_node.inputs.get(get_pretty_name(property))
                if prop_in:
                    node_tree.links.new(switch_node.outputs["Driver"], prop_in)
                else:
                    print ("   couldn't find: ", property, out_node.label, out_node.name)
                # this won't always work tho
            #Finally, it should be noted that we are assuming it uses the same object ...
            #  drivers from Rigify always should use the same object, but I want to support
            #  detecting drivers across objects.
        else: # we'll have to set this one up manually
            # Let's make the variable nodes, the Driver node, and the fCurve node.
            # Get the variable information
            if (True):
                var_nodes = []; num_vars = 0
                for num_vars, var in enumerate(fc.driver.variables):
                    target1, target2, bone_target, bone_target2 = [None]*4
                    var_data = {}
                    var_data["Variable Type"] = var.type
                    var_data["Property"] = ""
                    if len(var.targets) >= 1:
                        target1 = var.targets[0]
                        if (var_data["Variable Type"] != 'SINGLE_PROP'):
                            bone_target = var.targets[0].bone_target
                        else: # figure it out by the data path string.
                            target_string = var.targets[0].data_path
                            bone_target = target_string.split("pose.bones[\"")[1]; bone_target = bone_target.split("\"]")[0]
                            # we also need to get the property.
                            p_string = fc.driver.variables[0].targets[0].data_path
                            p_string = p_string.split("[\"")[-1]; p_string = p_string.split("\"]")[0]
                            var_data["Property"] = p_string
                        if (var_data["Variable Type"] == 'TRANSFORMS'):
                            transform_channel_map = {
                                "LOC_X"     : ('location', 0),
                                "LOC_Y"     : ('location', 1),
                                "LOC_Z"     : ('location', 2),
                                "ROT_X"     : ('rotation', 0),
                                "ROT_Y"     : ('rotation', 1),
                                "ROT_Z"     : ('rotation', 2),
                                "ROT_W"     : ('rotation', 3),
                                "SCALE_X"   : ('scale', 0),
                                "SCALE_Y"   : ('scale', 1),
                                "SCALE_Z"   : ('scale', 2),
                                "SCALE_AVG" : ('scale', 3), }
                            # if (var.transform_type in transform_channel_map.keys()):
                            #     var_data["Property"], var_data["Property Index"] = transform_channel_map[var.transform_type]
                            prRed("I am pretty sure this thing does not friggin work with whatever it is I commented above...")
                            var_data["Evaluation Space"] = var.targets[0].transform_space
                            var_data["Rotation Mode"] = var.targets[0].rotation_mode
                    if len(var.targets) == 2:
                        target2 = var.targets[1]
                        bone_target2 = var.targets[1].bone_target
                    # check if the variable already exists in the tree.
                    target_node1, target_node2 = None, None
                    if (target1 and bone_target):
                        target_node1 = node_tree.nodes[bone_target]
                    elif (target1 and not bone_target):
                        target_node1 = node_tree.nodes[target1]
                    if (target2 and bone_target2):
                        target_node2 = node_tree.nodes[bone_target2]
                    elif (target2 and not bone_target2):
                        target_node2 = node_tree.nodes[target2]


                    var_node = None
                    for n in driver_vars:
                        fail = False
                        if (inp := n.inputs['xForm 1']).is_linked:
                            if inp.links[0].from_node != target_node1:
                                fail = True
                        if (inp := n.inputs['xForm 2']).is_linked:
                            if inp.links[0].from_node != target_node2:
                                fail = True
                        #
                        if n.inputs[0].default_value != var_data["Variable Type"]:
                            fail = True
                        if n.inputs[1].default_value != var_data["Property"]:
                            fail = True
                        try:
                            if n.inputs[2].default_value != var_data["Property Index"]:
                                fail = True
                            if n.inputs[3].default_value != var_data["Evaluation Space"]:
                                fail = True
                            if n.inputs[4].default_value != var_data["Rotation Mode"]:
                                fail = True
                        except KeyError:
                            pass # this is a SCRIPTED node it seems
                        if not fail:
                            var_node = n
                            prWhite("Variable Node Found %s!" % var_node )
                            break # found it!
                    else:
                        var_node = node_tree.nodes.new("UtilityDriverVariable"); driver_vars.append(var_node)
                        prRed("Creating Node: %s" % var_node.name)
                        for key, value in var_data.items():
                            try:
                                var_node.inputs[key].default_value = value
                            except TypeError as e: # maybe it is a variable\
                                if key == "Variable Type":
                                    var_node.inputs[key].default_value = "SINGLE_PROP"
                                else: raise e
                        if (target1 and bone_target):
                            node_tree.links.new(node_tree.nodes[bone_target].outputs['xForm Out'], var_node.inputs['xForm 1'])
                        elif (target1 and not bone_target):
                            node_tree.links.new(node_tree.nodes[target1].outputs['xForm Out'], var_node.inputs['xForm 1'])
                        if (target2 and bone_target2):
                            node_tree.links.new(node_tree.nodes[bone_target2].outputs['xForm Out'], var_node.inputs['xForm 2'])
                        elif (target2 and not bone_target2):
                            node_tree.links.new(node_tree.nodes[target2].outputs['xForm Out'], var_node.inputs['xForm 2'])
                    var_nodes.append(var_node)
                    num_vars+=1 # so the len(num_vars) will be correct
                # get the keyframes from the driver fCurve
                keys = {}
                from mathutils import Vector
                if len(fc.keyframe_points) > 0:
                    # TODO: make this do more than co_ui
                    for i, k in enumerate(fc.keyframe_points):
                        keys[i] = {'co_ui':k.co_ui}
                else:
                    if ((len(fc.modifiers) == 0) or ((fc.evaluate(0) == 0) and (fc.evaluate(1) == 1))):
                        keys[0] = {'co_ui':Vector((0, 0))}
                        keys[1] = {'co_ui':Vector((1, 1))}
                    elif (fc.evaluate(0) == 1) and (fc.evaluate(1) == 0):
                        keys[0] = {'co_ui':Vector((0, 1))}
                        keys[1] = {'co_ui':Vector((1, 0))}
                    else:
                        prRed ("Could not get keys!")
                        # TODO find out why this happens
                        pass
#                                elif (fc.evaluate(0) == 1) and (fc.evaluate(1) == 0):
#                                    kf0 = fc.keyframe_points[0]; kf0.co_ui = (0, 1)
#                                    kf1 = fc.keyframe_points[1]; kf1.co_ui = (1, 0)
                # now get the fCurve
                fCurve_node = None
                for n in fcurves:
                    fc_ob = n.fake_fcurve_ob; node_fc = fc_ob.animation_data.action.fcurves[0]
                    node_keys = {}
                    for i, k in enumerate(node_fc.keyframe_points):
                        node_keys[i] = {'co_ui':k.co_ui}
                    # now let's see if they are the same:
                    if (keys != node_keys):
                        continue
                    fCurve_node = n
                    break
                else:
                    fCurve_node = node_tree.nodes.new("UtilityFCurve")
                    # fc_ob = fCurve_node.fake_fcurve_ob
                    # node_fc = fc_ob.animation_data.action.fcurves[0]
                    # fcurves.append(fCurve_node)
                    # while(node_fc.keyframe_points): # clear it, it has a default FC
                    #     node_fc.keyframe_points.remove(node_fc.keyframe_points[0], fast=True)
                    # node_fc.update()
                    # node_fc.keyframe_points.add(len(keys))
                    # for k, v in keys.items():
                    #     node_fc.keyframe_points[k].co_ui = v['co_ui']
                    #     # todo eventually the other dict elements ofc
                    for num_keys, (k, v) in enumerate(keys.items()):
                        fCurve_node.inputs.new("KeyframeSocket", "Keyframe."+str(num_keys).zfill(3))
                        kf_node = node_tree.nodes.new("UtilityKeyframe")
                        kf_node.inputs[0].default_value = v['co_ui'][0]
                        kf_node.inputs[1].default_value = v['co_ui'][1]
                        node_tree.links.new(kf_node.outputs[0], fCurve_node.inputs[num_keys])


                # NOW the driver itself
                driver_node = None
                # checc for it...
                driver_node = node_tree.nodes.new("UtilityDriver")
                driver_node.inputs["Driver Type"].default_value = fc.driver.type
                driver_node.inputs["Expression"].default_value = fc.driver.expression.replace ('var', 'a')
                # HACK, fix the above with a more robust solution

                node_tree.links.new(fCurve_node.outputs[0], driver_node.inputs['fCurve'])
                for i, var_node in zip(range(num_vars), var_nodes):
                    # TODO TODO BUG HACK
                    with context.temp_override(node=driver_node):
                        bpy.ops.mantis.driver_node_add_variable()
                    # This causes an error when you run it from the console! DO NOT leave this
                    node_tree.links.new(var_node.outputs[0], driver_node.inputs[-1])
                # HACK duplicated code from earlier...
                parameter = fc.data_path
                prWhite( "parameter: %s" % parameter)
                property = ''
                if len(parameter.split("[\"") ) == 3:
                    property = parameter.split(".")[-1]
                    if (property == 'mute'): # this is mapped to the 'Enable' socket...
                        prop_in = out_node.inputs.get('Enable')
                    else:
                        prop_in = out_node.inputs.get(get_pretty_name(property))
                        if not prop_in: # this is a HACK because my solution is terrible and also bad
                            if property == "head_tail":
                                prop_in = out_node.inputs.get("Head/Tail")
                                # the socket should probably know what Blender thing is being mapped to it as a custom prop
                    if not prop_in:
                        # try one last thing:
                        property = parameter.split("targets[")[-1]

                        target_index = int(property[0])
                        property = "targets[" + property # HACK lol
                        # get the property by index...
                        prop_in = out_node.inputs[target_index*2+6+1] # this is the weight, not the target
                    if prop_in:
                        prRed ("   found: %s, %s, %s" % (property, out_node.label, out_node.name))
                        node_tree.links.new(driver_node.outputs["Driver"], prop_in)
                    else:
                        prRed ("   couldn't find: %s, %s, %s" % (property, out_node.label, out_node.name))
                elif len(parameter.split("[\"") ) == 2:
                    property = parameter.split(".")[-1]
                else:
                    prWhite( "parameter: %s" % parameter)
                    prRed ("   couldn't find: ", property, out_node.label, out_node.name)

def set_parent_from_node(pb, bone_inherit_node, node_tree):
        bone = pb.bone
        possible_parent_nodes = bone_inherit_node.get(bone.parent.name)
        # Set the parent
        parent = None

        if not (possible_parent_nodes):
            parent = create_inheritance_node(pb, bone.parent.name, bone_inherit_node, node_tree)
        else:
            for ppn in possible_parent_nodes:
                # check if it has the right connected, inherit scale, inherit rotation
                if ppn.inputs["Connected"].default_value  != pb.bone.use_connect:
                    continue
                if ppn.inputs["Inherit Scale"].default_value != pb.bone.inherit_scale:
                    continue
                if ppn.inputs["Inherit Rotation"].default_value != pb.bone.use_inherit_rotation:
                    continue
                parent = ppn; break
            else:
                parent = create_inheritance_node(pb, bone.parent.name, bone_inherit_node, node_tree)
        return parent

def do_generate_geom(ob, node_tree, parent_node=None):
    ob_node = node_tree.nodes.new("xFormGeometryObject")
    ob_node.name = ob.name; ob_node.label = ob.name
    ob_node.inputs["Name"].default_value=ob.name+"_MANTIS"
    if ob.data:
        geometry_node = node_tree.nodes.new("InputExistingGeometryData")
        geometry_node.inputs[0].default_value=ob.data.name
        node_tree.links.new(input=geometry_node.outputs[0], output=ob_node.inputs["Geometry"])
    matrix_of = node_tree.nodes.new("UtilityMatrixFromXForm")
    existing_ob = node_tree.nodes.new("InputExistingGeometryObject")

    existing_ob.inputs["Name"].default_value = ob.name
    node_tree.links.new(input=existing_ob.outputs[0], output=matrix_of.inputs[0])
    node_tree.links.new(input=matrix_of.outputs[0], output=ob_node.inputs["Matrix"])

    # Generate Deformers
    prev_def_node = None
    for m in ob.modifiers:
        if m.type == "ARMATURE":
            def_node = node_tree.nodes.new("DeformerArmature")
            def_node.inputs["Blend Vertex Group"].default_value = m.vertex_group
            def_node.inputs["Invert Vertex Group"].default_value = m.invert_vertex_group
            def_node.inputs["Preserve Volume"].default_value = m.use_deform_preserve_volume
            def_node.inputs["Use Multi Modifier"].default_value = m.use_multi_modifier
            def_node.inputs["Use Envelopes"].default_value = m.use_bone_envelopes
            def_node.inputs["Use Vertex Groups"].default_value = m.use_vertex_groups
            # def_node.inputs["Copy Skin Weights From"]
            def_node.inputs["Skinning Method"].default_value="EXISTING_GROUPS"
            def_ob = node_tree.nodes.get(m.object.name)
            # get the deformer's target object...
            if def_ob:
                node_tree.links.new(input=def_ob.outputs["xForm Out"], output=def_node.inputs["Armature Object"])
            if prev_def_node:
                node_tree.links.new(input=prev_def_node.outputs["Deformer"], inputs=def_node.inputs["Deformer"])
            prev_def_node = def_node

    if prev_def_node:
        node_tree.links.new(input=prev_def_node.outputs["Deformer"], output=ob_node.inputs["Deformer"])

    if parent_node:
        node_tree.links.new(input=parent_node.outputs["Inheritance"], output=ob_node.inputs["Relationship"])


    # not doing this
    # matrix_node = node_tree.nodes.new("InputMatrix")
    # matrix_node.first_row=ob.matrix_world[0:3]
    # matrix_node.second_row=ob.matrix_world[4:7]
    # matrix_node.third_row=ob.matrix_world[8:11]
    # matrix_node.fourth_row=ob.matrix_world[12:15]
    # node_tree.links.new(input=matrix_node.outputs[0], output=ob_node.inputs["Matrix"])






def do_generate_armature(armOb, context, node_tree, parent_node=None):
        from time import time
        start = time()

        meta_rig_nodes = {}
        bone_inherit_node = {}
        do_after = set()


        armature = node_tree.nodes.new("xFormArmatureNode")
        mr_node_name = armOb.name
        if not (mr_node:= meta_rig_nodes.get(mr_node_name)):
            mr_node = node_tree.nodes.new("UtilityMetaRig")
            meta_rig_nodes[mr_node_name] = mr_node
            mr_node.inputs[0].search_prop=armOb
        node_tree.links.new(input=mr_node.outputs[0], output=armature.inputs["Matrix"])
        if parent_node:
            node_tree.links.new()




        bones = []
        for root in armOb.data.bones:
            if root.parent is None:
                iter_start= time()
                milestone=time()
                prPurple("got the bone paths", time() - milestone); milestone=time()
                armature.inputs["Name"].default_value = armOb.name + "_MANTIS"
                armature.name = armOb.name; armature.label = armOb.name

                bones.extend([root])

        if parent_node:
            node_tree.links.new(input=parent_node.outputs["Inheritance"], output=armature.inputs["Relationship"])



        # for bone_path in lines:
        for bone in bones:
            prGreen(time() - milestone); milestone=time()
            # first go through the bone path and find relevant information
            bone_node = node_tree.nodes.new("xFormBoneNode")
            bone_node.inputs["Name"].default_value = bone.name
            bone_node.name, bone_node.label = bone.name, bone.name
            matrix = bone.matrix_local.copy()
            bone_node.inputs["Matrix"].default_value = [
                    matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
                    matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],
                    matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3], # last element is bone length, for mantis
                    matrix[3][0], matrix[3][1], matrix[3][2], bone.length ] #matrix[3][3], ]
            mr_node_name = armOb.name+":"+bone.name
            if not (mr_node:= meta_rig_nodes.get(mr_node_name)):
                mr_node = node_tree.nodes.new("UtilityMetaRig")
                meta_rig_nodes[mr_node_name] = mr_node
                mr_node.inputs[0].search_prop=armOb
                mr_node.inputs[1].armature=armOb
                mr_node.inputs[1].bone=bone.name
                mr_node.inputs[1].default_value=bone.name
            node_tree.links.new(input=mr_node.outputs[0], output=bone_node.inputs["Matrix"])
            pb = armOb.pose.bones[bone.name]

            if bone.parent: # not a root
                parent = set_parent_from_node(pb, bone_inherit_node, node_tree)
                # prWhite("Got parent node", time() - milestone); milestone=time()
                if parent is None:
                    raise RuntimeError("No parent node?")
            else: # This is a root
                if (parent_list := bone_inherit_node.get(armOb.name)) is None:
                    parent = node_tree.nodes.new("linkInherit")
                    bone_inherit_node[armOb.name] = [parent]
                    node_tree.links.new(armature.outputs["xForm Out"], parent.inputs['Parent'])
                    parent.inputs["Inherit Rotation"].default_value = True
                else:
                    parent = parent_list[0]
                node_tree.links.new(parent.outputs["Inheritance"], bone_node.inputs['Relationship'])



            bone_node.inputs["Lock Location"].default_value = pb.lock_location
            bone_node.inputs["Lock Rotation"].default_value = pb.lock_rotation
            bone_node.inputs["Lock Scale"].default_value    = pb.lock_scale
            bone_node.inputs["Rotation Order"].default_value = pb.rotation_mode

            setup_custom_properties(bone_node, pb)
            setup_ik_settings(bone_node, pb)
            setup_vp_settings(bone_node, pb, do_after, node_tree)
            setup_df_settings(bone_node, pb)

            # BBONES
            bone_node.inputs["BBone X Size"].default_value = pb.bone.bbone_x
            bone_node.inputs["BBone Z Size"].default_value = pb.bone.bbone_z
            bone_node.inputs["BBone Segments"].default_value = pb.bone.bbone_segments
            if pb.bone.bbone_mapping_mode == "CURVED":
                bone_node.inputs["BBone HQ Deformation"].default_value = True
            bone_node.inputs["BBone Start Handle Type"].default_value = pb.bone.bbone_handle_type_start
            bone_node.inputs["BBone End Handle Type"].default_value = pb.bone.bbone_handle_type_end
            bone_node.inputs["BBone Custom Start Handle"].default_value = pb.bone.bbone_handle_type_start
            bone_node.inputs["BBone Custom End Handle"].default_value = pb.bone.bbone_handle_type_end

            bone_node.inputs["BBone X Curve-In"].default_value = pb.bone.bbone_curveinx
            bone_node.inputs["BBone Z Curve-In"].default_value = pb.bone.bbone_curveinz
            bone_node.inputs["BBone X Curve-Out"].default_value = pb.bone.bbone_curveoutx
            bone_node.inputs["BBone Z Curve-Out"].default_value = pb.bone.bbone_curveoutz

            # prRed("BBone Implementation is not complete, expect errors and missing features for now")


            #
            for c in pb.constraints:
                # prWhite("constraint %s for %s" % (c.name, pb.name), time() - milestone); milestone=time()
                # make relationship nodes and set up links...
                if ( c_node := create_relationship_node_for_constraint(node_tree, c)):
                    c_node.label = c.name
                    # this node definitely has a parent inherit node.
                    c_node.location = parent.location; c_node.location.x += 200

                    try:
                        node_tree.links.new(parent.outputs["Inheritance"], c_node.inputs['Input Relationship'])
                    except KeyError: # not a inherit node anymore
                        node_tree.links.new(parent.outputs["Output Relationship"], c_node.inputs['Input Relationship'])
                    parent = c_node

                    #Target Tasks:
                    if (hasattr(c, "target") and not hasattr(c, "subtarget")):
                        do_after.add( ("Object Target", c_node.name , c.target.name ) )
                    if (hasattr(c, "subtarget")):
                        if c.target and c.subtarget: # this node has a target, find the node associated with it...
                            do_after.add( ("Target", c_node.name , c.subtarget ) )
                        else:
                            do_after.add( ("Object Target", c_node.name , c.target.name ) )
                    if (hasattr(c, "pole_subtarget")):
                        if c.pole_target and c.pole_subtarget: # this node has a pole target, find the node associated with it...
                            do_after.add( ("Pole Target", c_node.name , c.pole_subtarget ) )
                    fill_parameters(c_node, c, context)
                    if (hasattr(c, "targets")): # Armature Modifier, annoying.
                        for i in range(len(c.targets)):
                            if (c.targets[i].subtarget):
                                do_after.add( ("Target."+str(i).zfill(3), c_node.name , c.targets[i].subtarget ) )
                    # Driver Tasks
                    if armOb.animation_data:
                        for fc in armOb.animation_data.drivers:
                            pb_string = fc.data_path.split("[\"")[1]; pb_string = pb_string.split("\"]")[0]
                            try:
                                c_string = fc.data_path.split("[\"")[2]; c_string = c_string.split("\"]")[0]
                                do_after.add ( ("driver", bone_node.name, c_node.name) )
                            except IndexError: # the above expects .pose.bones["some name"].constraints["some constraint"]
                                do_after.add ( ("driver", bone_node.name, bone_node.name) ) # it's a property I guess
            try:
                node_tree.links.new(parent.outputs["Inheritance"], bone_node.inputs['Relationship'])
            except KeyError: # may have changed, see above
                node_tree.links.new(parent.outputs["Output Relationship"], bone_node.inputs['Relationship'])
            prPurple("iteration: ", time() - iter_start)
            bones.extend(bone.children)
        finished_drivers = set()
        switches, driver_vars, fcurves, drivers = [],[],[],[]

        # Now do the tasks.
        for (task, in_node_name, out_node_name) in do_after:
            # prOrange(task, in_node_name, out_node_name)f
            if task in ['Object Target']:
                in_node  = node_tree.nodes[ in_node_name ]
                out_node= node_tree.nodes.new("InputExistingGeometryObject")
                out_node.inputs["Name"].default_value=out_node_name
                node_tree.links.new(out_node.outputs["Object"], in_node.inputs["Target"])
            if task in ['Target', 'Pole Target']:
                in_node  = node_tree.nodes[ in_node_name ]
                try:
                    out_node = node_tree.nodes[ out_node_name ]
                except KeyError:
                    prRed (f"Failed to find node: {out_node_name} as pole target for node: {in_node_name} and input {task}")
                #
                node_tree.links.new(out_node.outputs["xForm Out"], in_node.inputs[task])
            elif (task[:6] == 'Target'):
                in_node  = node_tree.nodes[ in_node_name ]
                out_node = node_tree.nodes[ out_node_name ]
                #
                node_tree.links.new(out_node.outputs["xForm Out"], in_node.inputs[task])
            elif task in ["Custom Object xForm Override"]:
                shape_xform_n = None
                for n in node_tree.nodes:
                    if n.name == out_node_name:
                        shape_xform_n = n
                        node_tree.links.new(shape_xform_n.outputs["xForm Out"], node_tree.nodes[in_node_name].inputs['Custom Object xForm Override'])
                        break
                else: # make it a task
                    prRed("Cannot set custom object transform override for %s to %s" % (in_node_name, out_node_name))

            elif task in ["driver"]:
                create_driver(in_node_name, out_node_name, armOb, finished_drivers, switches, driver_vars, fcurves, drivers, node_tree, context)

            # annoyingly, Rigify uses f-modifiers to setup its fcurves
            # I do not intend to support fcurve modifiers in Mantis at this time


        for child in armOb.children:
            its_parent = None
            parent_name = armOb.name
            if child.parent_type == "BONE":
                parent_name = child.parent_bone
            if not (possible_parent_nodes := bone_inherit_node.get(parent_name)):
                its_parent = create_inheritance_node(child, parent_name, bone_inherit_node, node_tree)
            else:
                for ppn in possible_parent_nodes: # check if it has the right connected, inherit scale, inherit rotation
                    if ppn.inputs["Connected"].default_value  != False: continue
                    if ppn.inputs["Inherit Scale"].default_value != "FULL": continue
                    if ppn.inputs["Inherit Rotation"].default_value != True: continue
                    its_parent = ppn; break
                else:
                    its_parent = create_inheritance_node(pb, parent_name, bone_inherit_node, node_tree)

            if child.type in ["MESH", "CURVE", "EMPTY"]:
                do_generate_geom(child, node_tree, its_parent)
            if child.type in ["ARMATURE"]:
                do_generate_armature(armOb, context, node_tree, parent_node=its_parent)

        for node in node_tree.nodes:
            node.select = False

        prGreen("Finished generating %d nodes in %f seconds." % (len(node_tree.nodes), time() - start))




        return armature



class GenerateMantisTree(Operator):
    """Generate Mantis Tree From Selected"""
    bl_idname = "mantis.generate_tree"
    bl_label = "Generate Mantis Tree from Selected"

    @classmethod
    def poll(cls, context):
        return (mantis_poll_op(context))

    def execute(self, context):
        space = context.space_data
        path = space.path
        node_tree = space.path[len(path)-1].node_tree

        do_profile=False

        #This will generate it in the current node tree and OVERWRITE!
        node_tree.nodes.clear() # is this wise?

        import cProfile
        from os import environ
        if environ.get("DOPROFILE"):
            do_profile=True

        node_tree.do_live_update = False
        node_tree.is_exporting = True
        try:
            if do_profile:
                cProfile.runctx("do_generate_armature(context.active_object, context, node_tree)", None, locals())
            else:
                do_generate_armature(context.active_object, context, node_tree)
            from .utilities import SugiyamaGraph
            for n in node_tree.nodes:
                n.select = True # Sugiyama sorting requires selection.
            SugiyamaGraph(node_tree, 16)
        except ImportError: # if for some reason Sugiyama isn't available
            pass
        finally:
            node_tree.do_live_update = True
            node_tree.is_exporting = False
            node_tree.prevent_next_exec = True

        return {"FINISHED"}

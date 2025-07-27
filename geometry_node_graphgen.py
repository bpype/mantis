from .utilities import (prRed, prGreen, prPurple, prWhite, prOrange,
                        wrapRed, wrapGreen, wrapPurple, wrapWhite,
                        wrapOrange,)


def gen_morph_target_nodes(mod_name, mod_ob, targets, context, use_offset=True):
    from bpy import data
    modifier = mod_ob.modifiers.new(mod_name, type='NODES')
    mod_ob.add_rest_position_attribute = True
    ng = data.node_groups.new(mod_name, "GeometryNodeTree")
    modifier.node_group = ng
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
    if use_offset == False:
        rest_position = position
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

    if use_offset == True:
        prev_node = ng.nodes.new("FunctionNodeInputVector")
    else:
        prev_node = position
    for i, node in enumerate(add_these):
        add = ng.nodes.new("ShaderNodeVectorMath"); add.operation="ADD"
        ng.links.new(prev_node.outputs[0], output=add.inputs[0])
        ng.links.new(node.outputs[0], output=add.inputs[1])
        prev_node = add
    if use_offset == True:
        ng.links.new(add.outputs[0], output=set_position.inputs["Offset"])
    else:
        ng.links.new(add.outputs[0], output=set_position.inputs["Position"])
    
    try:
        from .utilities import SugiyamaGraph
        SugiyamaGraph(ng, 12)
    except ImportError:
        pass # this is unlikely to fail since I package the wheel but if it does it shouldn't crash out.

    for socket, ob in object_map.items():
        modifier[socket]=ob
    return modifier, props_sockets

def gen_object_instance_node_group():
    from bpy import data
    ng = data.node_groups.new("Object Instance", "GeometryNodeTree")
    ng.interface.new_socket("Object", in_out = "INPUT", socket_type="NodeSocketObject")
    ng.interface.new_socket("As Instance", in_out = "INPUT", socket_type="NodeSocketBool")
    ng.interface.new_socket("Object Instance", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    inp = ng.nodes.new("NodeGroupInput")
    ob_node = ng.nodes.new("GeometryNodeObjectInfo")
    out = ng.nodes.new("NodeGroupOutput")
    ng.links.new(input=inp.outputs["Object"], output=ob_node.inputs["Object"])
    ng.links.new(input=inp.outputs["As Instance"], output=ob_node.inputs["As Instance"])
    ng.links.new(input=ob_node.outputs["Geometry"], output=out.inputs["Object Instance"])
    inp.location = (-200, 0)
    out.location = ( 200, 0)
    return ng

def gen_import_obj_node_group():
    import bpy
    from bpy import data, types
    from math import pi as PI
    tree=bpy.data.node_groups.new("Import OBJ","GeometryNodeTree")
    tree.is_modifier=True
    tree.interface.new_socket(name="Path",description="Path to a OBJ file",in_out="INPUT",socket_type="NodeSocketString")
    tree.interface.new_socket(name="Geometry",description="",in_out="OUTPUT",socket_type="NodeSocketGeometry")
    Group_Input = tree.nodes.new("NodeGroupInput")
    Group_Output = tree.nodes.new("NodeGroupOutput")
    Import_OBJ = tree.nodes.new("GeometryNodeImportOBJ")
    Realize_Instances = tree.nodes.new("GeometryNodeRealizeInstances")
    Rotate_Instances = tree.nodes.new("GeometryNodeRotateInstances")
    Rotate_Instances.inputs[2].default_value=[PI/2,0.0, 0.0] # assume standard axes
    tree.links.new(Group_Input.outputs[0],Import_OBJ.inputs[0])
    tree.links.new(Rotate_Instances.outputs[0],Realize_Instances.inputs[0])
    tree.links.new(Realize_Instances.outputs[0],Group_Output.inputs[0])
    tree.links.new(Import_OBJ.outputs[0],Rotate_Instances.inputs[0])
    try:
        from .utilities import SugiyamaGraph
        SugiyamaGraph(tree, 4)
    except: # there should not ever be a user error if this fails
        pass
    return tree

def gen_simple_flip_modifier():
    import bpy
    from bpy import data, types
    tree=bpy.data.node_groups.new("Simple Flip","GeometryNodeTree")
    tree.is_modifier=True
    tree.interface.new_socket(name="Geometry",description="",in_out="OUTPUT",socket_type="NodeSocketGeometry")
    tree.interface.new_socket(name="Geometry",description="",in_out="INPUT",socket_type="NodeSocketGeometry")
    tree.interface.new_socket(name="Flip X",description="",in_out="INPUT",socket_type="NodeSocketBool")
    tree.interface.new_socket(name="Flip Y",description="",in_out="INPUT",socket_type="NodeSocketBool")
    tree.interface.new_socket(name="Flip Z",description="",in_out="INPUT",socket_type="NodeSocketBool")
    Group_Input = tree.nodes.new("NodeGroupInput")
    Group_Output = tree.nodes.new("NodeGroupOutput")
    Set_Position = tree.nodes.new("GeometryNodeSetPosition")
    Position = tree.nodes.new("GeometryNodeInputPosition")
    Combine_XYZ = tree.nodes.new("ShaderNodeCombineXYZ")
    Map_Range = tree.nodes.new("ShaderNodeMapRange")
    Map_Range_001 = tree.nodes.new("ShaderNodeMapRange")
    Map_Range_002 = tree.nodes.new("ShaderNodeMapRange")
    Map_Range.inputs[3].default_value     =  1.0
    Map_Range_001.inputs[3].default_value =  1.0
    Map_Range_002.inputs[3].default_value =  1.0
    Map_Range.inputs[4].default_value     = -1.0
    Map_Range_001.inputs[4].default_value = -1.0
    Map_Range_002.inputs[4].default_value = -1.0
    Vector_Math = tree.nodes.new("ShaderNodeVectorMath")
    Vector_Math.operation = "MULTIPLY"
    tree.links.new(Set_Position.outputs[0],Group_Output.inputs[0])
    tree.links.new(Group_Input.outputs[0],Set_Position.inputs[0])
    tree.links.new(Group_Input.outputs[1],Map_Range.inputs[0])
    tree.links.new(Map_Range.outputs[0],Combine_XYZ.inputs[0])
    tree.links.new(Map_Range_001.outputs[0],Combine_XYZ.inputs[1])
    tree.links.new(Map_Range_002.outputs[0],Combine_XYZ.inputs[2])
    tree.links.new(Group_Input.outputs[2],Map_Range_001.inputs[0])
    tree.links.new(Group_Input.outputs[3],Map_Range_002.inputs[0])
    tree.links.new(Combine_XYZ.outputs[0],Vector_Math.inputs[1])
    tree.links.new(Position.outputs[0],Vector_Math.inputs[0])
    tree.links.new(Vector_Math.outputs[0],Set_Position.inputs[2])
    try:
        from .utilities import SugiyamaGraph
        SugiyamaGraph(tree, 4)
    except: # there should not ever be a user error if this fails
        pass
    return tree

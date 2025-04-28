from .node_container_common import *
from .base_definitions import MantisNode, NodeSocket

def TellClasses():
             
    return [ 
             # xForm
             xFormArmature,
             xFormBone,
             xFormGeometryObject,
             xFormObjectInstance,
             xFormCurvePin,
           ]

#*#-------------------------------#++#-------------------------------#*#
# X - F O R M   N O D E S
#*#-------------------------------#++#-------------------------------#*#

def reset_object_data(ob):
    # moving this to a common function so I can figure out the details later
    ob.constraints.clear()
    ob.animation_data_clear() # this is a little dangerous. TODO find a better solution since this can wipe animation the user wants to keep
    ob.modifiers.clear() # I would also like a way to copy modifiers and their settings, or bake them down. oh well

def get_parent_node(node_container, type = 'XFORM'):
    # type variable for selecting whether to get either 
    #   the parent xForm  or the inheritance node
    node_line, socket = trace_single_line(node_container, "Relationship")
    parent_nc = None
    for i in range(len(node_line)):
        # check each of the possible parent types.
        if ( (node_line[ i ].__class__.__name__ == 'LinkInherit') ):
            try: # it's the next one
                if (type == 'XFORM'):
                    return node_line[ i + 1 ]
                else: # type = 'LINK'
                    return node_line[ i ]
            except IndexError: # if there is no next one...
                return None # then there's no parent!
    return None

def get_matrix(node):
    matrix = node.evaluate_input('Matrix')
    if matrix is None:
        node_line, socket = trace_single_line(node, "Matrix")
        raise RuntimeError(wrapRed(f"No matrix found for Armature {node}"))
    return matrix

def set_object_parent(node):
        parent_nc = get_parent_node(node, type='LINK')
        if (parent_nc):
            parent = None
            if node.inputs["Relationship"].is_linked:
                trace = trace_single_line(node, "Relationship")
                for other_node in trace[0]:
                    if other_node is node: continue # lol
                    if (other_node.node_type == 'XFORM'):
                        parent = other_node; break
                if parent is None:
                    prWhite(f"INFO: no parent set for {node}.")
                    return
                prWhite(f"INFO: setting parent of {node} to {other_node}.")
                
                if (parent.bObject) is None:
                    raise GraphError(f"Could not get parent object from node {parent} for {node}")
                if isinstance(parent, xFormBone):
                    armOb= parent.bGetParentArmature()
                    node.bObject.parent = armOb
                    node.bObject.parent_type = 'BONE'
                    node.bObject.parent_bone = parent.bObject
                else:
                    node.bObject.parent = parent.bGetObject()

class xFormNode(MantisNode):
    def __init__(self, signature, base_tree, socket_templates=[]):
        super().__init__(signature, base_tree, socket_templates)
        self.node_type = 'XFORM'
        self.bObject=None

    # because new objects are created during prep phase
    def reset_execution(self): 
        super().reset_execution()
        self.prepared=False

class xFormArmature(xFormNode):
    '''A node representing an armature object'''
    
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Name"           ,
            "Rotation Order" ,
            "Matrix"         ,
            "Relationship"   ,
        ]
        outputs = [
         "xForm Out",
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.set_traverse([("Relationship", "xForm Out")])

    def bPrepare(self, bContext=None):
        self.parameters['Matrix'] = get_matrix(self)
        self.prepared = True

    def bExecute(self, bContext = None,):
        # from .utilities import get_node_prototype
        
        import bpy
        if (not isinstance(bContext, bpy.types.Context)):
            raise RuntimeError("Incorrect context")

        name = self.evaluate_input("Name")
        matrix = self.parameters['Matrix']
        reset_transforms = False

        #check if an object by the name exists
        if (name) and (ob := bpy.data.objects.get(name)):
            if (ob.animation_data):
                while (ob.animation_data.drivers):
                        ob.animation_data.drivers.remove(ob.animation_data.drivers[-1])
            for pb in ob.pose.bones:
                # clear it, even after deleting the edit bones, 
                #  if we create them again the pose bones will be reused 
                while (pb.constraints):
                    pb.constraints.remove(pb.constraints[-1])
                if reset_transforms:
                    pb.location = (0,0,0)
                    pb.rotation_euler = (0,0,0)
                    pb.rotation_quaternion = (1.0,0,0,0)
                    pb.rotation_axis_angle = (0,0,1.0,0)
                    pb.scale = (1.0,1.0,1.0)
            # feels ugly and bad, whatever
            collections = []
            for bc in ob.data.collections:
                collections.append(bc)
            for bc in collections:
                ob.data.collections.remove(bc)
            del collections
            # end ugly/bad


        else:
            # Create the Object
            ob = bpy.data.objects.new(name, bpy.data.armatures.new(name)) #create ob
            if (ob.name != name):
                raise RuntimeError("Could not create xForm object", name)
            
        self.bObject = ob.name
        ob.matrix_world = matrix.copy()
        ob.data.pose_position = 'REST'
        set_object_parent(self)

        # Link to Scene:
        if (ob.name not in bContext.view_layer.active_layer_collection.collection.objects):
            bContext.view_layer.active_layer_collection.collection.objects.link(ob)

        print( wrapGreen("Created Armature object: ")+ wrapWhite(ob.name))
        # Finalize the action
        # oddly, overriding context doesn't seem to work
        try:
            bpy.ops.object.select_all(action='DESELECT')
        except RuntimeError:
            pass # we're already in edit mode, should be OK to do this.
        bContext.view_layer.objects.active = ob
        selected=[]
        for other_ob in bpy.data.objects:
            if other_ob.mode == "EDIT":
                selected.append(other_ob)
        selected.append(ob)
        context_override = {"active_object":ob, "selected_objects":selected}
        print("Changing Armature Mode to " +wrapPurple("EDIT"))
        with bContext.temp_override(**context_override):
            bpy.ops.object.mode_set(mode='EDIT')
        if ob.mode != "EDIT":
            prRed("eh?")
        # clear it
        while (len(ob.data.edit_bones) > 0):
            ob.data.edit_bones.remove(ob.data.edit_bones[0])
        # bContext.view_layer.objects.active = prevAct

        self.executed = True

    def bGetObject(self, mode = ''):
        import bpy; return bpy.data.objects[self.bObject]

bone_inputs= [
         "Name",
         "Rotation Order",
         "Matrix",
         "Relationship",
         # IK settings
         "IK Stretch",
         "Lock IK",
         "IK Stiffness",
         "Limit IK",
         "X Min",
         "X Max",
         "Y Min",
         "Y Max",
         "Z Min",
         "Z Max",
         # Visual stuff
         "Bone Collection",
         "Hide",
         "Custom Object",
         "Custom Object xForm Override",
         "Custom Object Scale to Bone Length",
         "Custom Object Wireframe",
         "Custom Object Scale",
         "Custom Object Translation",
         "Custom Object Rotation",
         # Deform Stuff
         "Deform",
         "Envelope Distance",
         "Envelope Weight",
         "Envelope Multiply",
         "Envelope Head Radius",
         "Envelope Tail Radius",
         # BBone stuff:
         "BBone Segments",
         "BBone X Size",
         "BBone Z Size",
         "BBone HQ Deformation",
         "BBone X Curve-In",
         "BBone Z Curve-In",
         "BBone X Curve-Out",
         "BBone Z Curve-Out",
         "BBone Roll-In",
         "BBone Roll-Out",
         "BBone Inherit End Roll",
         "BBone Scale-In",
         "BBone Scale-Out",
         "BBone Ease-In",
         "BBone Ease-Out",
         "BBone Easing",
         "BBone Start Handle Type",
         "BBone Custom Start Handle",
         "BBone Start Handle Scale",
         "BBone Start Handle Ease",
         "BBone End Handle Type",
         "BBone Custom End Handle",
         "BBone End Handle Scale",
         "BBone End Handle Ease",
         # locks
         "Lock Location",
         "Lock Rotation",
         "Lock Scale",
]
class xFormBone(xFormNode):
    '''A node representing a bone in an armature'''
    # DO: make a way to identify which armature this belongs to
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        outputs = [
         "xForm Out",
        ]
        self.inputs.init_sockets(bone_inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.set_traverse([("Relationship", "xForm Out")])
    
    def bGetParentArmature(self):
        if (trace := trace_single_line(self, "Relationship")[0] ) :
            for i in range(len(trace)):
                # have to look in reverse, actually TODO
                if ( isinstance(trace[ i ], xFormArmature ) ):
                    return trace[ i ].bGetObject()
        return None
        #should do the trick...
    
    def bSetParent(self, eb):
        # print (self.bObject)
        from bpy.types import EditBone
        parent_nc = get_parent_node(self, type='LINK')
        # print (self, parent_nc.inputs['Parent'].from_node)
        parent=None
        if parent_nc.inputs['Parent'].links[0].from_node.node_type == 'XFORM':
            parent = parent_nc.inputs['Parent'].links[0].from_node.bGetObject(mode = 'EDIT')
        else:
            raise RuntimeError(wrapRed(f"Cannot set parent for node {self}"))

        if isinstance(parent, EditBone):
            eb.parent = parent
            
        eb.use_connect = parent_nc.evaluate_input("Connected")
        eb.use_inherit_rotation = parent_nc.evaluate_input("Inherit Rotation")
        eb.inherit_scale = parent_nc.evaluate_input("Inherit Scale")
        # otherwise, no need to do anything.
    
    def bPrepare(self, bContext=None):
        self.parameters['Matrix'] = get_matrix(self)
        self.prepared = True
    
    def bExecute(self, bContext = None,): #possibly will need to pass context?
        import bpy
        from mathutils import Vector
        if not (name := self.evaluate_input("Name")):
            raise RuntimeError(wrapRed(f"Could not set name for bone in {self}"))
        if (not isinstance(bContext, bpy.types.Context)):
            raise RuntimeError("Incorrect context")
        if not (xF := self.bGetParentArmature()):
            raise RuntimeError("Could not create edit bone: ", name, " from node:", self, " Reason: No armature object to add bone to.")

        matrix = self.parameters['Matrix']
        length = matrix[3][3]
        
        if (xF):
            if (xF.mode != "EDIT"):
                raise RuntimeError("Armature Object Not in Edit Mode, exiting...")
        #
        # Create the Object
        d = xF.data
        eb = d.edit_bones.new(name)

        # Bone Collections:
        #    We treat each separate string as a Bone Collection that this object belongs to
        #    Bone Collections are fully qualified by their hierarchy.
        #    Separate Strings with "|" and indicate hierarchy with ">". These are special characters.
        # NOTE: if the user names the collections differently at different times, this will take the FIRST definition and go with it
        sCols = self.evaluate_input("Bone Collection")
        bone_collections = sCols.split("|")
        for collection_list in bone_collections:
            hierarchy = collection_list.split(">")
            col_parent = None
            for sCol in hierarchy:
                if ( col := d.collections.get(sCol) ) is None:
                    col = d.collections.new(sCol)
                col.parent = col_parent
                col_parent = col
            col.assign(eb)
        
        if (eb.name != name):
            prRed(f"Expected bone of name: {name}, got {eb.name} instead.")
            raise RuntimeError("Could not create bone ", name, "; Perhaps there is a duplicate bone name in the node tree?")
        eb.matrix  = matrix.copy()
        tailoffset = Vector((0,length,0)) #Vector((0,self.tailoffset, 0))
        tailoffset = matrix.copy().to_3x3() @ tailoffset
        eb.tail    = eb.head + tailoffset
        if (eb.name != name):
            raise RuntimeError("Could not create edit bone: ", name)
        assert (eb.name), "Bone must have a name."
        self.bObject = eb.name
        # The bone should have relationships going in at this point.
        
        self.bSetParent(eb)

        if eb.head == eb.tail:
            raise RuntimeError(wrapRed(f"Could not create edit bone: {name} because bone head was located in the same place as bone tail."))
        
        # Setup Deform attributes...
        eb.use_deform            = self.evaluate_input("Deform")
        eb.envelope_distance     = self.evaluate_input("Envelope Distance")
        eb.envelope_weight       = self.evaluate_input("Envelope Weight")
        eb.use_envelope_multiply = self.evaluate_input("Envelope Multiply")
        eb.head_radius           = self.evaluate_input("Envelope Head Radius")
        eb.tail_radius           = self.evaluate_input("Envelope Tail Radius")

        print( wrapGreen("Created Bone: ") + wrapOrange(eb.name) + wrapGreen(" in ") + wrapWhite(self.bGetParentArmature().name))
        self.executed = True

    def bFinalize(self, bContext = None):
        do_bb=False
        b = self.bGetParentArmature().data.bones[self.bObject]
        b.bbone_x = self.evaluate_input("BBone X Size"); b.bbone_x = max(b.bbone_x, 0.0002)
        b.bbone_z = self.evaluate_input("BBone Z Size"); b.bbone_z = max(b.bbone_z, 0.0002)
        if (segs := self.evaluate_input("BBone Segments")) > 1:
            do_bb=True
            b.bbone_segments = segs
            b.bbone_x = self.evaluate_input("BBone X Size")
            b.bbone_z = self.evaluate_input("BBone Z Size")
            if self.evaluate_input("BBone HQ Deformation"):
                b.bbone_mapping_mode = "CURVED"
            # 'bbone_handle_type_start'    : ("BBone Start Handle Type", "AUTO"),
            # 'bbone_handle_type_end'      : ("BBone End Handle Type", "AUTO"),
            # 'bbone_custom_handle_start'  : ("BBone Custom Start Handle", "AUTO"),
            # 'bbone_custom_handle_end'    : ("BBone Custom End Handle", "AUTO"),
            if handle_type := self.evaluate_input("BBone Start Handle Type"):
                b.bbone_handle_type_start = handle_type
            if handle_type := self.evaluate_input("BBone End Handle Type"):
                b.bbone_handle_type_end = handle_type
            
            try:
                if (custom_handle := self.evaluate_input("BBone Custom Start Handle")):
                    b.bbone_custom_handle_start = self.bGetParentArmature().data.bones[custom_handle]
                # hypothetically we should support xForm inputs.... but we won't do that for now
                # elif custom_handle is None:
                #     b.bbone_custom_handle_start = self.inputs["BBone Custom Start Handle"].links[0].from_node.bGetObject().name
                if (custom_handle := self.evaluate_input("BBone Custom End Handle")):
                    b.bbone_custom_handle_end = self.bGetParentArmature().data.bones[custom_handle]
            except KeyError:
                prRed("Warning: BBone start or end handle not set because of missing bone in armature.")

            bone_props_socket= {
                'bbone_curveinx'     : ("BBone X Curve-In", 0.0),
                'bbone_curveinz'     : ("BBone Z Curve-In", 0.0),
                'bbone_curveoutx'    : ("BBone X Curve-Out", 0.0),
                'bbone_curveoutz'    : ("BBone Z Curve-Out", 0.0),
            }
            evaluate_sockets(self, b, bone_props_socket)
            # TODO this section should be done with props-socket thing
            b.bbone_handle_use_scale_start = self.evaluate_input("BBone Start Handle Scale")
            b.bbone_handle_use_scale_end = self.evaluate_input("BBone End Handle Scale")

            
        import bpy
        from .drivers import MantisDriver
        # prevAct = bContext.view_layer.objects.active
        # bContext.view_layer.objects.active = ob
        # bpy.ops.object.mode_set(mode='OBJECT')
        # bContext.view_layer.objects.active = prevAct
        #
        #get relationship
        # ensure we have a pose bone...
        # set the ik parameters
        #
        #
        # Don't need to bother about whatever that was
        
        pb = self.bGetParentArmature().pose.bones[self.bObject]
        rotation_mode = self.evaluate_input("Rotation Order")
        if rotation_mode == "AUTO": rotation_mode = "XYZ"
        pb.rotation_mode = rotation_mode
        pb.id_properties_clear()
        # these are kept around unless explicitly deleted.
        # from .utilities import get_node_prototype
        # np = get_node_prototype(self.signature, self.base_tree)
        driver = None
        do_prints=False

        # detect custom inputs
        for i, inp in enumerate(self.inputs.values()):
            if inp.name in bone_inputs:
                continue
            
            
            name = inp.name
            try:
                value = self.evaluate_input(inp.name)
            except KeyError as e:
                trace = trace_single_line(self, inp.name)
                if do_prints: print(trace[0][-1], trace[1])
                if do_prints: print (trace[0][-1].parameters)
                raise e
            # This may be driven, so let's do this:
            if do_prints: print (value)
            if (isinstance(value, tuple)):
                raise RuntimeError(f"The custom property type is not supported: {self}")
            if (isinstance(value, MantisDriver)):
                # the value should be the default for its socket...
                if do_prints: print (type(self.parameters[inp.name]))
                type_val_map = {
                    str:"",
                    bool:False,
                    int:0,
                    float:0.0,
                    bpy.types.bpy_prop_array:(0,0,0),
                    }
                driver = value
                value = type_val_map[type(self.parameters[inp.name])]
            if (value is None):
                raise RuntimeError("Could not set value of custom parameter")
                # it creates a more confusing error later sometimes, better to catch it here.
            
            # IMPORTANT: Is it possible for more than one driver to
            #   come through here, and for the variable to be
            #   overwritten?
                
            #TODO important
            #from rna_prop_ui import rna_idprop_ui_create
            # use this ^
            
            # add the custom properties to the **Pose Bone**
            pb[name] = value
            # This is much simpler now.
            ui_data = pb.id_properties_ui(name)
            description=''
            ui_data.update(
                description=description,#inp.description,
                default=value,)
            #if a number

            if type(value) == float:
                ui_data.update(
                    min = inp.min,
                    max = inp.max,
                    soft_min = inp.soft_min,
                    soft_max = inp.soft_max,)
                        
            elif type(value) == int:
                ui_data.update(
                    min = int(inp.min),
                    max = int(inp.max),
                    soft_min = int(inp.soft_min),
                    soft_max = int(inp.soft_max),)
            elif type(value) == bool:
                ui_data.update() # TODO I can't figure out what the update function expects because it isn't documented
        
        if (pb.is_in_ik_chain):
            # this  props_socket thing wasn't really meant to work here but it does, neat
            props_sockets = {
            'ik_stretch'          : ("IK Stretch", 0),
            'lock_ik_x'           : (("Lock IK", 0), False),
            'lock_ik_y'           : (("Lock IK", 1), False),
            'lock_ik_z'           : (("Lock IK", 2), False),
            'ik_stiffness_x'      : (("IK Stiffness", 0), 0.0),
            'ik_stiffness_y'      : (("IK Stiffness", 1), 0.0),
            'ik_stiffness_z'      : (("IK Stiffness", 2), 0.0),
            'use_ik_limit_x'      : (("Limit IK", 0), False),
            'use_ik_limit_y'      : (("Limit IK", 1), False),
            'use_ik_limit_z'      : (("Limit IK", 2), False),
            'ik_min_x'            : ("X Min", 0),
            'ik_max_x'            : ("X Max", 0),
            'ik_min_y'            : ("Y Min", 0),
            'ik_max_y'            : ("Y Max", 0),
            'ik_min_z'            : ("Z Min", 0),
            'ik_max_z'            : ("Z Max", 0),
            }
            evaluate_sockets(self, pb, props_sockets)
        if do_bb:
            props_sockets = {
            'bbone_curveinx'             : ("BBone X Curve-In", pb.bone.bbone_curveinx),
            'bbone_curveinz'             : ("BBone Z Curve-In", pb.bone.bbone_curveinz),
            'bbone_curveoutx'            : ("BBone X Curve-Out", pb.bone.bbone_curveoutx),
            'bbone_curveoutz'            : ("BBone Z Curve-Out", pb.bone.bbone_curveoutz),
            'bbone_easein'               : ("BBone Ease-In", 0),
            'bbone_easeout'              : ("BBone Ease-Out", 0),
            'bbone_rollin'               : ("BBone Roll-In", 0),
            'bbone_rollout'              : ("BBone Roll-Out", 0),
            'bbone_scalein'              : ("BBone Scale-In", (1,1,1)),
            'bbone_scaleout'             : ("BBone Scale-Out", (1,1,1)),
            }
            evaluate_sockets(self, pb, props_sockets)
            # we need to clear this stuff since our only real goal was to get some drivers from the above
            for attr_name in props_sockets.keys():
                try:
                    setattr(pb, attr_name, 0) # just clear it
                except ValueError:
                    setattr(pb, attr_name, (1.0,1.0,1.0)) # scale needs to be set to 1


            # important TODO... all of the drivers and stuff should be handled this way, right?
        # time to set up drivers!


        # just gonna add this to the end and build off it I guess
        props_sockets = {
            "lock_location"               : ("Lock Location", [False, False, False]),
            "lock_rotation"               : ("Lock Rotation", [False, False, False]),
            "lock_scale"                  : ("Lock Scale", [False, False, False]),
            'custom_shape_scale_xyz'      : ("Custom Object Scale",  (0.0,0.0,0.0) ),
            'custom_shape_translation'    : ("Custom Object Translation",  (0.0,0.0,0.0) ),
            'custom_shape_rotation_euler' : ("Custom Object Rotation",  (0.0,0.0,0.0) ),
            'use_custom_shape_bone_size'  : ("Custom Object Scale to Bone Length",  True,)
        }

        evaluate_sockets(self, pb, props_sockets)

        # this could probably be moved to bExecute
        props_sockets = {
            'hide'      : ("Hide", False),
            'show_wire' : ("Custom Object Wireframe", False),
        }
        evaluate_sockets(self, pb.bone, props_sockets)

        
        if (driver):
            pass
        # whatever I was doing there.... was stupid. CLEAN UP TODO
        # this is the right thing to do.
        finish_drivers(self)
        #
        # OK, visual settings
        #
        # Get the override xform's bone:



        pb.custom_shape_transform = None
        pb.custom_shape = None
        
        if len(self.inputs["Custom Object xForm Override"].links) > 0:
            trace = trace_single_line(self, "Custom Object xForm Override")
            try:
                pb.custom_shape_transform = trace[0][1].bGetObject()
            except AttributeError:
                pass
                    
        if len(self.inputs["Custom Object"].links) > 0:
            trace = trace_single_line(self, "Custom Object")
            try:
                ob = trace[0][1].bGetObject()
            except AttributeError:
                ob=None
            if type(ob) in [bpy.types.Object]:
                pb.custom_shape = ob 

    def bGetObject(self, mode = 'POSE'):
        if self.bObject is None: return None
        if mode in ["POSE", "OBJECT"] and self.bGetParentArmature().mode == "EDIT":
            raise RuntimeError("Cannot get Bone or PoseBone in Edit mode.")
        elif mode == "EDIT" and self.bGetParentArmature().mode != "EDIT":
            raise RuntimeError("Cannot get EditBone except in Edit mode.")
        try:
            if   (mode == 'EDIT'):
                return self.bGetParentArmature().data.edit_bones[self.bObject]
            elif (mode == 'OBJECT'):
                return self.bGetParentArmature().data.bones[self.bObject]
            elif (mode == 'POSE'):
                return self.bGetParentArmature().pose.bones[self.bObject]
        except Exception as e:
            prRed ("Cannot get bone for %s" % self)
            raise e

    def fill_parameters(self, prototype=None):
        # this is the fill_parameters that is run if it isn't a schema
        setup_custom_props(self)
        super().fill_parameters(prototype)
        # otherwise we will do this from the schema 
        # LEGIBILITY TODO - why? explain this?

class xFormGeometryObject(xFormNode):
    '''A node representing an armature object'''
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Name"             ,
            "Geometry"         ,
            "Matrix"           ,
            "Relationship"     ,
            "Deformer"         ,
            "Hide in Viewport" ,
            "Hide in Render"   ,
        ]
        outputs = [
          "xForm Out",
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.set_traverse([("Relationship", "xForm Out")])
        self.has_shape_keys = False

    def bPrepare(self, bContext = None,):
        import bpy
        if not self.evaluate_input("Name"):
            self.prepared = True
            self.executed = True
            # and return an error if there are any dependencies:
            if self.hierarchy_connections:
                raise GraphError(wrapRed(f"Cannot Generate object {self} because the chosen name is empty or invalid."))
            return
        self.bObject = bpy.data.objects.get(self.evaluate_input("Name"))
        trace = trace_single_line(self, "Geometry")
        if (not self.bObject):
            if trace[-1]:
                self.bObject = bpy.data.objects.new(self.evaluate_input("Name"), trace[-1].node.bGetObject())
        # handle mismatched data.
        data_wrong = False; data  = None
        if (self.inputs["Geometry"].is_linked and self.bObject.type == "EMPTY"):
            data_wrong = True; data = trace[-1].node.bGetObject()
        elif (not self.inputs["Geometry"].is_linked and not self.bObject.type == "EMPTY"):
            data_wrong = True
        # clumsy but functional
        if data_wrong:
            unlink_me = self.bObject
            unlink_me.name = "MANTIS_TRASH.000"
            for col in unlink_me.users_collection:
                col.objects.unlink(unlink_me)
            self.bObject = bpy.data.objects.new(self.evaluate_input("Name"), data)
        if self.bObject and (self.inputs["Geometry"].is_linked and self.bObject.type  in ["MESH", "CURVE"]):
            self.bObject.data = trace[-1].node.bGetObject()
        # NOW: find out if we need to duplicate the object data.
        dupe_data=False
        node_line = trace_single_line(self, "Deformer")[0]
        from .deformer_containers import DeformerHook
        for deformer in node_line:
            if isinstance(deformer, DeformerHook) and  \
               deformer.evaluate_input("Affect Curve Radius") == True and \
               self.bObject.type == 'CURVE':
                    print(f"INFO: Duplicating data {self.bObject.data.name} in {self} so it can be used for drivers.")
                    dupe_data=True; break
        if dupe_data:
            name = self.bObject.data.name
            # it has to be a curve
            data = bpy.data.curves.get(self.bObject.data.name+"_MANTIS")
            if not data:
                data=self.bObject.data.copy()
                data.name = name+"_MANTIS"
                data.animation_data_clear() # clear the drivers if there are
            self.bObject.data = data
        reset_object_data(self.bObject)
        matrix= get_matrix(self)
        self.parameters['Matrix'] = matrix
        try:
            set_object_parent(self)
        except: # I guess it isn't ready yet. we'll do it later
            pass # (This can happen when solving schema.)
        self.bObject.matrix_world = matrix
        self.prepared = True

    def bExecute(self, bContext = None,):
        try:
            bContext.collection.objects.link(self.bObject)
        except RuntimeError: #already in; but a dangerous thing to pass.
            pass
        self.has_shape_keys = False
        # putting this in bExecute simply prevents it from being run more than once.
        # maybe I should do that with the rest of bPrepare, too.
        props_sockets = {
            'hide_viewport'    : ("Hide in Viewport", False),
            'hide_render'      : ("Hide in Render", False),
        }
        evaluate_sockets(self, self.bObject, props_sockets)
        self.executed = True

    def bFinalize(self, bContext = None):
        matrix= get_matrix(self)
        set_object_parent(self)
        self.bObject.matrix_world = matrix
        for i, (driver_key, driver_item) in enumerate(self.drivers.items()):
            print (wrapGreen(i), wrapWhite(self), wrapPurple(driver_key))
            prOrange(driver_item)
        finish_drivers(self)
            
        
    def bGetObject(self, mode = 'POSE'):
        return self.bObject

class xFormObjectInstance(xFormNode):
    """Represents an instance of an existing geometry object."""
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree)
        inputs = [
            "Name"             ,
            "Source Object"    ,
            "As Instance"      ,
            "Matrix"           ,
            "Relationship"     ,
            "Deformer"         ,
            "Hide in Viewport" ,
            "Hide in Render"   ,
        ]
        outputs = [
          "xForm Out",
        ]
        self.inputs.init_sockets(inputs)
        self.outputs.init_sockets(outputs)
        self.init_parameters()
        self.links = {} # leave this empty for now!
        # now set up the traverse target...
        self.set_traverse([("Relationship", "xForm Out")])
        self.has_shape_keys = False # Shape Keys will make a dupe so this is OK

    def bPrepare(self, bContext = None,):
        from bpy import data
        empty_mesh = data.meshes.get("MANTIS_EMPTY_MESH")
        if not empty_mesh:
            empty_mesh = data.meshes.new("MANTIS_EMPTY_MESH")
        if not self.evaluate_input("Name"):
            self.prepared = True
            self.executed = True
            # and return an error if there are any dependencies:
            if self.hierarchy_connections:
                raise GraphError(wrapRed(f"Cannot Generate object {self} because the chosen name is empty or invalid."))
            return
        self.bObject = data.objects.get(self.evaluate_input("Name"))
        if (not self.bObject):
                self.bObject = data.objects.new(self.evaluate_input("Name"), empty_mesh)
        reset_object_data(self.bObject)
        matrix= get_matrix(self)
        self.parameters['Matrix'] = matrix
        set_object_parent(self)
        self.bObject.matrix_world = matrix
        self.prepared = True

    def bExecute(self, bContext = None,):
        try:
            bContext.collection.objects.link(self.bObject)
        except RuntimeError: #already in; but a dangerous thing to pass.
            pass
        self.has_shape_keys = False
        # putting this in bExecute simply prevents it from being run more than once.
        # maybe I should do that with the rest of bPrepare, too.
        props_sockets = {
            'hide_viewport'    : ("Hide in Viewport", False),
            'hide_render'      : ("Hide in Render", False),
        }
        evaluate_sockets(self, self.bObject, props_sockets)
        self.executed = True

    def bFinalize(self, bContext = None):
        # now we need to set the object instance up.
        from bpy import data
        trace = trace_single_line(self, "Source Object")
        for node in trace[0]:
            if node is self: continue # lol
            if (node.node_type == 'XFORM'):
                source_ob = node.bGetObject(); break
        modifier = self.bObject.modifiers.new("Object Instance", type='NODES')
        ng = data.node_groups.get("Object Instance")
        if ng is None:
            from .geometry_node_graphgen import gen_object_instance_node_group
            ng = gen_object_instance_node_group()
        modifier.node_group = ng
        modifier["Socket_0"] = source_ob
        modifier["Socket_1"] = self.evaluate_input("As Instance")
        for i, (driver_key, driver_item) in enumerate(self.drivers.items()):
            print (wrapGreen(i), wrapWhite(self), wrapPurple(driver_key))
            prOrange(driver_item)
        finish_drivers(self)

    def bGetObject(self, mode = 'POSE'):
        return self.bObject

from .base_definitions import MantisSocketTemplate as SockTemplate
from .misc_nodes_socket_templates import SplineIndexTemplate
xFormCurvePinSockets = [
    NameTemplate := SockTemplate(
        name="Name", is_input=True,  bl_idname='StringSocket',
        default_value='Curve Pin', blender_property='name' ),
    ParentCurveTemplate := SockTemplate(
        name="Parent Curve", is_input=True,  bl_idname='xFormSocket', ),
    SplineIndexTemplate,
    FactorTemplate := SockTemplate(
        name="Curve Pin Factor", is_input=True,  bl_idname='FloatFactorSocket',
        default_value=0.0, blender_property='offset_factor' ),
    ForwardAxisTemplate := SockTemplate(
        name="Forward Axis", is_input=True,  bl_idname='EnumFollowPathForwardAxis',
        default_value="FORWARD_Y", blender_property='forward_axis' ),
    UpAxisTemplate := SockTemplate(
        name="Up Axis", is_input=True,  bl_idname='EnumUpAxis',
        default_value="UP_Z", blender_property='up_axis' ),
    CurvePinDisplaySize := SockTemplate(
        name="Display Size", is_input=True,  bl_idname='FloatPositiveSocket',
        default_value=0.05, blender_property='empty_display_size'),
    xFormOutTemplate := SockTemplate(
        name="xForm Out", is_input=False,  bl_idname='xFormSocket', ),
]

class xFormCurvePin(xFormNode):
    """An xForm pinned to a specific location on a curve."""
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree,xFormCurvePinSockets)
        self.init_parameters(additional_parameters={"Matrix":None})

    def prep_driver_values(self, constraint):
        from .misc_nodes import UtilityDriver, UtilitySwitch
        for socket_name in ["Curve Pin Factor", "Forward Axis","Up Axis",]:
            if self.inputs.get(socket_name) is None: continue # in case it has been bypassed
            if self.inputs[socket_name].is_linked:
                link = self.inputs[socket_name].links[0]
                driver = link.from_node
                if isinstance(driver, UtilityDriver):
                    prop_amount = driver.evaluate_input("Property")
                elif isinstance(driver, UtilitySwitch):
                    xf=driver.GetxForm()
                    prop_amount = xf.evaluate_input(driver.evaluate_input('Parameter'))
                else:
                    return
                for template in self.socket_templates:
                    if template.name == socket_name: break
                setattr(constraint, template.blender_property, prop_amount )

    def bPrepare(self, bContext = None,):
        from bpy import data
        
        if not bContext: # lol
            import bpy
            bContext = bpy.context
        ob = data.objects.get(self.evaluate_input("Name"))
        if not ob:
            ob = data.objects.new(self.evaluate_input("Name"), None)
            ob.lock_location   = [True, True, True]
            ob.lock_rotation   = [True, True, True]
            ob.lock_scale      = [True, True, True]
            ob.lock_rotation_w = True
            ob.empty_display_type = 'CONE'
            ob.empty_display_size = 0.10

        self.bObject = ob
        
        reset_object_data(ob)
        
        node_line = trace_single_line(self, "Parent Curve")[0][1:] # slice excludes self
        for other_node in node_line:
            if other_node.node_type == 'XFORM':
                break
        else:
            raise GraphError(f"ERROR: {self} is not connected to a parent curve")
        if isinstance(other_node, (xFormArmature, xFormBone, xFormObjectInstance,)):
            raise GraphError(f"ERROR: {self} must be connected to curve,"
                              " not {other_node.__class__.__name__}")
        curve=other_node.bGetObject()
        if curve.type != 'CURVE':
            raise GraphError(f"ERROR: {self} must be connected to curve,"
                              " not {curve.type}")
        # we'll limit all the transforms so we can parent it
        #  because it is annoying to have a cluttered outliner.
        #
        # always do this so that everything stays consistent.
        spline_index = self.evaluate_input("Spline Index")
        from .utilities import get_extracted_spline_object
        curve = get_extracted_spline_object(curve, spline_index, self.mContext)
        # Link to Scene:
        for link_me in [ob, curve]:
            if (link_me.name not in bContext.view_layer.active_layer_collection.collection.objects):
                bContext.view_layer.active_layer_collection.collection.objects.link(link_me)

        c = ob.constraints.new("LIMIT_LOCATION")
        for max_min in ['max','min']:
            for axis in "xyz":
                setattr(c, "use_"+max_min+"_"+axis, True)
                setattr(c, max_min+"_"+axis, 0.0)
        c = ob.constraints.new("LIMIT_ROTATION")
        for axis in "xyz":
            setattr(c, "use_limit_"+axis, True)
            setattr(c, max_min+"_"+axis, 0.0)
        c = ob.constraints.new("LIMIT_SCALE")
        for max_min in ['max','min']:
            for axis in "xyz":
                setattr(c, "use_"+max_min+"_"+axis, True)
                setattr(c, max_min+"_"+axis, 1.0)
        c = ob.constraints.new("FOLLOW_PATH")
        c.target = curve
        c.use_fixed_location = True
        c.use_curve_radius = True
        c.use_curve_follow = True
        c.name = "Curve Pin"

        props_sockets = self.gen_property_socket_map()
        constraint_props_sockets = props_sockets.copy()
        del constraint_props_sockets['name']; del constraint_props_sockets['empty_display_size']
        del props_sockets['offset_factor']; del props_sockets['forward_axis']
        del props_sockets['up_axis']
        evaluate_sockets(self, c, constraint_props_sockets)
        evaluate_sockets(self, self.bObject, props_sockets)
        # this isn't usually run on xForm nodes so for now I need to set the
        #   driver's default values manually if I want a matrix now.
        # because the drivers may not have initialized yet.
        self.prep_driver_values(c)
        # now if all goes well... the matrix will be correct.
        dg = bContext.view_layer.depsgraph
        dg.update()
        # and the matrix should be correct now - copy because it may be modified
        self.parameters['Matrix'] = ob.matrix_world.copy()
        ob.parent=curve
        print( wrapGreen("Created Curve Pin: ") + wrapOrange(self.bObject.name) )
        self.prepared = True; self.executed = True

    def bFinalize(self, bContext = None):
        finish_drivers(self)
            
    def bGetObject(self, mode = 'POSE'):
        return self.bObject
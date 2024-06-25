from .node_container_common import *
from bpy.types import Node
from .base_definitions import MantisNode

def TellClasses():
             
    return [ 
             # xForm
             xFormRoot,
             xFormArmature,
             xFormBone,
             xFormGeometryObject,
           ]

#*#-------------------------------#++#-------------------------------#*#
# X - F O R M   N O D E S
#*#-------------------------------#++#-------------------------------#*#

# class xFormNull:
    # '''A node representing an Empty object'''
    # inputs =
    # {
     # "Name":None,
     # "Rotation Order":None,
     # "Matrix":None,
     # "Relationship":None,
    # }
    # outputs =
    # {
     # "xFormOut":None,
    # }
    # parameters =
    # {
     # "Name":None,
     # "Rotation Order":None,
     # "Matrix":None,
     # "Relationship":None,
    # }
    
    # def evaluate_input(self, input):
        # pass
    
    # def instantiate_blender_object(self):
        # pass
# for whatever reason, the above isn't implemented yet in the node-tree
# so I'm not implementing it here, either

class xFormRoot:
    '''A node representing the root of the scene.'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"World Out":NodeSocket(name="World Out", node = self),}
        self.parameters = {}
        self.links = {} # leave this empty for now!
        self.node_type = 'XFORM'
    
    def evaluate_input(self, input_name):
        return "ROOT"
    
    def bExecute(self, bContext = None,):
        pass
        
    def bFinalize(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self,):
        pass

class xFormArmature:
    '''A node representing an armature object'''
    
    bObject = None
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
         "Name"           : NodeSocket(is_input = True, name = "Name", node = self),
         "Rotation Order" : NodeSocket(is_input = True, name = "Rotation Order", node = self),
         "Matrix"         : NodeSocket(is_input = True, name = "Matrix", node = self),
         "Relationship"   : NodeSocket(is_input = True, name = "Relationship", node = self),
        }
        self.outputs = {
         "xForm Out" : NodeSocket(name="xForm Out", node = self),
        }
        self.parameters = {
         "Name":None,
         "Rotation Order":None,
         "Matrix":None,
         "Relationship":None,
        }
        self.links = {} # leave this empty for now!
        # now set up the traverse target...
        self.inputs["Relationship"].set_traverse_target(self.outputs["xForm Out"])
        self.outputs["xForm Out"].set_traverse_target(self.inputs["Relationship"])
        self.node_type = 'XFORM'
    
        
    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)
    
    def bExecute(self, bContext = None,):
        from .utilities import get_node_prototype
        
        import bpy
        if (not isinstance(bContext, bpy.types.Context)):
            raise RuntimeError("Incorrect context")

        name = self.evaluate_input("Name")
        matrix = self.evaluate_input('Matrix')


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
        ob.matrix_world = matrix
        
        # # first, get the parent object
        # parent_node = get_parent(self)
        # if hasattr(parent_node, "bObject"):
            # # this won't work of course, TODO
            # ob.parent = parent_node.bObject
            # # print (self.bObject)
        if True:
            from bpy.types import EditBone
            parent_nc = get_parent(self, type='LINK')
            if parent_nc:
                parent = parent_nc.inputs['Parent'].links[0].from_node.bGetObject(mode = 'OBJECT')
                ob.parent = parent
            
        
        # Link to Scene:
        if (ob.name not in bContext.view_layer.active_layer_collection.collection.objects):
            bContext.view_layer.active_layer_collection.collection.objects.link(ob)
        #self.bParent(bContext)
        
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
    
    # # not used yet
    # #
    # def bFinalize(self, bContext = None):
        # import bpy
        # ob = self.bGetObject()
        # prevAct = bContext.view_layer.objects.active
        # bContext.view_layer.objects.active = ob
        # bpy.ops.object.mode_set(mode='OBJECT')
        # print ("Changing Armature Mode to OBJECT")
        # bContext.view_layer.objects.active = prevAct

    def bGetObject(self, mode = ''):
        import bpy; return bpy.data.objects[self.bObject]

    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self,):
        fill_parameters(self)

class xFormBone:
    '''A node representing a bone in an armature'''
    # DO: make a way to identify which armature this belongs to
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
         "Name"           : NodeSocket(is_input = True, name = "Name", node = self,),
         "Rotation Order" : NodeSocket(is_input = True, name = "Rotation Order", node = self,),
         "Matrix"         : NodeSocket(is_input = True, name = "Matrix", node = self,),
         "Relationship"   : NodeSocket(is_input = True, name = "Relationship", node = self,),
         # IK settings
         "IK Stretch"     : NodeSocket(is_input = True, name = "IK Stretch", node = self,),
         "Lock IK"        : NodeSocket(is_input = True, name = "Lock IK", node = self,),
         "IK Stiffness"   : NodeSocket(is_input = True, name = "IK Stiffness", node = self,),
         "Limit IK"       : NodeSocket(is_input = True, name = "Limit IK", node = self,),
         "X Min"          : NodeSocket(is_input = True, name = "X Min", node = self,),
         "X Max"          : NodeSocket(is_input = True, name = "X Max", node = self,),
         "Y Min"          : NodeSocket(is_input = True, name = "Y Min", node = self,),
         "Y Max"          : NodeSocket(is_input = True, name = "Y Max", node = self,),
         "Z Min"          : NodeSocket(is_input = True, name = "Z Min", node = self,),
         "Z Max"          : NodeSocket(is_input = True, name = "Z Max", node = self,),
         # Visual stuff
         "Bone Collection"                         : NodeSocket(is_input = True, name = "Bone Collection", node = self,),
         "Hide"                               : NodeSocket(is_input = True, name = "Hide", node = self,),
         "Custom Object"                      : NodeSocket(is_input = True, name = "Custom Object", node = self,),
         "Custom Object xForm Override"       : NodeSocket(is_input = True, name = "Custom Object xForm Override", node = self,),
         "Custom Object Scale to Bone Length" : NodeSocket(is_input = True, name = "Custom Object Scale to Bone Length", node = self,),
         "Custom Object Wireframe"            : NodeSocket(is_input = True, name = "Custom Object Wireframe", node = self,),
         "Custom Object Scale"                : NodeSocket(is_input = True, name = "Custom Object Scale", node = self,),
         "Custom Object Translation"          : NodeSocket(is_input = True, name = "Custom Object Translation", node = self,),
         "Custom Object Rotation"             : NodeSocket(is_input = True, name = "Custom Object Rotation", node = self,),
         # Deform Stuff
         "Deform"               : NodeSocket(is_input = True, name = "Deform", node = self,),
         "Envelope Distance"    : NodeSocket(is_input = True, name = "Envelope Distance", node = self,),
         "Envelope Weight"      : NodeSocket(is_input = True, name = "Envelope Weight", node = self,),
         "Envelope Multiply"    : NodeSocket(is_input = True, name = "Envelope Multiply", node = self,),
         "Envelope Head Radius" : NodeSocket(is_input = True, name = "Envelope Head Radius", node = self,),
         "Envelope Tail Radius" : NodeSocket(is_input = True, name = "Envelope Tail Radius", node = self,),
        }
        
        self.outputs = {
         "xForm Out"       : NodeSocket(name = "xForm Out", node = self),
        }
        self.parameters = {
         "Name":None,
         "Rotation Order":None,
         "Matrix":None,
         "Relationship":None,
         # IK settings
         "IK Stretch":None,
         "Lock IK":None,
         "IK Stiffness":None,
         "Limit IK":None,
         "X Min":None,
         "X Max":None,
         "Y Min":None,
         "Y Max":None,
         "Z Min":None,
         "Z Max":None,
         "Hide":None,
         "Bone Collection":None,
         "Hide":None,
         "Custom Object":None,
         "Custom Object xForm Override":None,
         "Custom Object Scale to Bone Length":None,
         "Custom Object Wireframe":None,
         "Custom Object Scale":None,
         "Custom Object Translation":None,
         "Custom Object Rotation":None,
         "Deform"               : None,
         "Envelope Distance"    : None,
         "Envelope Weight"      : None,
         "Envelope Multiply"    : None,
         "Envelope Head Radius" : None,
         "Envelope Tail Radius" : None,
        }
        self.links = {} # leave this empty for now!
        # now set up the traverse target...
        self.inputs["Relationship"].set_traverse_target(self.outputs["xForm Out"])
        self.outputs["xForm Out"].set_traverse_target(self.inputs["Relationship"])
        self.node_type = 'XFORM'
        setup_custom_props(self)
             
    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self):
        fill_parameters(self)
    
    def bGetParentArmature(self):
        finished = False
        if (trace := trace_single_line(self, "Relationship")[0] ) :
            for i in range(len(trace)):
                # have to look in reverse, actually
                if ( isinstance(trace[ i ], xFormArmature ) ):
                    return trace[ i ].bGetObject()
        return None
        #should do the trick...
    
    def bSetParent(self, eb):
        # print (self.bObject)
        from bpy.types import EditBone
        parent_nc = get_parent(self, type='LINK')
        # print (self, parent_nc.inputs['Parent'].from_node)
        parent = parent_nc.inputs['Parent'].links[0].from_node.bGetObject(mode = 'EDIT')
        if isinstance(parent, EditBone):
            eb.parent = parent
        
        #DUMMY
        # I NEED TO GET THE LINK NC
        # IDIOT
            
        eb.use_connect = parent_nc.evaluate_input("Connected")
        eb.use_inherit_rotation = parent_nc.evaluate_input("Inherit Rotation")
        eb.inherit_scale = parent_nc.evaluate_input("Inherit Scale")
        # otherwise, no need to do anything.
        
         
    def bExecute(self, bContext = None,): #possibly will need to pass context?
        import bpy
        from mathutils import Vector
        if (not isinstance(bContext, bpy.types.Context)):
            raise RuntimeError("Incorrect context")
        xF = self.bGetParentArmature()
        
        name = self.evaluate_input("Name")
        matrix = self.evaluate_input("Matrix")
        
        length = matrix[3][3]
        
        if (xF):
            if (xF.mode != "EDIT"):
                raise RuntimeError("Armature Object Not in Edit Mode, exiting...")
        else:
            raise RuntimeError("Could not create edit bone: ", name, " from node:", self.signature, " Reason: No armature object to add bone to.")
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
            for i, sCol in enumerate(hierarchy):
                if ( col := d.collections.get(sCol) ) is None:
                    col = d.collections.new(sCol)
                col.parent = col_parent
                col_parent = col
            col.assign(eb)
        
        if (eb.name != name):
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
        
        assert (self.bObject), "eh? %s" % eb.name
        
        self.bSetParent(eb)
        
        
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
        pb.id_properties_clear()
        # these are kept around unless explicitly deleted.
        from .utilities import get_node_prototype
        np = get_node_prototype(self.signature, self.base_tree)
        driver = None
        do_prints=False
        for i, inp in enumerate(np.inputs):
            if ('Parameter' in inp.bl_idname):
                name = inp.name
                # print(inp.name)
                try:
                    value = self.evaluate_input(inp.name)
                except KeyError as e:
                    trace = trace_single_line(self, inp.name)
                    if do_prints: print(trace[0][-1], trace[1])
                    if do_prints: print (trace[0][-1].parameters)
                    #prop = trace[0][-1].parameters[trace[1].name]
                    raise e
                # This may be driven, so let's do this:
                if do_prints: print (value)
                if (isinstance(value, tuple)):
                    # it's either a CombineThreeBool or a CombineVector.
                    prRed("COMITTING SUICIDE NOW!!")
                    bpy.ops.wm.quit_blender()
                if (isinstance(value, MantisDriver)):
                    # the value should be the default for its socket...
                    if do_prints: print (type(inp.default_value))
                    type_val_map = {
                        str:"",
                        bool:False,
                        int:0,
                        float:0.0,
                        bpy.types.bpy_prop_array:(0,0,0),
                        }
                    driver = value
                    value = type_val_map[type(inp.default_value)]
                if (value is None):
                    prRed("This is probably not supposed to happen")
                    value = 0
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
                ui_data.update(
                    description=inp.description,
                    default=value,)
                #if a number
                for num_type in ['Float']:
                    if num_type in inp.bl_idname:
                        ui_data.update(
                            min = inp.min,
                            max = inp.max,
                            soft_min = inp.soft_min,
                            soft_max = inp.soft_max,)
                            
                for num_type in ['Int', 'Bool']:
                    # for some reason the types don't cast implicitly
                    if num_type in inp.bl_idname:
                        ui_data.update(
                            min = int(inp.min),
                            max = int(inp.max),
                            soft_min = int(inp.soft_min),
                            soft_max = int(inp.soft_max),)
                # Doesn't seem to work?
                #pb.property_overridable_library_set("["+name+"]", True)
        # Set up IK settings, these belong to the pose bone.
        if (pb.is_in_ik_chain): # cool!
            pb. ik_stretch = self.evaluate_input("IK Stretch")
            lock           = self.evaluate_input("Lock IK")
            stiffness      = self.evaluate_input("IK Stiffness")
            limit          = self.evaluate_input("Limit IK")
            pb.ik_min_x    = self.evaluate_input("X Min")
            pb.ik_max_x    = self.evaluate_input("X Max")
            pb.ik_min_y    = self.evaluate_input("Y Min")
            pb.ik_max_y    = self.evaluate_input("Y Max")
            pb.ik_min_z    = self.evaluate_input("Z Min")
            pb.ik_max_z    = self.evaluate_input("Z Max")
            pb.ik_stiffness_x  = stiffness[0]
            pb.ik_stiffness_y  = stiffness[1]
            pb.ik_stiffness_z  = stiffness[2]
            pb.lock_ik_x       = lock[0]
            pb.lock_ik_y       = lock[1]
            pb.lock_ik_z       = lock[2]
            pb. use_ik_limit_x = limit[0]
            pb.use_ik_limit_y  = limit[1]
            pb.use_ik_limit_z  = limit[2]
        # time to set up drivers!
        if (driver):
            pass
        #
        # OK, visual settings
        #
        # Get the override xform's bone:
        
        
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
        #
        pb.bone.hide = self.evaluate_input("Hide")
        pb.custom_shape_scale_xyz = self.evaluate_input("Custom Object Scale")
        pb.custom_shape_translation = self.evaluate_input("Custom Object Translation")
        pb.custom_shape_rotation_euler = self.evaluate_input("Custom Object Rotation")
        pb.use_custom_shape_bone_size = self.evaluate_input("Custom Object Scale to Bone Length")
        pb.bone.show_wire = self.evaluate_input("Custom Object Wireframe")
        # #
        # # D E P R E C A T E D
        # #
        # # Bone Groups
        # if bg_name := self.evaluate_input("Bone Group"): # this is a string
        #     obArm = self.bGetParentArmature()
        #     # Temporary! Temporary! HACK
        #     color_set_items= [
        #                        "DEFAULT",
        #                        "THEME01",
        #                        "THEME02",
        #                        "THEME03",
        #                        "THEME04",
        #                        "THEME05",
        #                        "THEME06",
        #                        "THEME07",
        #                        "THEME08",
        #                        "THEME09",
        #                        "THEME10",
        #                        "THEME11",
        #                        "THEME12",
        #                        "THEME13",
        #                        "THEME14",
        #                        "THEME15",
        #                        "THEME16",
        #                        "THEME17",
        #                        "THEME18",
        #                        "THEME19",
        #                        "THEME20",
        #                        # "CUSTOM",
        #                      ]
        #     try:
        #         bg = obArm.pose.bone_groups.get(bg_name)
        #     except SystemError:
        #         bg = None
        #         pass # no clue why this happens. uninitialzied?
        #     if not bg:
        #         bg = obArm.pose.bone_groups.new(name=bg_name)
        #         #HACK lol
        #         from random import randint
        #         bg.color_set = color_set_items[randint(0,14)]
        #         #15-20 are black by default, gross
        #         # this is good enough for now!
            
        #     pb.bone_group = bg
            
        
        

    def bGetObject(self, mode = 'POSE'):
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



class xFormGeometryObject:
    '''A node representing an armature object'''

    bObject = None

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
          "Name"           : NodeSocket(is_input = True, name = "Name", node = self),
          "Geometry" : NodeSocket(is_input = True, name = "Geometry", node = self),
          "Matrix"         : NodeSocket(is_input = True, name = "Matrix", node = self),
          "Relationship"   : NodeSocket(is_input = True, name = "Relationship", node = self),
        }
        self.outputs = {
          "xForm Out" : NodeSocket(is_input = False, name="xForm Out", node = self), }
        self.parameters = {
          "Name":None, 
          "Geometry":None, 
          "Matrix":None, 
          "Relationship":None, 
        }
        self.links = {} # leave this empty for now!
        # now set up the traverse target...
        self.inputs["Relationship"].set_traverse_target(self.outputs["xForm Out"])
        self.outputs["xForm Out"].set_traverse_target(self.inputs["Relationship"])
        self.node_type = "XFORM"
        self.bObject = None

    def bSetParent(self, ob):
        from bpy.types import Object, Bone
        parent_nc = get_parent(self, type='LINK')
        if (parent_nc):
            parent = parent_nc.inputs['Parent'].links[0].from_node
            parent_bOb = parent.bGetObject(mode = 'EDIT')
            if isinstance(parent_bOb, Bone):
                armOb= parent.bGetParentArmature()
                ob.parent = armOb
                ob.parent_type = 'BONE'
                ob.parent_bone = parent_bOb.name
            elif isinstance(parent, Object):
                ob.parent = parent
            # blender will do the matrix math for me IF I set the world
            #   matrix after setting the parent.
            #
            # deal with parenting settings here, if necesary
        
    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)

    def bExecute(self, bContext = None,):
        import bpy
        self.bObject = bpy.data.objects.get(self.evaluate_input("Name"))
        if not self.bObject:
            trace = trace_single_line(self, "Geometry")
            if trace[-1]:
                self.bObject = bpy.data.objects.new(self.evaluate_input("Name"), trace[-1].node.bGetObject())
        else: # clear it
            self.bObject.constraints.clear()
            # Don't clear this, we want to be able to reuse this
            # self.bObject.vertex_groups.clear()
            #
            # This is probably also not what we want - but for now it is OK
            self.bObject.modifiers.clear()
        try:
            bpy.context.collection.objects.link(self.bObject)
        except RuntimeError: #already in; but a dangerous thing to pass.
            pass
        
        self.bSetParent(self.bObject)
        self.bObject.matrix_world = self.evaluate_input("Matrix")
            
    def bFinalize(self, bContext = None):
        pass
        
    def bGetObject(self, mode = 'POSE'):
        return self.bObject

    def __repr__(self):
        return self.signature.__repr__()

    def fill_parameters(self):
        fill_parameters(self)

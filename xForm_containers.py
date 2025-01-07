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

class xFormRoot:
    '''A node representing the root of the scene.'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {}
        self.outputs = {"World Out":NodeSocket(name="World Out", node = self),}
        self.parameters = {}
        self.node_type = 'XFORM'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = True


class xFormArmature:
    '''A node representing an armature object'''
    
    bObject = None
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
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
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False

    
    def bExecute(self, bContext = None,):
        # from .utilities import get_node_prototype
        
        import bpy
        if (not isinstance(bContext, bpy.types.Context)):
            raise RuntimeError("Incorrect context")

        name = self.evaluate_input("Name")
        if not ( matrix := self.evaluate_input('Matrix')):
            raise RuntimeError(wrapRed(f"No matrix found for Armature {self}"))
        self.parameters['Matrix'] = matrix

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
class xFormBone:
    '''A node representing a bone in an armature'''
    # DO: make a way to identify which armature this belongs to
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
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
         # BBone stuff:
         "BBone Segments" : NodeSocket(is_input = True, name = "BBone Segments", node=self,),
         "BBone X Size" : NodeSocket(is_input = True, name = "BBone X Size", node=self,),
         "BBone Z Size" : NodeSocket(is_input = True, name = "BBone Z Size", node=self,),
         "BBone HQ Deformation" : NodeSocket(is_input = True, name = "BBone HQ Deformation", node=self,),
         "BBone X Curve-In" : NodeSocket(is_input = True, name = "BBone X Curve-In", node=self,),
         "BBone Z Curve-In" : NodeSocket(is_input = True, name = "BBone Z Curve-In", node=self,),
         "BBone X Curve-Out" : NodeSocket(is_input = True, name = "BBone X Curve-Out", node=self,),
         "BBone Z Curve-Out" : NodeSocket(is_input = True, name = "BBone Z Curve-Out", node=self,),
         "BBone Roll-In" : NodeSocket(is_input = True, name = "BBone Roll-In", node=self,),
         "BBone Roll-Out" : NodeSocket(is_input = True, name = "BBone Roll-Out", node=self,),
         "BBone Inherit End Roll" : NodeSocket(is_input = True, name = "BBone Inherit End Roll", node=self,),
         "BBone Scale-In" : NodeSocket(is_input = True, name = "BBone Scale-In", node=self,),
         "BBone Scale-Out" : NodeSocket(is_input = True, name = "BBone Scale-Out", node=self,),
         "BBone Ease-In" : NodeSocket(is_input = True, name = "BBone Ease-In", node=self,),
         "BBone Ease-Out" : NodeSocket(is_input = True, name = "BBone Ease-Out", node=self,),
         "BBone Easing" : NodeSocket(is_input = True, name = "BBone Easing", node=self,),
         "BBone Start Handle Type" : NodeSocket(is_input = True, name = "BBone Start Handle Type", node=self,),
         "BBone Custom Start Handle" : NodeSocket(is_input = True, name = "BBone Custom Start Handle", node=self,),
         "BBone Start Handle Scale" : NodeSocket(is_input = True, name = "BBone Start Handle Scale", node=self,),
         "BBone Start Handle Ease" : NodeSocket(is_input = True, name = "BBone Start Handle Ease", node=self,),
         "BBone End Handle Type" : NodeSocket(is_input = True, name = "BBone End Handle Type", node=self,),
         "BBone Custom End Handle" : NodeSocket(is_input = True, name = "BBone Custom End Handle", node=self,),
         "BBone End Handle Scale" : NodeSocket(is_input = True, name = "BBone End Handle Scale", node=self,),
         "BBone End Handle Ease" : NodeSocket(is_input = True, name = "BBone End Handle Ease", node=self,),

         # locks
         "Lock Location"    : NodeSocket(is_input = True, name = "Lock Location", node = self,),
         "Lock Rotation" : NodeSocket(is_input = True, name = "Lock Rotation", node = self,),
         "Lock Scale" : NodeSocket(is_input = True, name = "Lock Scale", node = self,),
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
         #
         "BBone Segments"  : None,
         "BBone X Size"  : None,
         "BBone Z Size"  : None,
         "BBone HQ Deformation"  : None,
         "BBone X Curve-In"  : None,
         "BBone Z Curve-In"  : None,
         "BBone X Curve-Out"  : None,
         "BBone Z Curve-Out"  : None,
         "BBone Roll-In"  : None,
         "BBone Roll-Out"  : None,
         "BBone Inherit End Roll"  : None,
         "BBone Scale-In"  : None,
         "BBone Scale-Out"  : None,
         "BBone Ease-In"  : None,
         "BBone Ease-Out"  : None,
         "BBone Easing"  : None,
         "BBone Start Handle Type"  : None,
         "BBone Custom Start Handle"  : None,
         "BBone Start Handle Scale"  : None,
         "BBone Start Handle Ease"  : None,
         "BBone End Handle Type"  : None,
         "BBone Custom End Handle"  : None,
         "BBone End Handle Scale"  : None,
         "BBone End Handle Ease"  : None,
        #
         "Lock Location"    : None,
         "Lock Rotation" : None,
         "Lock Scale" : None,
        }
        self.links = {} # leave this empty for now!
        # now set up the traverse target...
        self.inputs["Relationship"].set_traverse_target(self.outputs["xForm Out"])
        self.outputs["xForm Out"].set_traverse_target(self.inputs["Relationship"])
        self.node_type = 'XFORM'
        self.hierarchy_connections = []
        self.connections = []
        self.hierarchy_dependencies = []
        self.dependencies = []
        self.prepared = True
        self.executed = False
        self.input_length = len(self.inputs) # HACK HACK HACK 
    
    def bGetParentArmature(self):
        finished = False
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
        parent_nc = get_parent(self, type='LINK')
        # print (self, parent_nc.inputs['Parent'].from_node)
        parent=None
        if parent_nc.inputs['Parent'].links[0].from_node.node_type == 'XFORM':
            parent = parent_nc.inputs['Parent'].links[0].from_node.bGetObject(mode = 'EDIT')
        else:
            raise RuntimeError(wrapRed(f"Cannot set parent for node {self}"))

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
        if not (name := self.evaluate_input("Name")):
            raise RuntimeError(wrapRed(f"Could not set name for bone in {self}"))
        if (not isinstance(bContext, bpy.types.Context)):
            raise RuntimeError("Incorrect context")
        if not (xF := self.bGetParentArmature()):
            raise RuntimeError("Could not create edit bone: ", name, " from node:", self.signature, " Reason: No armature object to add bone to.")

        
        if not ( matrix := self.evaluate_input('Matrix')):
            # print(self.inputs['Matrix'].links[0].from_node.parameters)
            raise RuntimeError(wrapRed(f"No matrix found for Bone {self}"))
        
        self.parameters['Matrix'] = matrix
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

        if eb.head == eb.tail:
            raise RuntimeError(wrapRed(f"Could not create edit bone: {name} because bone head was located in the same place as bone tail."))

        
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
            
            b.bbone_curveinx = self.evaluate_input("BBone X Curve-In")
            b.bbone_curveinz = self.evaluate_input("BBone Z Curve-In")
            b.bbone_curveoutx = self.evaluate_input("BBone X Curve-Out")
            b.bbone_curveoutz = self.evaluate_input("BBone Z Curve-Out")
            # 'bbone_curveinx'             : ("BBone X Curve-In", pb.bone.bbone_curveinx),
            # 'bbone_curveinz'             : ("BBone Z Curve-In", pb.bone.bbone_curveinz),
            # 'bbone_curveoutx'            : ("BBone X Curve-Out", pb.bone.bbone_curveoutx),
            # 'bbone_curveoutz'            : ("BBone Z Curve-Out", pb.bone.bbone_curveoutz),
            
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

        # print (self.input_length)
        # even worse hack coming
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
                # it's either a CombineThreeBool or a CombineVector.
                prRed("COMITTING SUICIDE NOW!!")
                bpy.ops.wm.quit_blender()
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
            prRed("BBone Implementation is not complete, expect errors and missing features for now")
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
        # pb.bone.hide = self.evaluate_input("Hide")
        # pb.custom_shape_scale_xyz = self.evaluate_input("Custom Object Scale")
        # pb.custom_shape_translation = self.evaluate_input("Custom Object Translation")
        # pb.custom_shape_rotation_euler = self.evaluate_input("Custom Object Rotation")
        # pb.use_custom_shape_bone_size = self.evaluate_input("Custom Object Scale to Bone Length")
        # pb.bone.show_wire = self.evaluate_input("Custom Object Wireframe")


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

    def fill_parameters(self):
        # this is the fill_parameters that is run if it isn't a schema
        setup_custom_props(self)
        fill_parameters(self)
        # otherwise we will do this from the schema 

class xFormGeometryObject:
    '''A node representing an armature object'''

    bObject = None

    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
          "Name"           : NodeSocket(is_input = True, name = "Name", node = self),
          "Geometry" : NodeSocket(is_input = True, name = "Geometry", node = self),
          "Matrix"         : NodeSocket(is_input = True, name = "Matrix", node = self),
          "Relationship"   : NodeSocket(is_input = True, name = "Relationship", node = self),
          "Deformer"   : NodeSocket(is_input = True, name = "Relationship", node = self),
          "Hide in Viewport"   : NodeSocket(is_input = True, name = "Hide in Viewport", node = self),
          "Hide in Render"   : NodeSocket(is_input = True, name = "Hide in Render", node = self),
        }
        self.outputs = {
          "xForm Out" : NodeSocket(is_input = False, name="xForm Out", node = self), }
        self.parameters = {
          "Name":None, 
          "Geometry":None, 
          "Matrix":None, 
          "Relationship":None, 
          "Deformer":None,
          "Hide in Viewport":None,
          "Hide in Render":None,
        }
        self.links = {} # leave this empty for now!
        # now set up the traverse target...
        self.inputs["Relationship"].set_traverse_target(self.outputs["xForm Out"])
        self.outputs["xForm Out"].set_traverse_target(self.inputs["Relationship"])
        self.node_type = "XFORM"
        self.bObject = None
        self.prepared = False
        self.executed = False
        self.drivers = {}

    def bSetParent(self):
        from bpy.types import Object, Bone
        parent_nc = get_parent(self, type='LINK')
        if (parent_nc):
            parent = None
            if self.inputs["Relationship"].is_linked:
                trace = trace_single_line(self, "Relationship")
                for node in trace[0]:
                    if node is self: continue # lol
                    if (node.node_type == 'XFORM'):
                        parent = node; break
                if parent is None:
                    raise GraphError(f"Could not get parent node for {self}")
                if parent.bObject is None:
                    raise GraphError(f"Could not get parent object from node {parent} for {self}")
                if isinstance(parent, xFormBone):
                    armOb= parent.bGetParentArmature()
                    self.bObject.parent = armOb
                    self.bObject.parent_type = 'BONE'
                    self.bObject.parent_bone = parent.bObject
                    # self.bObject.matrix_parent_inverse = parent.parameters["Matrix"].inverted()
                elif isinstance(parent, xFormArmature):
                    self.bObject.parent = parent.bGetObject()

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
        # clear it
        self.bObject.constraints.clear()
        self.bObject.animation_data_clear() # this is a little dangerous. TODO find a better solution since this can wipe animation the user wants to keep
        self.bObject.modifiers.clear() # I would also like a way to copy modifiers and their settings, or bake them down. oh well
                    
        try:
            bpy.context.collection.objects.link(self.bObject)
        except RuntimeError: #already in; but a dangerous thing to pass.
            pass
        self.prepared = True

    def bExecute(self, bContext = None,):
        # putting this in bExecute simply prevents it from being run more than once.
        # maybe I should do that with the rest of bPrepare, too.
        props_sockets = {
            'hide_viewport'    : ("Hide in Viewport", False),
            'hide_render'      : ("Hide in Render", False),
        }
        evaluate_sockets(self, self.bObject, props_sockets)
        self.executed = True

    def bFinalize(self, bContext = None):
        self.bSetParent()
        matrix = self.evaluate_input("Matrix")
        self.parameters['Matrix'] = matrix
        self.bObject.matrix_world = matrix
        for i, (driver_key, driver_item) in enumerate(self.drivers.items()):
            print (wrapGreen(i), wrapWhite(self), wrapPurple(driver_key))
            prOrange(driver_item)
        finish_drivers(self)
            
        
    def bGetObject(self, mode = 'POSE'):
        return self.bObject


for c in TellClasses():
    setup_container(c)
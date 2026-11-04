from .utilities.node_common import *
from .base_definitions import MantisNode, NodeSocket
from .xForm_socket_templates import *
from .mantis_dataclasses import xForm_info

def TellClasses():

    return [
             # xForm
             xFormArmature,
             xFormBone,
             xFormGeometryObject,
             xFormObjectInstance,
             xFormCurvePin,
             xFormGetBone,
           ]

#*#-------------------------------#++#-------------------------------#*#
# X - F O R M   N O D E S
#*#-------------------------------#++#-------------------------------#*#

def reset_object_data(ob):
    # moving this to a common function so I can figure out the details later
    ob.id_properties_clear() # we must remove the custom properties so we can make them again.
    ob.constraints.clear()
    ob.animation_data_clear() # this is a little dangerous. TODO find a better solution since this can wipe animation the user wants to keep
    ob.modifiers.clear() # I would also like a way to copy modifiers and their settings, or bake them down. oh well

def get_parent_node(mantis_node, type = 'XFORM'):
    # type variable for selecting whether to get either
    #   the parent xForm  or the inheritance node
    node_line, _last_socket = trace_single_line(mantis_node, "Relationship")
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
    from bpy import data
    parent_xForm_info = get_parent_xForm_info(node)
    if parent_xForm_info.object_type  == '':
        return # no parent
    elif parent_xForm_info.object_type in ['armature', 'object']:
        parent = data.objects.get(parent_xForm_info.self_edit_name)
        if parent_xForm_info.parent_edit_name and parent is None:
            raise GraphError(f"Could not get parent object for node {node}.")
        node.bGetObject().parent = parent
    else: # it is a bone
        armOb = data.objects.get(parent_xForm_info.root_armature)
        node_ob = node.bGetObject()
        node_ob.parent = armOb; node_ob.parent_type = 'BONE'
        # this one expects a string.
        node_ob.parent_bone = parent_xForm_info.self_edit_name

class xFormNode(MantisNode):
    __slots__ = ()
    node_type = 'XFORM'
    passes=frozenset({'bPrepare', 'bTransform', 'bFinalize'})
    def __init__(self, signature, base_tree, socket_templates=[],
                 additional_parameters={}):
        super().__init__(signature, base_tree, socket_templates,
                         additional_parameters)
        self.bObject=None
        self.default_prepare_state = 0 # prepared, executed = False, False (complete reset)

    def check_drivers(self):
        for st in self.socket_templates:
            try:
                if st.is_animatable == False:
                    socket = st.name
                    multi = st.use_multi_input
                    vector = isinstance(st.default_value, tuple)
                    # if single property
                    if not multi and not vector:
                        has_driver = check_for_driver(self, socket)
                    elif not multi and vector:
                        for i in range(len(st.default_value)):
                            has_driver = check_for_driver(self, socket, i)
                            if has_driver: break
                    elif multi:
                        # TODO: this is a HACK, try and understand this later
                        if socket == 'Custom Properties':
                            has_driver = check_for_driver(self, socket,)
                        else:
                            for i in range(len(self.inputs[socket].links)):
                                has_driver = check_for_driver(self, socket, 0, i)
                                if has_driver: break
                    if has_driver:
                        raise GraphError(f"Error: Socket \"{socket}\" is not animatable and cannot be driven.")
            except Exception as e:
                # This isn't really an error and the user should not see it.
                from .__init__ import DOERROR
                if DOERROR:
                    raise e
    
    def setup_custom_props(self, ob, input):
        from .mantis_dataclasses import custom_prop_template
        # detect custom inputs
        for i, l in enumerate(self.inputs[input].links):
            # we need to trace back all inputs
            custom_prop_data = self.evaluate_input(input, i)
            if not isinstance(custom_prop_data, custom_prop_template): continue
            from .utilities.drivers import MantisDriver
            name = custom_prop_data.name
            if name in ob.keys():
                raise RuntimeError("Error: cannot create a custom property with "
                                   "the same name as an existing property.")
            prop_type = custom_prop_data.prop_type
            match prop_type:
                case 'BOOL':
                    value = custom_prop_data.default_value_bool
                case 'INT':
                    value = custom_prop_data.default_value_int
                case 'FLOAT':
                    value = custom_prop_data.default_value_float
                case 'VECTOR':
                    value = custom_prop_data.default_value_vector
                case 'STRING':
                    value = custom_prop_data.default_value_string
            if (value is None):
                raise RuntimeError("Could not set value of custom parameter")
                # it creates a more confusing error later sometimes, better to catch it here.
            ob[name] = value
            ui_data = ob.id_properties_ui(name)
            ui_data.update(
                default=value,
                description=custom_prop_data.description)
            #if a number, set the min/max values. it may overflow on the C side
            if type(value) in [float, int]:
                for prop_name in ['min', 'max', 'soft_min', 'soft_max', ]:
                    prop_value = getattr(custom_prop_data, prop_name)
                    if type(value) == int: prop_value = int(prop_value)
                    # DO: figure out the right way to prevent an oveflow
                    try: # we have to do this as a keyword argument like this
                        ui_data.update( **{prop_name:prop_value} )
                    except OverflowError: #this occurs when the value is inf
                        prRed(f"invalid value {prop_value} for custom prop {prop_name}"
                                f" of type {type(value)} in {self}. It will remain unset.")
            ob.property_overridable_library_set(f"[\"{name}\"]", True)
            pass

# TODO this should use the socket templates / prop_sockets system!
class xFormArmature(xFormNode):
    '''A node representing an armature object'''
    __slots__ = ()
    socket_templates = xFormArmatureSockets

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, self.socket_templates)
        setup_custom_property_inputs_outputs(self)

    def bPrepare(self, bContext=None):
        self.parameters['Matrix'] = get_matrix(self)
        self.prepared = True

    def bTransformPass(self, bContext = None,):
        # from .utilities import get_ui_node

        import bpy
        if (not isinstance(bContext, bpy.types.Context)):
            raise RuntimeError("Incorrect context")

        name = self.evaluate_input("Name")
        matrix = self.parameters['Matrix']
        reset_transforms = False

        #check if an object by the name exists
        if (name) and (ob := bpy.data.objects.get(name)):
            # Clear the drivers from BOTH the object/pose and the skeleton
            if (ob.animation_data):
                while (ob.animation_data.drivers):
                        ob.animation_data.drivers.remove(ob.animation_data.drivers[-1])
            if (ob.data.animation_data):
                while (ob.data.animation_data.drivers):
                        ob.data.animation_data.drivers.remove(ob.data.animation_data.drivers[-1])
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
        
        # it seems this data sticks around even if the object was deleted, so clear it here.
        ob.id_properties_clear()

        self.bObject = ob.name
        self.bRegisterObject('OBJECT', ob)
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

        ob.data.display_type = self.evaluate_input('Display Type')

        # This will OVERWRITE the root armature since bones have to trace back to this one.
        root_armature = ob.name
        parent_xForm_info = get_parent_xForm_info(self)
        my_info = xForm_info(
            object_type='armature',
            root_armature= ob.name,
            parent_pose_name=parent_xForm_info.self_pose_name,
            parent_edit_name=parent_xForm_info.self_edit_name,
            self_pose_name=ob.name,
            self_edit_name=ob.name,
        )
        self.parameters['xForm Out'] = my_info

        self.executed = True
    
    def bFinalize(self, bContext = None):
        # custom properties
        self.setup_custom_props(self.bGetObject(), "Custom Properties")
        finish_drivers(self)

    def bGetObject(self, mode = ''):
        import bpy; return bpy.data.objects[self.parameters['xForm Out'].self_pose_name]

class xFormBone(xFormNode):
    '''A node representing a bone in an armature'''
    __slots__ = ()
    socket_templates = xFormBoneSockets
    # DO: make a way to identify which armature this belongs to
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, xFormBoneSockets)
        setup_custom_property_inputs_outputs(self)

    def bGetParentArmature(self):
        parent_xForm_info = get_parent_xForm_info(self)
        from bpy import data
        return data.objects.get(parent_xForm_info.root_armature)

    def bSetParent(self, eb):
        from bpy import data
        parent_xForm_info = get_parent_xForm_info(self)
        parent_armature = data.objects.get( parent_xForm_info.root_armature)
        if parent_xForm_info.self_edit_name != parent_xForm_info.root_armature:
            parent_bone = parent_armature.data.edit_bones.get( parent_xForm_info.self_edit_name)
            eb.parent = parent_bone
            parent_mantis_node = get_parent_node(self, type = 'LINK') # get the link node.
            # TODO probably need to send the parenting info or at least the signatures of intervening nodes.
            eb.use_connect = parent_mantis_node.evaluate_input("Connected")
            eb.use_inherit_rotation = parent_mantis_node.evaluate_input("Inherit Rotation")
            eb.inherit_scale = parent_mantis_node.evaluate_input("Inherit Scale")

    def bPrepare(self, bContext=None):
        self.check_drivers()
        self.parameters['Matrix'] = get_matrix(self)
        self.prepared = True

    def bTransformPass(self, bContext = None,): #possibly will need to pass context?
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
        if self.inputs['Bone Collection'].links:
            bCol_groups = []
            for i, l in enumerate(self.inputs['Bone Collection'].links):
                bCol_group = self.evaluate_input("Bone Collection", index=i)
                bCol_groups.append(bCol_group)
            bCols = '|'.join(bCol_groups)
        else:
            bCols = self.evaluate_input("Bone Collection")
        if bCols: # it is actually possible to add a bone to no collections. odd.
            bone_collections = bCols.split("|")
            for collection_list in bone_collections:
                hierarchy = collection_list.split(">")
                col_parent = None
                for bCol in hierarchy:
                    if bCol is None: continue # I think this
                    if bCol == '': continue
                    if ( col := d.collections_all.get(bCol) ) is None:
                        col = d.collections.new(bCol)
                    col.parent = col_parent
                    col_parent = col
                if hierarchy[-1]: # will be "" or None if the box is empty
                    d.collections_all.get(hierarchy[-1]).assign(eb)

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
        self.bRegisterObject('BONE', xF, eb)
        # The bone should have relationships going in at this point.

        self.bSetParent(eb)

        if eb.head == eb.tail:
            raise RuntimeError(wrapRed(f"Could not create edit bone: {name} because"
                                        " bone head was located in the same place as"
                                        " bone tail."))

        # Setup Deform attributes...
        eb_props_sockets = self.gen_property_socket_map(prop_owner_group="edit_bone")
        b_objects = {'edit_bone':eb, 'pose_bone':None, 'bone':None, 'DEFAULT':None}
        evaluate_sockets(self, b_objects, eb_props_sockets)
        print( wrapGreen("Created Bone: ") + wrapOrange(eb.name) + wrapGreen(" in ") + wrapWhite(self.bGetParentArmature().name))

        parent_xForm_info = get_parent_xForm_info(self)
        my_info = xForm_info(
            object_type='bone',
            root_armature= xF.name,
            parent_pose_name=parent_xForm_info.self_pose_name,
            parent_edit_name=parent_xForm_info.self_edit_name,
            self_pose_name=eb.name,
            self_edit_name=eb.name,
        )
        self.parameters['xForm Out'] = my_info
        self.executed = True

    def set_bone_color(self, b, inherit_color, bContext):
        color_values = self.evaluate_input('Color')
        if color_values is None:
            prOrange(f"Warning: No color information found for {b.name}. This should not happen.")
            return
        if inherit_color and b.parent:
            b.color.palette=b.parent.color.palette
            if b.color.palette == 'CUSTOM':
                b.color.custom.active=b.parent.color.custom.active
                b.color.custom.normal=b.parent.color.custom.normal
                b.color.custom.select=b.parent.color.custom.select
            return

        from mathutils import Color
        color_active = Color(color_values[:3])
        color_normal = Color(color_values[3:6])
        color_select = Color(color_values[6:])
        is_theme_colors = False
        theme = bContext.preferences.themes[0]
        for i, color_set in enumerate(theme.bone_color_sets):
            if  ((color_active == color_set.active) and
                (color_normal == color_set.normal) and
                (color_select == color_set.select) ):
                            is_theme_colors=True; break
        if is_theme_colors:          # add 1, not 0-indexed
            b.color.palette = 'THEME'+str(i+1).zfill(2)
        elif    ((color_active == theme.view_3d.bone_pose_active) and
                (color_normal == theme.view_3d.bone_solid) and
                (color_select == theme.view_3d.bone_pose) ):
                        b.color.palette = 'DEFAULT'
        else:
            b.color.palette = 'CUSTOM'
            b.color.custom.active=color_active
            b.color.custom.normal=color_normal
            b.color.custom.select=color_select

    def bFinalize(self, bContext = None):

        b = self.bGetParentArmature().data.bones[self.bObject]
        # let's do bone colors first
        inherit_color = self.evaluate_input("Inherit Color")
        if len(self.inputs['Color'].links) > 0:
            inherit_color = False # use the link instead
        self.set_bone_color(b, inherit_color, bContext)
        if self.evaluate_input("BBone HQ Deformation"):
            b.bbone_mapping_mode = "CURVED"
        if handle_type := self.evaluate_input("BBone Start Handle Type"):
            b.bbone_handle_type_start = handle_type
        if handle_type := self.evaluate_input("BBone End Handle Type"):
            b.bbone_handle_type_end = handle_type
        try:
            if (custom_handle := self.evaluate_input("BBone Custom Start Handle")):
                b.bbone_custom_handle_start = self.bGetParentArmature().data.bones[custom_handle]
            if (custom_handle := self.evaluate_input("BBone Custom End Handle")):
                b.bbone_custom_handle_end = self.bGetParentArmature().data.bones[custom_handle]
        except KeyError:
            prRed("Warning: BBone start or end handle not set because of missing bone in armature.")

        pb = self.bGetParentArmature().pose.bones[self.bObject]
        pb.id_properties_clear()
        self.setup_custom_props(pb, "Custom Properties")
        b_objects = {'edit_bone':None, 'pose_bone':pb, 'bone':pb.bone, 'DEFAULT':None}
        props_sockets = self.gen_property_socket_map()
        evaluate_sockets(self, b_objects, props_sockets)

        # and in edit mode we need to explicitly set the bbone properties
        # I don't like this HACK but there seems to be no other way...
        # Better to ask forgiveness than permission. If anyone wants control over this, I'll solve the problem then
        # IN the near future, in fact, I think I'll make a BBone Rest Pose matrix thing
        # and allow users to set it from bezier curves
        pb.bone.bbone_easein = 1; pb.bone.bbone_easeout = 1

        finish_drivers(self)

        # TODO: I should not need a special case for this
        pb.custom_shape_transform = None
        pb.custom_shape = None
        from bpy.types import Object
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
            if type(ob) in {Object}:
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

class xFormGeometryObject(xFormNode):
    '''A node representing an armature object'''
    __slots__ = ("has_shape_keys")
    socket_templates = xFormGeometryObjectSockets
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, self.socket_templates)
        setup_custom_property_inputs_outputs(self)

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
        from .deformer_nodes import DeformerHook
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
            if data: # Delete it and regenerate it if it exists.
                data.name+="_TRASH.000" # but we can't actually delete it here
                # since previous executions of the graph may be using it.
                # instead, we'll rename it and use a new copy. This will probably
                # be deleted on its own by Blender's garbage collector.
                # if it isn't, then it is still in use and I may NOT touch it.
            data=self.bObject.data.copy(); data.animation_data_clear()
            data.name = name+"_MANTIS"
            self.bObject.data = data
        reset_object_data(self.bObject)
        matrix= get_matrix(self)
        self.parameters['Matrix'] = matrix
        try:
            set_object_parent(self)
        except: # I guess it isn't ready yet. we'll do it later
            pass # (This can happen when solving schema.)
        self.bObject.matrix_world = matrix

        parent_xForm_info = get_parent_xForm_info(self)
        root_armature = parent_xForm_info.root_armature
        my_info = xForm_info(
            object_type='object',
            root_armature= root_armature,
            parent_pose_name=parent_xForm_info.self_edit_name,
            parent_edit_name=parent_xForm_info.self_pose_name,
            self_pose_name=self.bObject.name,
            self_edit_name=self.bObject.name,
        )
        self.parameters['xForm Out'] = my_info
        self.bRegisterObject('OBJECT', self.bObject)
        self.prepared = True

    def bTransformPass(self, bContext = None,):
        try:
            bContext.collection.objects.link(self.bObject)
        except RuntimeError: #already in; but a dangerous thing to pass.
            pass
        self.has_shape_keys = False
        # putting this in bTransformPass simply prevents it from being run more than once.
        # maybe I should do that with the rest of bPrepare, too.
        props_sockets = self.property_socket_map
        evaluate_sockets(self, {"DEFAULT":self.bObject}, props_sockets)
        self.executed = True

    def bFinalize(self, bContext = None):
        matrix= get_matrix(self)
        set_object_parent(self)
        self.bObject.matrix_world = matrix
        # custom properties
        self.setup_custom_props(self.bGetObject(), "Custom Properties")
        finish_drivers(self)

    def bGetObject(self, mode = 'POSE'):
        return self.bObject

class xFormObjectInstance(xFormNode):
    """Represents an instance of an existing geometry object."""
    __slots__ = ("has_shape_keys")
    socket_templates = xFormGeometryObjectInstanceSockets

    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, self.socket_templates)
        self.has_shape_keys = False # Shape Keys will make a dupe so this is OK
        setup_custom_property_inputs_outputs(self)

    def ui_modify_socket(self, ui_socket, socket_name=None):
        if ui_socket.name == 'As Instance':
            change_handled = True
            try:
                self.bObject.modifiers[0]['Socket_1'] = ui_socket.default_value
            except Exception as e:
                print("Failed to update mantis socket because of %s" % e,
                        "Updating tree instead.")
            return change_handled
        else:
            return super().ui_modify_socket(ui_socket, socket_name)

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

        parent_xForm_info = get_parent_xForm_info(self)
        root_armature = parent_xForm_info.root_armature
        my_info = xForm_info(
            object_type='object',
            root_armature= root_armature,
            parent_pose_name=parent_xForm_info.self_edit_name,
            parent_edit_name=parent_xForm_info.self_pose_name,
            self_pose_name=self.bObject.name,
            self_edit_name=self.bObject.name,
        )
        self.parameters['xForm Out'] = my_info
        self.bRegisterObject('OBJECT', self.bObject)
        self.prepared = True

    def bTransformPass(self, bContext = None,):
        try:
            bContext.collection.objects.link(self.bObject)
        except RuntimeError: #already in; but a dangerous thing to pass.
            pass
        self.has_shape_keys = False
        # putting this in bTransformPass simply prevents it from being run more than once.
        # maybe I should do that with the rest of bPrepare, too.
        props_sockets = {
            'hide_viewport'    : ("Hide in Viewport", False),
            'hide_render'      : ("Hide in Render", False),
        }
        evaluate_sockets(self, {"DEFAULT":self.bObject}, props_sockets)
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
            from .utilities.geometry_node_graphgen import gen_object_instance_node_group
            ng = gen_object_instance_node_group()
        modifier.node_group = ng
        modifier["Socket_0"] = source_ob
        modifier["Socket_1"] = self.evaluate_input("As Instance")
        # custom properties
        self.setup_custom_props(self.bGetObject(), "Custom Properties")
        finish_drivers(self)

    def bGetObject(self, mode = 'POSE'):
        return self.bObject

class xFormCurvePin(xFormNode):
    """An xForm pinned to a specific location on a curve."""
    __slots__ = ()
    socket_templates = xFormCurvePinSockets
    passes=frozenset({'bPrepare', 'bFinalize'})
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, self.socket_templates,
            additional_parameters={"Matrix":None})
        setup_custom_property_inputs_outputs(self)

    def get_matrix_from_spline(self, spline_lookup):
        matrix = spline_lookup.matrix_at_u(self.parameters["Curve Pin Factor"])
        track_axis = self.parameters["Forward Axis"]; up_axis = self.parameters["Up Axis"]
        # Copy the original basis before changing anything.
        from mathutils import Vector
        tangent = Vector(matrix.col[1][:3]); normal = Vector(matrix.col[2][:3])
        # I have to take the Z axis and invert it because of the way Mantis calculates the normal
        # using the ribbon mesh rather which extrudes along the binormal
        # this is bad but it is too late to change this now, oh well
        normal *= -1 # I have checked this with every combination and it works
        track_sign = -1 if track_axis.startswith("TRACK_NEGATIVE_") else 1
        track_axis = track_axis[-1]; up_axis = up_axis[-1]
        axis_index = {"X": 0, "Y": 1, "Z": 2} #  there is probably a less stupid way to do this
        track_index = axis_index[track_axis]; up_index = axis_index[up_axis]
        if track_index == up_index: raise ValueError("Track and up_axis axes must be different")
        # Assign the requested axes.
        cols = [None, None, None]
        cols[track_index] = tangent * track_sign; cols[up_index] = normal
        # Fill the remaining axis to make a right-handed basis.
        # the bitanget calculation is order dependent if you want to stay right-handed
        if track_index != 0 and up_index != 0:   cols[0] = cols[1].cross(cols[2])
        elif track_index != 1 and up_index != 1: cols[1] = cols[2].cross(cols[0])
        else:                                    cols[2] = cols[0].cross(cols[1])
        matrix.col[0].xyz = cols[0]; matrix.col[1].xyz = cols[1]
        matrix.col[2].xyz = cols[2]
        return matrix

    def generate_constraints(self, ob, curve):
        # we'll limit all the transforms so we can parent it without
        # having to deal with the weird curve parenting (path-animation)
        c1 = ob.constraints.new("LIMIT_LOCATION")
        for max_min in ['max','min']:
            for axis in "xyz":
                setattr(c1, "use_"+max_min+"_"+axis, True)
                setattr(c1, max_min+"_"+axis, 0.0)
        c2 = ob.constraints.new("LIMIT_ROTATION")
        for axis in "xyz":
            setattr(c2, "use_limit_"+axis, True)
            setattr(c2, max_min+"_"+axis, 0.0)
        c3 = ob.constraints.new("LIMIT_SCALE")
        for max_min in ['max','min']:
            for axis in "xyz":
                setattr(c3, "use_"+max_min+"_"+axis, True)
                setattr(c3, max_min+"_"+axis, 1.0)
        c4 = ob.constraints.new("FOLLOW_PATH")
        c4.target = curve
        c4.use_fixed_location = True
        c4.use_curve_radius = True
        c4.use_curve_follow = True
        c4.name = "Curve Pin"
        return (c1, c2, c3, c4,)

    def bPrepare(self, bContext = None,):
        from bpy import data, context
        if not bContext: bContext = context # HACK is this wise?
        # Generate the empty
        ob = data.objects.get(self.evaluate_input("Name"))
        if not ob:
            ob = data.objects.new(self.evaluate_input("Name"), None)
            ob.lock_location   = [True, True, True]
            ob.lock_rotation   = [True, True, True]
            ob.lock_scale      = [True, True, True]
            ob.lock_rotation_w = True
            ob.empty_display_type = 'CONE'
            ob.empty_display_size = 0.10
        self.bObject = ob; self.bRegisterObject('OBJECT', ob); reset_object_data(ob)
        # Get the curve and check it
        node_line = trace_single_line(self, "Parent Curve")[0][1:] # slice excludes self
        for other_node in node_line:
            if other_node.node_type == 'XFORM': break
        else:
            raise GraphError(f"ERROR: {self} is not connected to a parent curve")
        if isinstance(other_node, (xFormArmature, xFormBone, xFormObjectInstance,)):
            raise GraphError(f"ERROR: {self} must be connected to curve,"
                              " not {other_node.__class__.__name__}")
        curve=other_node.bGetObject(); curve_name = curve.name
        if curve.type != 'CURVE':
            raise GraphError(f"ERROR: {self} must be connected to curve,"
                              " not {curve.type}")
        from .utilities.utilities import get_extracted_spline_object
        spline_index = self.evaluate_input("Spline Index")
        curve = get_extracted_spline_object(curve, spline_index, self.mContext)
        for link_me in [ob, curve]: # Link everything to the scene:
            if (link_me.name not in bContext.view_layer.active_layer_collection.collection.objects):
                bContext.view_layer.active_layer_collection.collection.objects.link(link_me)

        constraints = self.generate_constraints(ob, curve); c = constraints[-1]
        props_sockets = self.gen_property_socket_map()
        b_objects = {"constraint":c, "object":self.bObject}
        evaluate_sockets(self, b_objects, props_sockets)

        # Find the default values to set even if the properties are drive:
        enums =  ( None,
                ("FORWARD_X", "FORWARD_Y", "FORWARD_Z", "TRACK_NEGATIVE_X", "TRACK_NEGATIVE_Y", "TRACK_NEGATIVE_Z"),
                ("UP_X", "UP_Y", "UP_Z"),
                )
        for i, socket_name in enumerate(("Curve Pin Factor", "Forward Axis","Up Axis",)):
            if self.inputs.get(socket_name) is None: continue 
            enum = enums[i]
            for template in self.socket_templates:
                if template.name == socket_name: break
            prop_amount = find_driven_default_value(self, socket_name)
            # after all it may not be driven so it is probably a string if it is one of the axis properties.
            if isinstance(prop_amount, (int, float)) and enum: # it is actually driving an enum value instead...
                for i, enum_val in enumerate(enum):
                    # check if the prop amount is in the current int as the enum val
                    if i+1 > prop_amount: break
                prop_amount = enum_val
            self.parameters[socket_name] = prop_amount
            # Explicitly set the constraint attributes
            setattr(c, template.blender_property, prop_amount)

        # Now set the matrix - since this may provide dependencies to other nodes
        from .misc_nodes import get_from_curve_lut
        spline_lookup = get_from_curve_lut(curve_name, spline_index, bContext, self)
        matrix = self.get_matrix_from_spline(spline_lookup)
        # HACK: this is giving a local space matrix, and that's dumb
        # TODO: Mantis should handle coordinate space conversion automatically
        self.parameters['Matrix'] = matrix
        ob.parent=curve
        # NOTE: Blender does weird things with curve parenting when there is Path Animation
        #  and it sets the inverse parent matrix based on the evaluated matrix from the point
        #  on the curve set by path animation. (That's why we need all the WS limit constraints)
        print( wrapGreen("Created Curve Pin: ") + wrapOrange(self.bObject.name) )

        parent_xForm_info = get_parent_xForm_info(self)
        root_armature = parent_xForm_info.root_armature
        my_info = xForm_info(
            object_type='object',
            root_armature= root_armature,
            parent_pose_name=curve.name,
            parent_edit_name=curve.name,
            self_pose_name=self.bObject.name,
            self_edit_name=self.bObject.name,
        )
        self.parameters['xForm Out'] = my_info

        self.prepared = True; self.executed = True

    def bFinalize(self, bContext = None):
        # custom properties
        self.setup_custom_props(self.bGetObject(), "Custom Properties")
        finish_drivers(self)

    def bGetObject(self, mode = 'POSE'):
        return self.bObject

# special thank-you to Natalie Cuthbert, who submitted a patch for this
# it turned out, I already had this patch laying around
# because I was too busy with grad school I didn't succeed in collaborating
# so while I apologize for failing to get your name in the commit history
# now you get a special thank-you in Mantis instead!
class xFormGetBone(xFormNode):
    """Represents an instance of an existing geometry object."""
    __slots__ = ()
    socket_templates = xFormGetBoneSockets
    passes=frozenset({})
    def __init__(self, signature, base_tree):
        super().__init__(signature, base_tree, self.socket_templates)
        # this is just a getter
        self.prepared=True; self.executed=True; self.execution_prepared=True

    def reset_execution(self):
        super().reset_execution()
        self.prepared=True; self.executed=True; self.execution_prepared=True
    
    def bGetParentArmature(self):
        from bpy import data
        # the below function may return None, but data.objects.get expects a string
        return data.objects.get(self.evaluate_input("Parent Armature") or "")

    def bGetObject(self, mode = 'POSE'):
        bone = None
        self.bObject = self.evaluate_input("Bone")
        armature = self.bGetParentArmature()
        from bpy.types import Object
        assert armature is not None, f"{self} requires a parent armature input to operate."
        assert isinstance(armature, Object), f"{self}: The parent armature must be an armature object."
        if armature:
            assert armature.type == 'ARMATURE', f"{self}: The parent armature must be an armature object."
            match mode:
                case 'EDIT':
                    bone = armature.data.edit_bones.get(self.evaluate_input("Bone"))
                case 'OBJECT':
                    bone = armature.bones.get(self.evaluate_input("Bone"))
                case 'POSE':
                    bone = armature.pose.bones.get(self.evaluate_input("Bone"))
        assert self.bObject is not None, f"{self} failed to get the desired bone. Check if the bone name exists."
        self.bRegisterObject('BONE', armature, bone)
        return bone

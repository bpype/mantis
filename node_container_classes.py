# generic node classes

#everything here sucks and is dumb and needs renaiming

# this is stupid, lol
def TellClasses():
             # xForm
    return [ xFormRoot,
             xFormArmature,
             xFormBone,
             # special
             LinkInherit,
             # copy
             LinkCopyLocation,
             LinkCopyRotation,
             LinkCopyScale,
             LinkCopyTransforms,
             # limit
             LinkLimitLocation,
             LinkLimitRotation,
             LinkLimitScale,
             LinkLimitDistance,
             # tracking
             LinkStretchTo,
             LinkDampedTrack,
             LinkLockedTrack,
             LinkTrackTo,
             #misc
             LinkInheritConstraint,
             # IK
             LinkInverseKinematics,
             # utility
             InputFloat,
             InputVector,
             InputBoolean,
             InputBooleanThreeTuple,
             InputRotationOrder,
             InputTransformSpace,
             InputString,
             InputQuaternion,
             InputQuaternionAA,
             InputMatrix,
            ]
    #kinda a dumb way to do this but it werks so whatever
            
            


# have these so far
  # simple nodes:
             # InputFloatNode,
             # InputVectorNode,
             # InputBooleanNode,
             # InputBooleanThreeTupleNode,
             # InputRotationOrderNode,
             # InputTransformSpaceNode,
             # InputStringNode,
             # InputQuaternionNode,
             # InputQuaternionNodeAA,
             # InputMatrixNode,

  # xForm nodes:
        # xFormNullNode,
        # xFormBoneNode,
        # xFormRootNode,
        # xFormArmatureNode,
        

  # Link nodes:
             # LinkInheritNode,
             # LinkInverseKinematics,
             # LinkCopyLocationNode,
             # LinkCopyRotationNode,
             # LinkCopyScaleNode,
             # LinkInheritConstraintNode,
             # LinkCopyTransformNode,
             # LinkStretchToNode,
             # LinkDampedTrackNode,
             # LinkLockedTrackNode,
             # LinkTrackToNode,
             # LinkLimitLocationNode,
             # LinkLimitScaleNode,
             # LinkLimitRotationNode,
             # LinkLimitDistanceNode,]
             
             
#eventually add this:
    # def print_to_mantis_script():
        # #gonna eventually make this into a script
        # # that can be written and read from a text file
        # # and loaded into the interpretor
        # pass
# 



# DO THIS:
#  each node should have a name or UUID, since there must be a way to
#   associate them with the lines that are read from the input-graph
#  actually I cna and should just use the signature, since it can gimme
#   any prototype node I need, and it encodes relationships, too.


def fill_parameters(node_container, node_prototype):
    from .utilities import to_mathutils_value
    for key, value in node_container.parameters.items():
        node_socket = node_prototype.inputs.get(key)
        if not node_socket:
            #maybe the node socket has no name
            if ( ( len(node_prototype.inputs) == 0) and ( len(node_prototype.outputs) == 1) ):
                # this is a simple input node.
                node_socket = node_prototype.outputs[0]
            elif key == 'Mute':
                node_container.parameters[key] = node_prototype.mute
                continue
            else: # really don't know!
                raise RuntimeError("No node socket found for " + key + " when filling out node parameters.")
                continue
        
        if node_socket.bl_idname in  ['RelationshipSocket', 'xFormSocket']:
            continue
        
        elif hasattr(node_socket, "default_value"):
            default_value_type = type(node_socket.default_value)
            #print (default_value_type)
            math_val = to_mathutils_value(node_socket)
            if math_val:
                node_container.parameters[key] = math_val
            # maybe we can use it directly.. ?
            elif ( (default_value_type == str) or (default_value_type == bool) or
                 (default_value_type == float) or (default_value_type == int) ):
                node_container.parameters[key] = node_socket.default_value
            # HACK: there should be no sets, I think, but...
            elif default_value_type == set:
                node_container.parameters[key] = node_socket.default_value
                # TODO: make this make sense sometime in the future!
                # There should not be any sets!
            else:
                raise RuntimeError("No value found for " + key + " when filling out node parameters for " + node_prototype.name)
        else:
                print (key, node_socket)
                # do: remove these from parameters maybe
                # since they are always None if not connected
    # for key, value in node_container.parameters.items():
        # if value:
            # print (key, value)

def evaluate_input(node_container, input_name):
    # for simple cases
    trace = trace_single_line(node_container, input_name)
    prop = trace[0][-1].parameters.get(trace[1].to_socket)
    # WHY doesn't this work for the Matrix inputs .. ?
    
    return prop


def trace_node_lines(node_container):
    """ Tells the depth of a node within the node tree. """
    node_lines = []
    if hasattr(node_container, "inputs"):
        for key, socket in node_container.inputs.items():
            # Recrusive search through the tree.
            #  * checc each relevant input socket in the node
            #  * for EACH input, find the node it's connected to
            #    * repeat from here until you get all the lines
            if ( ( key in ["Relationship", "Parent", "Input Relationship", "Target"])
                          and (socket.is_connected) ):
                # it is necesary to check the key because of Link nodes,
                #   which don't really traverse like normal.
                # TODO: see if I can refactor this to make it traverse
                other = socket.from_node
                if (other):
                    other_lines = trace_node_lines(other)
                    if not other_lines:
                        node_lines.append([other])
                    for line in other_lines:
                        node_lines.append( [other] + line )
    return node_lines
    
    

def trace_single_line(node_container, input_name):
    """ Tells the depth of a node within the node tree. """
    nodes = [node_container]
    if hasattr(node_container, "inputs"):
        # Trace a single line
        if (socket := node_container.inputs.get(input_name) ):
            while (socket.is_connected):
                other = socket.from_node.outputs.get(socket.from_socket)
                if (other):
                    socket = other
                    if socket.can_traverse:
                        socket = socket.traverse_target
                        nodes.append(socket.to_node)
                    else: # this is an output.
                        nodes.append(socket.from_node)
                        break
                else:
                    break
    return nodes, socket


# this is same as the other, just flip from/to and in/out
def trace_single_line_up(node_container, output_name):
    """ Tells the depth of a node within the node tree. """
    nodes = [node_container]
    if hasattr(node_container, "outputs"):
        # Trace a single line
        if (socket := node_container.outputs.get(output_name) ):
            while (socket.is_connected):
                other = socket.to_node.inputs.get(socket.to_socket)
                if (other):
                    socket = other
                    if socket.can_traverse:
                        socket = socket.traverse_target
                        nodes.append(socket.from_node)
                    else: # this is an input.
                        nodes.append(socket.to_node)
                        break
                else:
                    break
    return nodes, socket

def node_depth(node_container):
    maxlen = 0
    for nodes in trace_node_lines(node_container):
        if (len(nodes) > maxlen):
            maxlen = len(nodes)
    return maxlen
        
def get_parent(node_container):
    node_line, socket = trace_single_line(node_container, "Relationship")
    parent_nc = None
    for i in range(len(node_line)):
        print (node_line[i])
        # check each of the possible parent types.
        if ( isinstance(node_line[ i ], LinkInherit) ):
            try: # it's the next one
                return node_line[ i + 1 ]
            except IndexError: # if there is no next one...
                return None # then there's no parent!
    return None
    # TO DO!
    #
    # make this do shorthand parenting - if no parent, then use World
    #  if the parent node is skipped, use the previous node (an xForm)
    #  with default settings.
    # it is OK to generate a new, "fake" node container for this!

def get_target_and_subtarget(node_container, constraint, input_name = "Target"):
    from bpy.types import PoseBone, Object
    subtarget = ''; target = node_container.evaluate_input(input_name)
    if target:
        if (isinstance(target.bGetObject(), PoseBone)):
            subtarget = target.bGetObject().name
            target = target.bGetParentArmature()
        elif (isinstance(target.bGetObject(), Object) ):
            target = target.bGetObject()
        else:
            raise RuntimeError("Cannot interpret constraint target!")
    if (input_name == 'Target'): # this is sloppy, but it werks
        constraint.target, constraint.subtarget = target, subtarget
    elif (input_name == 'Pole Target'):
        constraint.pole_target, constraint.pole_subtarget = target, subtarget






class NodeSocket:
    # this is not meant to be a particularly robust class
    # e.g., there will be no disconnect() method since it isn't needed
    # I just wanna have something persistent (an object)
    # I'd perfer to use pointers and structs, whatever
    is_input = False
    is_connected = False
    from_node = None
    to_node = None
    from_socket = None
    to_socket = None
    can_traverse = False
    traverse_target = None
    
    def __init__(self, is_input = False,
                 from_socket = None, to_socket = None,
                 from_node = None, to_node = None,
                 traverse_target = None):
        self.from_socket = from_socket
        self.to_socket   = to_socket
        self.from_node   = from_node
        self.to_node     = to_node
        self.is_input    = is_input
        if (self.is_input and (self.from_node or self.from_socket)):
            self.is_connected = True
        elif ( not self.is_input and (self.to_node or self.to_socket)):
            self.is_connected = True
        self.set_traverse_target(traverse_target)
        
    def connect(self, node, socket):
        if (self.is_input):
            self.from_node   = node
            self.from_socket = socket
        else:
            self.to_node   =  node
            self.to_socket = socket
        self.is_connected = True
    
    def set_traverse_target(self, traverse_target):
        if (traverse_target):
            self.traverse_target = traverse_target
            self.can_traverse = True
    
    def __repr__(self):
        if self.is_input:
            return ( self.to_node.__repr__() + "::" + self.to_socket )
        else:
            return (self.from_node.__repr__() + "::" + self.from_socket)
    
    


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
        self.outputs = {"xForm Out":NodeSocket(from_socket="xForm Out", from_node = self),}
        self.parameters = {}
        self.links = {} # leave this empty for now!
        self.node_type = 'XFORM'
    
    def init_to_node_line(line,):
        pass
    
    def evaluate_input(self, input_name):
        return "ROOT"
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

class xFormArmature:
    '''A node representing an armature object'''
    
    bObject = None
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
         "Name"           : NodeSocket(is_input = True, to_socket = "Name", to_node = self),
         "Rotation Order" : NodeSocket(is_input = True, to_socket = "Rotation Order", to_node = self),
         "Matrix"         : NodeSocket(is_input = True, to_socket = "Matrix", to_node = self),
         "Relationship"   : NodeSocket(is_input = True, to_socket = "Relationship", to_node = self),
        }
        self.outputs = {
         "xForm Out" : NodeSocket(from_socket="xForm Out", from_node = self),
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
        else:
            # Create the Object
            ob = bpy.data.objects.new(name, bpy.data.armatures.new(name)) #create ob
            if (ob.name != name):
                raise RuntimeError("Could not create xForm object", name)
            
        self.bObject = ob.name
        
        ob.matrix_world = matrix
        
        
        # first, get the parent object
        parent_node = get_parent(self)
        if hasattr(parent_node, "bObject"):
            # this won't work of course, TODO
            self.bObject.parent = parent_node.bObject
        
        # Link to Scene:
        if (ob.name not in bContext.view_layer.active_layer_collection.collection.objects):
            bContext.view_layer.active_layer_collection.collection.objects.link(ob)
        #self.bParent(bContext)
        
        # Finalize the action
        # prevAct = bContext.view_layer.objects.active
        bContext.view_layer.objects.active = ob
        bpy.ops.object.mode_set(mode='EDIT')
        print ("Changing Armature Mode to EDIT")
        # clear it
        while (len(ob.data.edit_bones) > 0):
            ob.data.edit_bones.remove(ob.data.edit_bones[0])
        # bContext.view_layer.objects.active = prevAct

        print ("Created Armature object: \""+ ob.name +"\"")
        
        
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
        import bpy
        return bpy.data.objects[self.bObject]
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

class xFormBone:
    '''A node representing a bone in an armature'''
    # DO: make a way to identify which armature this belongs to
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.executed = False
        self.signature = signature
        self.inputs = {
         "Name"           : NodeSocket(is_input = True, to_socket = "Name", to_node = self,),
         "Rotation Order" : NodeSocket(is_input = True, to_socket = "Rotation Order", to_node = self,),
         "Matrix"         : NodeSocket(is_input = True, to_socket = "Matrix", to_node = self,),
         "Relationship"   : NodeSocket(is_input = True, to_socket = "Relationship", to_node = self,),
         # IK settings
         "IK Stretch"     : NodeSocket(is_input = True, to_socket = "IK Stretch", to_node = self,),
         "Lock IK"        : NodeSocket(is_input = True, to_socket = "Lock IK", to_node = self,),
         "IK Stiffness"   : NodeSocket(is_input = True, to_socket = "IK Stiffness", to_node = self,),
         "Limit IK"       : NodeSocket(is_input = True, to_socket = "Limit IK", to_node = self,),
         "X Min"          : NodeSocket(is_input = True, to_socket = "X Min", to_node = self,),
         "X Max"          : NodeSocket(is_input = True, to_socket = "X Max", to_node = self,),
         "Y Min"          : NodeSocket(is_input = True, to_socket = "Y Min", to_node = self,),
         "Y Max"          : NodeSocket(is_input = True, to_socket = "Y Max", to_node = self,),
         "Z Min"          : NodeSocket(is_input = True, to_socket = "Z Min", to_node = self,),
         "Z Max"          : NodeSocket(is_input = True, to_socket = "Z Max", to_node = self,),
        }
        self.outputs = {
         "xForm Out"       : NodeSocket(from_socket = "xForm Out", from_node = self),
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
        }
        self.links = {} # leave this empty for now!
        # now set up the traverse target...
        self.inputs["Relationship"].set_traverse_target(self.outputs["xForm Out"])
        self.outputs["xForm Out"].set_traverse_target(self.inputs["Relationship"])
        self.node_type = 'XFORM'
        
    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)
    
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
        from bpy.types import EditBone
        parent_nc = get_parent(self)
        parent = parent_nc.bGetObject(mode = 'EDIT')
        if isinstance(parent, EditBone):
            print (parent.name)
            eb.parent = parent
        else:
            print(parent)
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
        matrix[3][3] = 1.0 # set this bacc, could cause problems otherwise.
        
        if (xF):
            if (xF.mode != "EDIT"):
                raise RuntimeError("Armature Object Not in Edit Mode, exiting...")
        else:
            raise RuntimeError("No armature object to add bone to.")
        #
        # Create the Object
        d = xF.data
        eb = d.edit_bones.new(name)
        
        if (eb.name != name):
            raise RuntimeError("Could not create bone ", name, "; Perhaps there is a duplicate bone name in the node tree?")
        eb.matrix  = matrix.copy()
        tailoffset = Vector((0,length,0)) #Vector((0,self.tailoffset, 0))
        tailoffset = matrix.copy().to_3x3() @ tailoffset
        eb.tail    = eb.head + tailoffset
        
        if (eb.name != name):
            raise RuntimeError("Could not create edit bone: ", name)
        self.bObject = eb.name
        # The bone should have relationships going in at this point.
        
        
            
        self.bSetParent(eb)
        
        
        return
        self.bParent(bContext)

        print ("Created Bone: \""+ eb.name+ "\" in \"" + self.bGetParentArmature().name +"\"")
        self.executed = True

    def bFinalize(self, bContext = None):
        # prevAct = bContext.view_layer.objects.active
        # bContext.view_layer.objects.active = ob
        # bpy.ops.object.mode_set(mode='OBJECT')
        # bContext.view_layer.objects.active = prevAct
        #
        #get relationship
        # ensure we have a pose bone...
        # set the ik parameters
        pass


    def bGetObject(self, mode = 'POSE'):
        if (mode == 'EDIT'):
            try:
                return self.bGetParentArmature().data.edit_bones[self.bObject]
            except KeyError:
                return None
        if (mode == 'OBJECT'):
            try:
                return self.bGetParentArmature().data.bones[self.bObject]
            except KeyError:
                return None
        if (mode == 'POSE'):
            try:
                return self.bGetParentArmature().pose.bones[self.bObject]
            except KeyError:
                return None
    
        
        

#*#-------------------------------#++#-------------------------------#*#
# L I N K   N O D E S
#*#-------------------------------#++#-------------------------------#*#

class LinkInherit:
    '''A node representing inheritance'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
         "Parent"           : NodeSocket(is_input = True, to_socket = "Parent", to_node = self,),
         # bone only:
         "Inherit Rotation" : NodeSocket(is_input = True, to_socket = "Inherit Rotation", to_node = self,),
         "Inherit Scale"    : NodeSocket(is_input = True, to_socket = "Inherit Scale", to_node = self,),
         "Connected"        : NodeSocket(is_input = True, to_socket = "Connected", to_node = self,),
        }
        self.outputs = { "Inheritance" : NodeSocket(from_socket = "Inheritance", from_node = self) }
        self.parameters = {
         "Parent":None,
         # bone only:
         "Inherit Rotation":None,
         "Inherit Scale":None,
         "Connected":None,
         "Mute":None,
        }
        self.links = {} # leave this empty for now!
        # now set up the traverse target...
        self.inputs["Parent"].set_traverse_target(self.outputs["Inheritance"])
        self.outputs["Inheritance"].set_traverse_target(self.inputs["Parent"])
        self.node_type = 'LINK'
    
        
    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)
    
    def bExecute(self, bContext = None,):
        # this is handled by the xForm objects, since it isn't really
        #  a constraint.
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)


class LinkCopyLocation:
    '''A node representing Copy Location'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, to_socket = "Input Relationship", to_node = self,),
            "Head/Tail"          : NodeSocket(is_input = True, to_socket = "Head/Tail", to_node = self,),
            "UseBBone"           : NodeSocket(is_input = True, to_socket = "UseBBone", to_node = self,),
            "Axes"               : NodeSocket(is_input = True, to_socket = "Axes", to_node = self,),
            "Invert"             : NodeSocket(is_input = True, to_socket = "Invert", to_node = self,),
            "Target Space"       : NodeSocket(is_input = True, to_socket = "Target Space", to_node = self,),
            "Owner Space"        : NodeSocket(is_input = True, to_socket = "Owner Space", to_node = self,),
            "Influence"          : NodeSocket(is_input = True, to_socket = "Influence", to_node = self,),
            "Target"             : NodeSocket(is_input = True, to_socket = "Target", to_node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(from_socket = "Output Relationship", from_node=self) }
        self.parameters = {
            "Input Relationship":None,
            "Head/Tail":None,
            "UseBBone":None,
            "Axes":None,
            "Invert":None,
            "Target Space":None,
            "Owner Space":None,
            "Influence":None,
            "Target":None,
            "Mute":None, }
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        
        
        
    def evaluate_input(self, input_name):
        if (input_name == 'Target'):            
            socket = self.inputs.get(input_name)
            return socket.from_node
            
        else:
            return evaluate_input(self, input_name)
    
    
    
    def GetxForm(self):
        # I don't think I have a function for getting children yet!
        trace = trace_single_line_up(self, "Output Relationship")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node
        return None



    def bExecute(self, context):
        
        c = self.GetxForm().bGetObject().constraints.new('COPY_LOCATION')
        get_target_and_subtarget(self, c)
        c.head_tail = self.evaluate_input("Head/Tail")
        c.use_bbone_shape = self.evaluate_input("UseBBone")

        c.owner_space = self.evaluate_input("Owner Space")
        c.target_space = self.evaluate_input("Target Space")
        c.invert_x = self.evaluate_input("Invert")[0]
        c.invert_y = self.evaluate_input("Invert")[1]
        c.invert_z = self.evaluate_input("Invert")[2]
        
        c.use_x = self.evaluate_input("Axes")[0]
        c.use_y = self.evaluate_input("Axes")[1]
        c.use_z = self.evaluate_input("Axes")[2]
        c.influence = self.evaluate_input("Influence")
        print ("Creating Copy Location Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        
        if self.parameters["Mute"]:
            c.enabled = False

    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)
        

class LinkCopyRotation:
    '''A node representing Copy Rotation'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, to_socket = "Input Relationship", to_node = self,),
            "RotationOrder"      : NodeSocket(is_input = True, to_socket = "RotationOrder", to_node = self,),
            "Rotation Mix"       : NodeSocket(is_input = True, to_socket = "Rotation Mix", to_node = self,),
            "Axes"               : NodeSocket(is_input = True, to_socket = "Axes", to_node = self,),
            "Invert"             : NodeSocket(is_input = True, to_socket = "Invert", to_node = self,),
            "Target Space"       : NodeSocket(is_input = True, to_socket = "Target Space", to_node = self,),
            "Owner Space"        : NodeSocket(is_input = True, to_socket = "Owner Space", to_node = self,),
            "Influence"          : NodeSocket(is_input = True, to_socket = "Influence", to_node = self,),
            "Target"             : NodeSocket(is_input = True, to_socket = "Target", to_node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(from_socket = "Output Relationship", from_node=self) }
        self.parameters = {
            "Input Relationship":None,
            "RotationOrder":None,
            "Rotation Mix":None,
            "Axes":None,
            "Invert":None,
            "Target Space":None,
            "Owner Space":None,
            "Influence":None,
            "Target":None,
            "Mute":None, }
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        
    def evaluate_input(self, input_name):
        if (input_name == 'Target'):            
            socket = self.inputs.get(input_name)
            return socket.from_node
            
        else:
            return evaluate_input(self, input_name)
    
    def GetxForm(self):
        # I don't think I have a function for getting children yet!
        trace = trace_single_line_up(self, "Output Relationship")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node
        return None

    def bExecute(self, context):
        
        c = self.GetxForm().bGetObject().constraints.new('COPY_ROTATION')
        
        get_target_and_subtarget(self, c)
        
        rotation_order = self.evaluate_input("RotationOrder")
        
        
        if ((rotation_order == 'QUATERNION') or (rotation_order == 'AXIS_ANGLE')):
            c.euler_order = 'AUTO'
        else:
            c.euler_order = rotation_order
        
        #c.mix_mode = self.evaluate_input("Rotation Mix")
        # kek, deal with this later
        # TODO HACK
        # dumb enums

        c.owner_space = self.evaluate_input("Owner Space")
        c.target_space = self.evaluate_input("Target Space")
        c.invert_x = self.evaluate_input("Invert")[0]
        c.invert_y = self.evaluate_input("Invert")[1]
        c.invert_z = self.evaluate_input("Invert")[2]
        
        c.use_x = self.evaluate_input("Axes")[0]
        c.use_y = self.evaluate_input("Axes")[1]
        c.use_z = self.evaluate_input("Axes")[2]
        c.influence = self.evaluate_input("Influence")
        print ("Creating Copy Rotation Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        
        if self.parameters["Mute"]:
            c.enabled = False

    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)
        
class LinkCopyScale:
    '''A node representing Copy Scale'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, to_socket = "Input Relationship", to_node = self,),
            "Offset"             : NodeSocket(is_input = True, to_socket = "Offset", to_node = self,),
            "Average"            : NodeSocket(is_input = True, to_socket = "Average", to_node = self,),
            "Additive"           : NodeSocket(is_input = True, to_socket = "Additive", to_node = self,),
            "Axes"               : NodeSocket(is_input = True, to_socket = "Axes", to_node = self,),
            #"Invert"             : NodeSocket(is_input = True, to_socket = "Invert", to_node = self,),
            "Target Space"       : NodeSocket(is_input = True, to_socket = "Target Space", to_node = self,),
            "Owner Space"        : NodeSocket(is_input = True, to_socket = "Owner Space", to_node = self,),
            "Influence"          : NodeSocket(is_input = True, to_socket = "Influence", to_node = self,),
            "Target"             : NodeSocket(is_input = True, to_socket = "Target", to_node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(from_socket = "Output Relationship", from_node=self) }
        self.parameters = {
            "Input Relationship":None,
            "Offset":None,
            "Average":None,
            "Axes":None,
            #"Invert":None,
            "Target Space":None,
            "Owner Space":None,
            "Influence":None,
            "Target":None,
            "Mute":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        
    def evaluate_input(self, input_name):
        if (input_name == 'Target'):            
            socket = self.inputs.get(input_name)
            return socket.from_node
            
        else:
            return evaluate_input(self, input_name)
    
    def GetxForm(self):
        trace = trace_single_line_up(self, "Output Relationship")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node
        return None

    def bExecute(self, context):
        
        c = self.GetxForm().bGetObject().constraints.new('COPY_SCALE')
        
        get_target_and_subtarget(self, c)
        
        c.use_offset       = self.evaluate_input("Offset")
        c.use_make_uniform = self.evaluate_input("Average")

        c.owner_space = self.evaluate_input("Owner Space")
        c.target_space = self.evaluate_input("Target Space")
        c.use_x = self.evaluate_input("Axes")[0]
        c.use_y = self.evaluate_input("Axes")[1]
        c.use_z = self.evaluate_input("Axes")[2]
        c.influence = self.evaluate_input("Influence")
        print ("Creating Copy Location Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        
        if self.parameters["Mute"]:
            c.enabled = False

    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

class LinkCopyTransforms:
    '''A node representing Copy Transfoms'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, to_socket = "Input Relationship", to_node = self,),
            "Head/Tail"          : NodeSocket(is_input = True, to_socket = "Head/Tail", to_node = self,),
            "UseBBone"           : NodeSocket(is_input = True, to_socket = "UseBBone", to_node = self,),
            "Additive"           : NodeSocket(is_input = True, to_socket = "Additive", to_node = self,),
            "Mix"                : NodeSocket(is_input = True, to_socket = "Mix", to_node = self,),
            "Target Space"       : NodeSocket(is_input = True, to_socket = "Target Space", to_node = self,),
            "Owner Space"        : NodeSocket(is_input = True, to_socket = "Owner Space", to_node = self,),
            "Influence"          : NodeSocket(is_input = True, to_socket = "Influence", to_node = self,),
            "Target"             : NodeSocket(is_input = True, to_socket = "Target", to_node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(from_socket = "Output Relationship", from_node=self) }
        self.parameters = {
            "Input Relationship":None,
            "Head/Tail":None,
            "UseBBone":None,
            "Mix":None,
            "Target Space":None,
            "Owner Space":None,
            "Influence":None,
            "Target":None,
            "Mute":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        
    def evaluate_input(self, input_name):
        if (input_name == 'Target'):            
            socket = self.inputs.get(input_name)
            return socket.from_node
            
        else:
            return evaluate_input(self, input_name)
    
    def GetxForm(self):
        trace = trace_single_line_up(self, "Output Relationship")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node
        return None

    def bExecute(self, context):
        
        c = self.GetxForm().bGetObject().constraints.new('COPY_TRANSFORMS')
        
        get_target_and_subtarget(self, c)
        
        c.head_tail       = self.evaluate_input("Head/Tail")
        c.use_bbone_shape = self.evaluate_input("UseBBone")
        c.mix_mode = self.evaluate_input("Mix")

        c.owner_space = self.evaluate_input("Owner Space")
        c.target_space = self.evaluate_input("Target Space")
        c.influence = self.evaluate_input("Influence")
        print ("Creating Copy Transforms Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        
        if self.parameters["Mute"]:
            c.enabled = False

    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

class LinkLimitLocation:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, to_socket = "Input Relationship", to_node = self,),
            "Use Max X"          : NodeSocket(is_input = True, to_socket = "Use Max X", to_node = self,),
            "Max X"              : NodeSocket(is_input = True, to_socket = "Max X", to_node = self,),
            "Use Max Y"          : NodeSocket(is_input = True, to_socket = "Use Max Y", to_node = self,),
            "Max Y"              : NodeSocket(is_input = True, to_socket = "Max Y", to_node = self,),
            "Use Max Z"          : NodeSocket(is_input = True, to_socket = "Use Max Z", to_node = self,),
            "Max Z"              : NodeSocket(is_input = True, to_socket = "Max Z", to_node = self,),
            "Use Min X"          : NodeSocket(is_input = True, to_socket = "Use Min X", to_node = self,),
            "Min X"              : NodeSocket(is_input = True, to_socket = "Min X", to_node = self,),
            "Use Min Y"          : NodeSocket(is_input = True, to_socket = "Use Min Y", to_node = self,),
            "Min Y"              : NodeSocket(is_input = True, to_socket = "Min Y", to_node = self,),
            "Use Min Z"          : NodeSocket(is_input = True, to_socket = "Use Min Z", to_node = self,),
            "Min Z"              : NodeSocket(is_input = True, to_socket = "Min Z", to_node = self,),
            "Affect Transform"   : NodeSocket(is_input = True, to_socket = "Affect Transform", to_node = self,),
            "Owner Space"        : NodeSocket(is_input = True, to_socket = "Owner Space", to_node = self,),
            "Influence"          : NodeSocket(is_input = True, to_socket = "Influence", to_node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(from_socket = "Output Relationship", from_node=self) }
        self.parameters = {
            "Input Relationship":None,
            "Use Max X":None,
            "Max X":None,
            "Use Max Y":None,
            "Max Y":None,
            "Use Max Z":None,
            "Max Z":None,
            "Use Min X":None,
            "Min X":None,
            "Use Min Y":None,
            "Min Y":None,
            "Use Min Z":None,
            "Min Z":None,
            "Affect Transform":None,
            "Owner Space":None,
            "Influence":None,
            "Mute":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        
    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)
    
    def GetxForm(self):
        trace = trace_single_line_up(self, "Output Relationship")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node
        return None

    def bExecute(self, context):
        c = self.GetxForm().bGetObject().constraints.new('LIMIT_LOCATION')
        #
        c.max_x       = self.evaluate_input("Max X")
        c.max_y       = self.evaluate_input("Max Y")
        c.max_z       = self.evaluate_input("Max Z")
        #
        c.min_x       = self.evaluate_input("Min X")
        c.min_y       = self.evaluate_input("Min Y")
        c.min_z       = self.evaluate_input("Min Z")
        
        c.use_max_x       = self.evaluate_input("Use Max X")
        c.use_max_y       = self.evaluate_input("Use Max Y")
        c.use_max_z       = self.evaluate_input("Use Max Z")
        #
        c.use_min_x       = self.evaluate_input("Use Min X")
        c.use_min_y       = self.evaluate_input("Use Min Y")
        c.use_min_z       = self.evaluate_input("Use Min Z")
        
        c.use_transform_limit = self.evaluate_input("Affect Transform")

        c.owner_space = self.evaluate_input("Owner Space")
        c.influence = self.evaluate_input("Influence")
        print ("Creating Limit Location Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        
        if self.parameters["Mute"]:
            c.enabled = False
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)
        
class LinkLimitRotation:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, to_socket = "Input Relationship", to_node = self,),
            "Use X"              : NodeSocket(is_input = True, to_socket = "Use X", to_node = self,),
            "Use Y"              : NodeSocket(is_input = True, to_socket = "Use Y", to_node = self,),
            "Use Z"              : NodeSocket(is_input = True, to_socket = "Use Z", to_node = self,),
            "Max X"              : NodeSocket(is_input = True, to_socket = "Max X", to_node = self,),
            "Max Y"              : NodeSocket(is_input = True, to_socket = "Max Y", to_node = self,),
            "Max Z"              : NodeSocket(is_input = True, to_socket = "Max Z", to_node = self,),
            "Min X"              : NodeSocket(is_input = True, to_socket = "Min X", to_node = self,),
            "Min Y"              : NodeSocket(is_input = True, to_socket = "Min Y", to_node = self,),
            "Min Z"              : NodeSocket(is_input = True, to_socket = "Min Z", to_node = self,),
            "Affect Transform"   : NodeSocket(is_input = True, to_socket = "Affect Transform", to_node = self,),
            "Owner Space"        : NodeSocket(is_input = True, to_socket = "Owner Space", to_node = self,),
            "Influence"          : NodeSocket(is_input = True, to_socket = "Influence", to_node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(from_socket = "Output Relationship", from_node=self) }
        self.parameters = {
            "Input Relationship":None,
            "Use X":None,
            "Use Y":None,
            "Use Z":None,
            "Max X":None,
            "Max Y":None,
            "Max Z":None,
            "Min X":None,
            "Min Y":None,
            "Min Z":None,
            "Affect Transform":None,
            "Owner Space":None,
            "Influence":None,
            "Mute":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        
    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)
    
    def GetxForm(self):
        trace = trace_single_line_up(self, "Output Relationship")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node
        return None

    def bExecute(self, context):
        c = self.GetxForm().bGetObject().constraints.new('LIMIT_ROTATION')
        #
        c.max_x       = self.evaluate_input("Max X")
        c.max_y       = self.evaluate_input("Max Y")
        c.max_z       = self.evaluate_input("Max Z")
        #
        c.min_x       = self.evaluate_input("Min X")
        c.min_y       = self.evaluate_input("Min Y")
        c.min_z       = self.evaluate_input("Min Z")
        #
        c.use_limit_x       = self.evaluate_input("Use X")
        c.use_limit_y       = self.evaluate_input("Use Y")
        c.use_limit_z       = self.evaluate_input("Use Z")
        #
        c.use_transform_limit = self.evaluate_input("Affect Transform")
        #
        c.owner_space = self.evaluate_input("Owner Space")
        c.influence = self.evaluate_input("Influence")
        print ("Creating Limit Rotation Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        
        if self.parameters["Mute"]:
            c.enabled = False
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)
        
class LinkLimitScale:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, to_socket = "Input Relationship", to_node = self,),
            "Use Max X"          : NodeSocket(is_input = True, to_socket = "Use Max X", to_node = self,),
            "Max X"              : NodeSocket(is_input = True, to_socket = "Max X", to_node = self,),
            "Use Max Y"          : NodeSocket(is_input = True, to_socket = "Use Max Y", to_node = self,),
            "Max Y"              : NodeSocket(is_input = True, to_socket = "Max Y", to_node = self,),
            "Use Max Z"          : NodeSocket(is_input = True, to_socket = "Use Max Z", to_node = self,),
            "Max Z"              : NodeSocket(is_input = True, to_socket = "Max Z", to_node = self,),
            "Use Min X"          : NodeSocket(is_input = True, to_socket = "Use Min X", to_node = self,),
            "Min X"              : NodeSocket(is_input = True, to_socket = "Min X", to_node = self,),
            "Use Min Y"          : NodeSocket(is_input = True, to_socket = "Use Min Y", to_node = self,),
            "Min Y"              : NodeSocket(is_input = True, to_socket = "Min Y", to_node = self,),
            "Use Min Z"          : NodeSocket(is_input = True, to_socket = "Use Min Z", to_node = self,),
            "Min Z"              : NodeSocket(is_input = True, to_socket = "Min Z", to_node = self,),
            "Affect Transform"   : NodeSocket(is_input = True, to_socket = "Affect Transform", to_node = self,),
            "Owner Space"        : NodeSocket(is_input = True, to_socket = "Owner Space", to_node = self,),
            "Influence"          : NodeSocket(is_input = True, to_socket = "Influence", to_node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(from_socket = "Output Relationship", from_node=self) }
        self.parameters = {
            "Input Relationship":None,
            "Use Max X":None,
            "Max X":None,
            "Use Max Y":None,
            "Max Y":None,
            "Use Max Z":None,
            "Max Z":None,
            "Use Min X":None,
            "Min X":None,
            "Use Min Y":None,
            "Min Y":None,
            "Use Min Z":None,
            "Min Z":None,
            "Affect Transform":None,
            "Owner Space":None,
            "Influence":None,
            "Mute":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        
    def evaluate_input(self, input_name):
        return evaluate_input(self, input_name)
    
    def GetxForm(self):
        trace = trace_single_line_up(self, "Output Relationship")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node
        return None

    def bExecute(self, context):
        c = self.GetxForm().bGetObject().constraints.new('LIMIT_SCALE')
        #
        c.max_x       = self.evaluate_input("Max X")
        c.max_y       = self.evaluate_input("Max Y")
        c.max_z       = self.evaluate_input("Max Z")
        #
        c.min_x       = self.evaluate_input("Min X")
        c.min_y       = self.evaluate_input("Min Y")
        c.min_z       = self.evaluate_input("Min Z")
        
        c.use_max_x       = self.evaluate_input("Use Max X")
        c.use_max_y       = self.evaluate_input("Use Max Y")
        c.use_max_z       = self.evaluate_input("Use Max Z")
        #
        c.use_min_x       = self.evaluate_input("Use Min X")
        c.use_min_y       = self.evaluate_input("Use Min Y")
        c.use_min_z       = self.evaluate_input("Use Min Z")
        
        c.use_transform_limit = self.evaluate_input("Affect Transform")

        c.owner_space = self.evaluate_input("Owner Space")
        c.influence = self.evaluate_input("Influence")
        print ("Creating Limit Scale Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        
        if self.parameters["Mute"]:
            c.enabled = False
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)
        
class LinkLimitDistance:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, to_socket = "Input Relationship", to_node = self,),
            "Head/Tail"          : NodeSocket(is_input = True, to_socket = "Head/Tail", to_node = self,),
            "UseBBone"           : NodeSocket(is_input = True, to_socket = "UseBBone", to_node = self,),
            "Distance"           : NodeSocket(is_input = True, to_socket = "Distance", to_node = self,),
            "Clamp Region"       : NodeSocket(is_input = True, to_socket = "Clamp Region", to_node = self,),
            "Affect Transform"   : NodeSocket(is_input = True, to_socket = "Affect Transform", to_node = self,),
            "Owner Space"        : NodeSocket(is_input = True, to_socket = "Owner Space", to_node = self,),
            "Target Space"       : NodeSocket(is_input = True, to_socket = "Target Space", to_node = self,),
            "Influence"          : NodeSocket(is_input = True, to_socket = "Influence", to_node = self,),
            "Target"             : NodeSocket(is_input = True, to_socket = "Target", to_node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(from_socket = "Output Relationship", from_node=self) }
        self.parameters = {
            "Input Relationship":None,
            "Head/Tail":None,
            "UseBBone":None,
            "Distance":None,
            "Clamp Region":None,
            "Affect Transform":None,
            "Owner Space":None,
            "Target Space":None,
            "Influence":None,
            "Target":None,
            "Mute":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        
    def evaluate_input(self, input_name):
        if (input_name == 'Target'):            
            socket = self.inputs.get(input_name)
            return socket.from_node
            
        else:
            return evaluate_input(self, input_name)

    def GetxForm(self):
        trace = trace_single_line_up(self, "Output Relationship")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node
        return None

    def bExecute(self, context):
        
        c = self.GetxForm().bGetObject().constraints.new('LIMIT_DISTANCE')
        
        get_target_and_subtarget(self, c)
        #
        c.distance            = self.evaluate_input("Distance")
        c.head_tail           = self.evaluate_input("Head/Tail")
        c.limit_mode          = self.evaluate_input("Clamp Region")
        c.use_bbone_shape     = self.evaluate_input("UseBBone")
        c.use_transform_limit = self.evaluate_input("Affect Transform")
        c.owner_space         = self.evaluate_input("Owner Space")
        c.target_space        = self.evaluate_input("Target Space")
        c.influence           = self.evaluate_input("Influence")
        print ("Creating Limit Distance Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        
        if self.parameters["Mute"]:
            c.enabled = False
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

# Tracking

class LinkStretchTo:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, to_socket = "Input Relationship", to_node = self,),
            "Head/Tail"          : NodeSocket(is_input = True, to_socket = "Head/Tail", to_node = self,),
            "UseBBone"           : NodeSocket(is_input = True, to_socket = "UseBBone", to_node = self,),
            "Original Length"    : NodeSocket(is_input = True, to_socket = "Original Length", to_node = self,),
            "Volume Variation"   : NodeSocket(is_input = True, to_socket = "Volume Variation", to_node = self,),
            "Use Volume Min"     : NodeSocket(is_input = True, to_socket = "Use Volume Min", to_node = self,),
            "Volume Min"         : NodeSocket(is_input = True, to_socket = "Volume Min", to_node = self,),
            "Use Volume Max"     : NodeSocket(is_input = True, to_socket = "Use Volume Max", to_node = self,),
            "Volume Max"         : NodeSocket(is_input = True, to_socket = "Volume Max", to_node = self,),
            "Smooth"             : NodeSocket(is_input = True, to_socket = "Smooth", to_node = self,),
            "Maintain Volume"    : NodeSocket(is_input = True, to_socket = "Maintain Volume", to_node = self,),
            "Rotation"           : NodeSocket(is_input = True, to_socket = "Rotation", to_node = self,),
            "Influence"          : NodeSocket(is_input = True, to_socket = "Influence", to_node = self,),
            "Target"             : NodeSocket(is_input = True, to_socket = "Target", to_node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(from_socket = "Output Relationship", from_node=self) }
        self.parameters = {
            "Input Relationship":None,
            "Head/Tail":None,
            "UseBBone":None,
            "Original Length":None,
            "Volume Variation":None,
            "Use Volume Min":None,
            "Volume Min":None,
            "Use Volume Max":None,
            "Volume Max":None,
            "Smooth":None,
            "Maintain Volume":None,
            "Rotation":None,
            "Influence":None,
            "Target":None,
            "Mute":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        
    def evaluate_input(self, input_name):
        if (input_name == 'Target'):            
            socket = self.inputs.get(input_name)
            return socket.from_node
            
        else:
            return evaluate_input(self, input_name)

    def GetxForm(self):
        trace = trace_single_line_up(self, "Output Relationship")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node
        return None

    def bExecute(self, context):
        
        c = self.GetxForm().bGetObject().constraints.new('STRETCH_TO')
        
        get_target_and_subtarget(self, c)
        
        c.head_tail       = self.evaluate_input("Head/Tail")
        c.use_bbone_shape = self.evaluate_input("UseBBone")
        c.bulge           = self.evaluate_input("Volume Variation")
        c.use_bulge_min   = self.evaluate_input("Use Volume Min")
        c.bulge_min       = self.evaluate_input("Volume Min")
        c.use_bulge_max   = self.evaluate_input("Use Volume Max")
        c.bulge_max       = self.evaluate_input("Volume Max")
        c.bulge_smooth    = self.evaluate_input("Smooth")
        c.keep_axis       = self.evaluate_input("Rotation")
        c.volume          = self.evaluate_input("Maintain Volume")
        c.rest_length     = self.evaluate_input("Original Length")
        c.influence       = self.evaluate_input("Influence")
        
        if (c.rest_length == 0):
            # this is meant to be set automatically.
            c.rest_length = self.GetxForm().bGetObject().bone.length
        

        print ("Creating Stretch-To Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        
        if self.parameters["Mute"]:
            c.enabled = False
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

class LinkDampedTrack:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, to_socket = "Input Relationship", to_node = self,),
            "Head/Tail"          : NodeSocket(is_input = True, to_socket = "Head/Tail", to_node = self,),
            "UseBBone"           : NodeSocket(is_input = True, to_socket = "UseBBone", to_node = self,),
            "Track Axis"         : NodeSocket(is_input = True, to_socket = "Track Axis", to_node = self,),
            "Influence"          : NodeSocket(is_input = True, to_socket = "Influence", to_node = self,),
            "Target"             : NodeSocket(is_input = True, to_socket = "Target", to_node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(from_socket = "Output Relationship", from_node=self) }
        self.parameters = {
            "Input Relationship":None,
            "Head/Tail":None,
            "UseBBone":None,
            "Track Axis":None,
            "Influence":None,
            "Target":None,
            "Mute":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        
    def evaluate_input(self, input_name):
        if (input_name == 'Target'):            
            socket = self.inputs.get(input_name)
            return socket.from_node
            
        else:
            return evaluate_input(self, input_name)

    def GetxForm(self):
        trace = trace_single_line_up(self, "Output Relationship")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node
        return None

    def bExecute(self, context):
        
        c = self.GetxForm().bGetObject().constraints.new('DAMPED_TRACK')
        
        get_target_and_subtarget(self, c)
        
        c.head_tail       = self.evaluate_input("Head/Tail")
        c.use_bbone_shape = self.evaluate_input("UseBBone")
        c.track_axis      = self.evaluate_input("Track Axis")
        c.influence       = self.evaluate_input("Influence")

        print ("Creating Damped-Track Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        
        if self.parameters["Mute"]:
            c.enabled = False
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

class LinkLockedTrack:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, to_socket = "Input Relationship", to_node = self,),
            "Head/Tail"          : NodeSocket(is_input = True, to_socket = "Head/Tail", to_node = self,),
            "UseBBone"           : NodeSocket(is_input = True, to_socket = "UseBBone", to_node = self,),
            "Track Axis"         : NodeSocket(is_input = True, to_socket = "Track Axis", to_node = self,),
            "Lock Axis"          : NodeSocket(is_input = True, to_socket = "Lock Axis", to_node = self,),
            "Influence"          : NodeSocket(is_input = True, to_socket = "Influence", to_node = self,),
            "Target"             : NodeSocket(is_input = True, to_socket = "Target", to_node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(from_socket = "Output Relationship", from_node=self) }
        self.parameters = {
            "Input Relationship":None,
            "Head/Tail":None,
            "UseBBone":None,
            "Track Axis":None,
            "Lock Axis":None,
            "Influence":None,
            "Target":None,
            "Mute":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        
    def evaluate_input(self, input_name):
        if (input_name == 'Target'):            
            socket = self.inputs.get(input_name)
            return socket.from_node
            
        else:
            return evaluate_input(self, input_name)

    def GetxForm(self):
        trace = trace_single_line_up(self, "Output Relationship")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node
        return None

    def bExecute(self, context):
        
        c = self.GetxForm().bGetObject().constraints.new('LOCKED_TRACK')
        
        get_target_and_subtarget(self, c)
        
        c.head_tail       = self.evaluate_input("Head/Tail")
        c.use_bbone_shape = self.evaluate_input("UseBBone")
        c.track_axis      = self.evaluate_input("Track Axis")
        c.lock_axis       = self.evaluate_input("Lock Axis")
        c.influence       = self.evaluate_input("Influence")

        print ("Creating Locked-Track Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        
        if self.parameters["Mute"]:
            c.enabled = False
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

class LinkTrackTo:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, to_socket = "Input Relationship", to_node = self,),
            "Head/Tail"          : NodeSocket(is_input = True, to_socket = "Head/Tail", to_node = self,),
            "UseBBone"           : NodeSocket(is_input = True, to_socket = "UseBBone", to_node = self,),
            "Track Axis"         : NodeSocket(is_input = True, to_socket = "Track Axis", to_node = self,),
            "Up Axis"            : NodeSocket(is_input = True, to_socket = "Up Axis", to_node = self,),
            "Use Target Z"       : NodeSocket(is_input = True, to_socket = "Use Target Z", to_node = self,),
            "Influence"          : NodeSocket(is_input = True, to_socket = "Influence", to_node = self,),
            "Target"             : NodeSocket(is_input = True, to_socket = "Target", to_node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(from_socket = "Output Relationship", from_node=self) }
        self.parameters = {
            "Input Relationship":None,
            "Head/Tail":None,
            "UseBBone":None,
            "Track Axis":None,
            "Up Axis":None,
            "Use Target Z":None, 
            "Influence":None,
            "Target":None,
            "Mute":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        
    def evaluate_input(self, input_name):
        if (input_name == 'Target'):            
            socket = self.inputs.get(input_name)
            return socket.from_node
            
        else:
            return evaluate_input(self, input_name)

    def GetxForm(self):
        trace = trace_single_line_up(self, "Output Relationship")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node
        return None

    def bExecute(self, context):
        
        c = self.GetxForm().bGetObject().constraints.new('TRACK_TO')
        
        get_target_and_subtarget(self, c)
        
        c.head_tail       = self.evaluate_input("Head/Tail")
        c.use_bbone_shape = self.evaluate_input("UseBBone")
        c.track_axis      = self.evaluate_input("Track Axis")
        c.up_axis         = self.evaluate_input("Up Axis")
        c.use_target_z    = self.evaluate_input("Use Target Z")
        c.influence       = self.evaluate_input("Influence")

        print ("Creating Track-To Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        
        if self.parameters["Mute"]:
            c.enabled = False
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

# relationships & misc.

class LinkInheritConstraint:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            "Input Relationship" : NodeSocket(is_input = True, to_socket = "Input Relationship", to_node = self,),
            "Location"           : NodeSocket(is_input = True, to_socket = "Location", to_node = self,),
            "Rotation"           : NodeSocket(is_input = True, to_socket = "Rotation", to_node = self,),
            "Scale"              : NodeSocket(is_input = True, to_socket = "Scale", to_node = self,),
            "Influence"          : NodeSocket(is_input = True, to_socket = "Influence", to_node = self,),
            "Target"             : NodeSocket(is_input = True, to_socket = "Target", to_node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(from_socket = "Output Relationship", from_node=self) }
        self.parameters = {
            "Input Relationship":None,
            "Location":None,
            "Rotation":None,
            "Scale":None,
            "Influence":None,
            "Target":None,
            "Mute":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        
    def evaluate_input(self, input_name):
        if (input_name == 'Target'):            
            socket = self.inputs.get(input_name)
            return socket.from_node
            
        else:
            return evaluate_input(self, input_name)

    def GetxForm(self):
        trace = trace_single_line_up(self, "Output Relationship")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node
        return None

    def bExecute(self, context):
        
        c = self.GetxForm().bGetObject().constraints.new('CHILD_OF')
        
        get_target_and_subtarget(self, c)
        
        c.use_location_x = self.evaluate_input("Location")[0]
        c.use_location_y = self.evaluate_input("Location")[1]
        c.use_location_z = self.evaluate_input("Location")[2]
        c.use_rotation_x = self.evaluate_input("Rotation")[0]
        c.use_rotation_y = self.evaluate_input("Rotation")[1]
        c.use_rotation_z = self.evaluate_input("Rotation")[2]
        c.use_scale_x    = self.evaluate_input("Scale")[0]
        c.use_scale_y    = self.evaluate_input("Scale")[1]
        c.use_scale_z    = self.evaluate_input("Scale")[2]
        c.influence      = self.evaluate_input("Influence")
        c.set_inverse_pending


        print ("Creating Child-of Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        
        if self.parameters["Mute"]:
            c.enabled = False
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

# Inverse Kinematics:

#
# r = self.inputs.new('BooleanSocket', "Inherit Rotation")
# c = self.inputs.new('BooleanSocket', "Connected")
# s = self.inputs.new('EnumInheritScale', "Inherit Scale")
# self.inputs.new ('xFormSocket', "Target")
# self.inputs.new ('xFormSocket', "Pole Target")
# self.inputs.new ('IKChainLengthSocket', "Chain Length")
# self.inputs.new ('BooleanSocket', "Use Tail")
# self.inputs.new ('BooleanSocket', "Stretch")
# self.inputs.new ('FloatFactorSocket', "Position")
# self.inputs.new ('FloatFactorSocket', "Rotation")
# self.inputs.new ('FloatFactorSocket', "Influence")
# self.outputs.new('RelationshipSocket', "Inheritance")
# self.inputs.new('xFormSocket', "Parent")
#

# Ugghh, this one is a little weird
# I treat IK as a kind of inheritance
#  that is mutually exclusive with other inheritance
#  since Blender and other softwares treat it specially, anyway
#  e.g. in Blender it's always treated as the last constraint
# While it may be annoying to have it always appear first in each bones'
#  stack, because this does not affect behaviour, I do not really care.
class LinkInverseKinematics:
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.inputs = {
            # Inheritance bits
            "Input Relationship"  : NodeSocket(is_input = True, to_socket = "Input Relationship", to_node = self,),
            "Inherit Rotation"    : NodeSocket(is_input = True, to_socket = "Inherit Rotation", to_node = self,),
            "Inherit Scale"       : NodeSocket(is_input = True, to_socket = "Inherit Scale", to_node = self,),
            "Connected"           : NodeSocket(is_input = True, to_socket = "Connected", to_node = self,),
            # Constraint stuff
            "Chain Length"        : NodeSocket(is_input = True, to_socket = "Chain Length", to_node = self,),
            "Use Tail"            : NodeSocket(is_input = True, to_socket = "Use Tail", to_node = self,),
            "Stretch"             : NodeSocket(is_input = True, to_socket = "Stretch", to_node = self,),
            "Position"            : NodeSocket(is_input = True, to_socket = "Position", to_node = self,),
            "Rotation"            : NodeSocket(is_input = True, to_socket = "Rotation", to_node = self,),
            "Influence"           : NodeSocket(is_input = True, to_socket = "Influence", to_node = self,),
            "Target"              : NodeSocket(is_input = True, to_socket = "Target", to_node = self,),
            "Pole Target"         : NodeSocket(is_input = True, to_socket = "Pole Target", to_node = self,), }
        self.outputs = {
            "Output Relationship" : NodeSocket(from_socket = "Output Relationship", from_node=self) }
        self.parameters = {
            "Input Relationship":None,
            "Inherit Rotation":None,
            "Inherit Scale":None,
            "Connected":None,
            "Chain Length":None,
            "Use Tail":None,
            "Stretch":None,
            "Position":None,
            "Rotation":None,
            "Influence":None,
            "Target":None, 
            "Pole Target":None,
            "Mute":None,}
        # now set up the traverse target...
        self.inputs["Input Relationship"].set_traverse_target(self.outputs["Output Relationship"])
        self.outputs["Output Relationship"].set_traverse_target(self.inputs["Input Relationship"])
        self.node_type = 'LINK'
        
    def evaluate_input(self, input_name):
        if (input_name == 'Target') or (input_name == 'Pole Target'):
            socket = self.inputs.get(input_name)
            return socket.from_node
        else:
            return evaluate_input(self, input_name)

    def GetxForm(self):
        trace = trace_single_line_up(self, "Output Relationship")
        for node in trace[0]:
            if (node.__class__ in [xFormRoot, xFormArmature, xFormBone]):
                return node
        return None

    def bExecute(self, context):
        # do not handle any inheritance stuff here, that is dealt with
        #  by the xForm nodes instead!
        myOb = self.GetxForm().bGetObject()
        c = self.GetxForm().bGetObject().constraints.new('IK')
        
        get_target_and_subtarget(self, c)
        get_target_and_subtarget(self, c, input_name = 'Pole Target')
        
        
        if (c.pole_target): # Calculate the pole angle, the user shouldn't have to.
            pole_object = c.pole_target
            pole_location = pole_object.matrix_world.decompose()[0]
            if (c.pole_subtarget):
                pole_object = c.pole_target.pose.bones[c.subtarget]
                pole_location = pole_object.matrix.decompose()[0]
            #HACK HACK
            handle_location = myOb.bone.tail_local if (self.evaluate_input("Use Tail")) else myOb.bone.head_local
            counter = 0
            parent = myOb
            base_bone = myOb
            while (parent is not None):
                if ((self.evaluate_input("Chain Length") != 0) and (counter > self.evaluate_input("Chain Length"))):
                    break
                base_bone = parent
                parent = parent.parent
                counter+=1
            head_location = base_bone.bone.head_local

            pole_normal = (handle_location - head_location).cross(pole_location - head_location)
            vector_u = myOb.bone.x_axis
            vector_v = pole_normal.cross(base_bone.bone.y_axis)
            angle = vector_u.angle(vector_v)
            if (vector_u.cross(vector_v).angle(base_bone.bone.y_axis) < 1):
                angle = -angle
            
            c.pole_angle = angle
        
        c.chain_count    = self.evaluate_input("Chain Length")
        c.use_tail       = self.evaluate_input("Use Tail")
        c.use_stretch    = self.evaluate_input("Stretch")
        c.weight         = self.evaluate_input("Position")
        c.orient_weight  = self.evaluate_input("Rotation")
        c.influence      = self.evaluate_input("Influence")
        # this should be sufficient, I think use_location and use_rotation
        #  are meaningless if the weight is 0, anyway.
        # Well, the minimum weight is 0.01, so we have to get the input again.
        c.use_location   = self.evaluate_input("Position") > 0 
        c.use_rotation   = self.evaluate_input("Rotation") > 0
        # this is a little annoying because the constraint can have a
        #  positive value for position/rotation without it being enabled.
        print ("Creating IK Constraint for bone: \""+ self.GetxForm().bGetObject().name + "\"")
        
        if self.parameters["Mute"]:
            c.enabled = False
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)




#*#-------------------------------#++#-------------------------------#*#
# G E N E R I C   N O D E S
#*#-------------------------------#++#-------------------------------#*#


# in reality, none of these inputs have names
#  so I am using the socket name for now
#  I suppose I could use any name :3
class InputFloat:
    '''A node representing float input'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.outputs = {"Float Input" : NodeSocket(from_socket = "Float Input", from_node=self) }
        self.parameters = {"Float Input":None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["Float Input"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)
    
class InputVector:
    '''A node representing vector input'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.outputs = {"VectorSocket" : NodeSocket(from_socket = 'VectorSocket', from_node=self) }
        self.parameters = {'VectorSocket':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["VectorSocket"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

class InputBoolean:
    '''A node representing boolean input'''
    
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.outputs = {"BooleanSocket" : NodeSocket(from_socket = 'BooleanSocket', from_node=self) }
        self.parameters = {'BooleanSocket':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["BooleanSocket"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

class InputBooleanThreeTuple:
    '''A node representing inheritance'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.outputs = {"BooleanThreeTupleSocket" : NodeSocket(from_socket = 'BooleanThreeTupleSocket', from_node=self) }
        self.parameters = {'BooleanThreeTupleSocket':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["BooleanThreeTupleSocket"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

class InputRotationOrder:
    '''A node representing string input for rotation order'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.outputs = {"RotationOrderSocket" : NodeSocket(from_socket = 'RotationOrderSocket', from_node=self) }
        self.parameters = {'RotationOrderSocket':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["RotationOrderSocket"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

class InputTransformSpace:
    '''A node representing string input for transform space'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.outputs = {"TransformSpaceSocket" : NodeSocket(from_socket = 'TransformSpaceSocket', from_node=self) }
        self.parameters = {'TransformSpaceSocket':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["TransformSpaceSocket"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

class InputString:
    '''A node representing string input'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.outputs = {"StringSocket" : NodeSocket(from_socket = 'StringSocket', from_node=self) }
        self.parameters = {'StringSocket':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["StringSocket"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

class InputQuaternion:
    '''A node representing quaternion input'''
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.outputs = {"QuaternionSocket" : NodeSocket(from_socket = 'QuaternionSocket', from_node=self) }
        self.parameters = {'QuaternionSocket':None, "Mute":None}
        self.node_type = 'UTILITY'
        
        
    def evaluate_input(self, input_name):
        return self.parameters["QuaternionSocket"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)

class InputQuaternionAA:
    '''A node representing axis-angle quaternion input'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.outputs  = {"QuaternionSocketAA" : NodeSocket(from_socket = 'QuaternionSocketAA', from_node=self) }
        self.parameters = {'QuaternionSocketAA':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["QuaternionSocketAA"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        fill_parameters(self, node_prototype)


class InputMatrix:
    '''A node representing axis-angle quaternion input'''
        
    def __init__(self, signature, base_tree):
        self.base_tree=base_tree
        self.signature = signature
        self.outputs  = {"Matrix" : NodeSocket(from_socket = 'Matrix', from_node=self) }
        self.parameters = {'Matrix':None, "Mute":None}
        self.node_type = 'UTILITY'
        
    def evaluate_input(self, input_name):
        return self.parameters["Matrix"]
    
    def bExecute(self, bContext = None,):
        pass
    
    def __repr__(self):
        return self.signature.__repr__()
        
    def fill_parameters(self, node_prototype):
        # this node is peculiar for how its data is input
        # It uses node properties that are not addressable as sockets.
        from mathutils import Matrix
        
        matrix = ( node_prototype.first_row[ 0], node_prototype.first_row[ 1], node_prototype.first_row[ 2], node_prototype.first_row[ 3],
                   node_prototype.second_row[0], node_prototype.second_row[1], node_prototype.second_row[2], node_prototype.second_row[3],
                   node_prototype.third_row[ 0], node_prototype.third_row[ 1], node_prototype.third_row[ 2], node_prototype.third_row[ 3],
                   node_prototype.fourth_row[0], node_prototype.fourth_row[1], node_prototype.fourth_row[2], node_prototype.fourth_row[3], )
        self.parameters["Matrix"] = Matrix([matrix[0:4], matrix[4:8], matrix[8:12], matrix[12:16]])
        print (self.parameters["Matrix"])
        

# # NOT YET IMPLEMENTED:
# class InputMatrixNode(Node, MantisNode):
    # '''A node representing matrix input'''
    # inputs = 
    # # the node is implemented as a set of sixteen float inputs
    # # but I think I can boil it down to one matrix input


# class ScaleBoneLengthNode(Node, MantisNode):
    # '''Scale Bone Length'''
    # pass


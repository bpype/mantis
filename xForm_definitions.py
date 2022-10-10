import bpy
from .base_definitions import xFormNode
from bpy.types import Node
from mantis.utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)
from .base_definitions import get_signature_from_edited_tree, get_is_name_unique


def TellClasses():
    return [
        # xFormNullNode,
        xFormBoneNode,
        xFormRootNode,
        xFormArmatureNode,
        xFormGeometryObjectNode,
        ]

def default_traverse(self, socket):
    if (socket == self.outputs["xForm Out"]):
        return self.inputs["Relationship"]
    if (socket == self.inputs["Relationship"]):
        return self.outputs["xForm Out"]
    return None

# Representing an Empty or non-armature-Object
# class xFormNullNode(Node, xFormNode):
#     '''A node representing a Null node'''
#     bl_idname = 'xFormNullNode'
#     bl_label = "Null"
#     bl_icon = 'EMPTY_AXIS'

#     # === Optional Functions ===
#     def init(self, context):
#         self.inputs.new('StringSocket', "Name")
#         self.inputs.new('RelationshipSocket', "Relationship")
#         self.inputs.new('RotationOrderSocket', "Rotation Order")
#         self.inputs.new('MatrixSocket', "Matrix")
#         self.outputs.new('xFormSocket', "xForm Out")


def check_if_connected(start, end, line):
    started=False
    for path_nc in line:
        prWhite("    ", path_nc.signature)
        if path_nc.signature == start.signature:
            started = True
        elif path_nc.signature == end.signature:
            break
        if started:
            if path_nc.inputs.get("Connected"):
                if path_nc.evaluate_input("Connected") == False:
                    return False
    else:
        return False
    return True

class xFormRootNode(Node, xFormNode):
    '''A node representing the world node'''
    bl_idname = 'xFormRootNode'
    bl_label = "World Root"
    bl_icon = 'WORLD'

    def init(self, context):
        self.outputs.new('RelationshipSocket', "World Out")
        
class xFormBoneNode(Node, xFormNode):
    '''A node representing a Bone'''
    bl_idname = 'xFormBoneNode'
    bl_label = "Bone"
    bl_icon = 'BONE_DATA'
    
    display_ik_settings : bpy.props.BoolProperty(default=False)
    display_vp_settings : bpy.props.BoolProperty(default=False)
    display_def_settings : bpy.props.BoolProperty(default=False)
    socket_count : bpy.props.IntProperty() # not needed anymore, right?
    
    error : bpy.props.BoolProperty(default=False)
    error_msg : bpy.props.StringProperty(default="")
    error_icon : bpy.props.StringProperty(default="NONE")
    
    def init(self, context):
        
        context = bpy.context
        if context.space_data:
            node_tree = context.space_data.path[0].node_tree
            from mantis import readtree
            prOrange("Updating from xFormBone init callback")
            node_tree.update_tree(context)
        
        self.inputs.new('StringSocket', "Name")
        self.inputs.new('RotationOrderSocket', "Rotation Order")
        self.inputs.new('RelationshipSocket', "Relationship")
        self.inputs.new('MatrixSocket', "Matrix")

        # IK SETTINGS
        a = []
        # a.append(self.inputs.new ('LabelSocket', "IK Settings"))
        a.append(self.inputs.new ('FloatFactorSocket', "IK Stretch"))
        a.append(self.inputs.new ('BooleanThreeTupleSocket', "Lock IK"))
        a.append(self.inputs.new ('NodeSocketVector', "IK Stiffness"))
        a.append(self.inputs.new ('BooleanThreeTupleSocket', "Limit IK"))
        a.append(self.inputs.new ('NodeSocketFloatAngle', "X Min"))
        a.append(self.inputs.new ('NodeSocketFloatAngle', "X Max"))
        a.append(self.inputs.new ('NodeSocketFloatAngle', "Y Min"))
        a.append(self.inputs.new ('NodeSocketFloatAngle', "Y Max"))
        a.append(self.inputs.new ('NodeSocketFloatAngle', "Z Min"))
        a.append(self.inputs.new ('NodeSocketFloatAngle', "Z Max"))
        #4-14
        
        # visual settings:
        b = []
        b.append(self.inputs.new ('LayerMaskSocket', "Layer Mask"))
        b.append(self.inputs.new ('xFormSocket', "Custom Object"))
        b.append(self.inputs.new ('xFormSocket', "Custom Object xForm Override"))
        b.append(self.inputs.new ('BooleanSocket', "Custom Object Scale to Bone Length"))
        b.append(self.inputs.new ('BooleanSocket', "Custom Object Wireframe"))
        b.append(self.inputs.new ('VectorScaleSocket', "Custom Object Scale"))
        b.append(self.inputs.new ('VectorSocket', "Custom Object Translation"))
        b.append(self.inputs.new ('VectorEulerSocket', "Custom Object Rotation"))
        b.append(self.inputs.new ('StringSocket', "Bone Group"))
        # 16-22
        # Deform Settings:
        c = []
        c.append(self.inputs.new ('BooleanSocket', "Deform"))
        c.append(self.inputs.new ('FloatPositiveSocket', "Envelope Distance"))
        c.append(self.inputs.new ('FloatFactorSocket',   "Envelope Weight"))
        c.append(self.inputs.new ('BooleanSocket', "Envelope Multiply"))
        c.append(self.inputs.new ('FloatPositiveSocket', "Envelope Head Radius"))
        c.append(self.inputs.new ('FloatPositiveSocket', "Envelope Tail Radius"))
        #24-28
        
        # c[0].default_value=False
        
        # Hide should be last
        b.append(self.inputs.new ('HideSocket',   "Hide"))
    
        
        for sock in a:
            sock.hide = True
        for sock in b:
            if sock.name in ['Custom Object', 'Layer Mask']:
                continue
            sock.hide = True
        for sock in c:
            if sock.name == 'Deform':
                continue
            sock.hide = True
            
        # Thinking about using colors for nodes, why not?
        # cxForm          = (0.443137, 0.242157, 0.188235,) #could even fetch the theme colors...
        # self.color=cxForm
        # self.use_custom_color=True
        self.socket_count = len(self.inputs)
        #
        self.outputs.new('xFormSocket', "xForm Out")
    
    def draw_buttons(self, context, layout):
        layout.label(text=self.error_msg, icon = self.error_icon)
        layout.operator("mantis.add_custom_property", text='+Add Custom Parameter')
        # layout.label(text="Edit Parameter ... not implemented")
        if (len(self.inputs) > self.socket_count):
            layout.operator("mantis.remove_custom_property", text='-Remove Custom Parameter')
        else:
            layout.label(text="")
    
    # def draw_label(self):
        # if not self.error:
            # return self.label
        # else:
            # return self.error_msg
        
    def display_update(self, parsed_tree, context):
        errors = []
        self.error_msg = ""
        self.error_icon = "NONE"
        self.error=False
        
        if context.space_data:
            node_tree = context.space_data.path[0].node_tree
            nc = parsed_tree.get(get_signature_from_edited_tree(self, context))
            other_nc = None
            if len(self.inputs.get("Relationship").links)>0:
                prev_node = self.inputs.get("Relationship").links[0].from_node
                if prev_node:
                    other_nc = parsed_tree.get(get_signature_from_edited_tree(prev_node, context))
            
            if nc and other_nc:
                self.display_vp_settings = nc.inputs["Custom Object"].is_connected
                self.display_def_settings = nc.evaluate_input("Deform")
                self.display_ik_settings = False
                #
                from .node_container_common import ( trace_all_lines_up,
                                                     trace_single_line)
                trace = trace_all_lines_up(nc, "xForm Out")
                
                for key in trace.keys():
                    if (ik_nc:= parsed_tree.get(key)):
                        if ik_nc.__class__.__name__ in ["LinkInverseKinematics"]:
                            # if the tree is invalid? This shouldn't be necessary.
                            if ik_nc.inputs["Input Relationship"].is_connected:
                                chain_count = ik_nc.evaluate_input("Chain Length")
                                if chain_count == 0:
                                    self.display_ik_settings = True
                                else:
                                    if ik_nc.evaluate_input("Use Tail") == False:
                                        chain_count+=1
                                    for line in trace[key]:
                                        # preprocess it to get rid of non-xForms:
                                        xForm_line=[]
                                        for path_nc in line:
                                            if path_nc == ik_nc:
                                                if ik_nc.inputs["Input Relationship"].links[0].from_node != prev_path_nc:
                                                    break # not a constraint connection
                                            if path_nc.node_type == 'XFORM':
                                                xForm_line.append(path_nc)
                                            prev_path_nc = path_nc
                                            
                                        else:
                                            if len(xForm_line) < chain_count:
                                                self.display_ik_settings = True
                
                inp = nc.inputs["Relationship"]
                link = None
                if inp.is_connected:
                    link = inp.links[0]
                while(link):
                    if link.from_node.__class__.__name__ in ["LinkInverseKinematics"]:
                        self.display_ik_settings = link.from_node.evaluate_input("Use Tail")
                        break
                    inp = link.from_node.outputs[link.from_socket]
                    inp = inp.traverse_target
                    if not inp:
                        break
                    if inp.links:
                        link = inp.links[0]
                    else:
                        link = None
                if get_is_name_unique(nc, parsed_tree) == False:
                    errors.append("Bone name is not unique.")
                    self.error_icon = "ERROR"
                    self.color=(1.0,0.0,0.0)
                    self.error=True
            else:
                errors.append("Bone is not connected to the tree.")
                self.color=(0.7,0.35,0.0)
                self.error_icon = "CANCEL"
                self.error=True
            #
        if self.display_ik_settings == True:
            for inp in self.inputs[4:14]:
                inp.hide = False
        else:
            for inp in self.inputs[4:14]:
                inp.hide = True
        if self.display_vp_settings == True:
            for inp in self.inputs[16:22]:
                inp.hide = False
        else:
            for inp in self.inputs[16:22]:
                inp.hide = True
        #
        if self.display_def_settings == True:
            for inp in self.inputs[24:29]:
                inp.hide = False
        else:
            for inp in self.inputs[24:29]:
                inp.hide = True
                
        if self.error:
            print (errors)
            self.use_custom_color=True
            self.error_msg= " and ".join(errors)
        else:
            self.color=(0.3,0.3,0.3)
            self.use_custom_color=False
                
        

    # def copy(ectype, archtype):
        # tree = ectype.id_data.parsed_tree
        # n = get_unique_name(ectype.name, tree)
        # ectype.name = "boink!"
        
        # # TODO: automatically avoid duplicating names
        # ectype.inputs["Name"].default_value = ""


class xFormArmatureNode(Node, xFormNode):
    '''A node representing an Armature object node'''
    bl_idname = 'xFormArmatureNode'
    bl_label = "Armature"
    bl_icon = 'OUTLINER_OB_ARMATURE'

    def init(self, context):
        self.inputs.new('StringSocket', "Name")
        self.inputs.new('RelationshipSocket', "Relationship")
        self.inputs.new('RotationOrderSocket', "Rotation Order")
        self.inputs.new('MatrixSocket', "Matrix")
        self.outputs.new('xFormSocket', "xForm Out")


class xFormGeometryObjectNode(Node, xFormNode):
    """Represents a curve or mesh object."""
    bl_idname = "xFormGeometryObject"
    bl_label = "Geometry Object"
    bl_icon = "EMPTY_AXIS"
    
    def init(self, context):
        self.inputs.new('StringSocket', "Name")
        self.inputs.new('GeometrySocket', "Geometry")
        self.inputs.new('MatrixSocket', "Matrix")
        self.inputs.new('RelationshipSocket', "Relationship")
        self.outputs.new('xFormSocket', "xForm Out")

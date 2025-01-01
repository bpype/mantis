import bpy
from .base_definitions import SchemaNode
from bpy.types import Node
from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)
from bpy.props import BoolProperty

from .utilities import get_socket_maps, relink_socket_map, do_relink


def TellClasses():
    return [
        # tree i/o
        SchemaIndex,
        SchemaArrayInput,
        SchemaArrayInputGet,
        SchemaArrayOutput,
        SchemaConstInput,
        SchemaConstOutput,
        SchemaOutgoingConnection,
        SchemaIncomingConnection,
        # # iterators
        # SchemaIntMath,
        # SchemaDeclarationValidWhen,
        ]


# IMPORTANT TODO:
# - check what happens when these get plugged into each other
# - probably disallow all or most of these connections in insert_link or update

class SchemaIndex(Node, SchemaNode):
    '''The current index of the schema execution'''
    bl_idname = 'SchemaIndex'
    bl_label = "Index"
    bl_icon = 'GIZMO'
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.outputs.new("IntSocket", "Index")
        self.outputs.new("IntSocket", "Schema Length")
        self.initialized = True


class SchemaArrayInput(Node, SchemaNode):
    '''Array Inputs'''
    bl_idname = 'SchemaArrayInput'
    bl_label = "Array Input"
    bl_icon = 'GIZMO'
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.update()

    def update(self):
        # self.initialized = False
        output_map = get_socket_maps(self)[1]
        self.outputs.clear()
        for item in self.id_data.interface.items_tree:
            if item.item_type == 'PANEL': continue
            if item.parent and item.in_out == 'INPUT' and item.parent.name == 'Array':
                relink_socket_map(self, self.outputs, output_map, item, in_out='OUTPUT')
        if '__extend__' in output_map.keys() and output_map['__extend__']:
            do_relink(self, None, output_map, in_out='OUTPUT', parent_name='Array' )
        if len(self.inputs)<1 or self.inputs[-1].bl_idname not in ["WildcardSocket"]:
            self.outputs.new('WildcardSocket', '', identifier='__extend__')
        # self.initialized = True

class SchemaArrayInputGet(Node, SchemaNode):
    '''Array Inputs'''
    bl_idname = 'SchemaArrayInputGet'
    bl_label = "Array Input at Index"
    bl_icon = 'GIZMO'
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.inputs.new('EnumArrayGetOptions', 'OoB Behaviour')
        self.inputs.new("IntSocket", "Index")
        self.update()

    def update(self):
        # self.initialized = False
        output_map = get_socket_maps(self)[1]
        self.outputs.clear()
        for item in self.id_data.interface.items_tree:
            if item.item_type == 'PANEL': continue
            if item.parent and item.in_out == 'INPUT' and item.parent.name == 'Array':
                relink_socket_map(self, self.outputs, output_map, item, in_out='OUTPUT')
        if '__extend__' in output_map.keys() and output_map['__extend__']:
            do_relink(self, None, output_map, in_out='OUTPUT', parent_name='Array' )
        if len(self.inputs)<1 or self.inputs[-1].bl_idname not in ["WildcardSocket"]:
            self.outputs.new('WildcardSocket', '', identifier='__extend__')
        # self.initialized = True

class SchemaArrayOutput(Node, SchemaNode):
    '''Array Inputs'''
    bl_idname = 'SchemaArrayOutput'
    bl_label = "Array Output"
    bl_icon = 'GIZMO'
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.update()

    def update(self):
        self.initialized = False
        input_map = get_socket_maps(self)[0]
        self.inputs.clear()
        for item in self.id_data.interface.items_tree:
            if item.item_type == 'PANEL': continue
            if item.parent and item.in_out == 'OUTPUT' and item.parent.name == 'Array':
                relink_socket_map(self, self.inputs, input_map, item, in_out='INPUT')
        if '__extend__' in input_map.keys() and input_map['__extend__']:
            do_relink(self, None, input_map, in_out='INPUT', parent_name='Array' )
        if len(self.inputs)<1 or self.inputs[-1].bl_idname not in ["WildcardSocket"]:
            self.inputs.new('WildcardSocket', '', identifier='__extend__')
        for s in self.outputs:
            s.input= True
        self.initialized = True

class SchemaConstInput(Node, SchemaNode):
    '''Constant Inputs'''
    bl_idname = 'SchemaConstInput'
    bl_label = "Constant Input"
    bl_icon = 'GIZMO'
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.update()

    def update(self):
        self.initialized = False
        output_map = get_socket_maps(self)[1]
        self.outputs.clear()
        for item in self.id_data.interface.items_tree:
            if item.item_type == 'PANEL': continue
            if item.parent and item.in_out == 'INPUT' and item.parent.name == 'Constant':
                relink_socket_map(self, self.outputs, output_map, item, in_out='OUTPUT')
        if '__extend__' in output_map.keys() and output_map['__extend__']:
            do_relink(self, None, output_map, in_out='OUTPUT', parent_name='Constant' )
        if len(self.inputs)<1 or self.inputs[-1].bl_idname not in ["WildcardSocket"]:
            self.outputs.new('WildcardSocket', '', identifier='__extend__')
        self.initialized = True



class SchemaConstOutput(Node, SchemaNode):
    '''Constant Outputs'''
    bl_idname = 'SchemaConstOutput'
    bl_label = "Constant Output"
    bl_icon = 'GIZMO'
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.update()

    def update(self):
        self.initialized = False
        input_map = get_socket_maps(self)[0]
        self.inputs.clear()
        s = self.inputs.new('IntSocket', "Expose when N==")
        for item in self.id_data.interface.items_tree:
            if item.item_type == 'PANEL': continue
            if item.parent and item.in_out == 'OUTPUT' and item.parent.name == 'Constant':
                relink_socket_map(self, self.inputs, input_map, item, in_out='INPUT')
        if '__extend__' in input_map.keys() and input_map['__extend__']:
            do_relink(self, None, input_map, in_out='INPUT', parent_name='Constant' )
        if len(self.inputs)<1 or self.inputs[-1].bl_idname not in ["WildcardSocket"]:
            self.inputs.new('WildcardSocket', '', identifier='__extend__')
        do_relink(self, s, input_map, in_out='INPUT')
        for s in self.outputs:
            s.input= True
        
        self.initialized = True



class SchemaOutgoingConnection(Node, SchemaNode):
    '''Outgoing Connections'''
    bl_idname = 'SchemaOutgoingConnection'
    bl_label = "Outgoing Connection"
    bl_icon = 'GIZMO'
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        # self.inputs.new('IntSocket', 'Valid From')
        # self.inputs.new('IntSocket', 'Valid Until')
        self.update()

    def update(self):
        self.initialized = False
        input_map = get_socket_maps(self)[0]
        self.inputs.clear()
        for item in self.id_data.interface.items_tree:
            if item.item_type == 'PANEL': continue
            if item.parent and item.in_out == 'OUTPUT' and item.parent.name == 'Connection':
                relink_socket_map(self, self.inputs, input_map, item, in_out='INPUT')
        if '__extend__' in input_map.keys() and input_map['__extend__']:
            do_relink(self, None, input_map, in_out='INPUT', parent_name='Connection' )
        if len(self.inputs)<1 or self.inputs[-1].bl_idname not in ["WildcardSocket"]:
            self.inputs.new('WildcardSocket', '', identifier='__extend__')
        for s in self.outputs:
            s.input= True
        self.initialized = True



class SchemaIncomingConnection(Node, SchemaNode):
    '''Incoming Connections'''
    bl_idname = 'SchemaIncomingConnection'
    bl_label = "Incoming Connection"
    bl_icon = 'GIZMO'
    initialized : bpy.props.BoolProperty(default = False)

    def init(self, context):
        self.update()

    def update(self):
        self.initialized = False
        output_map = get_socket_maps(self)[1]
        self.outputs.clear()
        for item in self.id_data.interface.items_tree:
            if item.item_type == 'PANEL': continue
            if item.parent and item.in_out == 'INPUT' and item.parent.name == 'Connection':
                relink_socket_map(self, self.outputs, output_map, item, in_out='OUTPUT')
        if '__extend__' in output_map.keys() and output_map['__extend__']:
            do_relink(self, None, output_map, in_out='OUTPUT', parent_name='Connection' )
        if len(self.inputs)<1 or self.inputs[-1].bl_idname not in ["WildcardSocket"]:
            self.outputs.new('WildcardSocket', '', identifier='__extend__')
        self.initialized = True



# have a string for name
# assign/get
# and a fallback if none
# get should take an integer: 0 = index, -1 = index -1, etc., no positive ints allowed
# class SchemaLocalVariable(Node, SchemaNode):
#     '''Constant Inputs'''
#     bl_idname = 'SchemaIncomingConnection'
#     bl_label = "Incoming Connection"
#     bl_icon = 'GIZMO'
    
#     def init(self, context):
#         # self.outputs.new("IntSocket", "Index")
#         pass


# class SchemaIntMath(Node, SchemaNode):
#     '''Int Math'''
#     bl_idname = 'SchemaIntMath'
#     bl_label = "Int Math"
#     bl_icon = 'GIZMO'
    
#     # def init(self, context):
#     #     self.update()


# class SchemaDeclarationValidWhen(Node, SchemaNode):
#     '''Declaration Valid When'''
#     bl_idname = 'SchemaDeclarationValidWhen'
#     bl_label = "Declaration Valid When"
#     bl_icon = 'GIZMO'
    
#     def init(self, context):
#         self.inputs.new('IntSocket', 'Valid From')
#         self.inputs.new('IntSocket', 'Valid Until')
#         self.inputs.new('IntSocket', 'Add to N') # +
#         self.inputs.new('IntSocket', 'Multiply N') # *
#         self.inputs.new('IntSocket', 'Modulo of N') # %
#         # self.inputs.new('IntSocket', 'n')


# I need to figure out what to do with this right here...
# There are a few options:
#  - an actual control flow (if, then) -- but I don' like that because it's not declarative
#  - "declaration valid when" statement that is basically a range with simple math rules
#      - this is funcionally almost entirely the same
#      - perhaps this sort of range plugs into the end of the schema?
#      - but I want it to operate kind of like a frame or simulation zone
#  - Begin / End declaration makes it more like a framed region
#      - hypothetically I don't need to have any begin and I can just imply it
#      - I don't wanna have to develop a bunch of code for dealing with new links that are only there for the sake of schema
#  - then I ran into the problem that the in/out connections are relevant to a specific declaration
#  - what I need is a way to modify the declaration in the loop, not a way to construct a bunch of different iterators....
#  - so maybe I can get away with basic maths only

# so I need a way to control a declaration by the index
#   - a switch node, maybe one with an arbitrary socket type like wildcard that just adapts
#   - it should be possible to do math with the index and len(schema)
#       - example, for naming a bone 'Center' if index == len(schema)//2
#            - the "if" is what annoys me about this
#       - making numbers and chiral identifiers for names
#       - array gets
#   - 



# class SchemaChoose(Node, SchemaNode):
#     '''Choose'''
#     bl_idname = 'SchemaChoose'
#     bl_label = "Choose"
#     bl_icon = 'GIZMO'
#     initialized : bpy.props.BoolProperty(default = False)
    
#     def init(self, context):
#         self.inputs.new('IntSocket', 'Number of Choices')
#         self.inputs.new('IntSocket', 'Choose Index')
#         self.outputs.new('WildcardSocket', 'Choice')
#         self.update()

#     def update(self):
#         self.initialized = False
#         input_map = get_socket_maps(self)[0]
#         # print (input_map)
#         self.inputs.clear()
#         self.inputs.new('IntSocket', 'Number of Choices')
#         self.inputs.new('IntSocket', 'Choose Index')
#         #
#         # update on this one requires being able to read the tree!
#             # self.inputs.new("WildcardSocket", "")
#         self.initialized = True
import bpy
from .base_definitions import SchemaUINode
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
        ]


# IMPORTANT TODO:
# - check what happens when these get plugged into each other
# - probably disallow all or most of these connections in insert_link or update

class SchemaIndex(Node, SchemaUINode):
    '''The current index of the schema execution'''
    bl_idname = 'SchemaIndex'
    bl_label = "Index"
    bl_icon = 'GIZMO'
    initialized : bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        self.outputs.new("IntSocket", "Index")
        self.outputs.new("IntSocket", "Schema Length")
        self.initialized = True


class SchemaArrayInput(Node, SchemaUINode):
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

class SchemaArrayInputGet(Node, SchemaUINode):
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

class SchemaArrayOutput(Node, SchemaUINode):
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

class SchemaConstInput(Node, SchemaUINode):
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



class SchemaConstOutput(Node, SchemaUINode):
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



class SchemaOutgoingConnection(Node, SchemaUINode):
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



class SchemaIncomingConnection(Node, SchemaUINode):
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


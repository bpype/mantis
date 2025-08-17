from bpy.types import Panel, Menu

def TellClasses():
    return [
        MantisActiveTreePanel,
        MantisNodeGroupsMenu,
        MantisAddArmature,
    ]

# Function to append submenu to context menu
def node_context_menu_draw(self, context):
    layout = self.layout
    layout.separator()  # Optional: Adds a separator before your submenu
    layout.operator_context = "INVOKE_DEFAULT"
    layout.operator("mantis.nodes_cleanup", text='Sort Selected Nodes')
    layout.operator("mantis.connect_nodes_to_input")
    layout.operator("mantis.select_nodes_of_type")
    layout.operator("mantis.import_from_component_library")
    # layout.menu('NODE_MT_context_menu_mantis')

# Function to append submenu to node add menu
def node_add_menu_draw(self, context):
    layout = self.layout
    layout.separator()  # Optional: Adds a separator before your submenu
    layout.menu("NODE_MT_add_mantis_groups")

# Function to append Mantis Component Packs to armature add menu
def armature_add_menu_draw(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("VIEW3D_MT_armature_add_mantis_packs")

# Function to append Mantis to Import Menu
def import_menu_draw(self, context):
    self.layout.operator("mantis.import_tree")

class MantisNodeGroupsMenu(Menu):
    """Menu to show available node groups"""
    bl_idname= "NODE_MT_add_mantis_groups"
    bl_label = "Components"
    def draw(self, context):
        node_tree = None
        # just gonna do the same thing we do in poll operators
        if not context.space_data:
            return
        if not hasattr(context.space_data, "path"):
            return
        try:
            node_tree = context.space_data.path[0].node_tree
        except IndexError: # not in the UI, for example, in a script instead.
            return
        if node_tree is None: # because the space is right but there is no selected tree.
            return
        # now we're clear to do the menu function
        layout = self.layout
        from bpy import data
        for ng in data.node_groups:
            if ng.bl_idname in ['MantisTree', 'SchemaTree']:
                if ng.name == node_tree.name and ng.bl_idname == node_tree.bl_idname:
                    continue # don't add the node group into itself.
                if ng.contains_tree(node_tree):
                    continue # don't create an infinite loop of node trees
                operator_settings = layout.operator(
                    "mantis.add_component", text=ng.name,
                    icon='NODE', emboss=False,)
                operator_settings.node_group_tree_name=ng.name
                operator_settings.tree_invoked = node_tree.name

class MantisAddArmature(Menu):
    """Menu to show the user's component pack library in the Add Armature menu"""
    bl_idname= "VIEW3D_MT_armature_add_mantis_packs"
    bl_label = "Mantis Rigs"
    def draw(self, context):
        # start showing the mantis packs
        from .preferences import get_bl_addon_object
        bl_mantis_addon = get_bl_addon_object()
        if bl_mantis_addon:
            components_path = bl_mantis_addon.preferences.ComponentsLibraryFolder
            # now we're clear to do the menu function
            layout = self.layout
            from .utilities import get_component_library_items
            component_items = get_component_library_items()
            for component_item in component_items:
                # how to "EXEC_DEFAULT" here?
                operator_settings = layout.operator( operator="mantis.import_tree_no_menu", text=component_item[1])
                from os import path as os_path
                operator_settings.filepath = os_path.join(components_path, component_item[0])

class MantisActiveTreePanel(Panel):
    """N-Panel menu for Mantis"""
    bl_label = "Active Tree"
    bl_idname = "MANTIS_PT_active_tree"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Mantis"
    bl_context = "scene"
    
    @classmethod
    def poll(cls, context):
        area = context.area
        if not area: return False
        if not area.spaces: return False
        spc = area.spaces[0]
        if spc.type != "NODE_EDITOR":
            return False
        if not spc.node_tree:
            return False
        if spc.node_tree.bl_idname != "MantisTree":
            return False
        return True
    
    def draw(self, context):
        area = context.area
        spc = area.spaces[0]
        nt = spc.node_tree
        layout = self.layout
        layout.label(text=f"Tree Hash: {nt.hash}")
        layout.prop(nt, "do_live_update", text='Live Updates',)
        layout.operator("mantis.invalidate_node_tree")
        layout.operator("mantis.execute_node_tree")
        layout.operator("mantis.force_display_update", text='Force Display Update')
        layout.operator("mantis.import_from_component_library")

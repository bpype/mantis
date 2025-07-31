from bpy.types import Panel, Menu

def TellClasses():
    return [
        MantisActiveTreePanel,
    ]


# Function to append submenu to context menu
def node_context_menu_draw(self, context):
    layout = self.layout
    layout.separator()  # Optional: Adds a separator before your submenu
    layout.operator_context = "INVOKE_DEFAULT"
    layout.operator("mantis.nodes_cleanup", text='Sort Selected Nodes')
    layout.operator("mantis.connect_nodes_to_input")
    layout.operator("mantis.select_nodes_of_type")
    # layout.menu('NODE_MT_context_menu_mantis')

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

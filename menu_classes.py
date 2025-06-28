from bpy.types import Panel

def TellClasses():
    return [
        MantisActiveTreePanel,
    ]

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
        if spc.node_tree.bl_idname != "MantisTree":
            return False
        return True
    
    def draw(self, context):
        area = context.area
        spc = area.spaces[0]
        nt = spc.node_tree
        layout = self.layout
        layout.prop(nt, "do_live_update", text='Live Updates',)
        layout.operator("mantis.execute_node_tree")

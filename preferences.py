import bpy
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
#

class MantisPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # JSONprefix: bpy.props.StringProperty(
    #     name = "Prefix code file",
    #     subtype = 'FILE_PATH',
    #     default = dir_path + '/preferences/prefix.json',)
    # JSONchiral: bpy.props.StringProperty(
    #     name = "Chiral Identifier file",
    #     subtype = 'FILE_PATH',
    #     default = dir_path + '/preferences/chiral_identifier.json',)
    # JSONseperator:bpy.props.StringProperty(
    #     name = "Seperator file",
    #     subtype = 'FILE_PATH',
    #     default = dir_path + '/preferences/seperator.json',)
    WidgetsLibraryFolder:bpy.props.StringProperty(
        name = "Widget Library Folder",
        subtype = 'FILE_PATH',
        default = os.path.join(dir_path, 'widgets'),)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Mantis Preferences")
        layout.prop(self, "WidgetsLibraryFolder", icon='FILE_FOLDER')
import bpy
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
#

def get_bl_addon_object(raise_error = False):
    from bpy import context
    try_these_first = ['bl_ext.repos.mantis', 'bl_ext.blender_modules_enabled.mantis']
    for mantis_key in try_these_first:
        bl_mantis_addon = context.preferences.addons.get(mantis_key)
        if bl_mantis_addon: break
    if bl_mantis_addon is None:
        if raise_error==True:
            raise RuntimeError("Mantis Preferences not found. This is a bug."
                            " Please report it on gitlab.")
        if raise_error==False:
            print(  "Mantis Preferences not found. This is a bug."
                    " Please report it on gitlab.")
    return bl_mantis_addon

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
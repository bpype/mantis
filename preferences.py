import bpy
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
#

def get_bl_addon_object(raise_error = False):
    from bpy import context
    try_these_first = ['bl_ext.repos.mantis', 'bl_ext.blender_modules_enabled.mantis', 'bl_ext.nodes_tools.mantis']
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

# Just look and see if it is a ridiculous choice and show an error popup if the user needs
#    to select a different directory
def filepath_idiot_test(path):
    def do_error_popup():
            def error_popup_draw(self, context):
                self.layout.label(text="A maximum of 1000 widget files is allowed in the Widget Library.")
                self.layout.label(text="Make sure the WIdget Library does not scan a huge number of files/folders.")
            from bpy import context
            context.window_manager.popup_menu(error_popup_draw, title="Error", icon='ERROR')
    try:
        if tot_files := sum([len(files) for r, d, files in os.walk(path)]) > 1000:
            do_error_popup()
            return ''
        else:
            return path
    except FileNotFoundError:
        return ''
    except RecursionError:
        do_error_popup()
        return ''

def widget_library_get(self):
    return self.widget_library_path
def widget_library_idiot_test(self, value):
    self.widget_library_path = filepath_idiot_test(value)

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
    widget_library_path : bpy.props.StringProperty()
    WidgetsLibraryFolder:bpy.props.StringProperty(
        name = "Widget Library Folder",
        get=widget_library_get,
        set=widget_library_idiot_test,
        subtype = 'FILE_PATH',
        default = os.path.join(dir_path, 'widgets'),)
    WidgetDefaultCollection:bpy.props.StringProperty(
        name = "Import Widgets into Collection",
        default = "Widgets",)
    CurveDefaultCollection:bpy.props.StringProperty(
        name = "Import Curves into Collection",
        default = "MetaCurves",)
    MetaArmatureDefaultCollection:bpy.props.StringProperty(
        name = "Import Meta-Armatures into Collection",
        default = "MetaRigs",)
    ComponentsLibraryFolder:bpy.props.StringProperty(
        name = "Component Library Folder",
        description = "Location of .rig files to place in the Add Armature menu.",
        subtype = 'FILE_PATH',
        default = os.path.join(dir_path, 'component_packs'),)
    ComponentsAutoLoadFolder:bpy.props.StringProperty(
        name = "Component Autoload Folder",
        description = "Location of .rig files to load automatically.",
        subtype = 'FILE_PATH',
        default = os.path.join(dir_path, 'auto_load_components'),)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Mantis Preferences")
        layout.prop(self, "WidgetsLibraryFolder", icon='FILE_FOLDER')
        layout.prop(self, "WidgetDefaultCollection")
        layout.prop(self, "ComponentsLibraryFolder", icon='FILE_FOLDER')
        layout.prop(self, "CurveDefaultCollection")
        layout.prop(self, "MetaArmatureDefaultCollection")
        layout.prop(self, "ComponentsAutoLoadFolder", icon='FILE_FOLDER')
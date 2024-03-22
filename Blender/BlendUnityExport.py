bl_info = {
    "name": "Unity Export",
    "author": "Glen Pearce",
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar > Unity Export",
    "category": "Development"}


import bpy
import math
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )
#Properties for export location string
class MySettings(PropertyGroup):
    filepath: bpy.props.StringProperty(
        name="FilePath",
        subtype = 'DIR_PATH',
        description="Choose export location",
        default="",
        maxlen=1024,
    )


class PANEL_PT_Panel(bpy.types.Panel):
    """
    Layout of the panel
    """

    # where the panel gets added
    bl_space_type = "VIEW_3D"  # gets shown in 3d viewport
    bl_region_type = "UI"  # referencing sidebar region

    # Label names
    bl_category = "UnityExport"  # sidebar tab name
    bl_label = "Unity Export"  # in the add-on, top of panel name

    # Draw out buttons/layout, add more buttons and layout options here
    def draw(self, context):
        """define the layout of the panel"""
        layout  = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        mytool = scene.my_tool

        row = self.layout.row()
        row.label(text="Unity Export")
        row = self.layout.row()
        row.operator("form.unity_export", text="Unity Export")
        layout.prop(mytool, "filepath")


class FORM_OT_unity_export(bpy.types.Operator):
    """
    Export a model made in Blender, with the correct transforms to match Unity.
    """
    bl_idname = "form.unity_export"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Applies transform values to match Unity and exports "  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    def execute(self, context):  # execute() is called when running the operator.

        #store selected object and all children of object
        obj = bpy.context.active_object

            #allows use of file path string
        mytool = context.scene.my_tool

        # change the scale & rotation to match Unity and apply
        obj.scale = (100, 100, 100)
        obj.rotation_euler[0] = -1.5708

        # Apply transforms to root object
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        #select all child objects of root object
        for child_object in obj.children_recursive:
            child_object.select_set(True)


        child_objects = bpy.context.selected_objects
        bpy.context.view_layer.objects.active = None  # Unset active object

        #set child objects active and apply transforms
        for child in child_objects:
            bpy.context.view_layer.objects.active = child
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

            bpy.context.view_layer.objects.active = None

        bpy.context.view_layer.objects.active = obj

        #Import FBX, file path is chosen by clicking the file icon on the panel of the add-on
        bpy.ops.export_scene.fbx(filepath=mytool.filepath + obj.name + ".fbx", check_existing=True, filter_glob='*.fbx', use_selection=False,
                                 use_visible=False, use_active_collection=False, global_scale=0.01,
                                 apply_unit_scale=False, apply_scale_options='FBX_SCALE_ALL', use_space_transform=False,
                                 bake_space_transform=False,
                                 object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'},
                                 use_mesh_modifiers=True, use_mesh_modifiers_render=True, mesh_smooth_type='OFF',
                                 use_subsurf=False,
                                 use_mesh_edges=False, use_tspace=False, use_triangles=False, use_custom_props=False,
                                 add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X',
                                 use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=True,
                                 bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True,
                                 bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True,
                                 bake_anim_step=1.0, bake_anim_simplify_factor=1.0, path_mode='AUTO',
                                 embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True,
                                 axis_forward='-Z', axis_up='Y')

        # Set the Unity transform values
        obj.scale = (.01, .01, .01)
        obj.rotation_euler[0] = 1.5708

        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)



        return {'FINISHED'}

# to enable and disable the add-on, register classes here

classes = (
    FORM_OT_unity_export,
    MySettings,
    PANEL_PT_Panel,

)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.my_tool



# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()

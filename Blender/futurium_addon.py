bl_info = {
    "name": "Futurium Tools",
    "author": "Glen Pearce",
    "blender": (2, 80, 0),
    "location": "3D Viewport > Sidebar > Futurium Tools",
    "category": "Development"}


import bpy
import math

#class for panel UI layout/setup
class Futurium_Panel(bpy.types.Panel):
    pass
    # where the panel gets added
    bl_space_type = "VIEW_3D"  # gets shown in 3d viewport
    bl_region_type = "UI"  # referencing sidebar region

    # Label names
    bl_category = "Futurium Tools"  # sidebar tab name
    bl_label = "Futurium Tools"  # in the add-on, top of panel name

    # Draw out buttons/layout, add more buttons and layout options here
    def draw(self, context):
        """define the layout of the panel"""

        row = self.layout.row()
        row.operator("form.maya_export", text="Maya Export")

        self.layout.separator()

        row = self.layout.row()
        row.operator("mat.reset_maya_mats", text="Reset Maya Mats")


# Class for resetting materials effected when importing maya lambert materials
class MAT_OT_reset_maya_mats(bpy.types.Operator):
    bl_idname = "mat.reset_maya_mats"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Reset Mats effected by Maya Import"  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    def execute(self, context):  # execute() is called when running the operator.

        # Takes Maya imports and sets to Opaque to prevent models looking inside out + sets metallic and specular to 0 as it looks like a white mat in maya
        print("materialReset")
        for mat in bpy.data.materials:
            mat.blend_method = 'OPAQUE'
            if not mat.use_nodes:
                mat.metallic = 0
                continue
            for n in mat.node_tree.nodes:
                if n.type == 'BSDF_PRINCIPLED':
                    n.inputs["Metallic"].default_value = 0
                    n.inputs["Specular"].default_value = 0

        return {'FINISHED'}  # Lets Blender know the operator finished successfully


# Class for setting the transforms to be like Maya on the selected object
class FORM_OT_maya_export(bpy.types.Operator):
    bl_idname = "form.maya_export"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Applies transform values to match Maya and exports "  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    def execute(self, context):  # execute() is called when running the operator.

        #store selected object and all children of object
        obj = bpy.context.active_object


        # change the scale & rotation to match Maya and apply
        obj.scale = (100, 100, 100)
        obj.rotation_euler[0] = -1.5708

        # Apply transforms to root object
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        #select all child objects of root object with exceptions
        for child_object in obj.children_recursive:
            if 'FakeInternals' in child_object.name or 'Curtain'  in child_object.name or 'Blinds'  in child_object.name:
                child_object.hide_set(True)
            else:
                child_object.select_set(True)
        child_objects = bpy.context.selected_objects
        bpy.context.view_layer.objects.active = None  # Unset active object

        #set child objects active and apply transforms
        for child in child_objects:
            bpy.context.view_layer.objects.active = child
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            print(child.name + "Applied")
            print("Transforms Applied: " + str(bpy.context.view_layer.objects.active))
            if child.name == 'BackDoorNode':
                child.rotation_euler[2] = math.radians(180)
            bpy.context.view_layer.objects.active = None

        bpy.context.view_layer.objects.active = obj

        #!!!!insert file path name here!!!! use double \ like the example "F:\\3DWork\\Futurium\\HouseFixing\\"
        #name of the file is the name of the root mesh
        #bpy.ops.export_scene.fbx(filepath= , use_selection=False, global_scale= 0.01 ,apply_scale_options= 'FBX_SCALE_ALL', use_metadata=True, check_existing=True, use_space_transform=False, use_visible=False, use_active_collection=True)
        bpy.ops.export_scene.fbx(filepath="F:\\3DWork\\Futurium\\HouseFixing\\" + obj.name + ".fbx", check_existing=True, filter_glob='*.fbx', use_selection=False,
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
        # figure out how to keep rotations and scales, probably store values then reset and add them back on?

        # Reset the maya transforms put on the objects
        obj.scale = (.01, .01, .01)
        obj.rotation_euler[0] = 1.5708

        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)



        return {'FINISHED'}


# to enable and disable the add-on, register classes here

def register():
    bpy.utils.register_class(MAT_OT_reset_maya_mats)
    bpy.utils.register_class(FORM_OT_maya_export)
    bpy.utils.register_class(Futurium_Panel)


def unregister():
    bpy.utils.unregister_class(MAT_OT_reset_maya_mats)
    bpy.utils.unregister_class(FORM_OT_maya_export)
    bpy.utils.unregister_class(Futurium_Panel)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()

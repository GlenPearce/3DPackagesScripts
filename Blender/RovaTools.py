bl_info = {
        "name": "Rova Tools",
        "description": "Tools used to make Rova easier.",
        "author": "Glen Pearce",
        "version": (1, 0),
        "blender": (4, 0, 0),
        "location": "3D Viewport > Sidebar > RovaTools",
        "warning": "", # used for warning icon and text in add-ons panel
        "category": "Development"
        }

import bpy
import random


class PANEL_PT_Panel(bpy.types.Panel):
    """
    Layout of the panel
    """

    # where the panel gets added
    bl_space_type = "VIEW_3D"  # gets shown in 3d viewport
    bl_region_type = "UI"  # referencing sidebar region

    # Label names
    bl_category = "RovaTools"  # sidebar tab name
    bl_label = "RovaTools"  # in the add-on, top of panel name

    # Draw out buttons/layout, add more buttons and layout options here
    def draw(self, context):
        """define the layout of the panel"""
        layout  = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = self.layout.row()
        row.label(text="Select faces in edit mode, then choose a colour below")
        row = self.layout.row()
        row.label(text="Vertex Painting Colours")
        row = self.layout.row()

        #Add new colours in here
        row.operator("form.paint_face", text="Red").color = (1,0,0,1)
        row.operator("form.paint_face", text="Blue").color = (0,0,1,1)
        row = self.layout.row()
        row.operator("form.paint_face", text="Green").color = (0,1,0,1)
        row.operator("form.paint_face", text="Yellow").color = (1,1,0,1)
        row = self.layout.row()
        row.operator("form.paint_face", text="Cyan").color = (0,1,1,1)
        row.operator("form.paint_face", text="Purple").color = (1,0,1,1)
        row.operator("form.paint_face", text="Orange").color = (1,0.5,0,1)



class MAT_OT_Paint(bpy.types.Operator):

    """
    Select faces on an object and quickly paint them, from a choice of colours
    """


    bl_idname = "form.paint_face"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Applies selected colour to selected faces "  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    color: bpy.props.FloatVectorProperty(size=4)

    def execute(self, context):  # execute() is called when running the operator.

        VertColDataName = "VertColour"

        #Checks for edit mode, single object, selection mode and that only 1 vertex data is available.
        if bpy.context.active_object.mode != 'EDIT':
            self.report({'INFO'}, "Need an to be in edit mode.")
            return {'CANCELLED'}

        if not bpy.context.tool_settings.mesh_select_mode[2]:
            self.report({'INFO'}, "Need an to be in face selection mode.")
            return {'CANCELLED'}

        if len(bpy.context.selected_objects) != 1:
            self.report({'INFO'}, "Select One Object.")
            return {'CANCELLED'}
    
        mesh = bpy.context.active_object.data

        #create new layer if not one available
        if not mesh.vertex_colors:
            vert_col = mesh.vertex_colors.new(name = VertColDataName)
            self.report({'INFO'}, "No Vertex Color data found, made new one.")
        
        #set the first color attribute as active, prevents creating an empty one when switching to vertex paint
        mesh.attributes.active_color_index = 0

        #set mode to vertex paint ready to paint face
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        
        #take selected face, paint each vert in face selection
        selected_faces = [face for face in mesh.polygons if face.select]
        for face in selected_faces:
            for loop_index in face.loop_indices:
                # Set the color for each vertex of the face
                mesh.vertex_colors.active.data[loop_index].color = self.color

        bpy.ops.object.mode_set(mode='EDIT')


        return {'FINISHED'}


class FORM_OT_unity_export(bpy.types.Operator):
    """
    Export a house made in Blender, with the correct transforms to match Unity. Excludes children of empties that should contain assets already with these transforms.
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

        # Apply rotation and scale transforms to root object
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        #select all child objects of root object with exceptions
        #hides children of exluded names for empties, to keep their transforms
        #ignores empties and applies transforms to empties unless they are called disc (lighting locations)
        for child_object in obj.children_recursive:
            for childchild_object in child_object.children_recursive:
                if childchild_object.type == 'MESH' or 'Disc' in childchild_object.name:
                    childchild_object.hide_set(True)
                else:
                    childchild_object.select_set(True)

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
                bpy.context.active_object.rotation_euler = (0, 0, math.radians(180))

            if 'Tag' in child_object.name and child_object.type != 'EMPTY':
                        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

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

classes = (
    PANEL_PT_Panel,
    MAT_OT_Paint
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)



def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == '__main__':
    register()
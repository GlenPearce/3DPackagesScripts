import bpy
import os


class PANEL_PT_Panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "RovaTools"
    bl_label = "RovaTools"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = self.layout.row()
        row.operator("form.resource_import", text="Import Rova Resources")
        row = self.layout.row()
        row.label(text="Import first ^^^ just the once :)")
        row = self.layout.row()
        row.operator("form.add_geo_node_modifier", text="Add ColourByAngle Modifier")
        row = self.layout.row()
        row.label(text="Select faces in edit mode, then choose a colour below")
        row = self.layout.row()
        row.label(text="Vertex Painting Colours")
        row = self.layout.row()
        row.operator("form.paint_face", text="Red").color = (1, 0, 0, 1)
        row.operator("form.paint_face", text="Blue").color = (0, 0, 1, 1)
        row = self.layout.row()
        row.operator("form.paint_face", text="Green").color = (0, 1, 0, 1)
        row.operator("form.paint_face", text="Yellow").color = (1, 1, 0, 1)
        row = self.layout.row()
        row.operator("form.paint_face", text="Cyan").color = (0, 1, 1, 1)
        row.operator("form.paint_face", text="Purple").color = (1, 0, 1, 1)
        row.operator("form.paint_face", text="Orange").color = (1, 0.5, 0, 1)


class MAT_OT_Paint(bpy.types.Operator):
    bl_idname = "form.paint_face"
    bl_label = "Applies selected colour to selected faces "
    bl_options = {'REGISTER', 'UNDO'}

    color: bpy.props.FloatVectorProperty(size=4)

    def execute(self, context):
        VertColDataName = "VertColour"

        if bpy.context.active_object.mode != 'EDIT':
            self.report({'INFO'}, "Need to be in edit mode.")
            return {'CANCELLED'}

        if not bpy.context.tool_settings.mesh_select_mode[2]:
            self.report({'INFO'}, "Need to be in face selection mode.")
            return {'CANCELLED'}

        if len(bpy.context.selected_objects) != 1:
            self.report({'INFO'}, "Select One Object.")
            return {'CANCELLED'}

        mesh = bpy.context.active_object.data

        if not mesh.vertex_colors:
            vert_col = mesh.vertex_colors.new(name=VertColDataName)
            self.report({'INFO'}, "No Vertex Color data found, made new one.")

        mesh.attributes.active_color_index = 0
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        selected_faces = [face for face in mesh.polygons if face.select]
        for face in selected_faces:
            for loop_index in face.loop_indices:
                mesh.vertex_colors.active.data[loop_index].color = self.color

        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}


class FORM_OT_resource_import(bpy.types.Operator):
    bl_idname = "form.resource_import"
    bl_label = "Imports geometry node tool, texture atlas, debug material and colonist ref mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        path = os.path.join(os.path.dirname(__file__), 'RovaResources', 'RovaResources.blend')
        print("Blend file path:", path)

        try:
            with bpy.data.libraries.load(path) as (data_from, data_to):
                # Filter to load only meshes, materials, and geometry nodes (node groups)
                data_to.meshes = data_from.meshes
                data_to.materials = data_from.materials
                data_to.node_groups = data_from.node_groups

            self.report({'INFO'}, "Imported successfully.")

        except OSError as e:
            self.report({'ERROR'}, f"Failed to load blend file: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}


class FORM_OT_add_geo_node_modifier(bpy.types.Operator):
    bl_idname = "form.add_geo_node_modifier"
    bl_label = "Add ColourByAngle Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh.")
            return {'CANCELLED'}

        node_group_name = "ColourByAngleNode"
        if node_group_name not in bpy.data.node_groups:
            self.report({'ERROR'}, f"Node group '{node_group_name}' does not exist.")
            return {'CANCELLED'}

        geo_node_modifier = obj.modifiers.new(name=node_group_name, type='NODES')
        geo_node_modifier.node_group = bpy.data.node_groups[node_group_name]

        self.report({'INFO'}, f"Added '{node_group_name}' Geometry Node modifier.")
        return {'FINISHED'}


classes = (
    PANEL_PT_Panel,
    MAT_OT_Paint,
    FORM_OT_resource_import,
    FORM_OT_add_geo_node_modifier
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    print("Rova Tools registered successfully.")

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    print("Rova Tools unregistered successfully.")

if __name__ == '__main__':
    register()

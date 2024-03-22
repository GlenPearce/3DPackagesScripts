bl_info = {
        "name": "Paint Faces",
        "description": "Vertex paint selected faces with a single click.",
        "author": "Glen Pearce",
        "version": (1, 0),
        "blender": (4, 0, 0),
        "location": "3D Viewport > Sidebar > FacePainting",
        "warning": "", # used for warning icon and text in add-ons panel
        "category": "Painting"
        }

import bpy
import random

VertColDataName = "VertColour"

class PANEL_PT_Panel(bpy.types.Panel):
    """
    Layout of the panel
    """

    # where the panel gets added
    bl_space_type = "VIEW_3D"  # gets shown in 3d viewport
    bl_region_type = "UI"  # referencing sidebar region

    # Label names
    bl_category = "FacePainting"  # sidebar tab name
    bl_label = "FacePainting"  # in the add-on, top of panel name

    # Draw out buttons/layout, add more buttons and layout options here
    def draw(self, context):
        """define the layout of the panel"""
        layout  = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = self.layout.row()
        row.label(text="Choose the faces in edit mode, then choose a colour below")
        row = self.layout.row()
        row.label(text="Painting Colours")
        row = self.layout.row()

        #Add new colours in here
        row.operator("form.paint_face", text="Paint Red").color = (1,0,0,1)
        row.operator("form.paint_face", text="Paint Blue").color = (0,0,1,1)
        row.operator("form.paint_face", text="Paint Green").color = (0,1,0,1)
        row = self.layout.row()
        row.operator("form.paint_face", text="Paint Yellow").color = (1,1,0,1)
        row.operator("form.paint_face", text="Paint Cyan").color = (0,1,1,1)
        row.operator("form.paint_face", text="Paint Purple").color = (1,0,1,1)
        row = self.layout.row()
        row.operator("form.paint_face", text="Paint Orange").color = (1,0.5,0,1)



class MAT_OT_Paint(bpy.types.Operator):

    """
    Select faces on an object and quickly paint them, from a choice of colours
    """

    bl_idname = "form.paint_face"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Applies selected colour to selected faces "  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    color: bpy.props.FloatVectorProperty(size=4)

    def execute(self, context):  # execute() is called when running the operator.

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
    
        active_obj = bpy.context.active_object
        
        
        if not active_obj.data.vertex_colors:
            active_obj.data.vertex_colors.new(name = VertColDataName)
            self.report({'INFO'}, "No Vertex Colour data found, made new one")

        mesh = active_obj.data
        color_layer = mesh.vertex_colors[VertColDataName]

        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        
        selected_faces = [face for face in mesh.polygons if face.select]

        for face in selected_faces:
            for loop_index in face.loop_indices:
                # Set the color for each vertex of the face
                mesh.vertex_colors.active.data[loop_index].color = self.color

        bpy.ops.object.mode_set(mode='EDIT')


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
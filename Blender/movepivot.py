bl_info = {
    "name": "Move Pivot GP",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy


class MovePivotGp(bpy.types.Operator):
    """My Pivot Moving Script"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "move.pivot_gp"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Move Pivot"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.


    def execute(self, context):

        #check for object mode as unable to move pivot in edit mode
        if bpy.context.mode == 'OBJECT':
            #activating
            if not bpy.context.scene.tool_settings.use_transform_data_origin:
                self.report({'INFO'}, "Pivot Moving.")

                #snapping settings
                bpy.context.scene.tool_settings.snap_elements = {'VERTEX', 'EDGE_MIDPOINT'}
                bpy.context.scene.tool_settings.snap_target = 'CLOSEST'
                bpy.context.scene.tool_settings.use_snap = True

                bpy.context.scene.tool_settings.use_transform_data_origin = True
                bpy.ops.wm.tool_set_by_id(name="builtin.move")

            # deactivating
            elif bpy.context.scene.tool_settings.use_transform_data_origin:
                self.report({'INFO'}, "Stopped Pivot Moving.")

                bpy.context.scene.tool_settings.use_transform_data_origin = False
                bpy.context.scene.tool_settings.use_snap = False
                bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
                self.tool_set = False

        #if not in object mode, informs user it only works in object mode
        else:
            self.report({'INFO'}, "This operator only works in Object Mode.")
            return {'CANCELLED'}

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(MovePivotGp.bl_idname)

#KM and KMI sections are for adding the operator to a keymap, it is currently assigned to equals sign
addon_keymaps = []

def register():
    bpy.utils.register_class(MovePivotGp)
    bpy.types.VIEW3D_MT_object.append(menu_func)  # Adds the new operator to an existing menu.

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type= 'VIEW_3D')
        kmi = km.keymap_items.new('move.pivot_gp', type = 'EQUAL', value = 'PRESS')
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(MovePivotGp)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()

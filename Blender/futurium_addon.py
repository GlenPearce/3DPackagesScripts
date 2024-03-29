bl_info = {
    "name": "Futurium Tools",
    "author": "Glen Pearce",
    "blender": (2, 80, 0),
    "location": "3D Viewport > Sidebar > Futurium Tools",
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
    front_door_type: bpy.props.IntProperty(
        name = "FrontDoorType",
        description = "Choose front door style",
        default = 0,
        max = 99,
    )


class PANEL_PT_Futurium_Panel(bpy.types.Panel):
    """
    Layout of the panel
    """

    # where the panel gets added
    bl_space_type = "VIEW_3D"  # gets shown in 3d viewport
    bl_region_type = "UI"  # referencing sidebar region

    # Label names
    bl_category = "Futurium Tools"  # sidebar tab name
    bl_label = "Futurium Tools"  # in the add-on, top of panel name

    # Draw out buttons/layout, add more buttons and layout options here
    def draw(self, context):
        """define the layout of the panel"""
        layout  = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        mytool = scene.my_tool

        row = self.layout.row()
        row.label(text="Maya Tools")
        row = self.layout.row()
        row.operator("form.maya_export", text="Maya Export")
        layout.prop(mytool, "filepath")

        self.layout.separator()

        row = self.layout.row()
        row.operator("mat.reset_maya_mats", text="Reset Maya Mats")

        self.layout.separator()

        row = self.layout.row()
        row.label(text="Plans")
        row = self.layout.row()
        row.operator("form.move_dxf", text="Move DXF Plans").angle = math.radians(0)
        row = self.layout.row()
        row.operator("form.move_dxf", text="Move DXF Plans Stairs").angle = math.radians(-90)

        row = self.layout.row()
        row.label(text="House Creation")
        row = self.layout.row()
        row.operator("form.rename_by_material", text="Rename by Material")
        row = self.layout.row()
        row.operator("form.square_topology", text="Square Topology")
        row = self.layout.row()
        row.operator("form.brick_uv", text="UV Bricks")
        row = self.layout.row()
        row.operator("form.front_door", text="Place Front Door")
        layout.prop(mytool, "front_door_type")



class MAT_OT_reset_maya_mats(bpy.types.Operator):
    """
    Resets Materials affected when importing Maya Lambert materials into Blender
    """
    bl_idname = "mat.reset_maya_mats"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Reset Mats affected by Maya Import"  # Display name in the interface.
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
                    n.inputs["Specular IOR Level"].default_value = 0

        return {'FINISHED'}  # Lets Blender know the operator finished successfully


class FORM_OT_move_dxf(bpy.types.Operator):
    """
    Once DXF plans are imported, use this tool to set the pivot of each componant to be central to the active object. Also un parents, deletes empties and converts curves.
    """
    bl_idname = "form.move_dxf"  # Unique identifier for buttons and menu items to reference.
    bl_label = "move and sort pivot of selected DXF plans"  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    angle: bpy.props.FloatProperty(name="Angle", default=0, step=math.radians(90), subtype='ANGLE')

    def execute(self, context):  # execute() is called when running the operator.
        # Once the user selects the parts of the plans needed for the model, this script takes each part, sets the pivot to be central
        # of the outer walls, moves all to 0,0,0 world space, and scales by.001

        import bpy

        # Changes transform pivot point to bounding box to ensure the pivot goes in the middle of the outer walls
        bpy.context.scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'

        # Select the desired object to have as the pivot centre as active object
        pivot_obj = bpy.context.active_object

        # Stores selected objects
        selected_objects = bpy.context.selected_objects

        # go through selected, convert curves to meshes and unparents any that need it
        for obj in selected_objects:

            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False)

            # converts curves to meshes
            if obj.type == 'CURVE':
                bpy.ops.object.convert(target='MESH', )

            #Clears any previous transforms (found random rotations on some plans which effected unparenting)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

            # unparents all and keeps transforms
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Select the pivot_obj object & set as active
        pivot_obj.select_set(True)
        bpy.context.view_layer.objects.active = pivot_obj

        # Sets the active pivot to be central to the mesh, then moves the 3D cursor to that location
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        bpy.context.scene.cursor.location = bpy.context.view_layer.objects.active.location

        # Apply scale to each selected object
        for obj in selected_objects:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


        bpy.ops.view3d.snap_cursor_to_center()

        # Switch back to the previous context
        # bpy.context.area.type = 'TEXT_EDITOR'

        # Snap selected objects to the cursor
        for obj in selected_objects:
            bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
            obj.rotation_euler.rotate_axis('Y', self.angle)


        # deletes leftover empties
        for obj in selected_objects:
            if not obj.type == 'EMPTY':
                obj.select_set(False)

        bpy.ops.object.delete()

        #reselects the original objects
        for obj in selected_objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = pivot_obj

        return {'FINISHED'}  # Lets Blender know the operator finished successfully

class FORM_OT_maya_export(bpy.types.Operator):
    """
    Export a house made in Blender, with the correct transforms to match Maya. Excludes children of empties that should contain assets already with these transforms.
    """
    bl_idname = "form.maya_export"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Applies transform values to match Maya and exports "  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    def execute(self, context):  # execute() is called when running the operator.

        #store selected object and all children of object
        obj = bpy.context.active_object

            #allows use of file path string
        mytool = context.scene.my_tool

        # change the scale & rotation to match Maya and apply
        obj.scale = (100, 100, 100)
        obj.rotation_euler[0] = -1.5708

        # Apply transforms to root object
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        excluded_names = (
            'FakeInternals',
            'Lighting',
            'SwitchesSockets',
            'Appliances',
            'Props',
            'InteriorDoors'
        )
        #select all child objects of root object with exceptions
        #hides children of exluded names for empties, to keep their transforms
        #ignores empties and applies transforms to empties unless they are called disc (lighting locations)
        for child_object in obj.children_recursive:
            if child_object.type == 'EMPTY' and any(name in child_object.name for name in excluded_names):
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

        # Set the maya transform values
        obj.scale = (.01, .01, .01)
        obj.rotation_euler[0] = 1.5708

        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)



        return {'FINISHED'}

class FORM_OT_square_toplogy(bpy.types.Operator):
    """
    Squares off topology, mainly used for carpet and exterior walls after using the geometry nodes tool to create the house.
    """
    bl_idname = "form.square_topology"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Applies squared topology to selected mesh "  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    def execute(self, context):  # execute() is called when running the operator.

        # Select the object you want to bisect
        obj = bpy.context.active_object
        bpy.context.view_layer.objects.active = obj

        if bpy.context.active_object == None:
            self.report({'INFO'}, "Need an Object selected.")
            return {'CANCELLED'}


        # Switch to Edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        mesh = bpy.context.edit_object.data

        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.001)

        bpy.ops.mesh.select_all(action='DESELECT')

        bpy.ops.mesh.edges_select_sharp(sharpness=0.5)
        bpy.ops.mesh.mark_sharp()

        bpy.ops.mesh.select_all(action='DESELECT')

        obj_index = obj.pass_index

        print(obj_index)

        bpy.ops.mesh.select_all(action='DESELECT')

        # Loop to create bisect loop cuts for each vertex, loops through twice to help with seperated mesh islands
        for i in range(2):
            for vert in mesh.vertices:
                # get vertex index
                vert_index = vert.index

                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_linked_pick(deselect=False, delimit={'SHARP'}, object_index=obj_index,
                                                index=vert_index)

                # Y Axis Cut
                bpy.ops.mesh.bisect(plane_co=(vert.co), plane_no=(1.0, 0, 0), use_fill=False, clear_inner=False,
                                    clear_outer=False, threshold=0.001, xstart=0, xend=0, ystart=0, yend=0, flip=False,
                                    cursor=0)

                bpy.ops.mesh.select_all(action='DESELECT')

                bpy.ops.mesh.select_linked_pick(deselect=False, delimit={'SHARP'}, object_index=obj_index,
                                                index=vert_index)

                # X Axis Cut
                bpy.ops.mesh.bisect(plane_co=(vert.co), plane_no=(0, -1.0, 0), use_fill=False, clear_inner=False,
                                    clear_outer=False, threshold=0.001, xstart=0, xend=0, ystart=0, yend=0, flip=False,
                                    cursor=0)

                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_all(action='SELECT')

                # Z Axis Cut
                bpy.ops.mesh.bisect(plane_co=(vert.co), plane_no=(0, 0, 1.0), use_fill=False, clear_inner=False,
                                    clear_outer=False, threshold=0.001, xstart=0, xend=0, ystart=0, yend=0, flip=False,
                                    cursor=0)

            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=0.001)

        return {'FINISHED'}

class FORM_OT_rename_by_material(bpy.types.Operator):
    """
    Once the geometry nodes tool is used to create the house, it should then be seperated by material. This tool then applies the correct naming to each mesh depending on the material applied.
    """
    bl_idname = "form.rename_by_material"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Renames the house meshes depending on material"  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    def execute(self, context):  # execute() is called when running the operator.

        for obj in  bpy.context.selected_objects:
            if obj.type == 'MESH' and len(obj.data.materials) > 0:
                # Get the name of the first material assigned to the object
                material_name = obj.data.materials[0].name

                # Remove the first 4 letters from the material name (Ext_ or Int_)
                new_name = material_name[4:]

                # Rename the object with the modified name
                obj.name = new_name



                #Naming exceptions
            if obj.name == "ColleridgeYellow":
                obj.name = "Brick"
            if obj.name == "AstonRedSandface":
                obj.name = "LowBrick"

            else:
                self.report({'INFO'}, "Some Objects were not meshes or did not have materials.")

        return {'FINISHED'}

class FORM_OT_brick_uv(bpy.types.Operator):
    """
    UV's selected brick meshes to the correct scale and also moves down slightly to line up grout line corretly
    """

    bl_idname = "form.brick_uv"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Applies correct scale brick UVs"  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    def execute(self, context):  # execute() is called when running the operator.

        bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.uv.muv_uvw_box_map(size=14.4, rotation=(0, 0, 0), tex_aspect=1, assign_uvmap=True)

        original_area = bpy.context.area.type

        for obj in bpy.context.selected_objects:
            bpy.context.area.ui_type = 'UV'
            # Move UV map down by 1mm on the Y-axis
            bpy.ops.uv.select_all(action='SELECT')
            bpy.ops.transform.translate(value=(0, 0.00022, 0))
            bpy.context.area.ui_type = original_area


        return {'FINISHED'}

class FORM_OT_place_front_door(bpy.types.Operator):
    """
    places the chosen front door, at the location of the temporary point made by running the geometry nodes tool
    """

    bl_idname = "form.front_door"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Places the chosen front door to the temporary location made with the house tool"  # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    def execute(self, context):  # execute() is called when running the operator.
        #use of int input
        mytool = context.scene.my_tool
        front_door = mytool.front_door_type

        temp_location_name = 'Front_Door'
        location_to_snap = None

        #find index of collection that the generated house should be in
        target_collection = bpy.data.collections.find("CreatedHouse")
        if not target_collection:
            self.report({'INFO'}, "No CreatedHouse collection, make one and throw the generated house in it.")
            return {'CANCELLED'}
        
        #set the temp location as active, set origin to centre
        if temp_location_name in bpy.data.objects:
            bpy.context.view_layer.objects.active = bpy.data.objects[temp_location_name]
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            location_to_snap = bpy.context.view_layer.objects.active

        else:
            self.report({'INFO'}, "Front_Door not found. Run the house tool and seperate as shown in docs.")
            return {'CANCELLED'}

        #converts front door location into empty, this can then be dragged into the main heirachy with the rest of the door parts
        bpy.ops.object.empty_add(location= location_to_snap.location)

        #select the chosen door, duplicate and set its position to the front door empty position
        #move the dupliacted objects and make them children objects of the front door empty
        bpy.ops.object.select_all(action='DESELECT')
        front_door_size = "FrontDoors_1023mm"
        bpy.context.view_layer.objects.active = bpy.data.objects[front_door_size].children[front_door]
        for child in bpy.context.view_layer.objects.active.children:
            child.select_set(True)
        bpy.ops.object.duplicate_move(TRANSFORM_OT_translate = {"value": location_to_snap.location})


        bpy.ops.object.move_to_collection(collection_index=target_collection)
        bpy.context.view_layer.objects.active = location_to_snap
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        

        self.report({'INFO'}, "updated")

        return {'FINISHED'}



# to enable and disable the add-on, register classes here

classes = (
    MAT_OT_reset_maya_mats,
    FORM_OT_maya_export,
    FORM_OT_move_dxf,
    FORM_OT_square_toplogy,
    FORM_OT_rename_by_material,
    FORM_OT_brick_uv,
    MySettings,
    PANEL_PT_Futurium_Panel,
    FORM_OT_place_front_door
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

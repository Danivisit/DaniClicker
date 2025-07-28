bl_info = {
    "name": "DaniClicker",
    "blender": (4, 1, 0),
    "category": "Object",
    "author": "Danivisit",
    "version": (1, 6, 1),
    "description": "Spawn objects interactively in 3D space by clicking anywhere. ESC to exit spawn mode."
}

import bpy
import random
from mathutils import Euler
from math import radians
from bpy_extras import view3d_utils

class SpawnSettings(bpy.types.PropertyGroup):
    spawn_object: bpy.props.PointerProperty(
        name="Object to Spawn",
        type=bpy.types.Object,
        description="Select the object to spawn"
    )
    scale_factor: bpy.props.FloatProperty(
        name="Scale",
        description="Scale factor for spawned objects",
        default=1.0,
        min=0.00,
        max=10.00
    )
    rot_x: bpy.props.BoolProperty(
        name="X",
        description="Allow random rotation around X axis",
        default=False
    )
    rot_y: bpy.props.BoolProperty(
        name="Y",
        description="Allow random rotation around Y axis",
        default=False
    )
    rot_z: bpy.props.BoolProperty(
        name="Z",
        description="Allow random rotation around Z axis",
        default=False
    )
    is_spawning: bpy.props.BoolProperty(
        name="Is Spawning",
        description="Is spawn mode active",
        default=False
    )

class OBJECT_OT_SpawnModalOperator(bpy.types.Operator):
    bl_idname = "object.spawn_modal_operator"
    bl_label = "Spawn Mode"
    bl_description = "Click anywhere in 3D to spawn objects, ESC to exit spawn mode"

    _timer = None

    def modal(self, context, event):
        settings = context.scene.spawn_settings

        if event.type == 'ESC' and event.value == 'PRESS':
            settings.is_spawning = False
            self.report({'INFO'}, "Spawn mode exited")
            if self._timer:
                context.window_manager.event_timer_remove(self._timer)
            self.show_thanks(context)
            return {'FINISHED'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            spawn_obj = settings.spawn_object
            scale = settings.scale_factor
            rot_x = settings.rot_x
            rot_y = settings.rot_y
            rot_z = settings.rot_z

            if spawn_obj is None:
                self.report({'ERROR'}, "Spawn object not selected")
                return {'RUNNING_MODAL'}

            region = context.region
            rv3d = context.space_data.region_3d
            coord = (event.mouse_region_x, event.mouse_region_y)

            ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
            ray_direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)

            spawn_loc = ray_origin + ray_direction * 10

            new_obj = spawn_obj.copy()
            if spawn_obj.data:
                new_obj.data = spawn_obj.data.copy()
            context.collection.objects.link(new_obj)

            new_obj.location = spawn_loc
            new_obj.scale = (scale, scale, scale)

            r_x = radians(random.uniform(0, 360)) if rot_x else 0
            r_y = radians(random.uniform(0, 360)) if rot_y else 0
            r_z = radians(random.uniform(0, 360)) if rot_z else 0

            new_obj.rotation_euler = Euler((r_x, r_y, r_z), 'XYZ')
            new_obj.select_set(True)

            self.report({'INFO'}, f"Spawned object at {spawn_loc}")

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        settings = context.scene.spawn_settings
        spawn_obj = settings.spawn_object

        if spawn_obj is None:
            self.report({'ERROR'}, "Please select an object to spawn")
            return {'CANCELLED'}

        settings.is_spawning = True
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)

        self.report({'INFO'}, "Spawn mode started: Left Click to spawn, ESC to finish")
        self.show_thanks(context)
        return {'RUNNING_MODAL'}

    def show_thanks(self, context):
        context.workspace.status_text_set("Thank you for using my free to use plugin!")

class OBJECT_PT_DaniClickerPanel(bpy.types.Panel):
    bl_label = "DaniClicker"
    bl_idname = "OBJECT_PT_daniclicker_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DaniClicker'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.spawn_settings

        layout.label(text="Spawn Settings", icon='MESH_ICOSPHERE')
        layout.prop(settings, "spawn_object")
        layout.prop(settings, "scale_factor")

        layout.separator()

        layout.label(text="Randomize Rotation")
        row = layout.row(align=True)
        row.prop(settings, "rot_x")
        row.prop(settings, "rot_y")
        row.prop(settings, "rot_z")

        layout.separator()

        if not settings.is_spawning:
            layout.operator("object.spawn_modal_operator", text="Start Spawn Mode", icon='PLAY')
        else:
            layout.label(text="Spawn Mode active... Press ESC to stop", icon='TIME')

classes = (
    SpawnSettings,
    OBJECT_OT_SpawnModalOperator,
    OBJECT_PT_DaniClickerPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.spawn_settings = bpy.props.PointerProperty(type=SpawnSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.spawn_settings

if __name__ == "__main__":
    register()
bl_info = {
    "name": "Quadspheres",
    "author": "emerald chylde",
    "version": (0, 9),
    "blender": (4, 5, 0),
    "location": "Add > Mesh > Quads",
    "description": "Creates a quadsphere. Shift + A > Quads",
    "category": "Add Mesh",
    "doc_url": "https://github.com/emrld-chld/Quadspheres",
}

import bpy
import mathutils

# ------------------------------
# Scene properties for remembering settings
# ------------------------------
def init_scene_props():
    scene = bpy.types.Scene
    scene.quadsphere_radius = bpy.props.FloatProperty(name="Radius", default=1.0, min=0.01)
    scene.quadsphere_cuts = bpy.props.IntProperty(name="Number of cuts", default=10, min=1)
    scene.quadsphere_smoothness = bpy.props.FloatProperty(name="Smoothness", default=1.0, min=0.0, max=1.0)
    scene.quadsphere_subsurf_levels = bpy.props.IntProperty(name="Subsurf Levels", default=0, min=0, max=6)
    scene.quadsphere_subsurf_apply = bpy.props.BoolProperty(name="Apply Subsurf", default=False)
    scene.quadsphere_multires_levels = bpy.props.IntProperty(name="Multires Levels", default=1, min=0, max=6)


# ------------------------------
# Operator
# ------------------------------
class QUADSPHERE_OT_add(bpy.types.Operator):
    bl_idname = "mesh.quadsphere_add"
    bl_label = "Add Quadsphere"
    bl_options = {'REGISTER', 'UNDO'}

    radius: bpy.props.FloatProperty(name="Radius", default=1.0, min=0.01, options={'SKIP_SAVE'})
    cuts: bpy.props.IntProperty(name="Number of cuts", default=10, min=1, options={'SKIP_SAVE'})
    smoothness: bpy.props.FloatProperty(name="Smoothness", default=1.0, min=0.0, max=1.0, options={'SKIP_SAVE'})
    subsurf_levels: bpy.props.IntProperty(name="Subsurf Levels", default=0, min=0, max=6, options={'SKIP_SAVE'})
    subsurf_apply: bpy.props.BoolProperty(name="Apply", default=False, options={'SKIP_SAVE'})
    multires_levels: bpy.props.IntProperty(name="Multires Levels", default=0, min=0, max=6, options={'SKIP_SAVE'})
    use_preset: bpy.props.BoolProperty(name="Use Preset", default=False, options={'HIDDEN', 'SKIP_SAVE'})

    def invoke(self, context, event):
        scene = context.scene
        
        # Only load saved settings if NOT using a preset
        if not self.use_preset:
            self.radius = scene.quadsphere_radius
            self.cuts = scene.quadsphere_cuts
            self.smoothness = scene.quadsphere_smoothness
            self.subsurf_levels = scene.quadsphere_subsurf_levels
            self.subsurf_apply = scene.quadsphere_subsurf_apply
            self.multires_levels = scene.quadsphere_multires_levels
        # If using preset, keep the values set in the menu (don't load from scene)
        
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "radius")
        layout.prop(self, "cuts")
        layout.prop(self, "smoothness")

        row = layout.row(align=True)
        row.prop(self, "subsurf_levels")
        row.prop(self, "subsurf_apply", text="Apply", toggle=True)

        layout.prop(self, "multires_levels")

    def execute(self, context):
        scene = context.scene

        # Only save settings if NOT using a preset
        if not self.use_preset:
            scene.quadsphere_radius = self.radius
            scene.quadsphere_cuts = self.cuts
            scene.quadsphere_smoothness = self.smoothness
            scene.quadsphere_subsurf_levels = self.subsurf_levels
            scene.quadsphere_subsurf_apply = self.subsurf_apply
            scene.quadsphere_multires_levels = self.multires_levels

        # Create cube
        bpy.ops.mesh.primitive_cube_add(size=self.radius)
        obj = context.active_object

        # Subdivide
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide(number_cuts=self.cuts)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Subsurf modifier
        if self.subsurf_levels > 0:
            subsurf = obj.modifiers.new(name="Subsurf", type='SUBSURF')
            subsurf.levels = self.subsurf_levels
            if self.subsurf_apply:
                bpy.ops.object.modifier_apply(modifier=subsurf.name)

        # Multires modifier - FIXED
        if self.multires_levels > 0:
            multires = obj.modifiers.new(name="Multires", type='MULTIRES')
            # Subdivide the multires modifier the correct number of times
            for i in range(self.multires_levels):
                bpy.ops.object.multires_subdivide(modifier="Multires")

        # Smooth (spherify)
        if self.smoothness > 0.0:
            mesh = obj.data
            center = mathutils.Vector((0, 0, 0))
            for v in mesh.vertices:
                direction = (v.co - center).normalized()
                target = direction * self.radius
                v.co = v.co.lerp(target, self.smoothness)

        return {'FINISHED'}


# ------------------------------
# Quads menu
# ------------------------------
class QUADSPHERE_MT_menu(bpy.types.Menu):
    bl_label = "Quads"
    bl_idname = "VIEW3D_MT_quads_menu"

    def draw(self, context):
        layout = self.layout
        
        # Default quadsphere - remembers settings
        layout.operator("mesh.quadsphere_add", text="Quadsphere")
        
        # Preset quadspheres - always use default settings
        op = layout.operator("mesh.quadsphere_add", text="Quadsphere + Subsurf 3")
        op.use_preset = True
        op.radius = 1.0
        op.cuts = 10
        op.smoothness = 1.0
        op.subsurf_levels = 3
        op.subsurf_apply = False
        op.multires_levels = 0
        
        op = layout.operator("mesh.quadsphere_add", text="Quadsphere + Subsurf 4")
        op.use_preset = True
        op.radius = 1.0
        op.cuts = 10
        op.smoothness = 1.0
        op.subsurf_levels = 4
        op.subsurf_apply = False
        op.multires_levels = 0
        
        op = layout.operator("mesh.quadsphere_add", text="Quadsphere + Subsurf 3 (Applied)")
        op.use_preset = True
        op.radius = 1.0
        op.cuts = 10
        op.smoothness = 1.0
        op.subsurf_levels = 3
        op.subsurf_apply = True
        op.multires_levels = 0
        
        op = layout.operator("mesh.quadsphere_add", text="Quadsphere + Subsurf 4 (Applied)")
        op.use_preset = True
        op.radius = 1.0
        op.cuts = 10
        op.smoothness = 1.0
        op.subsurf_levels = 4
        op.subsurf_apply = True
        op.multires_levels = 0
        
        op = layout.operator("mesh.quadsphere_add", text="Quadsphere + Multires 3")
        op.use_preset = True
        op.radius = 1.0
        op.cuts = 10
        op.smoothness = 1.0
        op.subsurf_levels = 0
        op.subsurf_apply = False
        op.multires_levels = 3
        
        op = layout.operator("mesh.quadsphere_add", text="Quadsphere + Multires 4")
        op.use_preset = True
        op.radius = 1.0
        op.cuts = 10
        op.smoothness = 1.0
        op.subsurf_levels = 0
        op.subsurf_apply = False
        op.multires_levels = 4


# ------------------------------
# Add to Shift+A menu above Mesh
# ------------------------------
def menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("VIEW3D_MT_quads_menu")


# ------------------------------
# Registration
# ------------------------------
classes = [
    QUADSPHERE_OT_add,
    QUADSPHERE_MT_menu,
]

def register():
    init_scene_props()
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_add.prepend(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

"""
create_scene.py  –  Blender headless script
Creates a rotating cube, camera, and lighting.
Renders a 3-second 480p 24 FPS animation (Cycles CPU) to PNG frames.

Usage:
    blender --background --python-exit-code 1 --python create_scene.py
"""

import bpy
import math
import os

# ── Cleanup default scene ───────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene

# ── Settings ────────────────────────────────────────────────────────
FPS = 24
DURATION_SEC = 3
TOTAL_FRAMES = FPS * DURATION_SEC  # 72 frames
RES_X, RES_Y = 854, 480            # 480p widescreen
OUTPUT_DIR = os.path.join(os.getcwd(), "frames")

os.makedirs(OUTPUT_DIR, exist_ok=True)

scene.frame_start = 1
scene.frame_end = TOTAL_FRAMES
scene.render.fps = FPS
scene.render.resolution_x = RES_X
scene.render.resolution_y = RES_Y
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = os.path.join(OUTPUT_DIR, "frame_")

# ── Cycles CPU renderer ────────────────────────────────────────────
scene.render.engine = "CYCLES"
prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "NONE"  # CPU only
scene.cycles.device = "CPU"
scene.cycles.samples = int(os.environ.get("CYCLES_SAMPLES") or "32")
scene.cycles.use_denoising = True

# ── World background ───────────────────────────────────────────────
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes["Background"]
bg_node.inputs["Color"].default_value = (0.05, 0.05, 0.08, 1.0)

# ── Cube ────────────────────────────────────────────────────────────
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "RotatingCube"

# Material
mat = bpy.data.materials.new("CubeMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.1, 0.5, 0.9, 1.0)   # blue
bsdf.inputs["Roughness"].default_value = 0.3
bsdf.inputs["Metallic"].default_value = 0.6
cube.data.materials.append(mat)

# Keyframe rotation: full 360° around Z over all frames
cube.rotation_euler = (0, 0, 0)
cube.keyframe_insert(data_path="rotation_euler", frame=1)
cube.rotation_euler = (math.radians(360), 0, math.radians(360))
cube.keyframe_insert(data_path="rotation_euler", frame=TOTAL_FRAMES)

# ── Camera ──────────────────────────────────────────────────────────
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 50
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (5, -5, 4)

# Point camera at cube
direction = cube.location - cam_obj.location
rot_quat = direction.to_track_quat("-Z", "Y")
cam_obj.rotation_euler = rot_quat.to_euler()

scene.camera = cam_obj

# ── Key Light (Sun) ────────────────────────────────────────────────
sun_data = bpy.data.lights.new("SunLight", type="SUN")
sun_data.energy = 3.0
sun_data.color = (1.0, 0.95, 0.9)
sun_obj = bpy.data.objects.new("SunLight", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(-30))

# ── Fill Light (Point) ─────────────────────────────────────────────
fill_data = bpy.data.lights.new("FillLight", type="POINT")
fill_data.energy = 150.0
fill_data.color = (0.7, 0.85, 1.0)
fill_obj = bpy.data.objects.new("FillLight", fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (-4, 3, 2)

# ── Floor Plane (optional ground) ──────────────────────────────────
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -1))
floor = bpy.context.active_object
floor.name = "Floor"
floor_mat = bpy.data.materials.new("FloorMat")
floor_mat.use_nodes = True
floor_bsdf = floor_mat.node_tree.nodes["Principled BSDF"]
floor_bsdf.inputs["Base Color"].default_value = (0.15, 0.15, 0.15, 1.0)
floor_bsdf.inputs["Roughness"].default_value = 0.8
floor.data.materials.append(floor_mat)

# ── Render Animation ───────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"  Rendering {TOTAL_FRAMES} frames at {RES_X}x{RES_Y} @ {FPS} FPS")
print(f"  Engine: Cycles CPU | Samples: {scene.cycles.samples}")
print(f"  Output: {OUTPUT_DIR}")
print(f"{'='*60}\n")

bpy.ops.render.render(animation=True)

print("\n✅ Render complete!")

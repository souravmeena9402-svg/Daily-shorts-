import bpy
import sys
import math
import os
import json

# Parse arguments passed after "--"
argv = sys.argv
if "--" in argv:
    args = argv[argv.index("--") + 1:]
else:
    args = []

topic = args[0] if len(args) > 0 else "orbit"
variant = int(args[1]) if len(args) > 1 else 0
total_frames = int(args[2]) if len(args) > 2 else 240
output_video_path = args[3] if len(args) > 3 else "output/scene3d.mp4"

# 1. Clean up default scene
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderEngine') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderEngine.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scene.render.resolution_x = 720
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = total_frames

# Video output settings
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.ffmpeg.ffmpeg_preset = 'VERYFAST'
scene.render.filepath = output_video_path

# World Dark Deep Space Background
world = bpy.data.worlds.new("SpaceWorld")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.01, 0.015, 0.03, 1.0) # Deep navy space
    bg_node.inputs[1].default_value = 0.5

# 2. Camera Setup (Vertical 9:16 Cinematic Framing)
cam_data = bpy.data.cameras.new("CinematicCam")
cam_obj = bpy.data.objects.new("CinematicCam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0, -7.5, 1.2)
cam_obj.rotation_euler = (math.radians(82), 0, 0)
cam_data.lens = 45 # 45mm cinematic lens

# 3. Dramatic Studio Lighting
def add_light(name, ltype, loc, color, energy):
    light_data = bpy.data.lights.new(name=name, type=ltype)
    light_data.color = color
    light_data.energy = energy
    light_obj = bpy.data.objects.new(name=name, object_data=light_data)
    scene.collection.objects.link(light_obj)
    light_obj.location = loc
    return light_obj

add_light("KeyLight", 'AREA', (3.5, -4, 4), (0.2, 0.8, 1.0), 350)     # Neon Cyan
add_light("RimLight", 'POINT', (-3.5, 3, 2), (1.0, 0.6, 0.1), 400)    # Warm Gold Rim
add_light("FillLight", 'AREA', (0, -6, -2), (0.4, 0.1, 0.8), 120)     # Subtle Purple fill

# Helper: Create Glowing Material
def create_glow_mat(name, color, emission_strength=4.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new(type='ShaderNodeOutputMaterial')
    emit = nodes.new(type='ShaderNodeEmission')
    emit.inputs['Color'].default_value = color
    emit.inputs['Strength'].default_value = emission_strength
    mat.node_tree.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    return mat

# Helper: Create Metallic Glossy PBR Material
def create_pbr_mat(name, base_color, metallic=0.9, roughness=0.15):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
    return mat

cyan_glow = create_glow_mat("CyanGlow", (0.0, 0.9, 1.0, 1.0), 5.0)
gold_glow = create_glow_mat("GoldGlow", (1.0, 0.7, 0.1, 1.0), 6.0)
magenta_glow = create_glow_mat("MagentaGlow", (1.0, 0.1, 0.5, 1.0), 4.0)
dark_metal = create_pbr_mat("DarkMetal", (0.05, 0.07, 0.12, 1.0), 0.95, 0.2)
glass_chrome = create_pbr_mat("Chrome", (0.8, 0.85, 0.9, 1.0), 1.0, 0.05)

# 4. Build Procedural 3D Models based on topic
if topic == 'orbit':
    # Central Sun / Star
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.75, location=(0, 0, 0))
    sun = bpy.context.active_object
    sun.data.materials.append(gold_glow)

    # Inner Orbit Planet
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(1.8, 0, 0))
    p1 = bpy.context.active_object
    p1.data.materials.append(cyan_glow)

    # Outer Orbit Planet
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=(3.4, 0, 0))
    p2 = bpy.context.active_object
    p2.data.materials.append(magenta_glow)

    # Orbit rings
    bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.015, location=(0,0,0))
    bpy.context.active_object.data.materials.append(cyan_glow)
    bpy.ops.mesh.primitive_torus_add(major_radius=3.4, minor_radius=0.015, location=(0,0,0))
    bpy.context.active_object.data.materials.append(magenta_glow)

    # Animate Planets & Camera Orbit
    for f in range(1, total_frames + 1):
        t = f / 24.0
        # Planet 1 orbit
        p1.location.x = 1.8 * math.cos(t * 2.2)
        p1.location.y = 1.8 * math.sin(t * 2.2)
        p1.keyframe_insert(data_path="location", frame=f)
        # Planet 2 orbit (slower)
        p2.location.x = 3.4 * math.cos(t * 0.9)
        p2.location.y = 3.4 * math.sin(t * 0.9)
        p2.keyframe_insert(data_path="location", frame=f)
        # Cinematic Camera Slow Pan & Track
        cam_obj.location.x = 0.8 * math.sin(t * 0.3)
        cam_obj.location.z = 1.2 + 0.4 * math.cos(t * 0.3)
        cam_obj.keyframe_insert(data_path="location", frame=f)

elif topic == 'echo':
    # 3D Sound Emitter Station
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(-2.4, 0, 0))
    emitter = bpy.context.active_object
    emitter.data.materials.append(cyan_glow)

    # 3D Cliff Wall with geometric detail
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(2.5, 0, 0))
    cliff = bpy.context.active_object
    cliff.scale = (0.3, 3.5, 2.5)
    cliff.data.materials.append(gold_glow)

    # Expanding 3D Sonic Echo Rings
    echo_rings = []
    for i in range(4):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.6, minor_radius=0.02, location=(-2.4, 0, 0))
        ring = bpy.context.active_object
        ring.rotation_euler.y = math.radians(90)
        ring.data.materials.append(cyan_glow)
        echo_rings.append(ring)

    for f in range(1, total_frames + 1):
        t = f / 24.0
        for i, ring in enumerate(echo_rings):
            phase = ((t * 0.8) + i * 0.25) % 1.0
            x_pos = -2.4 + 4.9 * phase
            ring.location.x = x_pos
            scale_val = 0.3 + 1.8 * math.sin(phase * math.pi)
            ring.scale = (scale_val, scale_val, scale_val)
            ring.keyframe_insert(data_path="location", frame=f)
            ring.keyframe_insert(data_path="scale", frame=f)

else:
    # Generic Modern 3D Gyroscope / Tech Core for other physics concepts
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0, 0, 0))
    core = bpy.context.active_object
    core.data.materials.append(cyan_glow)

    bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.06, location=(0, 0, 0))
    ring1 = bpy.context.active_object
    ring1.data.materials.append(glass_chrome)

    bpy.ops.mesh.primitive_torus_add(major_radius=2.4, minor_radius=0.04, location=(0, 0, 0))
    ring2 = bpy.context.active_object
    ring2.data.materials.append(gold_glow)

    for f in range(1, total_frames + 1):
        t = f / 24.0
        ring1.rotation_euler = (t * 1.5, t * 1.1, 0)
        ring2.rotation_euler = (0, t * 0.8, t * 1.7)
        ring1.keyframe_insert(data_path="rotation_euler", frame=f)
        ring2.keyframe_insert(data_path="rotation_euler", frame=f)

# 5. Render Scene to Video
print(f"--- STARTING BLENDER 3D RENDER ({total_frames} frames) ---")
bpy.ops.render.render(animation=True)
print("--- BLENDER 3D RENDER COMPLETE ---")
                      

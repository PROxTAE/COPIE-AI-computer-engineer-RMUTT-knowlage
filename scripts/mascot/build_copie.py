"""Build the COPIE web mascot in Blender 5.x.

Run: blender -b --python scripts/mascot/build_copie.py
The reference PNG remains untouched. Outputs go to assets/mascot/3d/.
"""

from pathlib import Path
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "mascot" / "3d"
OUT.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for material in list(bpy.data.materials):
    bpy.data.materials.remove(material)


def mat(name, color, roughness=0.65, metallic=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    node = m.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = (*color, 1)
    node.inputs["Roughness"].default_value = roughness
    node.inputs["Metallic"].default_value = metallic
    return m


white = mat("COPIE warm white", (0.96, 0.95, 0.94), 0.86)
ear_inner = mat("Ear inner pearl", (0.91, 0.88, 0.89), 0.9)
blush = mat("Soft blush", (0.85, 0.80, 0.80), 0.96)
eye_dark = mat("Eye midnight blue", (0.012, 0.026, 0.13), 0.18)
eye_blue = mat("Eye cobalt", (0.005, 0.19, 0.94), 0.14)
eye_glint = mat("Eye glint", (0.92, 0.97, 1), 0.1)
navy = mat("Headset navy", (0.035, 0.055, 0.18), 0.36)
blue = mat("Headset electric blue", (0.008, 0.13, 0.85), 0.25)
shirt = mat("RMUTT shirt dark brown", (0.12, 0.095, 0.102), 0.86)
shirt_seam = mat("Shirt seam", (0.075, 0.059, 0.062), 0.9)
pants = mat("Dark trousers", (0.065, 0.067, 0.079), 0.9)
button = mat("Shirt button", (0.022, 0.023, 0.026), 0.32)
silver = mat("Laptop silver", (0.61, 0.64, 0.69), 0.27, 0.56)
silver_edge = mat("Laptop edge", (0.33, 0.37, 0.43), 0.25, 0.55)
screen = mat("Laptop screen navy", (0.015, 0.03, 0.085), 0.22)
screen_glow = mat("Laptop screen glow", (0.035, 0.24, 0.62), 0.37)
crest_orange = mat("Crest orange", (0.89, 0.31, 0.025), 0.6)
crest_teal = mat("Crest teal", (0.035, 0.54, 0.52), 0.55)
crest_gold = mat("Crest gold", (0.87, 0.62, 0.12), 0.55)

root = bpy.data.objects.new("COPIE_MODEL_ROOT", None)
bpy.context.collection.objects.link(root)


def parent(obj, name=None):
    if name:
        obj.name = name
    obj.parent = root
    return obj


def smooth(obj):
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True
    return obj


def uv(name, center, scale, material, segments=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=center)
    o = parent(bpy.context.object, name)
    o.scale = scale
    o.data.materials.append(material)
    return smooth(o)


def cube(name, center, scale, material, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o = parent(bpy.context.object, name)
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("Soft corners", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return o


def tube(name, points, radius, material, resolution=4):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 24
    curve.bevel_depth = radius
    curve.bevel_resolution = resolution
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for node, co in zip(spline.bezier_points, points):
        node.co = co
        node.handle_left_type = "AUTO"
        node.handle_right_type = "AUTO"
    obj = parent(bpy.data.objects.new(name, curve))
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def polygon(name, vertices, material, y):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(x, y, z) for x, z in vertices], [], [tuple(range(len(vertices)))])
    mesh.update()
    obj = parent(bpy.data.objects.new(name, mesh))
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def catmull(points, subdivisions=8):
    result = []
    count = len(points)
    for i in range(count):
        p0, p1, p2, p3 = [points[j % count] for j in (i - 1, i, i + 1, i + 2)]
        for k in range(subdivisions):
            t = k / subdivisions
            result.append(tuple(0.5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * t +
                (2*p0[d]-5*p1[d]+4*p2[d]-p3[d])*t*t +
                (-p0[d]+3*p1[d]-3*p2[d]+p3[d])*t*t*t) for d in range(2)))
    return result


# Character faces the camera along negative Y. The outline keeps the broad,
# softly pointed cheeks and large ears of the supplied concept image.
outline = catmull([
    (0, 3.72), (0.48, 3.77), (0.98, 4.28), (1.24, 4.33),
    (1.39, 3.78), (1.28, 3.48), (1.52, 3.30), (1.67, 2.97),
    (1.52, 2.75), (1.58, 2.45), (1.38, 2.31), (1.34, 2.04),
    (0.92, 1.93), (0.54, 1.96), (0, 1.91), (-0.54, 1.96),
    (-0.92, 1.93), (-1.34, 2.04), (-1.38, 2.31), (-1.58, 2.45),
    (-1.52, 2.75), (-1.67, 2.97), (-1.52, 3.30), (-1.28, 3.48),
    (-1.39, 3.78), (-1.24, 4.33), (-0.98, 4.28), (-0.48, 3.77),
])
mid_z = 3.115
rings = [
    (0.0, -0.50), (0.56, -0.47), (0.81, -0.38),
    (0.95, -0.22), (1.0, -0.02), (0.99, 0.17),
    (0.88, 0.39), (0.54, 0.52), (0.0, 0.54),
]
verts = []
for scale, y in rings:
    verts.extend([(x*scale, y, mid_z + (z-mid_z)*scale) for x,z in outline])
n = len(outline)
faces = []
for j in range(len(rings)-1):
    for i in range(n):
        a, b = j*n+i, j*n+(i+1)%n
        faces.append((a,b,b+n,a+n))
mesh = bpy.data.meshes.new("Rounded cat silhouette mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()
head = parent(bpy.data.objects.new("COPIE large white cat head", mesh))
bpy.context.collection.objects.link(head)
head.data.materials.append(white)
smooth(head)

# Face details are deliberately tiny and readable at chat-widget scale.
for sign in (-1, 1):
    uv("Cobalt oval eye", (sign*0.50,-0.503,3.05), (0.102,0.038,0.165), eye_dark)
    uv("Blue lower eye", (sign*0.50,-0.540,2.99), (0.083,0.022,0.080), eye_blue)
    uv("Eye light reflection", (sign*0.525,-0.559,3.12), (0.020,0.009,0.032), eye_glint, 16, 8)
    uv("Pale round cheek", (sign*0.82,-0.496,2.87), (0.092,0.014,0.047), blush, 24, 12)
    polygon("Inner ear blush", [(sign*1.02,4.02),(sign*1.17,4.17),(sign*1.25,3.83)], ear_inner, -0.25)

# Padded headset arc, side cups, bright cobalt accent rings, and boom mic.
tube("Headset upper band", [(-1.18,0.03,3.57),(-0.82,0.11,4.17),
     (0,0.13,4.37),(0.82,0.11,4.17),(1.18,0.03,3.57)], 0.080, navy)
for sign in (-1,1):
    uv("Headset ear cushion", (sign*1.50,-0.12,3.34), (0.215,0.30,0.38), navy)
    uv("Headset blue outer cup", (sign*1.68,-0.14,3.32), (0.068,0.242,0.30), blue)
    uv("Headset navy cap", (sign*1.725,-0.14,3.32), (0.042,0.212,0.26), navy)
tube("Boom microphone arm", [(1.65,-0.30,3.18),(1.63,-0.52,2.90),
     (1.43,-0.75,2.77),(1.18,-0.83,2.78)], 0.032, navy)
uv("Microphone foam tip", (1.16,-0.84,2.78), (0.14,0.065,0.073), navy)

# Shirt, collar, pocket and RMUTT-inspired small crest. It is decorative
# geometry; replace this detail with licensed logo artwork if exactness matters.
cube("Dark student shirt torso", (0,0.0,1.40), (1.33,0.74,1.10), shirt, 0.22)
polygon("Left shirt collar", [(-0.44,1.92),(-0.03,1.85),(-0.22,1.65),(-0.46,1.77)], shirt_seam, -0.392)
polygon("Right shirt collar", [(0.44,1.92),(0.03,1.85),(0.22,1.65),(0.46,1.77)], shirt_seam, -0.392)
cube("Button placket", (0,-0.391,1.38), (0.063,0.016,0.75), shirt_seam, 0.008)
for z in (1.64,1.40,1.16):
    uv("Black shirt button", (0,-0.409,z), (0.025,0.010,0.025), button, 16, 8)
cube("Shirt breast pocket", (0.38,-0.395,1.43), (0.29,0.018,0.24), shirt_seam, 0.018)
tube("Pocket opening", [(0.24,-0.411,1.55),(0.52,-0.411,1.55)], 0.008, shirt)
uv("University crest gold base", (-0.39,-0.408,1.64), (0.072,0.013,0.088), crest_gold, 20, 10)
uv("University crest teal center", (-0.39,-0.425,1.64), (0.048,0.011,0.056), crest_teal, 20, 10)
uv("University crest orange spire", (-0.39,-0.430,1.73), (0.022,0.010,0.060), crest_orange, 16, 8)

# Sleeves, paws and stout dark legs. Paws wrap under the laptop base.
for sign in (-1,1):
    uv("Brown short sleeve", (sign*0.70,-0.02,1.62), (0.30,0.31,0.31), shirt)
    uv("White forearm", (sign*0.80,-0.30,1.38), (0.235,0.25,0.28), white)
    uv("Laptop supporting paw", (sign*0.60,-0.72,1.32), (0.245,0.185,0.165), white)
    uv("Dark trouser leg", (sign*0.33,0.02,0.53), (0.36,0.36,0.63), pants)
    uv("Rounded dark shoe", (sign*0.34,-0.16,0.18), (0.39,0.49,0.20), pants)

# An open small silver laptop held in front, turned slightly so its keyboard
# reads in the silhouette and the cat's full face stays unobstructed.
laptop_base = cube("Open laptop keyboard base", (0,-0.78,1.30), (1.46,0.88,0.072), silver, 0.036)
keyboard = cube("Laptop keyboard dark inset", (0,-0.79,1.344), (1.19,0.56,0.007), silver_edge, 0.022)
for row in range(3):
    for col in range(10):
        cube("Keyboard key", ((col-4.5)*0.103,-0.98+row*0.14,1.352),
             (0.077,0.078,0.005), button, 0.006)
lid = cube("Open laptop screen lid", (0,-0.36,1.76), (1.46,0.060,0.94), silver, 0.043)
lid.rotation_euler[0] = math.radians(14)
panel = cube("Dark laptop display", (0,-0.403,1.76), (1.28,0.011,0.77), screen, 0.022)
panel.rotation_euler[0] = math.radians(14)
for z,w in ((1.89,0.70),(1.76,0.92),(1.63,0.55)):
    strip = cube("Abstract screen line", (0,-0.419,z), (w,0.006,0.025), screen_glow, 0.009)
    strip.rotation_euler[0] = math.radians(14)

# Place camera and lights outside the exported mascot root for previews only.
bpy.ops.object.camera_add(location=(0,-9.4,3.0))
camera = bpy.context.object
camera.name = "Preview camera only"
direction = Vector((0,0,2.2)) - camera.location
camera.rotation_euler = direction.to_track_quat("-Z","Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = 5.3
bpy.context.scene.camera = camera

def area(name, location, power, size):
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = "DISK"
    light.data.size = size
    light.rotation_euler = (Vector((0,0,2.2))-light.location).to_track_quat("-Z","Y").to_euler()

area("Soft key", (-3,-5,6), 760, 6)
area("Soft fill", (3,-4,3), 380, 5)
area("Soft rim", (0,3,5), 550, 4)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 48
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(OUT / "copie-front-laptop-preview.png")
scene.view_settings.view_transform = "AgX"
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "copie-mascot-web.blend"))
bpy.ops.render.render(write_still=True)

bpy.ops.object.select_all(action="DESELECT")
root.select_set(True)
for child in root.children_recursive:
    child.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.gltf(
    filepath=str(OUT / "copie-mascot-web.glb"),
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_yup=True,
)
print("COPIE outputs:", OUT)

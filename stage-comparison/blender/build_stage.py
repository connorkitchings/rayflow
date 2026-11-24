"""Build two editable, untimed looks in Blender 4.5 with BlenderDMX 2.3.2.

Run with BlenderDMX enabled:
    blender -b --python-exit-code 1 -P build_stage.py -- --output /path/to/output
The default fixture source is the grandMA3 2.5.1 macOS demo MVR.
"""

import argparse
import math
import sys
import zipfile
from pathlib import Path
from types import SimpleNamespace

import bpy
from mathutils import Matrix, Vector


def geometry(name, mesh, material, collection):
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if material is not None:
        obj.data.materials.append(material)
    return obj


def material(name, color, metallic=0.0, roughness=0.55):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


def collection(name):
    result = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(result)
    return result


def finish_primitive(name, mat, group):
    obj = bpy.context.object
    obj.name = name
    for old_group in list(obj.users_collection):
        old_group.objects.unlink(obj)
    group.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj


def box(name, position, size, mat, group):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = finish_primitive(name, mat, group)
    for vertex in obj.data.vertices:
        vertex.co.x *= size[0]
        vertex.co.y *= size[1]
        vertex.co.z *= size[2]
    return obj


def tube(name, start, end, radius, mat, group, sides=12):
    a, b = Vector(start), Vector(end)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=sides, radius=radius, depth=(b - a).length, location=(a + b) * 0.5
    )
    obj = finish_primitive(name, mat, group)
    obj.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    return obj


def truss(y, z, mat, group):
    # One lightweight editable wire bundle per truss.
    curve = bpy.data.curves.new("Truss chords and lacing", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.024
    curve.bevel_resolution = 1

    def bar(p, q, scale=1):
        spline = curve.splines.new("POLY")
        spline.points.add(1)
        for point, xyz in zip(spline.points, (p, q)):
            point.co = (*xyz, 1)
            point.radius = scale

    for dy in (-0.121, 0.121):
        for dz in (0.024, 0.266):
            bar((-5.5, y + dy, z + dz), (5.5, y + dy, z + dz))
        for i in range(22):
            x = -5.5 + i * 0.5
            height = 0.024 if i % 2 else 0.266
            bar((x, y + dy, z + height), (x + 0.5, y + dy, z + 0.29 - height), 0.58)
    for x in (-5.5, 5.5):
        for dz in (0.024, 0.266):
            bar((x, y - 0.121, z + dz), (x, y + 0.121, z + dz))
    return geometry("Downstage truss" if y < 0 else "Upstage truss", curve, mat, group)


def scenery():
    group = collection("Stage | floor, riser and trusses")
    dark = material("Charcoal stage deck", (0.088, 0.093, 0.105), 0.12, 0.41)
    edge = material("Deck edging", (0.12, 0.136, 0.144), 0.55, 0.35)
    steel = material("Brushed aluminium", (0.48, 0.51, 0.55), 0.65, 0.3)
    black = material("Equipment black", (0.034, 0.038, 0.044), 0.18, 0.53)
    box("Stage deck | 12 × 10 m", (0, 2, -0.2), (12, 10, 0.4), dark, group)
    box("Drum riser | 3 × 2 m", (0, 5, 0.225), (3, 2, 0.45), dark, group)
    box("Deck front fascia", (0, -3.005, -0.09), (12, 0.015, 0.032), edge, group)
    for x in (-4, -2, 0, 2, 4):
        box("Panel joint", (x, 2, 0.001), (0.012, 10, 0.002), black, group)
    for y in (-1, 1, 3, 5):
        box("Panel joint", (0, y, 0.001), (12, 0.012, 0.002), black, group)
    truss(-2, 6, steel, group)
    truss(6, 7, steel, group)

    dress = collection("Concert dressing | drums, microphones and wedges")
    gold = material("Hammered bronze", (0.51, 0.31, 0.115), 0.72, 0.29)
    wine = material("Drum shells", (0.22, 0.067, 0.027), 0.5, 0.28)
    skin = material("Drum heads", (0.41, 0.38, 0.31), 0.15, 0.55)
    tube("Kick drum shell", (0, 4.48, 0.88), (0, 5.20, 0.88), 0.43, wine, dress, 48)
    tube("Kick front head", (0, 4.45, 0.88), (0, 4.48, 0.88), 0.43, black, dress, 48)
    for x, y, h, r in (
        (-0.6, 4.95, 1.04, 0.22),
        (0.56, 5.03, 0.98, 0.29),
        (-0.27, 4.99, 1.43, 0.21),
        (0.24, 5.04, 1.44, 0.22),
    ):
        tube("Drum shell", (x, y, h - 0.24), (x, y, h), r, wine, dress, 32)
        tube("Drum skin", (x, y, h), (x, y, h + 0.018), r, skin, dress, 32)
        tube("Drum rim", (x, y, h - 0.20), (x, y, h - 0.18), r * 1.03, steel, dress, 32)
    for x, y, h, r in (
        (-0.93, 4.95, 1.62, 0.24),
        (0.91, 5.19, 1.78, 0.36),
        (-0.62, 5.59, 1.92, 0.33),
        (0.36, 5.53, 1.93, 0.30),
    ):
        tube("Cymbal stand", (x, y, 0.45), (x, y, h + 0.07), 0.014, steel, dress)
        bpy.ops.mesh.primitive_cone_add(
            vertices=48, radius1=r, radius2=0.042, depth=0.053, location=(x, y, h)
        )
        finish_primitive("Cymbal", gold, dress)
    for x, y in ((-3.4, 1.2), (0, 0.6), (3.4, 1.2)):
        tube("Microphone stand", (x, y, 0.02), (x, y, 1.41), 0.014, steel, dress)
        tube(
            "Microphone boom",
            (x, y, 1.37),
            (x + 0.15, y + 0.32, 1.62),
            0.014,
            steel,
            dress,
        )
        tube(
            "Microphone",
            (x + 0.15, y + 0.28, 1.62),
            (x + 0.15, y + 0.43, 1.62),
            0.032,
            black,
            dress,
        )
        for angle in (0, 2.09, 4.19):
            tube(
                "Stand leg",
                (x, y, 0.15),
                (x + 0.28 * math.cos(angle), y + 0.28 * math.sin(angle), 0.02),
                0.013,
                black,
                dress,
            )
        monitor = box(
            "Wedge monitor", (x, y - 0.83, 0.18), (0.67, 0.44, 0.25), black, dress
        )
        monitor.rotation_euler.x = math.radians(-17)
    box("Venue floor", (0, 2, -0.45), (250, 250, 0.1), black, dress)
    # Drapery gives washes a real surface behind the band.
    cloth = material("Velour cyclorama", (0.14, 0.134, 0.15), 0, 0.87)
    mesh = bpy.data.meshes.new("Pleated soft goods")
    vertices = []
    faces = []
    for i in range(161):
        x = -7 + i * 14 / 160
        y = 7.70 + 0.11 * math.cos(x * 7.5)
        vertices.extend(((x, y, -0.5), (x, y, 6.65)))
        if i:
            j = 2 * i
            faces.append((j - 2, j, j + 1, j - 1))
    mesh.from_pydata(vertices, [], faces)
    curtain = geometry("Black upstage drape", mesh, cloth, dress)
    for face in curtain.data.polygons:
        face.use_smooth = True


def performers():
    group = collection("Performers | movable scale figures")
    shirt = material("Performers | charcoal cotton", (0.119, 0.118, 0.139))
    denim = material("Performers | denim", (0.045, 0.054, 0.072))
    face = material("Performers | warm neutral", (0.54, 0.34, 0.22))
    hair = material("Performers | hair and shoes", (0.045, 0.038, 0.037))
    wood = material("Instruments | amber wood", (0.36, 0.13, 0.032), 0.22)

    def shape(root, name, position, radius, mat):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10)
        obj = finish_primitive(name, mat, group)
        obj.parent = root
        obj.location = position
        obj.scale = radius
        for poly in obj.data.polygons:
            poly.use_smooth = True
        return obj

    def limb(root, name, a, b, width, mat):
        axis = Vector(b) - Vector(a)
        obj = shape(
            root,
            name,
            (Vector(a) + Vector(b)) / 2,
            (width, width, axis.length / 2 + width * 0.35),
            mat,
        )
        obj.rotation_euler = axis.to_track_quat("Z", "Y").to_euler()

    positions = (
        ("Guitar", -3.25, 1.79, 0),
        ("Vocal", 0.15, 1.19, 0),
        ("Bass", 3.55, 1.79, 0),
        ("Drums", 0, 5.6, 0.45),
    )
    for role, x, y, z in positions:
        root = bpy.data.objects.new(f"Performer | {role}", None)
        group.objects.link(root)
        root.location = (x, y, z)
        root.empty_display_type = "PLAIN_AXES"
        root.empty_display_size = 0.2
        seated = role == "Drums"
        h = -0.36 if seated else 0
        shape(root, "Torso", (0, 0, 1.18 + h), (0.218, 0.13, 0.30), shirt)
        shape(root, "Hips", (0, 0.02, 0.91 + h), (0.169, 0.125, 0.16), denim)
        shape(root, "Neck", (0, 0, 1.48 + h), (0.072, 0.075, 0.11), face)
        shape(root, "Head", (0, -0.015, 1.62 + h), (0.112, 0.115, 0.151), face)
        shape(root, "Hair", (0, 0.005, 1.70 + h), (0.116, 0.115, 0.089), hair)
        shape(root, "Nose", (0, -0.122, 1.61 + h), (0.026, 0.038, 0.04), face)
        for side in (-1, 1):
            shoulder = (side * 0.194, 0, 1.37 + h)
            elbow = (side * 0.244, -0.055, 1.12 + h)
            hand = (side * 0.145, -0.185, 1.30 + h)
            if role in ("Bass", "Guitar"):
                hand = (
                    (side * 0.22, -0.17, 1.22 + h)
                    if side > 0
                    else (-0.03, -0.25, 1.02 + h)
                )
            limb(root, "Sleeve", shoulder, elbow, 0.074, shirt)
            limb(root, "Forearm", elbow, hand, 0.050, face)
            shape(root, "Hand", hand, (0.054, 0.04, 0.059), face)
            hip = (side * 0.095, 0.02, 0.88 + h)
            knee = (side * 0.14, -0.31 if seated else -0.025, 0.47)
            foot = (side * 0.17, -0.23 if seated else 0.01, 0.10)
            limb(root, "Thigh", hip, knee, 0.095, denim)
            limb(root, "Shin", knee, foot, 0.072, denim)
            shape(
                root,
                "Shoe",
                (foot[0], foot[1] - 0.04, 0.073),
                (0.09, 0.155, 0.067),
                hair,
            )
        if role in ("Bass", "Guitar"):
            body = shape(
                root,
                "Instrument body",
                (-0.035, -0.185, 1.0),
                (0.158, 0.047, 0.20),
                wood,
            )
            body.rotation_euler.y = -0.4
            limb(
                root,
                "Instrument neck",
                (0.045, -0.183, 1.075),
                (0.52, -0.178, 1.355),
                0.022,
                wood,
            )
        elif seated:
            for side in (-1, 1):
                limb(
                    root,
                    "Drumstick",
                    (side * 0.145, -0.185, 1.30 + h),
                    (side * 0.30, -0.46, 1.24 + h),
                    0.009,
                    wood,
                )


def camera(name, position, target, lens, group):
    data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, data)
    group.objects.link(cam)
    cam.location = position
    cam.rotation_euler = (
        (Vector(target) - Vector(position)).to_track_quat("-Z", "Y").to_euler()
    )
    data.lens = lens
    return cam


def area(name, location, target, power, color, size, group):
    light = bpy.data.lights.new(name, "AREA")
    obj = bpy.data.objects.new(name, light)
    group.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (
        (Vector(target) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    )
    light.energy = power
    light.color = color
    light.shape = "DISK"
    light.size = size
    light.volume_factor = 0
    return obj


def rig(dmx, demo):
    with zipfile.ZipFile(demo) as archive:
        for profile in ("MAC Ultra Performance", "MAC Aura XB"):
            name = f"Martin Professional@{profile}.gdtf"
            destination = Path(dmx.get_addon_path()) / "assets/profiles" / name
            data = archive.read(name)
            try:
                with destination.open("xb") as dst:
                    dst.write(data)
            except FileExistsError:
                if destination.read_bytes() != data:
                    raise FileExistsError(
                        f"A different fixture profile exists at {destination}."
                    ) from None
    rows = [
        (range(1, 5), (-3, -1, 1, 3), 6, 7, "MAC Ultra Performance", "Basic", 1, 48),
        (
            range(101, 105),
            (-4.5, -1.5, 1.5, 4.5),
            -2,
            6,
            "MAC Aura XB",
            "Standard",
            193,
            14,
        ),
        (range(105, 109), (-4, -2, 2, 4), 6, 7, "MAC Aura XB", "Standard", 249, 14),
    ]
    focuses = {}
    for ids, xs, y, z, profile, mode, first, footprint in rows:
        for i, (fid, x) in enumerate(zip(ids, xs)):
            name = f"Martin Professional@{profile}.gdtf"
            address = first + i * footprint
            mover = fid < 100
            target = (
                (-x * 1.1, 0.8, 0.35)
                if mover
                else (x * 0.75, 2.1 if y < 0 else 2.8, 0.75)
            )
            focuses[fid] = target
            dmx.addFixture(
                name,
                mode,
                [SimpleNamespace(universe=0, address=address, dmx_break=1)],
                (1, 1, 1, 1),
                True,
                True,
                position=Matrix.Translation((x, y, z)),
                focus_point=Matrix.Translation(target),
                fixture_id=str(fid),
                fixture_id_numeric=fid,
                user_fixture_name=f"{fid} {profile}",
                show_error=False,
            )
            fixture = dmx.fixtures[-1]
            assert fixture.dmx_breaks[0].channels_count == footprint
            # BlenderDMX supplies a spotlight, a moving head, and a focus target.
            lamp = fixture.lights[0].object
            lamp.data.use_nodes = False
            lamp.data.spot_size = math.radians(8.5 if mover else 49)
            lamp.data.spot_blend = 0.23 if mover else 0.80
            lamp.data.shadow_soft_size = 0.05
            lamp.data.name = f"{fid} | {profile}"
            fixture.objects["Target"].object.name = f"Focus {fid}"
    # The add-on initializes pan/tilt values as subsequent fixtures are added.
    # Set each world-space focus after the full patch exists.
    for fixture in dmx.fixtures:
        fid = int(fixture.fixture_id)
        fixture.ignore_movement_dmx = True
        fixture.objects["Target"].object.matrix_world = Matrix.Translation(focuses[fid])
        for obj in fixture.collection.objects:
            if obj.type == "MESH":
                obj.visible_shadow = False
    bpy.context.view_layer.update()
    return [(int(f.fixture_id), f) for f in dmx.fixtures]


def looks(units):
    for frame in (1, 2):
        for fid, fixture in units:
            lamp = fixture.lights[0].object.data
            if fid < 100:
                color = (0.024, 0.53, 1) if fid in (1, 4) else (0.018, 0.20, 1)
                energy = 28000 if frame == 2 else 0
            elif fid < 105:
                color, energy = (1, 0.57, 0.30), 550
            else:
                color, energy = (
                    ((1, 0.22, 0.04), 1700)
                    if frame == 1
                    else ((0.44, 0.12, 0.95), 2000)
                )
            lamp.energy = energy
            lamp.color = color
            for prop in ("energy", "color"):
                lamp.keyframe_insert(data_path=prop, frame=frame)
            for member in fixture.emitter_materials:
                shader = next(
                    n for n in member.material.node_tree.nodes if n.type == "EMISSION"
                )
                for prop, val in (
                    ("Color", (*color, 1)),
                    ("Strength", 4.0 if energy else 0.0),
                ):
                    socket = shader.inputs[prop]
                    socket.default_value = val
                    socket.keyframe_insert(data_path="default_value", frame=frame)


def overhead_labels(units):
    labels = collection("Rig plan annotations")
    ink = bpy.data.materials.new("Rig plan | white lettering")
    ink.use_nodes = True
    tree = ink.node_tree
    emit = tree.nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = (0.80, 0.89, 1.0, 1)
    emit.inputs["Strength"].default_value = 2.2
    tree.links.new(emit.outputs[0], tree.nodes["Material Output"].inputs["Surface"])

    def label(name, x, y, size):
        text = bpy.data.curves.new(name, "FONT")
        text.body = name
        text.size = size
        text.align_x = "CENTER"
        obj = geometry(name, text, ink, labels)
        obj.location = (x, y, 8.1)

    for fid, fixture in units:
        root = fixture.objects["Root"].object
        x, y, _ = root.matrix_world.translation
        label(str(fid), x, y - 0.53, 0.30)
    label("UPSTAGE", 0, 6.68, 0.25)
    label("AUDIENCE", 0, -3.48, 0.25)
    labels.hide_render = True
    labels.hide_viewport = True
    return labels


def prepare_render():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 40
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.cycles.volume_bounces = 1
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 750
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.color = (0.02, 0.02, 0.02)
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.065,
        0.078,
        0.10,
        1,
    )
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.14
    group = collection("Views and photographic fill")
    audience = camera("Audience", (0, -18, 7), (0, 2, 3), 36, group)
    overhead = camera("Overhead rig plan", (0, 2, 20), (0, 2, 0), 30, group)
    overhead.rotation_euler = (0, 0, 0)
    overhead.data.type = "ORTHO"
    overhead.data.ortho_scale = 18.5
    area(
        "Ambient venue bounce",
        (0, -5.5, 8.8),
        (0, 3, 2),
        300,
        (0.63, 0.70, 1),
        9,
        group,
    )
    plan_light = area(
        "Work light | overhead plan",
        (0, 1, 14),
        (0, 2, 0),
        1600,
        (0.95, 0.96, 1),
        12,
        group,
    )
    plan_light.hide_render = True
    fog = material("Fine theatrical haze", (1, 1, 1))
    tree = fog.node_tree
    tree.nodes.remove(tree.nodes["Principled BSDF"])
    scatter = tree.nodes.new("ShaderNodeVolumeScatter")
    scatter.inputs["Density"].default_value = 0.032
    scatter.inputs["Anisotropy"].default_value = 0.25
    tree.links.new(scatter.outputs[0], tree.nodes["Material Output"].inputs["Volume"])
    haze = box("Haze volume", (0, 2, 4), (16, 15, 9), fog, group)
    haze.display_type = "WIRE"
    scene.camera = audience
    return audience, overhead, plan_light, haze


def render(out, name):
    bpy.context.scene.render.filepath = str(out / name)
    bpy.ops.render.render(write_still=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument(
        "--demo",
        type=Path,
        default=Path.home()
        / "MALightingTechnology/gma3_2.5.1/shared/resource/lib_mvr/Demostage_MVR.mvr",
    )
    parser.add_argument(
        "--draft", action="store_true", help="Make smaller preview images"
    )
    args = parser.parse_args(
        sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    )
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    output_names = ("Stage.blend", "amber.png", "crossed-blue.png", "overhead.png")
    if any((out / name).exists() for name in output_names):
        raise FileExistsError(
            f"Choose a fresh output folder to protect files in {out}."
        )
    scene = bpy.context.scene
    if not hasattr(scene, "dmx"):
        raise RuntimeError("Enable BlenderDMX 2.3.2 before running the stage builder.")
    if scene.dmx.collection:
        raise RuntimeError("Start with a new empty show to protect existing rig data.")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    scene.dmx.new()
    scene.dmx.copy_default_profiles_to_user_folder()
    scenery()
    performers()
    units = rig(scene.dmx, args.demo)
    looks(units)
    labels = overhead_labels(units)
    audience, overhead, plan_light, haze = prepare_render()
    scene.frame_start = 1
    scene.frame_end = 2
    scene.timeline_markers.new("Amber | stage look", frame=1)
    scene.timeline_markers.new("Crossed blue | stage look", frame=2)
    scene.frame_set(2)
    scene.unit_settings.system = "METRIC"
    for screen in bpy.data.screens:
        for a in screen.areas:
            if a.type == "VIEW_3D":
                a.spaces.active.region_3d.view_perspective = "CAMERA"
                a.spaces.active.overlay.show_overlays = False
                a.spaces.active.shading.type = "RENDERED"
    if args.draft:
        scene.render.resolution_percentage = 50
        scene.cycles.samples = 6
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = None
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "Stage.blend"), compress=True)
    for frame, name in ((1, "amber.png"), (2, "crossed-blue.png")):
        scene.frame_set(frame)
        render(out, name)
    labels.hide_viewport = False
    labels.hide_render = False
    scene.camera = overhead
    plan_light.hide_render = False
    haze.hide_render = True
    scene.frame_set(1)
    render(out, "overhead.png")
    print(
        "Built a 12-fixture stage with two looks and an overhead rig view.", flush=True
    )


if __name__ == "__main__":
    main()

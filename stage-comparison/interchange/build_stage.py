# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = ["trimesh==5.2.1", "numpy==2.3.2", "scipy==1.18.1", "pillow==13.0.0"]
# ///
"""Rebuild the fixed RayFlow comparison stage from grandMA3's demo MVR."""

import argparse
from io import BytesIO
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

import trimesh

MOVER = "Martin Professional@MAC Ultra Performance"
WASH = "Martin Professional@MAC Aura XB"


def uid(label):
    return str(uuid5(NAMESPACE_URL, "rayflow:comparison:" + label)).upper()


def position(element, xyz):
    translation = ",".join(f"{v * 1000:g}" for v in xyz)
    ET.SubElement(element, "Matrix").text = "{1,0,0}{0,1,0}{0,0,1}{" + translation + "}"


def scene_xml():
    root = ET.Element("GeneralSceneDescription", verMajor="1", verMinor="5")
    ET.SubElement(root, "UserData")
    scene = ET.SubElement(root, "Scene")
    layers = ET.SubElement(scene, "Layers")
    layer = ET.SubElement(
        layers, "Layer", name="RayFlow Concert Stage", uuid=uid("layer")
    )
    objects = ET.SubElement(layer, "ChildList")
    aux = ET.SubElement(scene, "AUXData")

    for model in ("Deck", "Riser", "Truss"):
        symbol = ET.SubElement(aux, "Symdef", uuid=uid("model-" + model), name=model)
        ET.SubElement(
            ET.SubElement(symbol, "ChildList"), "Geometry3D", fileName=model + ".glb"
        )

    scenery = [
        ("Concert deck", "Deck", (0, 2, -0.2)),
        ("Drum riser", "Riser", (0, 5, 0.225)),
        ("Downstage truss", "Truss", (0, -2, 6)),
        ("Upstage truss", "Truss", (0, 6, 7)),
    ]
    for name, model, xyz in scenery:
        obj = ET.SubElement(objects, "SceneObject", uuid=uid(name), name=name)
        position(obj, xyz)
        geometries = ET.SubElement(obj, "Geometries")
        ET.SubElement(
            geometries,
            "Symbol",
            uuid=uid(name + "-instance"),
            symdef=uid("model-" + model),
        )

    fixtures = [
        (i + 1, MOVER, "Basic", 1 + 48 * i, (x, 6, 7))
        for i, x in enumerate((-3, -1, 1, 3))
    ]
    for i, x in enumerate((-4.5, -1.5, 1.5, 4.5, -4, -2, 2, 4)):
        xyz = (x, -2, 6) if i < 4 else (x, 6, 7)
        fixtures.append((101 + i, WASH, "Standard", 193 + 14 * i, xyz))

    for fid, profile, mode, slot, xyz in fixtures:
        name = f"Spot {fid}" if profile == MOVER else f"Wash {fid}"
        fixture = ET.SubElement(objects, "Fixture", uuid=uid(name), name=name)
        position(fixture, xyz)
        ET.SubElement(fixture, "GDTFSpec").text = profile
        ET.SubElement(fixture, "GDTFMode").text = mode
        addresses = ET.SubElement(fixture, "Addresses")
        ET.SubElement(addresses, "Address", {"break": "0"}).text = str(slot)
        ET.SubElement(fixture, "FixtureID").text = str(fid)
        ET.SubElement(fixture, "UnitNumber").text = "0"
    ET.indent(root)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def make_truss(reference):
    description = ET.fromstring(reference.read("GeneralSceneDescription.xml"))
    geometry = description.find(".//Symdef[@name='Symbol 5']/ChildList/Geometry3D")
    if geometry is None:
        raise ValueError("The demo stage is missing the Symbol 5 truss mesh.")
    data = reference.read(geometry.attrib["fileName"])
    mesh = trimesh.load_scene(BytesIO(data), file_type="glb").to_geometry()
    # In a glTF mesh Y points up. Put the underside at fixture hang height.
    mesh.apply_translation(
        [-mesh.bounds[0, 0], -mesh.bounds[0, 1], -mesh.bounds.mean(axis=0)[2]]
    )
    mesh.apply_scale([2.75 / mesh.extents[0], 1, 1])
    bays = []
    for i in range(4):
        bay = mesh.copy()
        bay.apply_translation([2.75 * i - 5.5, 0, 0])
        bays.append(bay)
    return trimesh.util.concatenate(bays).export(file_type="glb")


def build(source, output):
    assets = {"GeneralSceneDescription.xml": scene_xml()}
    for model, size, color in [
        ("Deck", (12, 0.4, 10), [60, 64, 71, 255]),
        ("Riser", (3, 0.45, 2), [88, 90, 96, 255]),
    ]:
        mesh = trimesh.creation.box(extents=size)
        mesh.visual.vertex_colors = color
        assets[model + ".glb"] = mesh.export(file_type="glb")
    with ZipFile(source) as reference:
        assets["Truss.glb"] = make_truss(reference)
        for name in (MOVER, WASH):
            assets[name + ".gdtf"] = reference.read(name + ".gdtf")
    with ZipFile(output, "x", compression=ZIP_DEFLATED) as archive:
        for name, data in assets.items():
            archive.writestr(name, data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="MA's Demostage_MVR.mvr")
    parser.add_argument("output", type=Path, help="new .mvr path")
    args = parser.parse_args()
    build(args.source, args.output)

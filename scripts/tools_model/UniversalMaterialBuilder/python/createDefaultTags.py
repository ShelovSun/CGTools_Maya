import json
import os

def resetTags():
    script_path = os.path.realpath(__file__)
    script_path = script_path.rsplit("\\",2)[0]
    tags_path = script_path + "\\util\\tags.json"
    tags = {}

    tags["diffuse"] = ["diffuse","color","albedo"]
    tags["ao"] = ["ambient", "ao", "occlusion"]
    tags["reflection"] = ["reflection","refl","specular"]
    tags["roughness"] = ["roughness", "ruff", "gloss", "glossiness"]
    tags["metalness"] = ["metal", "metalness"]
    tags["refraction"] = ["refraction", "refr"]
    tags["subsurface"] = ["sss", "subsurface"]
    tags["bump"] = ["bump", "height"]
    tags["normal"] = ["normal", "norm"]
    tags["displacement"] = ["displacement", "disp"]
    tags["emission"] = ["emission", "emissive"]
    tags["opacity"] = ["opacity", "alpha", "cutout"]


    with open(tags_path, 'w') as tagsFile:
        json.dump(tags, tagsFile, indent=4)


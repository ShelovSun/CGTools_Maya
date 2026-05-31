def createRsMaterial():
    # Import Modules
    import maya.cmds as cmds
    import json
    import os

    # Set Path
    script_path = os.path.realpath(__file__)
    script_path = script_path.rsplit("\\", 2)[0]
    materialInformation_path = script_path + "\\util\\material_information_tmp.json"

    redshiftVersion = cmds.pluginInfo("redshift4maya", q = True, version = True) #3.5.03
    redshiftVersion = redshiftVersion.split(".")

    materialSelection = "RedshiftMaterial"
    if int(redshiftVersion[0]) >= 3 and int(redshiftVersion[1]) >= 5: 
        materialSelection = "RedshiftStandardMaterial"

    # Get Information
    sel = cmds.ls(selection=True)
    with open(materialInformation_path) as json_file:
        information_dict = json.load(json_file)
        for dict in information_dict:
            if dict == "material_dict":
                name = information_dict[dict]["name"]
                rgbColorSpace = information_dict['material_dict']['rgbColorSpace']
                rawColorSpace = information_dict['material_dict']['rawColorSpace']
                udim = information_dict['material_dict']['udim']
                udimMethode = information_dict['material_dict']['udimMethode'] + 1
                assignMaterial = information_dict['material_dict']['assignMaterial']
                fullControl = information_dict['material_dict']['fullControl']

            if dict == "diffuse_dict":
                diffuseName = information_dict[dict]["name"]
                diffusePath = information_dict[dict]["path"]

            if dict == "ao_dict":
                aoName = information_dict[dict]["name"]
                aoPath = information_dict[dict]["path"]

            if dict == "reflection_dict":
                reflectionName = information_dict[dict]["name"]
                reflectionPath = information_dict[dict]["path"]

            if dict == "roughness_dict":
                roughnessName = information_dict[dict]["name"]
                roughnessPath = information_dict[dict]["path"]

            if dict == "metalness_dict":
                metalnessName = information_dict[dict]["name"]
                metalnessPath = information_dict[dict]["path"]

            if dict == "refraction_dict":
                refractionName = information_dict[dict]["name"]
                refractionPath = information_dict[dict]["path"]

            if dict == "subsurface_dict":
                subsurfaceName = information_dict[dict]["name"]
                subsurfacePath = information_dict[dict]["path"]

            if dict == "bump_dict":
                bumpName = information_dict[dict]["name"]
                bumpPath = information_dict[dict]["path"]

            if dict == "normal_dict":
                normalName = information_dict[dict]["name"]
                normalPath = information_dict[dict]["path"]

            if dict == "displacement_dict":
                displacementName = information_dict[dict]["name"]
                displacementPath = information_dict[dict]["path"]

            if dict == "emission_dict":
                emissionName = information_dict[dict]["name"]
                emissionPath = information_dict[dict]["path"]

            if dict == "opacity_dict":
                opacityName = information_dict[dict]["name"]
                opacityPath = information_dict[dict]["path"]


    if materialSelection == "RedshiftMaterial":
        # create Material
        rsMaterial = cmds.shadingNode("RedshiftMaterial", asShader=True, n=name)
        rsMaterialSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, n=name + "_SG")
        cmds.connectAttr('%s.outColor' % rsMaterial, '%s.surfaceShader' % rsMaterialSG)

        channelFileList = []

        # create diffuse
        if "diffuse_dict" in information_dict:
            diffuseFile = cmds.shadingNode("file", asTexture=True, n=diffuseName)
            cmds.setAttr(diffuseFile + ".colorSpace", rgbColorSpace, type="string")
            cmds.setAttr(diffuseFile + ".ignoreColorSpaceFileRules", 1)
            cmds.setAttr(diffuseFile + ".fileTextureName", diffusePath, typ="string")
            channelFileList.append(diffuseFile)
            if fullControl:
                diffuse_cc = cmds.shadingNode("RedshiftColorCorrection", asTexture=True, n="diffuse_cc")
                cmds.connectAttr(diffuseFile + ".outColor", diffuse_cc + ".input")
                cmds.connectAttr(diffuse_cc + ".outColor", rsMaterial + ".diffuse_color")

            else:
                cmds.connectAttr(diffuseFile + ".outColor", rsMaterial + ".diffuse_color")

        # create ao
        if "ao_dict" in information_dict:
            aoFile = cmds.shadingNode("file", asTexture=True, n=aoName)
            cmds.setAttr(aoFile + ".fileTextureName", aoPath, typ="string")
            cmds.setAttr(aoFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(aoFile + ".alphaIsLuminance", 1)
            cmds.setAttr(aoFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(aoFile)
            if fullControl:
                ao_remap = cmds.shadingNode("remapValue", asUtility=True, n="ao_remap")
                cmds.connectAttr(aoFile + ".outAlpha", ao_remap + ".inputValue")
                cmds.connectAttr(ao_remap + ".outValue", rsMaterial + ".diffuse_weight")

            else:
                cmds.connectAttr(aoFile + ".outAlpha", rsMaterial + ".diffuse_weight")

        # create reflection
        if "reflection_dict" in information_dict:
            reflectionFile = cmds.shadingNode("file", asTexture=True, n=reflectionName)
            cmds.setAttr(reflectionFile + ".fileTextureName", reflectionPath, typ="string")
            cmds.setAttr(reflectionFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(reflectionFile + ".alphaIsLuminance", 1)
            cmds.setAttr(reflectionFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(reflectionFile)
            if fullControl:
                reflection_remap = cmds.shadingNode("remapValue", asUtility=True, n="reflection_remap")
                cmds.connectAttr(reflectionFile + ".outAlpha", reflection_remap + ".inputValue")
                cmds.connectAttr(reflection_remap + ".outValue", rsMaterial + ".refl_weight")

            else:
                cmds.connectAttr(reflectionFile + ".outAlpha", rsMaterial + ".refl_weight")

        # create roughness
        if "roughness_dict" in information_dict:
            roughnessFile = cmds.shadingNode("file", asTexture=True, n=roughnessName)
            cmds.setAttr(roughnessFile + ".fileTextureName", roughnessPath, typ="string")
            cmds.setAttr(roughnessFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(roughnessFile + ".alphaIsLuminance", 1)
            cmds.setAttr(roughnessFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(roughnessFile)
            if fullControl:
                roughness_remap = cmds.shadingNode("remapValue", asUtility=True, n="roughness_remap")
                cmds.connectAttr(roughnessFile + ".outAlpha", roughness_remap + ".inputValue")
                cmds.connectAttr(roughness_remap + ".outValue", rsMaterial + ".refl_roughness")

            else:
                cmds.connectAttr(roughnessFile + ".outAlpha", rsMaterial + ".refl_roughness")

        # create metalness
        if "metalness_dict" in information_dict:
            metalnessFile = cmds.shadingNode("file", asTexture=True, n=metalnessName)
            cmds.setAttr(metalnessFile + ".fileTextureName", metalnessPath, typ="string")
            cmds.setAttr(metalnessFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(metalnessFile + ".alphaIsLuminance", 1)
            cmds.setAttr(metalnessFile + ".ignoreColorSpaceFileRules", 1)
            cmds.setAttr(rsMaterial + ".refl_fresnel_mode", 2)
            channelFileList.append(metalnessFile)
            if fullControl:
                metalness_remap = cmds.shadingNode("remapValue", asUtility=True, n="metalness_remap")
                cmds.connectAttr(metalnessFile + ".outAlpha", metalness_remap + ".inputValue")
                cmds.connectAttr(metalness_remap + ".outValue", rsMaterial + ".refl_metalness")

            else:
                cmds.connectAttr(metalnessFile + ".outAlpha", rsMaterial + ".refl_metalness")

        # create refraction
        if "refraction_dict" in information_dict:
            refractionFile = cmds.shadingNode("file", asTexture=True, n=refractionName)
            cmds.setAttr(refractionFile + ".fileTextureName", refractionPath, typ="string")
            cmds.setAttr(refractionFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(refractionFile + ".alphaIsLuminance", 1)
            cmds.setAttr(refractionFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(refractionFile)
            if fullControl:
                refraction_remap = cmds.shadingNode("remapValue", asUtility=True, n="refraction_remap")
                cmds.connectAttr(refractionFile + ".outAlpha", refraction_remap + ".inputValue")
                cmds.connectAttr(refraction_remap + ".outValue", rsMaterial + ".refr_weight")

            else:
                cmds.connectAttr(refractionFile + ".outAlpha", rsMaterial + ".refr_weight")

        # create subsurface
        if "subsurface_dict" in information_dict:
            cmds.setAttr(rsMaterial + ".ms_amount", 1)
            subsurfaceFile = cmds.shadingNode("file", asTexture=True, n=subsurfaceName)
            cmds.setAttr(subsurfaceFile + ".colorSpace", rgbColorSpace, type="string")
            cmds.setAttr(subsurfaceFile + ".ignoreColorSpaceFileRules", 1)
            cmds.setAttr(subsurfaceFile + ".fileTextureName", subsurfacePath, typ="string")
            channelFileList.append(subsurfaceFile)
            if fullControl:
                subsurface_cc = cmds.shadingNode("RedshiftColorCorrection", asTexture=True, n="subsurface_cc")
                cmds.connectAttr(subsurfaceFile + ".outColor", subsurface_cc + ".input")
                cmds.connectAttr(subsurface_cc + ".outColor", rsMaterial + ".ms_color0")

            else:
                cmds.connectAttr(subsurfaceFile + ".outColor", rsMaterial + ".ms_color0")

        # create bump
        if "bump_dict" in information_dict:
            bumpFile = cmds.shadingNode("file", asTexture=True, n=bumpName)
            bumpNode = cmds.shadingNode("RedshiftBumpMap", asTexture=True, n=bumpName + "_bumpNode")
            cmds.setAttr(bumpFile + ".fileTextureName", bumpPath, typ="string")
            cmds.setAttr(bumpFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(bumpFile + ".alphaIsLuminance", 1)
            cmds.setAttr(bumpFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(bumpFile)
            if fullControl:
                bump_remap = cmds.shadingNode("remapHsv", asUtility=True, n="bump_remap")
                cmds.connectAttr(bumpFile + ".outColor", bump_remap + ".color")
                cmds.connectAttr(bump_remap + ".outColor", bumpNode + ".input")

            else:
                cmds.connectAttr(bumpFile + ".outColor", bumpNode + ".input")

            cmds.connectAttr(bumpNode + ".out", rsMaterial + ".bump_input")

        # create normal
        if "normal_dict" in information_dict:
            normalFile = cmds.shadingNode("file", asTexture=True, n=normalName)
            normalNode = cmds.shadingNode("RedshiftBumpMap", asTexture=True, n=normalName + "_normalNode")
            cmds.setAttr(normalNode + ".scale", 1)
            cmds.setAttr(normalNode + ".inputType", 1)
            cmds.setAttr(normalFile + ".fileTextureName", normalPath, typ="string")
            cmds.setAttr(normalFile + ".colorSpace", rawColorSpace, type="string")
            cmds.connectAttr(normalFile + ".outColor", normalNode + ".input")
            cmds.setAttr(normalFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(normalFile)
            if "bump_dict" not in information_dict:
                cmds.connectAttr(normalNode + ".out", rsMaterial + ".bump_input")

            if "bump_dict" in information_dict:
                bumpBlenderNode = cmds.shadingNode("RedshiftBumpBlender", asTexture = True, n=normalFile + "_bump_blender")
                cmds.connectAttr(bumpBlenderNode + ".outColor", rsMaterial + ".bump_input", force=True)
                cmds.connectAttr(normalNode + ".out", bumpBlenderNode + ".baseInput", force=True)
                cmds.connectAttr(bumpNode + ".out", bumpBlenderNode + ".bumpInput0", force=True)
                cmds.setAttr(bumpBlenderNode + ".bumpWeight0", 1)
                cmds.setAttr(bumpBlenderNode + ".additive", 1)

        # create displacement
        if "displacement_dict" in information_dict:
            displacementFile = cmds.shadingNode("file", asTexture=True, n=displacementName)
            displacementNode = cmds.shadingNode("RedshiftDisplacement", asShader=True, n=displacementName + "_displacementNode")
            cmds.setAttr(displacementFile + ".fileTextureName", displacementPath, typ="string")
            cmds.setAttr(displacementFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(displacementFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(displacementFile)
            if fullControl:
                displacement_remap = cmds.shadingNode("remapHsv", asUtility=True, n="displacement_remap")
                cmds.connectAttr(displacementFile + ".outColor", displacement_remap + ".color")
                cmds.connectAttr(displacement_remap + ".outColor", displacementNode + ".texMap")

            else:
                cmds.connectAttr(displacementFile + ".outColor", displacementNode + ".texMap")


            cmds.connectAttr(displacementNode + ".out", rsMaterialSG + ".rsDisplacementShader")

        # create emission
        if "emission_dict" in information_dict:
            emissionFile = cmds.shadingNode("file", asTexture=True, n=emissionName)
            cmds.setAttr(emissionFile + ".fileTextureName", emissionPath, typ="string")
            cmds.setAttr(emissionFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(emissionFile + ".alphaIsLuminance", 1)
            cmds.setAttr(emissionFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(emissionFile)

            if fullControl:
                emission_cc = cmds.shadingNode("RedshiftColorCorrection", asTexture=True, n="emission_cc")
                cmds.connectAttr(emissionFile + ".outColor", emission_cc + ".input")
                cmds.connectAttr(emission_cc + ".outColor", rsMaterial + ".emission_color")

            else:
                cmds.connectAttr(emissionFile + ".outColor", rsMaterial + ".emission_color")

        # create opacity
        if "opacity_dict" in information_dict:
            opacityFile = cmds.shadingNode("file", asTexture=True, n=opacityName)
            cmds.setAttr(opacityFile + ".fileTextureName", opacityPath, typ="string")
            cmds.setAttr(opacityFile + ".colorSpace", rgbColorSpace, type="string")
            cmds.setAttr(opacityFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(opacityFile)

            if fullControl:
                opacity_cc = cmds.shadingNode("RedshiftColorCorrection", asTexture=True, n="opacity_cc")
                cmds.connectAttr(opacityFile + ".outColor", opacity_cc + ".input")
                cmds.connectAttr(opacity_cc + ".outColor", rsMaterial + ".opacity_color")

            else:
                cmds.connectAttr(opacityFile + ".outColor", rsMaterial + ".opacity_color")

        # Check Udim
        if udim:
            for f in channelFileList:
                cmds.setAttr(f + ".uvTilingMode", udimMethode)

        # Assign Material
        if assignMaterial == 1:
            if len(sel) > 0:
                cmds.sets(sel, edit=True, forceElement=rsMaterialSG)

        # create 2D Texture Node and connect to each in textureFileList
        if len(channelFileList) > 0:
            p2d = cmds.shadingNode('place2dTexture', name="place2d", asUtility=True)
        for channelFiles in channelFileList:
            cmds.connectAttr(p2d + ".outUV", channelFiles + ".uvCoord")
            cmds.connectAttr(p2d + ".outUvFilterSize", channelFiles + ".uvFilterSize")
            cmds.connectAttr(p2d + ".vertexCameraOne", channelFiles + ".vertexCameraOne")
            cmds.connectAttr(p2d + ".vertexUvOne", channelFiles + ".vertexUvOne")
            cmds.connectAttr(p2d + ".vertexUvThree", channelFiles + ".vertexUvThree")
            cmds.connectAttr(p2d + ".vertexUvTwo", channelFiles + ".vertexUvTwo")
            cmds.connectAttr(p2d + ".coverage", channelFiles + ".coverage")
            cmds.connectAttr(p2d + ".mirrorU", channelFiles + ".mirrorU")
            cmds.connectAttr(p2d + ".mirrorV", channelFiles + ".mirrorV")
            cmds.connectAttr(p2d + ".noiseUV", channelFiles + ".noiseUV")
            cmds.connectAttr(p2d + ".offset", channelFiles + ".offset")
            cmds.connectAttr(p2d + ".repeatUV", channelFiles + ".repeatUV")
            cmds.connectAttr(p2d + ".rotateFrame", channelFiles + ".rotateFrame")
            cmds.connectAttr(p2d + ".rotateUV", channelFiles + ".rotateUV")
            cmds.connectAttr(p2d + ".stagger", channelFiles + ".stagger")
            cmds.connectAttr(p2d + ".translateFrame", channelFiles + ".translateFrame")
            cmds.connectAttr(p2d + ".wrapU", channelFiles + ".wrapU")
            cmds.connectAttr(p2d + ".wrapV", channelFiles + ".wrapV")




    if materialSelection == "RedshiftStandardMaterial":
        # create Material
        rsMaterial = cmds.shadingNode("RedshiftStandardMaterial", asShader=True, n=name)
        rsMaterialSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, n=name + "_SG")
        cmds.connectAttr('%s.outColor' % rsMaterial, '%s.surfaceShader' % rsMaterialSG)

        channelFileList = []

        # create diffuse
        if "diffuse_dict" in information_dict:
            diffuseFile = cmds.shadingNode("file", asTexture=True, n=diffuseName)
            cmds.setAttr(diffuseFile + ".colorSpace", rgbColorSpace, type="string")
            cmds.setAttr(diffuseFile + ".ignoreColorSpaceFileRules", 1)
            cmds.setAttr(diffuseFile + ".fileTextureName", diffusePath, typ="string")
            channelFileList.append(diffuseFile)
            if fullControl:
                diffuse_cc = cmds.shadingNode("RedshiftColorCorrection", asTexture=True, n="diffuse_cc")
                cmds.connectAttr(diffuseFile + ".outColor", diffuse_cc + ".input")
                cmds.connectAttr(diffuse_cc + ".outColor", rsMaterial + ".base_color")

            else:
                cmds.connectAttr(diffuseFile + ".outColor", rsMaterial + ".base_color")

        # create ao
        if "ao_dict" in information_dict:
            aoFile = cmds.shadingNode("file", asTexture=True, n=aoName)
            cmds.setAttr(aoFile + ".fileTextureName", aoPath, typ="string")
            cmds.setAttr(aoFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(aoFile + ".alphaIsLuminance", 1)
            cmds.setAttr(aoFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(aoFile)
            if fullControl:
                ao_remap = cmds.shadingNode("remapValue", asUtility=True, n="ao_remap")
                cmds.connectAttr(aoFile + ".outAlpha", ao_remap + ".inputValue")
                cmds.connectAttr(ao_remap + ".outValue", rsMaterial + ".base_color_weight")

            else:
                cmds.connectAttr(aoFile + ".outAlpha", rsMaterial + ".base_color_weight")

        # create reflection
        if "reflection_dict" in information_dict:
            reflectionFile = cmds.shadingNode("file", asTexture=True, n=reflectionName)
            cmds.setAttr(reflectionFile + ".fileTextureName", reflectionPath, typ="string")
            cmds.setAttr(reflectionFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(reflectionFile + ".alphaIsLuminance", 1)
            cmds.setAttr(reflectionFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(reflectionFile)
            if fullControl:
                reflection_remap = cmds.shadingNode("remapValue", asUtility=True, n="reflection_remap")
                cmds.connectAttr(reflectionFile + ".outAlpha", reflection_remap + ".inputValue")
                cmds.connectAttr(reflection_remap + ".outValue", rsMaterial + ".refl_weight")

            else:
                cmds.connectAttr(reflectionFile + ".outAlpha", rsMaterial + ".refl_weight")

        # create roughness
        if "roughness_dict" in information_dict:
            roughnessFile = cmds.shadingNode("file", asTexture=True, n=roughnessName)
            cmds.setAttr(roughnessFile + ".fileTextureName", roughnessPath, typ="string")
            cmds.setAttr(roughnessFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(roughnessFile + ".alphaIsLuminance", 1)
            cmds.setAttr(roughnessFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(roughnessFile)
            if fullControl:
                roughness_remap = cmds.shadingNode("remapValue", asUtility=True, n="roughness_remap")
                cmds.connectAttr(roughnessFile + ".outAlpha", roughness_remap + ".inputValue")
                cmds.connectAttr(roughness_remap + ".outValue", rsMaterial + ".refl_roughness")

            else:
                cmds.connectAttr(roughnessFile + ".outAlpha", rsMaterial + ".refl_roughness")

        # create metalness
        if "metalness_dict" in information_dict:
            metalnessFile = cmds.shadingNode("file", asTexture=True, n=metalnessName)
            cmds.setAttr(metalnessFile + ".fileTextureName", metalnessPath, typ="string")
            cmds.setAttr(metalnessFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(metalnessFile + ".alphaIsLuminance", 1)
            cmds.setAttr(metalnessFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(metalnessFile)
            if fullControl:
                metalness_remap = cmds.shadingNode("remapValue", asUtility=True, n="metalness_remap")
                cmds.connectAttr(metalnessFile + ".outAlpha", metalness_remap + ".inputValue")
                cmds.connectAttr(metalness_remap + ".outValue", rsMaterial + ".metalness")

            else:
                cmds.connectAttr(metalnessFile + ".outAlpha", rsMaterial + ".metalness")

        # create refraction
        if "refraction_dict" in information_dict:
            refractionFile = cmds.shadingNode("file", asTexture=True, n=refractionName)
            cmds.setAttr(refractionFile + ".fileTextureName", refractionPath, typ="string")
            cmds.setAttr(refractionFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(refractionFile + ".alphaIsLuminance", 1)
            cmds.setAttr(refractionFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(refractionFile)
            if fullControl:
                refraction_remap = cmds.shadingNode("remapValue", asUtility=True, n="refraction_remap")
                cmds.connectAttr(refractionFile + ".outAlpha", refraction_remap + ".inputValue")
                cmds.connectAttr(refraction_remap + ".outValue", rsMaterial + ".refr_weight")

            else:
                cmds.connectAttr(refractionFile + ".outAlpha", rsMaterial + ".refr_weight")

        # create subsurface
        if "subsurface_dict" in information_dict:
            cmds.setAttr(rsMaterial + ".ms_amount", 1)
            subsurfaceFile = cmds.shadingNode("file", asTexture=True, n=subsurfaceName)
            cmds.setAttr(subsurfaceFile + ".colorSpace", rgbColorSpace, type="string")
            cmds.setAttr(subsurfaceFile + ".ignoreColorSpaceFileRules", 1)
            cmds.setAttr(subsurfaceFile + ".fileTextureName", subsurfacePath, typ="string")
            channelFileList.append(subsurfaceFile)
            if fullControl:
                subsurface_cc = cmds.shadingNode("RedshiftColorCorrection", asTexture=True, n="subsurface_cc")
                cmds.connectAttr(subsurfaceFile + ".outColor", subsurface_cc + ".input")
                cmds.connectAttr(subsurface_cc + ".outColor", rsMaterial + ".ms_color")

            else:
                cmds.connectAttr(subsurfaceFile + ".outColor", rsMaterial + ".ms_color")

        # create bump
        if "bump_dict" in information_dict:
            bumpFile = cmds.shadingNode("file", asTexture=True, n=bumpName)
            bumpNode = cmds.shadingNode("RedshiftBumpMap", asTexture=True, n=bumpName + "_bumpNode")
            cmds.setAttr(bumpFile + ".fileTextureName", bumpPath, typ="string")
            cmds.setAttr(bumpFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(bumpFile + ".alphaIsLuminance", 1)
            cmds.setAttr(bumpFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(bumpFile)
            if fullControl:
                bump_remap = cmds.shadingNode("remapHsv", asUtility=True, n="bump_remap")
                cmds.connectAttr(bumpFile + ".outColor", bump_remap + ".color")
                cmds.connectAttr(bump_remap + ".outColor", bumpNode + ".input")

            else:
                cmds.connectAttr(bumpFile + ".outColor", bumpNode + ".input")

            cmds.connectAttr(bumpNode + ".out", rsMaterial + ".bump_input")

        # create normal
        if "normal_dict" in information_dict:
            normalFile = cmds.shadingNode("file", asTexture=True, n=normalName)
            normalNode = cmds.shadingNode("RedshiftBumpMap", asTexture=True, n=normalName + "_normalNode")
            cmds.setAttr(normalNode + ".scale", 1)
            cmds.setAttr(normalNode + ".inputType", 1)
            cmds.setAttr(normalFile + ".fileTextureName", normalPath, typ="string")
            cmds.setAttr(normalFile + ".colorSpace", rawColorSpace, type="string")
            cmds.connectAttr(normalFile + ".outColor", normalNode + ".input")
            cmds.setAttr(normalFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(normalFile)
            if "bump_dict" not in information_dict:
                cmds.connectAttr(normalNode + ".out", rsMaterial + ".bump_input")

            if "bump_dict" in information_dict:
                bumpBlenderNode = cmds.shadingNode("RedshiftBumpBlender", asTexture = True, n=normalFile + "_bump_blender")
                cmds.connectAttr(bumpBlenderNode + ".outColor", rsMaterial + ".bump_input", force=True)
                cmds.connectAttr(normalNode + ".out", bumpBlenderNode + ".baseInput", force=True)
                cmds.connectAttr(bumpNode + ".out", bumpBlenderNode + ".bumpInput0", force=True)
                cmds.setAttr(bumpBlenderNode + ".bumpWeight0", 1)
                cmds.setAttr(bumpBlenderNode + ".additive", 1)

        # create displacement
        if "displacement_dict" in information_dict:
            displacementFile = cmds.shadingNode("file", asTexture=True, n=displacementName)
            displacementNode = cmds.shadingNode("RedshiftDisplacement", asShader=True, n=displacementName + "_displacementNode")
            cmds.setAttr(displacementFile + ".fileTextureName", displacementPath, typ="string")
            cmds.setAttr(displacementFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(displacementFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(displacementFile)
            if fullControl:
                displacement_remap = cmds.shadingNode("remapHsv", asUtility=True, n="displacement_remap")
                cmds.connectAttr(displacementFile + ".outColor", displacement_remap + ".color")
                cmds.connectAttr(displacement_remap + ".outColor", displacementNode + ".texMap")

            else:
                cmds.connectAttr(displacementFile + ".outColor", displacementNode + ".texMap")


            cmds.connectAttr(displacementNode + ".out", rsMaterialSG + ".rsDisplacementShader")

        # create emission
        if "emission_dict" in information_dict:
            emissionFile = cmds.shadingNode("file", asTexture=True, n=emissionName)
            cmds.setAttr(emissionFile + ".fileTextureName", emissionPath, typ="string")
            cmds.setAttr(emissionFile + ".colorSpace", rawColorSpace, type="string")
            cmds.setAttr(emissionFile + ".alphaIsLuminance", 1)
            cmds.setAttr(emissionFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(emissionFile)

            if fullControl:
                emission_cc = cmds.shadingNode("RedshiftColorCorrection", asTexture=True, n="emission_cc")
                cmds.connectAttr(emissionFile + ".outColor", emission_cc + ".input")
                cmds.connectAttr(emission_cc + ".outColor", rsMaterial + ".emission_color")

            else:
                cmds.connectAttr(emissionFile + ".outColor", rsMaterial + ".emission_color")

        # create opacity
        if "opacity_dict" in information_dict:
            opacityFile = cmds.shadingNode("file", asTexture=True, n=opacityName)
            cmds.setAttr(opacityFile + ".fileTextureName", opacityPath, typ="string")
            cmds.setAttr(opacityFile + ".colorSpace", rgbColorSpace, type="string")
            cmds.setAttr(opacityFile + ".ignoreColorSpaceFileRules", 1)
            channelFileList.append(opacityFile)

            if fullControl:
                opacity_cc = cmds.shadingNode("RedshiftColorCorrection", asTexture=True, n="opacity_cc")
                cmds.connectAttr(opacityFile + ".outColor", opacity_cc + ".input")
                cmds.connectAttr(opacity_cc + ".outColor", rsMaterial + ".opacity_color")

            else:
                cmds.connectAttr(opacityFile + ".outColor", rsMaterial + ".opacity_color")

        # Check Udim
        if udim:
            for f in channelFileList:
                cmds.setAttr(f + ".uvTilingMode", udimMethode)

        # Assign Material
        if assignMaterial == 1:
            if len(sel) > 0:
                cmds.sets(sel, edit=True, forceElement=rsMaterialSG)

        # create 2D Texture Node and connect to each in textureFileList
        if len(channelFileList) > 0:
            p2d = cmds.shadingNode('place2dTexture', name="place2d", asUtility=True)
        for channelFiles in channelFileList:
            cmds.connectAttr(p2d + ".outUV", channelFiles + ".uvCoord")
            cmds.connectAttr(p2d + ".outUvFilterSize", channelFiles + ".uvFilterSize")
            cmds.connectAttr(p2d + ".vertexCameraOne", channelFiles + ".vertexCameraOne")
            cmds.connectAttr(p2d + ".vertexUvOne", channelFiles + ".vertexUvOne")
            cmds.connectAttr(p2d + ".vertexUvThree", channelFiles + ".vertexUvThree")
            cmds.connectAttr(p2d + ".vertexUvTwo", channelFiles + ".vertexUvTwo")
            cmds.connectAttr(p2d + ".coverage", channelFiles + ".coverage")
            cmds.connectAttr(p2d + ".mirrorU", channelFiles + ".mirrorU")
            cmds.connectAttr(p2d + ".mirrorV", channelFiles + ".mirrorV")
            cmds.connectAttr(p2d + ".noiseUV", channelFiles + ".noiseUV")
            cmds.connectAttr(p2d + ".offset", channelFiles + ".offset")
            cmds.connectAttr(p2d + ".repeatUV", channelFiles + ".repeatUV")
            cmds.connectAttr(p2d + ".rotateFrame", channelFiles + ".rotateFrame")
            cmds.connectAttr(p2d + ".rotateUV", channelFiles + ".rotateUV")
            cmds.connectAttr(p2d + ".stagger", channelFiles + ".stagger")
            cmds.connectAttr(p2d + ".translateFrame", channelFiles + ".translateFrame")
            cmds.connectAttr(p2d + ".wrapU", channelFiles + ".wrapU")
            cmds.connectAttr(p2d + ".wrapV", channelFiles + ".wrapV")
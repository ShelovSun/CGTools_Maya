import maya.cmds as cmds
import pymel.core as pm
import os
import xml.etree.ElementTree as ET
import maya.mel as mel


class xmlToRedShift():
	
	print('Import as RedShift --------------')
	xmlFile = ''
	fbxFile = ''

	tree = ''
	root = ''

	XMLmaterials = ''
	XMLlights = ''
	XMLcameras = ''
	XMLrenderSettings = ''

	def importFile(self):
		cmds.file( f=True, new=True )
		pm.mel.FBXImport(f=self.fbxFile)

	def setRender(self):
		if not cmds.pluginInfo( 'redshift4maya', query=True, loaded=True ):
			cmds.loadPlugin('redshift4maya')
		
		pm.setAttr("defaultRenderGlobals.currentRenderer", "redshift")
		
	def removeTemporalObjs(self):
		caca = cmds.ls()
		for o in caca:
			if 'LIGHTPOS' in o or 'CAMPOS' in o:
				try:
					cmds.delete(o)
				except:
					pass

	def createCamera(self): #===================================== CAMERAS
		if self.XMLcameras == None: return
		for XMLcamera in self.XMLcameras:
			XMLcam = XMLcamera.attrib
			XMLcamName = XMLcam.get('name')
			#Delete first if already obj/cam with this name, or else conflict.
			try:
				cmds.delete(XMLcamName)
			except:
				pass
			
			try: #CAM SETTINGS ===
				newCam = cmds.camera(name=XMLcamName)
				if XMLcam.get('focallength'):
					pm.setAttr(newCam[1] + '.focalLength', float(XMLcam.get('focallength')))
					pm.setAttr(newCam[1] + '.farClipPlane', 100000.000)
					
			except Exception as e:
				print('Skip Cam Setting...', e)
			
			try:
				cmds.matchTransform(newCam, 'CAMPOS_' + XMLcamName)
			except Exception as e:
				print("Cam skipped... " + str(e))
			try:
				cmds.rename(newCam[0], XMLcamName)
			except Exception as e:
				print('Skip Cam Name...', e)
			try:
				cmds.lookThru( XMLcamName, 'perspView' )
			except:
				pass

	def rgbConv(self, diffColor):
		try:
			Colors = diffColor.split()
			col1 = float(Colors[0])/255
			col2 = float(Colors[1])/255
			col3 = float(Colors[2])/255
		
			return [col1, col2, col3]
		except:
			print('rgbConv skipped...')
			return [0, 0, 0]

	def setRenderSettings(self):
		mel.eval('redshiftRegisterRenderer(); redshiftGetRedshiftOptionsNode(true);')
		cmds.setAttr('redshiftOptions.secondaryGIEngine',4)
		cmds.setAttr('redshiftOptions.primaryGIEngine',4)
		#availableCuda= maya.mel.eval('rsPreference -q "AllCudaDevices";')
		try:
			resolution = self.XMLrenderSettings.find('resolution')
			xmlWidth = int(resolution.attrib['name'].split(',')[0])
			xmlHeight = int(resolution.attrib['name'].split(',')[1])
			pm.setAttr("defaultResolution.width",xmlWidth)
			pm.setAttr("defaultResolution.height",xmlHeight)
			#pm.setAttr("defaultResolution.pixelAspect", 1.0)
			pm.setAttr("defaultResolution.deviceAspectRatio", float(xmlWidth)/float(xmlHeight))
		except:
			print('Render settings skipped')
			
	def set_renderer(self):
		name = "redshift4maya"
		if not pm.pluginInfo(name, q=True, loaded=True): #Try to set Load and Autoload of renderer... It may not work...
			pm.loadPlugin(name)
			pm.pluginInfo(name, edit=True, autoload=True)
		pm.setAttr("defaultRenderGlobals.currentRenderer", "redshift") #Set Renderer

	def create_file_node(self, name, path, ru=1.0, rv=1.0, rotW = 0.0):
		textureName=name
		#textureName= "".join([ c if c.isalnum() else "_" for c in textureName])
		file_node = pm.shadingNode('file', name=textureName, asTexture=True, isColorManaged=True)
		file_node.fileTextureName.set(path)
		
		twoDTexture = pm.shadingNode('place2dTexture',asUtility=True)
		pm.connectAttr(twoDTexture + '.coverage',file_node + '.coverage') 
		pm.connectAttr(twoDTexture + '.translateFrame', file_node + '.translateFrame') 
		pm.connectAttr(twoDTexture + '.rotateFrame', file_node +'.rotateFrame') 
		pm.connectAttr(twoDTexture + '.mirrorU', file_node +'.mirrorU')
		pm.connectAttr(twoDTexture + '.mirrorV',file_node +'.mirrorV')
		pm.connectAttr(twoDTexture + '.stagger', file_node +'.stagger')
		pm.connectAttr(twoDTexture + '.wrapU', file_node +'.wrapU')     
		pm.connectAttr(twoDTexture + '.wrapV', file_node +'.wrapV') 
		pm.connectAttr(twoDTexture + '.repeatUV', file_node +'.repeatUV')
		pm.connectAttr(twoDTexture + '.offset', file_node +'.offset') 
		pm.connectAttr(twoDTexture + '.rotateUV', file_node +'.rotateUV')
		pm.connectAttr(twoDTexture + '.noiseUV', file_node +'.noiseUV')
		pm.connectAttr(twoDTexture + '.vertexUvOne', file_node +'.vertexUvOne') 
		pm.connectAttr(twoDTexture + '.vertexUvTwo', file_node +'.vertexUvTwo')
		pm.connectAttr(twoDTexture + '.vertexUvThree', file_node +'.vertexUvThree')
		pm.connectAttr(twoDTexture + '.vertexCameraOne', file_node +'.vertexCameraOne') 
		pm.connectAttr(twoDTexture + '.outUV', file_node +'.uv')
		pm.connectAttr(twoDTexture + '.outUvFilterSize', file_node +'.uvFilterSize')

		try:
			cmds.connectAttr(twoDTexture + '.outUV', file_node + '.' + 'uvCoord', force=True)
		except Exception as e:
			print(e)


		#ru=float(param.attrib["coord_U_Tiling"])
		#rv=float(param.attrib["coord_V_Tiling"])
		cmds.setAttr('%s.repeatU'%twoDTexture, ru)
		cmds.setAttr('%s.repeatV'%twoDTexture, rv)
		cmds.setAttr('%s.rotateUV'%twoDTexture, rotW)
		return file_node

	def get_textures(self, mat, shader):
		textures = mat.findall("shader")
		for tex in textures:
			texture_node = None
			if tex.attrib["type"] == "Bitmaptexture":
				xmlBitmapFilename = tex.attrib["filename"]
				xmlBitmapShaderName = tex.attrib["shaderName"]
				texMaps = tex.findall("param")
				ru = 1.0
				rv = 1.0
				rotW = 1.0
				try:
					for texMap in texMaps:
						if texMap.attrib["type"] == "StandardUVGen":
							ru = float(texMap.attrib["coord_U_Tiling"])
							rv = float(texMap.attrib["coord_V_Tiling"])
							rotW = float(texMap.attrib["coord_W_angle"])
				except:
					pass

				texture_node = self.create_file_node(xmlBitmapShaderName, xmlBitmapFilename, ru, rv, rotW)

			if texture_node:
				rendName = '_RS' #RedShift
				newMatName = mat.attrib['name'] + rendName
				try:
					print('Connect nodes...')
					def connectNode(nodeOut, nodeIn, mapType='Default'):
						try:
							cmds.connectAttr( texture_node + nodeOut, newMatName + nodeIn, force=True)
						except Exception as e:
							print("Node skipped... " + str(e) )
							
					if tex.attrib["shaderName"] == 'vraylightopacitymap': connectNode('.outAlpha', '.alpha')
					if tex.attrib["shaderName"] == 'diffuse_map': connectNode('.outColor', '.diffuse_color')
					if tex.attrib["shaderName"] == 'vraylightlightmap': connectNode('.outColor', '.color')
					if tex.attrib["shaderName"] == 'opacity_map': connectNode('.outColor', '.opacity_color')
					if tex.attrib["shaderName"] == 'vrayreflection_glossiness_map': 
						connectNode('.outAlpha', '.refl_roughness')
						try:
							cmds.setAttr(texture_node + '.invert', 1)
						except:
							pass
					if 'bump_map' in tex.attrib["shaderName"]:
						try:
							bump_node = pm.shadingNode('RedshiftBumpMap', name=newMatName + '_bump', asTexture=True, isColorManaged=True)
							if mat.attrib['matType'] == 'VRayMtl':
								bumpValue = float(mat.attrib['vraybump_value']) / 1000
							if mat.attrib['matType'] == 'Standardmaterial':
								bumpValue = float(mat.attrib['bump_value']) / 1000
							cmds.setAttr(bump_node + '.scale', bumpValue)
							cmds.connectAttr( texture_node + '.outColor', bump_node + '.input', force=True)
							cmds.connectAttr( bump_node + '.out', newMatName + '.bump_input', force=True)
						except:
							print("Bump Node skipped...")

				except KeyError:
					print('Shader Skipped' + ' ' + tex.attrib["shaderName"])
					#pm.warning(str(tex.attrib["shaderName"] + " is currently a unsupported shader type"))

	def findMatInXml(self, matName):
		result = 0
		for material in self.XMLmaterials:
			xmlMat = material.attrib
			xmlMatName = xmlMat.get('name')
			xmlMatType = xmlMat.get('matType')
			if matName in xmlMatName:
				return xmlMatType
				#if 'multiplier' in xmlMat: result = 'VRayLightMtl'
				#if 'vrayreflectionIOR_value' in xmlMat: result = 'VRayMtl'
		return result

	#=================================================================================
	#=================================================================================
	#SETTINGS FROM XML ===============================================================
	def settingsFromXMLtoMat(self, matNew, matOld):
		for material in self.root.iter('vraylightmtl'):
			xmlMat = material.attrib
			matName = xmlMat.get('name')
			matVray = xmlMat.get('vray')
			matType = xmlMat.get('matType')
			#IF MATERIAL IN XML: VRAY -- LIGHTMATERIAL:
			if matOld == matName and matType == 'VRayLightMtl':
				cmds.setAttr(matNew + '.color', *self.rgbConv(xmlMat.get('color')), type="float3")
				cmds.setAttr(matNew + '.intensity', float(xmlMat.get('multiplier')))
		for material in self.root.iter('material'):
			try:
				xmlMat = material.attrib
				matName = xmlMat.get('name')
				matVray = xmlMat.get('vray')
				matType = xmlMat.get('matType')
				
				#IF MATERIAL IN XML: VRAY -- MATERIAL
				if matOld == matName and matType == 'VRayMtl':
					cmds.setAttr(matNew + '.diffuse_color', *self.rgbConv(xmlMat.get('diffuse_color')), type="float3")
					cmds.setAttr(matNew + '.refl_weight', 1)
					cmds.setAttr(matNew + '.refr_weight', 1)
					cmds.setAttr(matNew + '.refl_roughness', 1 - float(xmlMat.get('vrayreflection_glossiness')))
					cmds.setAttr(matNew + '.refl_color', *self.rgbConv(xmlMat.get('vrayreflection_color')), type="float3")
					cmds.setAttr(matNew + '.refr_color', *self.rgbConv(xmlMat.get('vrayrefraction_color')), type="float3")
					if xmlMat.get('vrayreflection_fresnel') == 'false': cmds.setAttr(matNew + '.refl_ior', 0)
		
				#IF MATERIAL IN XML: STANDARD MATERIAL
				if matOld == matName and matType == 'Standardmaterial':
					cmds.setAttr(matNew + '.refl_weight', 0)
					cmds.setAttr(matNew + '.refr_weight', 0)
					cmds.setAttr(matNew + '.diffuse_color', *self.rgbConv(xmlMat.get('diffuse_color')), type="float3")
			except Exception as e:
				print('Mat Settings skipped', e)
				
	#=================================================================================
	#Creates new material and replaces the old inside Shading Group
	def replaceWithMat(self, matOld, shadingGroup, matType):
		newMat = matOld + "_RS"
		if matType == 'Standardmaterial':
			cmds.shadingNode('RedshiftMaterial', name = newMat, asShader=True)
		if matType == 'VRayMtl':
			cmds.shadingNode('RedshiftMaterial', name = newMat, asShader=True)
		if matType == 'VRayLightMtl':
			cmds.shadingNode('RedshiftIncandescent', name = newMat, asShader=True)
		cmds.connectAttr(newMat + '.outColor', shadingGroup + '.surfaceShader', force=True)
		cmds.delete(matOld)
		self.settingsFromXMLtoMat(newMat, matOld)

	def create_light_node(self, light): #=============== LIGHTS ======================================================
		try:
			lightName = light.attrib["name"]
			if light.attrib["v_type"] != 'sun':
				if light.attrib["v_area_type"] == 'Plane' and light.attrib["v_type"] == 'area':
					#pm.createNode(pm.nt.VRayLightRectShape, p=lightName)
					light_node = pm.createNode(pm.nt.RedshiftPhysicalLight, p=light.attrib["name"])
					cmds.setAttr(lightName + '.scaleY' , float(light.attrib["height"]))
					cmds.setAttr(lightName + '.scaleX' , float(light.attrib["width"]))
					cmds.setAttr(lightName + '.intensity' , float(light.attrib["multiplier"]))
					cmds.setAttr(lightName + '.color' , *self.rgbConv(light.attrib["color"]), type="float3")
					if light.attrib["invisible"] == 'true':
						cmds.setAttr(lightName + '.areaVisibleInRender' , 0)
						
		except Exception as e:
			print(str(e))
	def create_light_nodeIES(self, light): #=============== IES LIGHT ======================================================
		try:
			lightName = light.attrib["name"]
			light_node = pm.createNode('RedshiftIESLight', p=light.attrib["name"])
			pm.sets('defaultLightSet', forceElement=light.attrib["name"])
			
			cmds.setAttr(lightName +'.profile' , light.attrib["ies_file"], type="string")
			cmds.setAttr(lightName +'.multiplier' , float(light.attrib["power"]) / 1000)
			#cmds.setAttr(lightName + '.exposure' , 10)
			#cmds.setAttr(lightName + '.rotateAxisX' , 90)
			#cmds.setAttr(lightName + '.rotateAxisZ' , -90)
			cmds.setAttr(lightName + '.scaleX' , 100)
			cmds.setAttr(lightName + '.scaleY' , 100)
			cmds.setAttr(lightName + '.scaleZ' , 100)

		except Exception as e:
			print(str(e))

	def setLights(self):
		if self.XMLlights:
			for light in self.XMLlights:
				lightName = light.attrib["name"]
				#VRAY - Area Light
				try:
					if light.attrib["vray"] == 'true' and light.attrib["v_type"] == 'area':
						self.create_light_node(light)
				except:
					pass
				#VRAY - IES Light
				try:
					if light.attrib["vray"] == 'true' and light.attrib["type"] == 'VRayIES':
						self.create_light_nodeIES(light)
				except:
					pass

	#====================================================================================================================

	def convertMats(self):
		#List shading groups to see what material is used
		#then check if exist in xml to read info from there...
		shadingGroup_list = cmds.ls(type='shadingEngine')
		for sg in shadingGroup_list:
			surfaceShader = cmds.listConnections(sg + ".surfaceShader")
			if surfaceShader:
				if self.findMatInXml(surfaceShader[0]):
					matType = self.findMatInXml(surfaceShader[0])
					self.replaceWithMat(surfaceShader[0], sg, matType) #Send Material to change With Shading Group to put the new Material
		
		#List Textures in XML and call Add Textures function
		for material in self.root.find('materials'):
			self.get_textures(material, 'cacacaca') #Add Textures

	def start(self, xmlFile=None, fbxFile=None):
		self.xmlFile = xmlFile
		self.fbxFile = fbxFile

		self.tree = ET.parse(xmlFile)
		self.root = self.tree.getroot()

		self.XMLmaterials = self.root.find("materials")
		self.XMLlights = self.root.find("lights")
		self.XMLcameras = self.root.find("cameras")
		self.XMLrenderSettings = self.root.find("rsettings")

		self.importFile()
		self.setRender()
		self.setRenderSettings()
		self.convertMats()
		self.setLights()
		self.createCamera()
		self.removeTemporalObjs()
		
		try:
			pm.setAttr("hardwareRenderingGlobals.textureMaxResolution", 512)
		except:
			pass
		try:
			pm.setAttr("defaultArnoldRenderOptions.abortOnError", 0)
		except:
			pass

		mel.eval('modelEditor -e -twoSidedLighting true modelPanel4')
		mel.eval('modelEditor -e -displayTextures true modelPanel4')
		print('---= MaxToMaya /// Complete. =---')
		
# xmlToRedShift().start()
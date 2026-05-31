import maya.cmds as cmds
import pymel.core as pm
import os
import xml.etree.ElementTree as ET
import maya.mel as mel

class xmlToStandard():
	
	print('Import as Standard --------------')

	xmlFile = ''
	fbxFile = ''

	tree = ''
	root = ''

	XMLmaterials = ''
	XMLlights = ''
	XMLcameras = ''
	XMLrenderSettings = ''
	XMLwirecolors = ''

	def importFile(self):
		cmds.file( f=True, new=True )
		pm.mel.FBXImport(f=self.fbxFile)

	def removeTemporalObjs(self):
		caca = cmds.ls()
		for o in caca:
			if 'LIGHTPOS' in o or 'CAMPOS' in o:
				try:
					cmds.delete(o)
				except:
					pass

	def setRender(self):
		try:
			pm.setAttr("defaultRenderGlobals.currentRenderer", "mayaSoftware")
		except:
			print("Set Standard render skipped...")


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
				print(('Skip Cam Setting...', e))

			try:
				cmds.matchTransform(newCam, 'CAMPOS_' + XMLcamName)
			except Exception as e:
				print(("Cam skipped... " + str(e)))
			try:
				cmds.rename(newCam[0], XMLcamName)
			except Exception as e:
				print(('Skip Cam Name...', e))
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
			
	def rgbToFloat(self, rgbValue):
		try:
			Colors = rgbValue.split()
			r = float(Colors[0])/255
			g = float(Colors[1])/255
			b = float(Colors[2])/255
			
			rgbToFloat = (r + g + b) /3
			
			return rgbToFloat
		except:
			print('rgbToFloat skipped...')
			return [0, 0, 0]

	def setRenderSettings(self):
		try:
			pm.setAttr("defaultRenderQuality.enableRaytracing", 1)
		except:
			pass

		try:
			resolution = self.XMLrenderSettings.find('resolution')
			xmlWidth = int(resolution.attrib['name'].split(',')[0])
			xmlHeight = int(resolution.attrib['name'].split(',')[1])
			pm.setAttr("defaultResolution.width",xmlWidth)
			pm.setAttr("defaultResolution.height",xmlHeight)
			pm.setAttr("defaultResolution.deviceAspectRatio", float(xmlWidth)/float(xmlHeight))

		# 	pm.setAttr("vraySettings.giOn", 1)
		except:
			print('Render settings skipped')

			
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
			cmds.connectAttr( twoDTexture + '.outUV', file_node + '.' + 'uvCoord' , force=True)
		except:
			pass

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
				rendName = '_SM'
				newMatName = mat.attrib['name'] + rendName
				try:
					print('Connect nodes...')
					def connectNode(nodeOut, nodeIn, mapType='Default'):
						try:
							cmds.connectAttr( texture_node + nodeOut, newMatName + nodeIn, force=True)
						except Exception as e:
							print(("Node skipped... " + str(e) ))
							
					if tex.attrib["shaderName"] == 'vraylightopacitymap': connectNode('.outColor', '.opacity')
					if tex.attrib["shaderName"] == 'diffuse_map': connectNode('.outColor', '.color')
					if tex.attrib["shaderName"] == 'vraylightlightmap': connectNode('.outColor', '.color')
					if tex.attrib["shaderName"] == 'opacity_map': connectNode('.outColor', '.opacityMap')
					#if tex.attrib["shaderName"] == 'vrayreflection_glossiness_map': connectNode('.outColor', '.specularRoughness') # CHEKEAR
					if tex.attrib["shaderName"] == 'vraylightlightmap': connectNode('.outColor', '.illumColor')
					# if tex.attrib["shaderName"] == 'bump_map': connectNode('.outNormal', '.normalCamera')

					if 'bump_map' in tex.attrib["shaderName"]:
						try:
							bump_node = pm.shadingNode('bump2d', name=newMatName + '_bump', asUtility=True)
							if mat.attrib['matType'] == 'VRayMtl':
								bumpValue = float(mat.attrib['vraybump_value']) / 1000
							if mat.attrib['matType'] == 'Standardmaterial':
								bumpValue = float(mat.attrib['bump_value']) / 1000
							cmds.connectAttr( texture_node + '.outAlpha', bump_node + '.bumpValue', force=True)
							cmds.connectAttr( bump_node + '.outNormal', newMatName + '.normalCamera', force=True)
							cmds.setAttr(bump_node + '.bumpDepth', 0.1)

							try:
								cmds.setAttr(bump_node + '.bumpDepth', 0.1)
							except:
								pass
						except:
							print("Bump Node skipped...")

				except KeyError:
					print(('Shader Skipped' + ' ' + tex.attrib["shaderName"]))
					#pm.warning(str(tex.attrib["shaderName"] + " is currently a unsupported shader type"))


	def findMatInXml(self, matName):
		result = 0
		for material in self.XMLmaterials:
			xmlMat = material.attrib
			xmlMatName = xmlMat.get('name')

			# print("in scene: " + matName + " in xml: " + xmlMatName)

			xmlMatType = xmlMat.get('matType')


			if matName in xmlMatName:
				return xmlMatType
				#if 'multiplier' in xmlMat: result = 'VRayLightMtl'
				#if 'vrayreflectionIOR_value' in xmlMat: result = 'VRayMtl'
		return result

	def setWireColors(self):
		for obj in self.XMLwirecolors:
			xmlObj = obj.attrib
			xmlObjName = xmlObj.get('name')
			xmlObjWirecolor = xmlObj.get('wirecolor')

	#=================================================================================
	#=================================================================================
	#SETTINGS FROM XML ===============================================================
	def settingsFromXMLtoMat(self, matNew, matOld):

		#IF MATERIAL IN XML: VRAY - LIGHTMATERIAL:
		for material in self.root.iter('vraylightmtl'):
			xmlMat = material.attrib
			matName = xmlMat.get('name')
			matVray = xmlMat.get('vray')
			matType = xmlMat.get('matType')
			if matOld == matName and matType == 'VRayLightMtl':
				cmds.setAttr(matNew + '.incandescence', *self.rgbConv(xmlMat.get('color')), type="float3")
				#cmds.setAttr(matNew + '.colorMultiplier', float(xmlMat.get('multiplier')) )

				#if xmlMat.get('opacity_multiplyColor') == 'true': cmds.setAttr(matNew + '.multiplyColorByOpacity', 1)
				#if xmlMat.get('twoSided') == 'true': cmds.setAttr(matNew + '.emitOnBackSide', 1)
		#IF MATERIAL IN XML:
		for material in self.root.iter('material'):
			try:
				xmlMat = material.attrib
				matName = xmlMat.get('name')
				matVray = xmlMat.get('vray')
				matType = xmlMat.get('matType')
				
				#IF MATERIAL IN XML: VRAY -- MATERIAL
				if matOld == matName and matType == 'VRayMtl':
					cmds.setAttr(matNew + '.color', *self.rgbConv(xmlMat.get('diffuse_color')), type="float3")
					# cmds.setAttr(matNew + '.specular', 1)
				
					# if self.rgbToFloat(xmlMat.get('vrayrefraction_color')) > 0.5:
					# 	cmds.setAttr(matNew + '.transmission', 1)
					# else:
					# 	cmds.setAttr(matNew + '.transmission', self.rgbToFloat(xmlMat.get('vrayrefraction_color')))
					
					# cmds.setAttr(matNew + '.cosinePower', float(xmlMat.get('vrayrefraction_glossiness')))
					# cmds.setAttr(matNew + '.refractionIOR', float(xmlMat.get('vrayrefraction_ior')))

					cmds.setAttr(matNew + '.reflectivity', 0)

					cmds.setAttr(matNew + '.specularColor', *self.rgbConv(xmlMat.get('vrayreflection_color')), type="float3")
					# cmds.setAttr(matNew + '.cosinePower', float(xmlMat.get('vrayreflection_glossiness')))
					cmds.setAttr(matNew + '.transparency', *self.rgbConv(xmlMat.get('vrayrefraction_color')), type="float3")

					# cmds.setAttr(matNew + '.bumpMult', float(xmlMat.get('vraybump_value')))

					if xmlMat.get('vrayreflection_fresnel') == 'false':
						cmds.setAttr(matNew + '.reflectivity', 1)
		
				#IF MATERIAL IN XML: STANDARD MATERIAL
				if matOld == matName and matType == 'Standardmaterial':
					cmds.setAttr(matNew + '.color', *self.rgbConv(xmlMat.get('diffuse_color')), type="float3")
					cmds.setAttr(matNew + '.cosinePower', 0.5)
			except Exception as e:
				print(('Mat Settings skipped', e))


		# cmds.confirmDialog( title='MaxToMaya: TEST', message='TEST')
		# cmds.setAttr(matNew + '.color', *self.rgbConv(xmlMat.get('255 0 0')), type="float3")

				
	#=================================================================================
	#Creates new material and replaces the old inside Shading Group
	def replaceWithMat(self, matOld, shadingGroup, matType):
		print(('MAT TYPE: ' * 20))
		print(matType)
		newMat = matOld + "_SM"
		if matType == 'Standardmaterial':
			cmds.shadingNode('phong', name = newMat, asShader=True)
		if matType == 'VRayMtl':
			cmds.shadingNode('phong', name = newMat, asShader=True)
		if matType == 'VRayLightMtl':
			cmds.shadingNode('phong', name = newMat, asShader=True)
		try:
			cmds.connectAttr(newMat + '.outColor', shadingGroup + '.surfaceShader', force=True)
			cmds.delete(matOld)
		except:
			pass

		self.settingsFromXMLtoMat(newMat, matOld)

	def create_light_node(self, light): #=============== LIGHTS ======================================================
		try:
			lightName = light.attrib["name"]
			if light.attrib["v_type"] != 'sun':
				if light.attrib["v_area_type"] == 'Plane' and light.attrib["v_type"] == 'area':
					light_node = pm.createNode('areaLight', p=light.attrib["name"])
					pm.sets('defaultLightSet', forceElement=light.attrib["name"])
					
					cmds.setAttr(lightName + '.useDepthMapShadows' , 1)
					cmds.setAttr(lightName + '.scaleY' , float(light.attrib["height"]))
					cmds.setAttr(lightName + '.scaleX' , float(light.attrib["width"]))
					
					# cmds.setAttr(lightName + '.scaleZ' , float(light.attrib["width"]))
					cmds.setAttr(lightName + '.intensity' , float(light.attrib["multiplier"]) / 100)
					
					# cmds.setAttr(lightName + '.lightColor' , 255,0,0 , type="float3")
					cmds.setAttr(lightName + '.color' , *self.rgbConv(light.attrib["color"]), type="float3")
					# cmds.setAttr(lightName + '.invisible' , 1)
		except Exception as e:
			print((str(e)))
			
	def create_light_nodeIES(self, light): #=============== IES LIGHT ======================================================
		try:
			lightName = light.attrib["name"]
			light_node = pm.createNode('VRayLightIESShape', p=light.attrib["name"])
			pm.sets('defaultLightSet', forceElement=light.attrib["name"])
			cmds.setAttr(lightName +'.iesFile' , light.attrib["ies_file"], type="string")
			cmds.setAttr(lightName +'.intensityMult' , float(light.attrib["power"]) / 17000 )
			cmds.setAttr(lightName +'.softShadows' , 1 )


			# cmds.setAttr(lightName + '.rotateAxisX' , 90)
			# cmds.setAttr(lightName + '.rotateAxisZ' , -90)
			# cmds.setAttr(lightName + '.scaleX' , 100)
			# cmds.setAttr(lightName + '.scaleY' , 100)
			# cmds.setAttr(lightName + '.scaleZ' , 25)
		except Exception as e:
			print((str(e)))

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
						print ('light skip')
						# self.create_light_nodeIES(light)
				except:
					pass

	#====================================================================================================================

	def convertMats(self):
		#List shading groups to see what material is used
		#then check if exist in xml to read info from there...

		shadingGroup_list = cmds.ls(type='shadingEngine')
		for sg in shadingGroup_list:
			surfaceShader = cmds.listConnections(sg + ".surfaceShader")
			print(('-----'*50))
			print(surfaceShader)
			print(('-----'*50))
			if surfaceShader:
				print(('AAA'*50))
				if self.findMatInXml(surfaceShader[0]):
					print(('XX' * 50))
					matType = self.findMatInXml(surfaceShader[0])
					print(('******'*10))
					self.replaceWithMat(surfaceShader[0], sg, matType) #Send Material to change With Shading Group to put the new Material
		
		#List Textures in XML and call Add Textures function
		for material in self.root.find('materials'):
			self.get_textures(material, 'cacacaca') #Add Textures

	def start(self, xmlFile=None, fbxFile=None, testMode=False):

		self.xmlFile = xmlFile
		self.fbxFile = fbxFile

		self.tree = ET.parse(xmlFile)
		self.root = self.tree.getroot()

		self.XMLmaterials = self.root.find("materials")
		self.XMLlights = self.root.find("lights")
		self.XMLcameras = self.root.find("cameras")
		self.XMLrenderSettings = self.root.find("rsettings")
		self.XMLwirecolors = self.root.find("geometrys")
		if testMode == False:
			self.importFile()
		self.setRender()
		self.setRenderSettings()
		# self.setWireColors()
		self.convertMats()
		self.setLights()
		if testMode == False:
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
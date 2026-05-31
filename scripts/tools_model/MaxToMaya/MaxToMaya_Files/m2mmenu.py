import maya.cmds as cmds
import pymel.core as pm
import os
import xml.etree.ElementTree as ET
import maya.mel as mel
class generateMenu():
	import maya.cmds as cmds
	import pymel.core as pm
	import os
	import xml.etree.ElementTree as ET
	import maya.mel as mel

	menuName = "- 3DtoAll -" #parent menu to create if not found
	oldMenuNameToDelete = "MaxToMaya" #old menu to delete if found
	gMainWindow = mel.eval('$tmpVar=$gMainWindow')
	mayaVersion = cmds.about(v=True)
	pathMayaIcons = os.path.expanduser("~/maya/")
	pathIcon = os.path.expanduser("~/maya/plug-ins/MaxToMaya_Files/MaxToMaya_icon.png")
	pathIconMac = "/users/Shared/Autodesk/maya/plug-ins/MaxToMaya_Files/MaxToMaya_icon.png"
	
	try:
		cmds.sysFile( pathIcon, copy= pathMayaIcons + mayaVersion + "/prefs/icons/MaxToMaya_icon.png" )# Windows
	except:
		pass
	try:
		cmds.sysFile( pathIconMac, copy= "/users/Shared/Autodesk/maya/icons/MaxToMaya_icon.png" )# Mac
	except:
		pass
	try:
		cmds.sysFile( pathIconMac, copy= "/users/Shared/Autodesk/maya/" + mayaVersion + "/icons/MaxToMaya_icon.png" )# Mac
	except:
		pass
	
	
	def menuCreate(self, gMainWindow, menuName):
		parentMenu = cmds.menu(parent=gMainWindow, tearOff=True, label=menuName)
		return parentMenu
	
	def menuSubItemCreate(self, menuId):
		cmds.menuItem( parent=menuId, d=True, dl="MaxToMaya" )
		cmds.menuItem( parent=menuId, l=">> Import from 3ds Max", i="MaxToMaya_icon.png", c="mel.eval('maxtomaya')")
	
	def menuSubItemFind(self, menuId, menuSubItemName):
		menuItems = cmds.menu(menuId, query=True, itemArray=True)
		if menuItems == None:
			return "EMPTY"
		else:
			for mi in menuItems:
				itemLabel = cmds.menuItem( mi, query=True, label=True )
				if itemLabel == menuSubItemName:
					return mi
	
	def menuFind(self, menuName):
		for x in range(0,200):
			menuNumber = "menu" + str(x)
			try:
				itemLabel = cmds.menu(menuNumber, query=True, label=True)
				if itemLabel == menuName:
					return "menu" + str(x)
			except:
				pass


	def daztomayaMenuFix(self):
		#Source Files:
		fileDaztomayaNew = os.path.expanduser("~/maya/plug-ins/MaxToMaya_Files/fix_dtm.py")
		fileDaztomayaMenuNew = os.path.expanduser("~/maya/plug-ins/MaxToMaya_Files/fix_dtmmenu.pyc")
		
		#Target to Overwrite:
		fileDaztomayaOld = os.path.expanduser("~/maya/plug-ins/DazToMaya.py")
		fileDaztomayaMenuOld = os.path.expanduser("~/maya/plug-ins/DazToMaya_Files/d2m_menu.pyc")
		
		#Check if DazToMaya files found, overwrite them.
		
		if os.path.isfile(fileDaztomayaOld):
			try:
				cmds.sysFile( fileDaztomayaNew, copy=fileDaztomayaOld )# Windows
				cmds.sysFile( fileDaztomayaMenuNew, copy=fileDaztomayaMenuOld )# Windows
			except:
				pass
			
	#---- START ------------------------------------------------------------------
	def start(self):
		mayamenu = self.menuFind(self.oldMenuNameToDelete)
		threedtoallmenu = self.menuFind(self.menuName)

		self.daztomayaMenuFix()
		
		if mayamenu != None:
			cmds.deleteUI(mayamenu) #Eliminar menu
			
		if threedtoallmenu != None:
			menuSubItem = self.menuSubItemFind(threedtoallmenu, ">> Import from 3ds Max")
			try:
				cmds.deleteUI(menuSubItem)
			except:
				pass
			menuSubItem = self.menuSubItemFind(threedtoallmenu, "MaxToMaya")
			try:
				cmds.deleteUI(menuSubItem)
			except:
				pass
			self.menuSubItemCreate(threedtoallmenu)
		else:
			threedtoallmenu = self.menuCreate(self.gMainWindow, self.menuName)
			self.menuSubItemCreate(threedtoallmenu)
	
	#---- REMOVE MENU ------------------------------------------------------------
	# Remove subItems, if main menu empty remove menu too
	
	def remove(self):
		threedtoallmenu = self.menuFind(self.menuName)
		
		if threedtoallmenu != None:
			menuSubItem = self.menuSubItemFind(threedtoallmenu, "MaxToMaya")
			if menuSubItem != None and menuSubItem != "EMPTY":
				cmds.deleteUI(menuSubItem)
			menuSubItem = self.menuSubItemFind(threedtoallmenu, ">> Import from 3ds Max")
			if menuSubItem != None and menuSubItem != "EMPTY":
				cmds.deleteUI(menuSubItem)
			menuSubItem = self.menuSubItemFind(threedtoallmenu, "MaxToMaya")
			if menuSubItem == "EMPTY":
				cmds.deleteUI(threedtoallmenu)
				
			
			
print("START")
def start():
	generateMenu().start()
def remove():
	generateMenu().remove()
#generateMenu().remove()
start()
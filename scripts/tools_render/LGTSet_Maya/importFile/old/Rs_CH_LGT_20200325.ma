//Maya ASCII 2018ff09 scene
//Name: Rs_CH_LGT.ma
//Last modified: Mon, Mar 09, 2020 05:48:49 PM
//Codeset: 936
requires maya "2018ff09";
requires -nodeType "displayPoints" "Type" "2.0a";
requires -nodeType "RedshiftOptions" -nodeType "RedshiftPostEffects" -nodeType "RedshiftPhysicalLight"
		 -nodeType "RedshiftDomeLight" "redshift4maya" "3.0.12";
requires "stereoCamera" "10.0";
requires "AM_Glossy_30" "3.0";
requires "TurtleForMaya50" "0.352";
requires "3delight_for_maya2009" "2";
requires "elastikSolver" "0.990";
requires "TurtleForMaya80" "4.0.0.6";
requires "3delight_for_maya2011" "2";
requires "3delight_for_maya2012" "6.0.2";
requires "TurtleForMaya70" "2.1.0.0";
requires "AM_Velvet" "3.0";
requires "qualoth-2014-x64" "4.0-5";
requires "AmatShader" "1.0";
requires "MayaMan" "2.0.1";
requires "AT_MPView" "RC 1";
requires "MiarmyProForMaya2012" "2.2";
requires "AT_Scatter" "VersionTag_INSTALL_0-0-8298554";
requires "randomGrid" "1.3";
requires "cTag.py" "1.0";
requires "anzovinRigNodes" "1.0";
requires "ArnoldExport" "0.1";
requires "RenderMan_for_Maya" "3.0.1";
requires "NormalBump2D" "1.0";
requires "BI" ".0";
requires "correctShape2013x64" "0.0.7 build Friday 12/5/12 2:15 AM";
requires "afiLocatorNode" "0.0.1 13/11/09";
requires "BPT_Bevel" "1.0";
requires "TSMG.py" "1.0.8";
requires "MayaMan_m6" "1.2.12";
requires "ByronsPolyTools" "1.0";
requires "HSVadjust2" "4.0";
requires "Vue_xStream" "7.00";
requires "shaveNode" "1.1";
requires "CausticVisualizer" "1.0.205.9508";
requires "JSNormalMapper_2009_64" "2009";
requires "CorrectiveShape70" "7.0";
requires "NoiseD" "1.42";
requires "LEGO_EasyFlex" "7.0";
requires "CpClothPlugin" "5.0";
requires "FumeFX" "FumeFX3.5-DEMO-2013_06_03";
requires "FurryBall_2009" "1.3.3.950";
requires "FurryBall_2013" "3.2.2.2515";
requires "composeMatrix" "2012";
requires "VRayForMaya80" "1.0";
requires "TurtleForMaya60" "0.352";
requires "InkworksMaterial" "1.1 (1131)";
requires "underworldBlendShape" "v1.02";
requires "JSNormalMapper_2012x64" "6.0";
requires "faceMachine" "1.0";
requires "LXFMLImport" "5.0";
requires "MayaKrakatoa" "1.0";
requires "fStretch" "1.0.1";
requires "skinShapeDeformer" "1.0";
requires "MayaMan_m4" "1.0.1";
requires "MayaMan_m5" "1.2.12";
requires "MySceneNode.py" "1.5";
requires "N_Loc" "3.0";
requires "RBViewportRenderer" "1.51";
requires "RealFakeGI" "0.3";
requires "RenNodeHair.so.1" "2.0";
requires "SpeedTree FBX Importers.py" "Unknown";
requires "TechCgfxShader" "1.2.20110111";
requires "TurtleForMaya2008" "4.1.0.7";
requires "TurtleForMaya2009" "5.0.0.5";
requires "smshadeplugin.py" "1.1.2";
requires "TurtleForMaya85" "4.1.0.4";
requires "am_metaballs" "3.0";
requires "anisotropicShader.mll" "1.0";
requires "cartoonShader50" "5.0";
requires "cellShader" "2.5";
requires "depthShader.so" "1.0";
requires "epCurveNode" "2013";
requires "finalRender" "1.0";
requires "granny_maya_0" "2.8.39.0";
requires "ikSmoothStretch2" "2013";
requires "instSurf.so" "1.0";
requires "jlCollisionDeformer.py" "0.9.4.0";
requires "jptInstSurf" "1.0";
requires "libCausticMap" "2.0";
requires "libSkinA" "1.0";
requires "libSkinShader" "1.0";
requires "locusChRig" "2012";
requires "locusChRig_00" "2012";
requires "spMayaStitch" "1.0";
requires "locusChRig_02" "2012";
requires "moebiusPass" "4.0";
requires "locusChRig_t2_00" "2013";
requires "locusChRig_t2_02" "2013";
requires "locusChRig_v2" "2013";
requires "magicAssetNode.py" "Unknown";
requires "maxwell" "2.5.12";
requires "mayalive" "2010";
requires "poseReader" "6.0";
requires "md_RayDiffuse" "1.0";
requires "mtor" "2.1";
requires "mtorsubdiv" "1.1";
requires "mvl" "1.0pre1";
requires "nfxMaya400" "4.0.0";
requires "ngSkinTools" "1.0beta.920";
requires "notepad" "1.0";
requires "pdiMaya2lmx" "2.3";
requires "pdiMaya2x" "2.1";
requires "physx" "PhysxForMaya (2.86.00820.10150) , compiled 8/19/2012 1:03:57 AM";
requires "pointOnNurbsMesh" "3.0";
requires "poseDeformer" "6.0";
requires "psdNodes_00" "2013";
requires "qualoth" "3.1-8";
requires "qualoth_2013_x64" "4.1-1";
requires "rbfSolver.py" "1.0";
requires "realflow" "2013.0.1";
requires "rigAdditionalNodes_01" "2013";
requires "rpmaya" "2.0";
requires "saveNode" "8.5";
requires "stereoCamera" "10.0";
requires "stereoCameraParallelView" "2.0";
requires "stretchMesh" "1.6";
requires "syflex" "3.52";
requires "vrayformaya2008" "1.0";
requires "wobble2013-x64" "1.0";
requires "xfrog" "1.0";
requires "xfrog4.0" "1.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2018";
fileInfo "version" "2018";
fileInfo "cutIdentifier" "201807191615-2c29512b8a";
fileInfo "osv" "Microsoft Windows 8 Business Edition, 64-bit  (Build 9200)\n";
createNode transform -n "Rs_CH_LGT";
	rename -uid "A158E7D2-49ED-61CA-1D9F-04A9FAA052C6";
	setAttr ".rlio[0]" 1 yes 0;
createNode transform -n "Mend_Ctrl" -p "Rs_CH_LGT";
	rename -uid "4FFBBBD1-4EA1-299F-9A69-9CB6D5FAD23F";
	setAttr ".s" -type "double3" 35.311687325336187 35.311687325336187 35.311687325336187 ;
createNode nurbsCurve -n "Mend_CtrlShape" -p "Mend_Ctrl";
	rename -uid "C0644AEA-4617-F7E7-9556-908605B489E7";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		0.78361162489122449 4.7982373409884731e-17 -0.7836116248912246
		6.7857323231109122e-17 6.7857323231109122e-17 -1.1081941875543877
		-0.78361162489122449 4.7982373409884719e-17 -0.78361162489122438
		-1.1081941875543881 3.5177356190060272e-33 -5.7448982375248304e-17
		-0.78361162489122449 -4.7982373409884725e-17 0.78361162489122449
		-1.1100856969603225e-16 -6.7857323231109171e-17 1.1081941875543884
		0.78361162489122449 -4.7982373409884719e-17 0.78361162489122438
		1.1081941875543881 -9.2536792101100989e-33 1.511240500779959e-16
		0.78361162489122449 4.7982373409884731e-17 -0.7836116248912246
		6.7857323231109122e-17 6.7857323231109122e-17 -1.1081941875543877
		-0.78361162489122449 4.7982373409884719e-17 -0.78361162489122438
		;
createNode transform -n "RIM_A_Ctrl" -p "Mend_Ctrl";
	rename -uid "F890220D-41FE-D76E-403E-0383E8FA34BB";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -24.064227395494573 -46.982539200727508 0 ;
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.028319235803906165 0.028319235803906162 0.028319235803906165 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
createNode bezierCurve -n "RIM_A_CtrlShape" -p "RIM_A_Ctrl";
	rename -uid "79254689-41D9-4F25-753E-4686EE340F06";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".cc" -type "dataBezierCurve" 
		3 19 0 no 3
		24 0 0 0 1 1 1 2 2 2 3 3 3 4 4 4 5 5 5 6 6 6 7 7 7
		22
		0 0 0
		0 0 0
		12 0 12
		12 0 12
		12 0 12
		8 0 12
		8 0 12
		8 0 12
		8 0 164.58612750542235
		8 0 164.58612750542235
		8 0 164.58612750542235
		-8 0 164.58612750542235
		-8 0 164.58612750542235
		-8 0 164.58612750542235
		-8 0 12
		-8 0 12
		-8 0 12
		-12 0 12
		-12 0 12
		-12 0 12
		0 0 0
		0 0 0
		;
createNode transform -n "polyToCurve4" -p "RIM_A_Ctrl";
	rename -uid "C66BDA16-4E29-E94D-9854-C088C5DB6B68";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".t" -type "double3" 3.1124999742588493 0 109.06268831974981 ;
	setAttr ".r" -type "double3" -89.999999999999986 89.999999999999986 0 ;
	setAttr ".s" -type "double3" 0.56055562757094124 0.56055562757094124 0.56055562757094124 ;
createNode nurbsCurve -n "polyToCurveShape4" -p "polyToCurve4";
	rename -uid "8EDAC1D9-4DBC-20B3-598D-F19D602B6D47";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".cc" -type "nurbsCurve" 
		1 24 2 no 3
		25 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
		25
		5.1571903228759766 11.944629669189453 0
		1.5414876937866211 11.944629669189453 0
		1.5414876937866211 0 0
		3.2201652526855469 0 0
		3.2201652526855469 5.0522317886352539 0
		4.7973556518554688 5.0522317886352539 0
		8.2004966735839844 0 0
		10.282149314880371 0 0
		6.2950420379638672 5.5928926467895508 0
		6.8360333442687988 5.8566946983337402 0
		7.3130583763122559 6.1720666885375977 0
		7.7259507179260254 6.5386781692504883 0
		8.0747108459472656 6.9568595886230469 0
		8.3519010543823242 7.4163641929626465 0
		8.5499172210693359 7.9072728157043457 0
		8.6685953140258789 8.4292564392089844 0
		8.7082643508911133 8.9826450347900391 0
		8.6510744094848633 9.6621494293212891 0
		8.479339599609375 10.255868911743164 0
		8.1930580139160156 10.763801574707031 0
		7.792231559753418 11.185951232910156 0
		7.2839670181274414 11.517851829528809 0
		6.6753721237182617 11.75504207611084 0
		5.9664463996887207 11.897191047668457 0
		5.1571903228759766 11.944629669189453 0
		;
createNode transform -n "polyToCurve5" -p "RIM_A_Ctrl";
	rename -uid "98205B35-4D78-9309-CCFC-2F9DE44FF915";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".t" -type "double3" 3.1124999742588493 0 109.06268831974981 ;
	setAttr ".r" -type "double3" -89.999999999999986 89.999999999999986 0 ;
	setAttr ".s" -type "double3" 0.56055562757094124 0.56055562757094124 0.56055562757094124 ;
createNode nurbsCurve -n "polyToCurveShape5" -p "polyToCurve5";
	rename -uid "93FF1EA6-42DD-5E32-E15D-A9B357E8CBBD";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 2 no 3
		5 0 1 2 3 4
		5
		13.641488075256348 11.944629669189453 0
		11.946611404418945 11.944629669189453 0
		11.946611404418945 0 0
		13.641488075256348 0 0
		13.641488075256348 11.944629669189453 0
		;
createNode transform -n "polyToCurve6" -p "RIM_A_Ctrl";
	rename -uid "12E74E2C-4695-2B54-FB91-30957E211E10";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".t" -type "double3" 3.1124999742588493 0 109.06268831974981 ;
	setAttr ".r" -type "double3" -89.999999999999986 89.999999999999986 0 ;
	setAttr ".s" -type "double3" 0.56055562757094124 0.56055562757094124 0.56055562757094124 ;
createNode nurbsCurve -n "polyToCurveShape6" -p "polyToCurve6";
	rename -uid "1B184B4B-490D-A338-75E3-77AA1610A9C7";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".cc" -type "nurbsCurve" 
		1 13 2 no 3
		14 0 1 2 3 4 5 6 7 8 9 10 11 12 13
		14
		19.087106704711914 11.944629669189453 0
		16.748098373413086 11.944629669189453 0
		16.748098373413086 0 0
		18.200826644897461 0 0
		18.200826644897461 9.7256202697753906 0
		21.393718719482422 0.79884302616119385 0
		23.030908584594727 0.79884302616119385 0
		26.319999694824219 9.7024803161621094 0
		26.319999694824219 0 0
		27.909917831420898 0 0
		27.909917831420898 11.944629669189453 0
		25.805950164794922 11.944629669189453 0
		22.401157379150391 2.7034711837768555 0
		19.087106704711914 11.944629669189453 0
		;
createNode transform -n "polyToCurve7" -p "RIM_A_Ctrl";
	rename -uid "7D24322E-4311-02FE-4327-95855875FE02";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".t" -type "double3" 3.1124999742588493 0 109.06268831974981 ;
	setAttr ".r" -type "double3" -89.999999999999986 89.999999999999986 0 ;
	setAttr ".s" -type "double3" 0.56055562757094124 0.56055562757094124 0.56055562757094124 ;
createNode nurbsCurve -n "polyToCurveShape7" -p "polyToCurve7";
	rename -uid "BED09208-4572-014F-73A8-228A76366C57";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".cc" -type "nurbsCurve" 
		1 4 2 no 3
		5 0 1 2 3 4
		5
		36.983638763427734 0 0
		30.115537643432617 0 0
		30.115537643432617 -1.1943801641464233 0
		36.983638763427734 -1.1943801641464233 0
		36.983638763427734 0 0
		;
createNode transform -n "polyToCurve8" -p "RIM_A_Ctrl";
	rename -uid "5A480E08-4BAD-82F5-4BBE-14A540FB15C8";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".t" -type "double3" 3.1124999742588493 0 109.06268831974981 ;
	setAttr ".r" -type "double3" -89.999999999999986 89.999999999999986 0 ;
	setAttr ".s" -type "double3" 0.56055562757094124 0.56055562757094124 0.56055562757094124 ;
createNode nurbsCurve -n "polyToCurveShape8" -p "polyToCurve8";
	rename -uid "0498E4D9-4E3A-B3C1-9CA2-4F8AB3370AF4";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".cc" -type "nurbsCurve" 
		1 8 2 no 3
		9 0 1 2 3 4 5 6 7 8
		9
		44.239337921142578 11.944629669189453 0
		42.560661315917969 11.944629669189453 0
		37.823139190673828 0 0
		39.394546508789063 0 0
		40.712398529052734 3.3008265495300293 0
		45.778182983398438 3.3008265495300293 0
		47.07586669921875 0 0
		48.904296875 0 0
		44.239337921142578 11.944629669189453 0
		;
createNode transform -n "polyToCurve9" -p "RIM_A_Ctrl";
	rename -uid "B8E5F78D-4369-A4A8-06A2-5ABCD222A245";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".t" -type "double3" 3.1124999742588493 0 109.06268831974981 ;
	setAttr ".r" -type "double3" -89.999999999999986 89.999999999999986 0 ;
	setAttr ".s" -type "double3" 0.56055562757094124 0.56055562757094124 0.56055562757094124 ;
createNode nurbsCurve -n "polyToCurveShape9" -p "polyToCurve9";
	rename -uid "906E07F2-47B0-B544-05D4-FFB9D7E83762";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".cc" -type "nurbsCurve" 
		1 15 2 no 3
		16 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
		16
		4.2918128967285156 10.6666259765625 0
		5.4608144760131836 10.551173210144043 0
		6.2956275939941406 10.204813957214355 0
		6.796745777130127 9.6277141571044922 0
		6.9636754989624023 8.8197088241577148 0
		6.9128570556640625 8.2458972930908203 0
		6.7603998184204102 7.7456016540527344 0
		6.5064692497253418 7.3184914588928223 0
		6.1509008407592773 6.9645676612854004 0
		5.6976413726806641 6.6871185302734375 0
		5.1509666442871094 6.4887771606445313 0
		4.5105485916137695 6.3698701858520508 0
		3.7767155170440674 6.3302345275878906 0
		3.2295475006103516 6.3302345275878906 0
		3.2295475006103516 10.6666259765625 0
		4.2918128967285156 10.6666259765625 0
		;
createNode transform -n "polyToCurve10" -p "RIM_A_Ctrl";
	rename -uid "264EBD68-4E04-B0E8-F4C2-06A43C77625C";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".t" -type "double3" 3.1124999742588493 0 109.06268831974981 ;
	setAttr ".r" -type "double3" -89.999999999999986 89.999999999999986 0 ;
	setAttr ".s" -type "double3" 0.56055562757094124 0.56055562757094124 0.56055562757094124 ;
createNode nurbsCurve -n "polyToCurveShape10" -p "polyToCurve10";
	rename -uid "7D3A50E4-4904-D907-E937-6A86FADC03F2";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".cc" -type "nurbsCurve" 
		1 3 2 no 3
		4 0 1 2 3
		4
		43.242961883544922 9.7127265930175781 0
		45.273090362548828 4.5808281898498535 0
		41.207736968994141 4.5808281898498535 0
		43.242961883544922 9.7127265930175781 0
		;
createNode transform -n "KEY_Ctrl" -p "Mend_Ctrl";
	rename -uid "A887845A-4CE6-C011-5013-62BF5F594C42";
	setAttr ".wfcc" -type "float3" 0.28400001 0.014000003 0 ;
	setAttr ".uoc" 2;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -33.231552117587761 73.338597776745374 0 ;
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.028319235803906165 0.028319235803906169 0.028319235803906165 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
createNode bezierCurve -n "KEY_CtrlShape" -p "KEY_Ctrl";
	rename -uid "88968FB6-410E-02E0-BB2F-8E9D1253159D";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0.28400001 0.014000003 0 ;
	setAttr ".uoc" 2;
	setAttr ".cc" -type "dataBezierCurve" 
		3 19 0 no 3
		24 0 0 0 1 1 1 2 2 2 3 3 3 4 4 4 5 5 5 6 6 6 7 7 7
		22
		0 0 0
		0 0 0
		12 0 12
		12 0 12
		12 0 12
		8 0 12
		8 0 12
		8 0 12
		8 0 164.58612750542235
		8 0 164.58612750542235
		8 0 164.58612750542235
		-8 0 164.58612750542235
		-8 0 164.58612750542235
		-8 0 164.58612750542235
		-8 0 12
		-8 0 12
		-8 0 12
		-12 0 12
		-12 0 12
		-12 0 12
		0 0 0
		0 0 0
		;
createNode transform -n "polyToCurve1" -p "KEY_Ctrl";
	rename -uid "27786EC2-48CE-EA4F-0A56-3A8E27B48B09";
	setAttr ".wfcc" -type "float3" 0.28400001 0.014000003 0 ;
	setAttr ".uoc" 2;
	setAttr ".t" -type "double3" 3.3264304354583558 0 105.39924102556922 ;
	setAttr ".r" -type "double3" -90.000000000000057 90 -5.2767107339304438e-15 ;
	setAttr ".s" -type "double3" 0.55535269263694886 0.55535269263694886 0.56118434432931108 ;
createNode nurbsCurve -n "polyToCurveShape1" -p "polyToCurve1";
	rename -uid "1B384522-41E4-4106-FF52-ECA668A5D03C";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0.28400001 0.014000003 0 ;
	setAttr ".uoc" 2;
	setAttr ".cc" -type "nurbsCurve" 
		1 11 2 no 3
		12 0 1 2 3 4 5 6 7 8 9 10 11
		12
		3.1314051151275635 11.944629669189453 0
		1.5414876937866211 11.944629669189453 0
		1.5414876937866211 0 0
		3.1314051151275635 0 0
		3.1314051151275635 6.0530581474304199 0
		8.3532238006591797 0 0
		10.49537181854248 0 0
		4.9905786514282227 6.245455265045166 0
		9.6692571640014648 11.944629669189453 0
		7.965785026550293 11.944629669189453 0
		3.1314051151275635 6.0690913200378418 0
		3.1314051151275635 11.944629669189453 0
		;
createNode transform -n "polyToCurve3" -p "KEY_Ctrl";
	rename -uid "69470282-447D-5F00-1940-4AAAA2D2AB20";
	setAttr ".wfcc" -type "float3" 0.28400001 0.014000003 0 ;
	setAttr ".uoc" 2;
	setAttr ".t" -type "double3" 3.3264304354583549 4.0675640425458421e-31 99.445993662281253 ;
	setAttr ".r" -type "double3" -90.000000000000057 90 0 ;
	setAttr ".s" -type "double3" 0.55535269263694909 0.55535269263694909 0.56118434432931108 ;
createNode nurbsCurve -n "polyToCurveShape3" -p "polyToCurve3";
	rename -uid "9FD5638C-48A0-4BC2-CAF1-40B9D1B5A639";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0.28400001 0.014000003 0 ;
	setAttr ".uoc" 2;
	setAttr ".cc" -type "nurbsCurve" 
		1 9 2 no 3
		10 0 1 2 3 4 5 6 7 8 9
		10
		21.741321563720703 11.944629669189453 0
		19.806612014770508 11.944629669189453 0
		23.793554306030273 4.9876036643981934 0
		23.793554306030273 0 0
		25.488430023193359 0 0
		25.488430023193359 5.0200004577636719 0
		29.757852554321289 11.944629669189453 0
		28.183801651000977 11.944629669189453 0
		24.844959259033203 6.5451245307922363 0
		21.741321563720703 11.944629669189453 0
		;
createNode transform -n "polyToCurve2" -p "KEY_Ctrl";
	rename -uid "70793E67-4503-498E-07CB-B7BBF787EB07";
	setAttr ".wfcc" -type "float3" 0.28400001 0.014000003 0 ;
	setAttr ".uoc" 2;
	setAttr ".t" -type "double3" 3.3264304354583549 8.0118685686509011e-31 103.71270642176179 ;
	setAttr ".r" -type "double3" -90.000000000000057 90 0 ;
	setAttr ".s" -type "double3" 0.55535269263694909 0.55535269263694909 0.56118434432931108 ;
createNode nurbsCurve -n "polyToCurveShape2" -p "polyToCurve2";
	rename -uid "5B31FC6E-4A7D-B36F-CCD5-ECA987FC01C7";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0.28400001 0.014000003 0 ;
	setAttr ".uoc" 2;
	setAttr ".cc" -type "nurbsCurve" 
		1 12 2 no 3
		13 0 1 2 3 4 5 6 7 8 9 10 11 12
		13
		18.959835052490234 11.944629669189453 0
		12.285289764404297 11.944629669189453 0
		12.285289764404297 0 0
		19.306777954101563 0 0
		19.306777954101563 1.2671074867248535 0
		13.980165481567383 1.2671074867248535 0
		13.980165481567383 5.5928926467895508 0
		18.152727127075195 5.5928926467895508 0
		18.152727127075195 6.8439674377441406 0
		13.980165481567383 6.8439674377441406 0
		13.980165481567383 10.677521705627441 0
		18.959835052490234 10.677521705627441 0
		18.959835052490234 11.944629669189453 0
		;
createNode transform -n "Rs_Light" -p "Mend_Ctrl";
	rename -uid "A1ADC7BD-4B26-AD48-EFBC-EBA71657CBA2";
	setAttr ".s" -type "double3" 0.028319235803906165 0.028319235803906165 0.028319235803906165 ;
createNode transform -n "Rs_RIM_C" -p "Rs_Light";
	rename -uid "30555381-4378-B890-92E0-A2892ABE0401";
	setAttr ".v" no;
	setAttr -s 4 ".rlio[0:3]" 1 yes 0 1 yes 0 1 
		yes 0 1 yes 0;
	setAttr ".t" -type "double3" 2.0594761371612549 135.57862854003906 7.8068289756774902 ;
	setAttr ".r" -type "double3" -118.13352217590489 -4.4652062475765808 96.878022953038311 ;
	setAttr ".s" -type "double3" 82.770027282231553 82.770027282231553 82.770027282231553 ;
createNode RedshiftPhysicalLight -n "Rs_RIM_CShape" -p "Rs_RIM_C";
	rename -uid "2DCCBDD1-453D-809D-BEB3-ED81312815B7";
	setAttr -k off ".v";
	setAttr -s 3 ".rlio[0:2]" 1 yes 0 1 yes 0 1 
		yes 0;
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".lightType" 3;
	setAttr ".color" -type "float3" 0.59327132 0.57700002 1 ;
	setAttr ".intensity" 0.5;
	setAttr ".shadowTransparency" 0.30000001192092896;
	setAttr ".SAMPLINGOVERRIDES_shadowSamplesScale" 20;
	setAttr ".SAMPLINGOVERRIDES_numShadowSamples" 64;
	setAttr ".affectedByRefraction" 1;
	setAttr ".glossyRayContributionScale" 0.087209299206733704;
	setAttr ".aovLightGroup" -type "string" "RIM_C";
	setAttr ".de" 2;
	setAttr ".urs" yes;
createNode transform -n "Rs_RIM_B" -p "Rs_Light";
	rename -uid "539B95EC-4F2D-388F-9348-56BD96CCA5BA";
	setAttr ".v" no;
	setAttr -s 3 ".rlio[0:2]" 1 yes 0 1 yes 0 1 
		yes 0;
	setAttr ".t" -type "double3" 2.0594761371612549 135.57862854003906 7.8068289756774902 ;
	setAttr ".r" -type "double3" -118.13352217590489 -4.4652062475765808 96.878022953038311 ;
	setAttr ".s" -type "double3" 82.770027282231553 82.770027282231553 82.770027282231553 ;
createNode RedshiftPhysicalLight -n "Rs_RIM_BShape" -p "Rs_RIM_B";
	rename -uid "1CBE357C-4588-0D9D-2CF8-2CA8C3EACA3C";
	setAttr -k off ".v";
	setAttr -s 2 ".rlio[0:1]" 1 yes 0 1 yes 0;
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".lightType" 3;
	setAttr ".color" -type "float3" 0.59327132 0.57700002 1 ;
	setAttr ".intensity" 0.5;
	setAttr ".shadowTransparency" 0.30000001192092896;
	setAttr ".SAMPLINGOVERRIDES_shadowSamplesScale" 20;
	setAttr ".SAMPLINGOVERRIDES_numShadowSamples" 64;
	setAttr ".affectedByRefraction" 1;
	setAttr ".glossyRayContributionScale" 0.087209299206733704;
	setAttr ".aovLightGroup" -type "string" "RIM_B";
	setAttr ".de" 2;
	setAttr ".urs" yes;
createNode transform -n "Rs_RIM_A" -p "Rs_Light";
	rename -uid "6D9556A3-4377-E900-F171-FE84C22B3C3C";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr -s 2 ".rlio[0:1]" 1 yes 0 1 yes 0;
	setAttr ".t" -type "double3" 0 0 215.03509344481955 ;
	setAttr ".s" -type "double3" 39.976022922922937 39.976022922922937 83.001400178616805 ;
	setAttr ".rp" -type "double3" 0 0 -215.03509344481958 ;
	setAttr ".sp" -type "double3" 0 0 -2.5907405535577697 ;
	setAttr ".spt" -type "double3" 0 0 -212.44435289126181 ;
createNode RedshiftPhysicalLight -n "Rs_RIM_AShape" -p "Rs_RIM_A";
	rename -uid "77A80344-4816-AD64-F630-5D812D5674C1";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 0 1 ;
	setAttr ".uoc" 2;
	setAttr ".rlio[0]" 1 yes 0;
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".lightType" 3;
	setAttr ".color" -type "float3" 0.59327132 0.57700002 1 ;
	setAttr ".intensity" 0.5;
	setAttr ".shadowTransparency" 0.30000001192092896;
	setAttr ".SAMPLINGOVERRIDES_shadowSamplesScale" 20;
	setAttr ".SAMPLINGOVERRIDES_numShadowSamples" 64;
	setAttr ".affectedByRefraction" 1;
	setAttr ".glossyRayContributionScale" 0.087209299206733704;
	setAttr ".aovLightGroup" -type "string" "RIM_A";
	setAttr ".de" 2;
	setAttr ".urs" yes;
createNode orientConstraint -n "Rs_RIM_A_orientConstraint1" -p "Rs_RIM_A";
	rename -uid "D1C27AB8-4D7E-61BB-1ED0-6D8FA24677D9";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "bezier1W0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -24.064227395494573 -46.982539200727508 0 ;
	setAttr -k on ".w0";
createNode transform -n "Rs_KEY" -p "Rs_Light";
	rename -uid "4E772D10-4F94-E52D-0CC4-B3A36659EBDD";
	setAttr ".rlio[0]" 1 yes 0;
	setAttr ".t" -type "double3" 0 0 215.06295381426787 ;
	setAttr ".s" -type "double3" 82.770027282231553 82.770027282231553 82.770027282231553 ;
	setAttr ".rp" -type "double3" 0 0 -215.06295381426784 ;
	setAttr ".sp" -type "double3" 0 0 -2.598319233131821 ;
	setAttr ".spt" -type "double3" 0 0 -212.46463458113601 ;
createNode RedshiftPhysicalLight -n "Rs_KEYShape" -p "Rs_KEY";
	rename -uid "86968D6F-4B52-E4F8-C56A-06B3F5770A39";
	setAttr -k off ".v";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".lightType" 3;
	setAttr ".intensity" 2;
	setAttr ".SAMPLINGOVERRIDES_shadowSamplesScale" 32;
	setAttr ".SAMPLINGOVERRIDES_numShadowSamples" 128;
	setAttr ".affectedByRefraction" 1;
	setAttr ".glossyRayContributionScale" 0.5;
	setAttr ".aovLightGroup" -type "string" "KEY";
	setAttr ".de" 2;
	setAttr ".urs" yes;
createNode orientConstraint -n "Rs_KEY_orientConstraint1" -p "Rs_KEY";
	rename -uid "26BF68AB-4274-AFE2-B834-2FB83F35E9AA";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "KEY_CtrlW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -33.231552117587761 73.338597776745374 0 ;
	setAttr -k on ".w0";
createNode transform -n "Rs_FILL_Dome" -p "Rs_Light";
	rename -uid "4848FA4D-4FBE-752C-C5C4-0A8594F6EC88";
	setAttr ".rlio[0]" 1 yes 0;
	setAttr ".r" -type "double3" 0 90 0 ;
createNode RedshiftDomeLight -n "Rs_FILL_DomeShape" -p "Rs_FILL_Dome";
	rename -uid "D5F91F22-4C22-FA60-BABB-6DADAE90C539";
	setAttr -k off ".v";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".saturation0" 35;
	setAttr ".viewportResolution" 1024;
	setAttr ".tex0" -type "string" "Y:/美术/【美术】视频合成素材Video composite/特效素材/HDR天空素材/Map_Hdr/Picture_Map/hdr/DClientSetupFJ/Desert_Highway/Road_to_MonumentValley_Env.hdr";
	setAttr ".background_enable" no;
	setAttr ".affectedByRefraction" 1;
	setAttr ".aovLightGroup" -type "string" "FILL";
createNode transform -s -n "persp";
	rename -uid "C9EA6023-4B6D-847A-9A9A-B09E041A5C9F";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 190.9158596559941 398.79925200815507 404.60306519722036 ;
	setAttr ".r" -type "double3" -40.538352729596944 26.599999999998566 0 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "B37932C1-45A8-F5AC-DD41-AF90ED2A7E96";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 575.87330031738884;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "37B6791D-4D6E-4640-1456-84BDDCF039FD";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 12.074740822156294 1000.1 104.08151930118517 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "4E3684CA-4A49-74C6-506A-4AB60B8D0560";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 124.47944335307203;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	rename -uid "585482AD-4044-1738-CF05-9BB04C7610C1";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "A6441094-41AE-BA33-F007-8AA96B14013D";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	rename -uid "06437E0B-4311-C771-5BA1-A29084DFB032";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "85F9B09F-4214-5645-1FCC-248A204FE065";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "transform1";
	rename -uid "1F7E92C8-441A-40DE-6BBC-02A2F1482643";
	setAttr ".hio" yes;
createNode displayPoints -n "displayPoints1" -p "transform1";
	rename -uid "F698AD8D-42A4-E230-9404-F49E9CF7EABF";
	setAttr -k off ".v";
	setAttr ".boundingBoxes" -type "vectorArray" 0 ;
	setAttr ".hio" yes;
createNode transform -n "transform2";
	rename -uid "1CC0B691-4AEC-8BF9-E3A9-FEB4735F4910";
	setAttr ".hio" yes;
createNode displayPoints -n "displayPoints2" -p "transform2";
	rename -uid "98A29416-4966-6BD9-1A4C-AEB350BE47E7";
	setAttr -k off ".v";
	setAttr ".boundingBoxes" -type "vectorArray" 0 ;
	setAttr ".hio" yes;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "52819FEE-479A-8318-C109-29926B96CE29";
	setAttr -s 5 ".lnk";
	setAttr -s 5 ".slnk";
createNode RedshiftOptions -s -n "redshiftOptions";
	rename -uid "46702457-41FB-60D5-077B-38A38F73F216";
createNode RedshiftPostEffects -n "defaultRedshiftPostEffects";
	rename -uid "338EA440-43E5-0C4A-E15E-6085AD83DF07";
	setAttr ".clrMgmtDisplayMode" -type "string" "RS_COLORMANAGEMENTDISPLAYMODE_SRGB";
	setAttr -s 2 ".cr[1]" -type "float2" 1 1;
	setAttr -s 2 ".cg[1]" -type "float2" 1 1;
	setAttr -s 2 ".cb[1]" -type "float2" 1 1;
	setAttr -s 2 ".cl[1]" -type "float2" 1 1;
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "3E7ADEC1-49D1-7C38-0E4C-41AC5AC303D7";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "DF4EEDBF-4E98-053E-AD43-1A952403C6E7";
createNode displayLayerManager -n "layerManager";
	rename -uid "838403C3-467D-0A1D-32B6-ADB564575790";
createNode displayLayer -n "defaultLayer";
	rename -uid "C3B3A5B1-42A1-E0C2-5C7C-1EA2053660B7";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "4EBF481A-44B9-3A8A-ABDA-6E809EAAD16C";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "434408BB-4938-5060-C35D-69B49ECD6D08";
	setAttr ".g" yes;
createNode script -n "uiConfigurationScriptNode";
	rename -uid "FA01335D-463B-6AF9-718F-B3B7F73003A5";
	setAttr ".b" -type "string" (
		"// Maya Mel UI Configuration File.\n//\n//  This script is machine generated.  Edit at your own risk.\n//\n//\n\nglobal string $gMainPane;\nif (`paneLayout -exists $gMainPane`) {\n\n\tglobal int $gUseScenePanelConfig;\n\tint    $useSceneConfig = $gUseScenePanelConfig;\n\tint    $nodeEditorPanelVisible = stringArrayContains(\"nodeEditorPanel1\", `getPanel -vis`);\n\tint    $nodeEditorWorkspaceControlOpen = (`workspaceControl -exists nodeEditorPanel1Window` && `workspaceControl -q -visible nodeEditorPanel1Window`);\n\tint    $menusOkayInPanels = `optionVar -q allowMenusInPanels`;\n\tint    $nVisPanes = `paneLayout -q -nvp $gMainPane`;\n\tint    $nPanes = 0;\n\tstring $editorName;\n\tstring $panelName;\n\tstring $itemFilterName;\n\tstring $panelConfig;\n\n\t//\n\t//  get current state of the UI\n\t//\n\tsceneUIReplacement -update $gMainPane;\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Top View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"top\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n"
		+ "            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n"
		+ "            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n"
		+ "\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Side View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"side\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n"
		+ "            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n"
		+ "            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n"
		+ "            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Front View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"front\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n"
		+ "            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n"
		+ "            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n"
		+ "            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Persp View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"persp\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n"
		+ "            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n"
		+ "            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n"
		+ "            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1316\n            -height 683\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"ToggledOutliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"ToggledOutliner\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -docTag \"isolOutln_fromSeln\" \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 1\n            -showReferenceMembers 1\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n"
		+ "            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n"
		+ "            -expandAttribute 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n"
		+ "            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n"
		+ "            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"graphEditor\" (localizedPanelLabel(\"Graph Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n"
		+ "                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 1\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n"
		+ "                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 1\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 1\n                -autoFitTime 0\n                -snapTime \"integer\" \n"
		+ "                -snapValue \"none\" \n                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -showCurveNames 0\n                -showActiveCurveNames 0\n                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 0\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                -valueLinesToggle 1\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dopeSheetPanel\" (localizedPanelLabel(\"Dope Sheet\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 1\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n"
		+ "                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n"
		+ "                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -autoFitTime 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -showSummary 1\n                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"timeEditorPanel\" (localizedPanelLabel(\"Time Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Time Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"clipEditorPanel\" (localizedPanelLabel(\"Trax Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -autoFitTime 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"sequenceEditorPanel\" (localizedPanelLabel(\"Camera Sequencer\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -autoFitTime 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 1 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperGraphPanel\" (localizedPanelLabel(\"Hypergraph Hierarchy\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n                -showConstraintLabels 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n"
		+ "                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperShadePanel\" (localizedPanelLabel(\"Hypershade\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"visorPanel\" (localizedPanelLabel(\"Visor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"nodeEditorPanel\" (localizedPanelLabel(\"Node Editor\")) `;\n\tif ($nodeEditorPanelVisible || $nodeEditorWorkspaceControlOpen) {\n"
		+ "\t\tif (\"\" == $panelName) {\n\t\t\tif ($useSceneConfig) {\n\t\t\t\t$panelName = `scriptedPanel -unParent  -type \"nodeEditorPanel\" -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n"
		+ "                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -editorMode \"default\" \n                $editorName;\n\t\t\t}\n\t\t} else {\n\t\t\t$label = `panel -q -label $panelName`;\n\t\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n"
		+ "                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -editorMode \"default\" \n                $editorName;\n\t\t\tif (!$useSceneConfig) {\n\t\t\t\tpanel -e -l $label $panelName;\n\t\t\t}\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"createNodePanel\" (localizedPanelLabel(\"Create Node\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"polyTexturePlacementPanel\" (localizedPanelLabel(\"UV Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"UV Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"renderWindowPanel\" (localizedPanelLabel(\"Render View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"shapePanel\" (localizedPanelLabel(\"Shape Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tshapePanel -edit -l (localizedPanelLabel(\"Shape Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"posePanel\" (localizedPanelLabel(\"Pose Editor\")) `;\n\tif (\"\" != $panelName) {\n"
		+ "\t\t$label = `panel -q -label $panelName`;\n\t\tposePanel -edit -l (localizedPanelLabel(\"Pose Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynRelEdPanel\" (localizedPanelLabel(\"Dynamic Relationships\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"relationshipPanel\" (localizedPanelLabel(\"Relationship Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"referenceEditorPanel\" (localizedPanelLabel(\"Reference Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"componentEditorPanel\" (localizedPanelLabel(\"Component Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Component Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynPaintScriptedPanelType\" (localizedPanelLabel(\"Paint Effects\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"scriptEditorPanel\" (localizedPanelLabel(\"Script Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"profilerPanel\" (localizedPanelLabel(\"Profiler Tool\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Profiler Tool\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"contentBrowserPanel\" (localizedPanelLabel(\"Content Browser\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Content Browser\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"Stereo\" (localizedPanelLabel(\"Stereo\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Stereo\")) -mbv $menusOkayInPanels  $panelName;\nstring $editorName = ($panelName+\"Editor\");\n            stereoCameraView -e \n                -camera \"persp\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"smoothShaded\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -holdOuts 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 0\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n"
		+ "                -textureDisplay \"modulate\" \n                -textureMaxSize 32768\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -depthOfFieldPreview 1\n                -maxConstantTransparency 1\n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 4 4 \n                -bumpResolution 4 4 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 0\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n"
		+ "                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -controllers 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n"
		+ "                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                -captureSequenceNumber -1\n                -width 0\n                -height 0\n                -sceneRenderFilter 0\n                -displayMode \"centerEye\" \n                -viewColor 0 0 0 1 \n                -useCustomBackground 1\n                $editorName;\n            stereoCameraView -e -viewSelected 0 $editorName;\n            stereoCameraView -e \n                -pluginObjects \"gpuCacheDisplayFilter\" 1 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\tif ($useSceneConfig) {\n        string $configName = `getPanel -cwl (localizedPanelLabel(\"Current Layout\"))`;\n        if (\"\" != $configName) {\n\t\t\tpanelConfiguration -edit -label (localizedPanelLabel(\"Current Layout\")) \n\t\t\t\t-userCreated false\n\t\t\t\t-defaultImage \"vacantCell.xP:/\"\n\t\t\t\t-image \"\"\n\t\t\t\t-sc false\n\t\t\t\t-configString \"global string $gMainPane; paneLayout -e -cn \\\"single\\\" -ps 1 100 100 $gMainPane;\"\n\t\t\t\t-removeAllPanels\n"
		+ "\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Persp View\")) \n\t\t\t\t\t\"modelPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1316\\n    -height 683\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1316\\n    -height 683\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 5 -size 12 -divisions 5 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels no -displayOrthographicLabels no -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "5B9EC2A6-4571-BFC1-A9F8-769FCAED5469";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
select -ne :time1;
	setAttr -av -k on ".cch";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr ".o" 1;
	setAttr -av ".unw" 1;
	setAttr -k on ".etw";
	setAttr -av -k on ".tps";
	setAttr -av -k on ".tms";
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".aasc" 16;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -cb on ".cch";
	setAttr -cb on ".ihi";
	setAttr -cb on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".st";
	setAttr -cb on ".an";
	setAttr -cb on ".pt";
select -ne :renderGlobalsList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
select -ne :defaultShaderList1;
	setAttr -cb on ".cch";
	setAttr -cb on ".ihi";
	setAttr -cb on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 4 ".s";
select -ne :postProcessList1;
	setAttr -cb on ".cch";
	setAttr -cb on ".ihi";
	setAttr -cb on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".p";
select -ne :defaultRenderUtilityList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
select -ne :defaultRenderingList1;
	setAttr -k on ".ihi";
select -ne :lightList1;
	setAttr -s 5 ".l";
select -ne :initialShadingGroup;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -cb on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".macc";
	setAttr -k on ".macd";
	setAttr -k on ".macq";
	setAttr -k on ".mcfr";
	setAttr -k on ".ifg";
	setAttr -k on ".clip";
	setAttr -k on ".edm";
	setAttr -k on ".edl";
	setAttr ".ren" -type "string" "redshift";
	setAttr -av -k on ".esr";
	setAttr -k on ".ors";
	setAttr -cb on ".sdf";
	setAttr -av ".outf" 51;
	setAttr ".imfkey" -type "string" "tif";
	setAttr -k on ".gama";
	setAttr -cb on ".an";
	setAttr -k on ".ar";
	setAttr -k on ".fs";
	setAttr -k on ".ef";
	setAttr -av -k on ".bfs";
	setAttr -k on ".me";
	setAttr -k on ".se";
	setAttr -k on ".be";
	setAttr -cb on ".ep";
	setAttr -k on ".fec";
	setAttr -av -k on ".ofc";
	setAttr -cb on ".ofe";
	setAttr -cb on ".efe";
	setAttr -cb on ".oft";
	setAttr -k on ".umfn";
	setAttr -k on ".ufe";
	setAttr ".pff" yes;
	setAttr -k on ".peie";
	setAttr -cb on ".ifp" -type "string" "<RenderLayer>/<RenderLayer>";
	setAttr -k on ".rv";
	setAttr -k on ".comp";
	setAttr -k on ".cth";
	setAttr -k on ".soll";
	setAttr -k on ".sosl";
	setAttr -k on ".rd";
	setAttr -k on ".lp";
	setAttr -av -k on ".sp";
	setAttr -k on ".shs";
	setAttr -k on ".lpr";
	setAttr -cb on ".gv";
	setAttr -cb on ".sv";
	setAttr -k on ".mm";
	setAttr -k on ".npu";
	setAttr -k on ".itf";
	setAttr -k on ".shp";
	setAttr -cb on ".isp";
	setAttr -k on ".uf";
	setAttr -k on ".oi";
	setAttr -k on ".rut";
	setAttr -k on ".mot";
	setAttr -av -k on ".mb";
	setAttr -av -k on ".mbf";
	setAttr -k on ".afp";
	setAttr -k on ".pfb";
	setAttr -k on ".pram";
	setAttr -k on ".poam";
	setAttr -k on ".prlm";
	setAttr -k on ".polm";
	setAttr -k on ".prm";
	setAttr -k on ".pom";
	setAttr -cb on ".pfrm";
	setAttr -cb on ".pfom";
	setAttr -av -k on ".bll";
	setAttr -av -k on ".bls";
	setAttr -av -k on ".smv";
	setAttr -k on ".ubc";
	setAttr -k on ".mbc";
	setAttr -cb on ".mbt";
	setAttr -k on ".udbx";
	setAttr -k on ".smc";
	setAttr -k on ".kmv";
	setAttr -cb on ".isl";
	setAttr -cb on ".ism";
	setAttr -cb on ".imb";
	setAttr -k on ".rlen";
	setAttr -av -k on ".frts";
	setAttr -k on ".tlwd";
	setAttr -k on ".tlht";
	setAttr -k on ".jfc";
	setAttr -cb on ".rsb";
	setAttr -k on ".ope";
	setAttr -k on ".oppf";
	setAttr -cb on ".hbl";
select -ne :defaultResolution;
	setAttr -av -k on ".cch";
	setAttr -av -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -av ".w" 2048;
	setAttr -av ".h" 2048;
	setAttr -av ".pa" 1;
	setAttr -av -k on ".al";
	setAttr -av ".dar" 1;
	setAttr -av -k on ".ldar";
	setAttr -av -k on ".dpi";
	setAttr -av -k on ".off";
	setAttr -av -k on ".fld";
	setAttr -av -k on ".zsl";
	setAttr -av -k on ".isu";
	setAttr -av -k on ".pdu";
select -ne :defaultLightSet;
	setAttr -s 5 ".dsm";
select -ne :hardwareRenderGlobals;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr ".ctrs" 256;
	setAttr -av ".btrs" 512;
	setAttr -k off ".fbfm";
	setAttr -k off -cb on ".ehql";
	setAttr -k off -cb on ".eams";
	setAttr -k off -cb on ".eeaa";
	setAttr -k off -cb on ".engm";
	setAttr -k off -cb on ".mes";
	setAttr -k off -cb on ".emb";
	setAttr -av -k off -cb on ".mbbf";
	setAttr -k off -cb on ".mbs";
	setAttr -k off -cb on ".trm";
	setAttr -k off -cb on ".tshc";
	setAttr -k off ".enpt";
	setAttr -k off -cb on ".clmt";
	setAttr -k off -cb on ".tcov";
	setAttr -k off -cb on ".lith";
	setAttr -k off -cb on ".sobc";
	setAttr -k off -cb on ".cuth";
	setAttr -k off -cb on ".hgcd";
	setAttr -k off -cb on ".hgci";
	setAttr -k off -cb on ".mgcs";
	setAttr -k off -cb on ".twa";
	setAttr -k off -cb on ".twz";
	setAttr -k on ".hwcc";
	setAttr -k on ".hwdp";
	setAttr -k on ".hwql";
	setAttr -k on ".hwfr";
	setAttr -k on ".soll";
	setAttr -k on ".sosl";
	setAttr -k on ".bswa";
	setAttr -k on ".shml";
	setAttr -k on ".hwel";
connectAttr "Rs_RIM_A_orientConstraint1.crx" "Rs_RIM_A.rx";
connectAttr "Rs_RIM_A_orientConstraint1.cry" "Rs_RIM_A.ry";
connectAttr "Rs_RIM_A_orientConstraint1.crz" "Rs_RIM_A.rz";
connectAttr "Rs_RIM_A.ro" "Rs_RIM_A_orientConstraint1.cro";
connectAttr "Rs_RIM_A.pim" "Rs_RIM_A_orientConstraint1.cpim";
connectAttr "RIM_A_Ctrl.r" "Rs_RIM_A_orientConstraint1.tg[0].tr";
connectAttr "RIM_A_Ctrl.ro" "Rs_RIM_A_orientConstraint1.tg[0].tro";
connectAttr "RIM_A_Ctrl.pm" "Rs_RIM_A_orientConstraint1.tg[0].tpm";
connectAttr "Rs_RIM_A_orientConstraint1.w0" "Rs_RIM_A_orientConstraint1.tg[0].tw"
		;
connectAttr "Rs_KEY_orientConstraint1.crx" "Rs_KEY.rx";
connectAttr "Rs_KEY_orientConstraint1.cry" "Rs_KEY.ry";
connectAttr "Rs_KEY_orientConstraint1.crz" "Rs_KEY.rz";
connectAttr "Rs_KEY.ro" "Rs_KEY_orientConstraint1.cro";
connectAttr "Rs_KEY.pim" "Rs_KEY_orientConstraint1.cpim";
connectAttr "KEY_Ctrl.r" "Rs_KEY_orientConstraint1.tg[0].tr";
connectAttr "KEY_Ctrl.ro" "Rs_KEY_orientConstraint1.tg[0].tro";
connectAttr "KEY_Ctrl.pm" "Rs_KEY_orientConstraint1.tg[0].tpm";
connectAttr "Rs_KEY_orientConstraint1.w0" "Rs_KEY_orientConstraint1.tg[0].tw";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "defaultRedshiftPostEffects.msg" ":redshiftOptions.postEffects";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "defaultRedshiftPostEffects.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "Rs_FILL_DomeShape.ltd" ":lightList1.l" -na;
connectAttr "Rs_KEYShape.ltd" ":lightList1.l" -na;
connectAttr "Rs_RIM_AShape.ltd" ":lightList1.l" -na;
connectAttr "Rs_RIM_BShape.ltd" ":lightList1.l" -na;
connectAttr "Rs_RIM_CShape.ltd" ":lightList1.l" -na;
connectAttr "Rs_FILL_Dome.iog" ":defaultLightSet.dsm" -na;
connectAttr "Rs_KEY.iog" ":defaultLightSet.dsm" -na;
connectAttr "Rs_RIM_A.iog" ":defaultLightSet.dsm" -na;
connectAttr "Rs_RIM_B.iog" ":defaultLightSet.dsm" -na;
connectAttr "Rs_RIM_C.iog" ":defaultLightSet.dsm" -na;
// End of Rs_CH_LGT.ma

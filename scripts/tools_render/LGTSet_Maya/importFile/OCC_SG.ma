//Maya ASCII 2014 scene
//Name: occ.ma
//Last modified: Tue, Dec 22, 2015 01:21:42 PM
//Codeset: 936
requires maya "2014";
requires -nodeType "mentalrayFramebuffer" -nodeType "mentalrayOutputPass" -nodeType "mentalrayRenderPass"
		 -nodeType "mentalrayUserBuffer" -nodeType "mentalraySubdivApprox" -nodeType "mentalrayCurveApprox"
		 -nodeType "mentalraySurfaceApprox" -nodeType "mentalrayDisplaceApprox" -nodeType "mentalrayOptions"
		 -nodeType "mentalrayGlobals" -nodeType "mentalrayItemsList" -nodeType "mentalrayShader"
		 -nodeType "mentalrayUserData" -nodeType "mentalrayText" -nodeType "mentalrayTessellation"
		 -nodeType "mentalrayPhenomenon" -nodeType "mentalrayLightProfile" -nodeType "mentalrayVertexColors"
		 -nodeType "mentalrayIblShape" -nodeType "mapVizShape" -nodeType "mentalrayCCMeshProxy"
		 -nodeType "cylindricalLightLocator" -nodeType "discLightLocator" -nodeType "rectangularLightLocator"
		 -nodeType "sphericalLightLocator" -nodeType "CgSssAdapter" -nodeType "abcimport"
		 -nodeType "mia_physicalsun" -nodeType "mia_physicalsky" -nodeType "mia_material"
		 -nodeType "mia_material_x" -nodeType "mia_roundcorners" -nodeType "mia_exposure_simple"
		 -nodeType "mia_portal_light" -nodeType "mia_light_surface" -nodeType "mia_exposure_photographic"
		 -nodeType "mia_exposure_photographic_rev" -nodeType "mia_lens_bokeh" -nodeType "mia_envblur"
		 -nodeType "mia_ciesky" -nodeType "mia_photometric_light" -nodeType "mib_texture_vector"
		 -nodeType "mib_texture_remap" -nodeType "mib_texture_rotate" -nodeType "mib_bump_basis"
		 -nodeType "mib_bump_map" -nodeType "mib_passthrough_bump_map" -nodeType "mib_bump_map2"
		 -nodeType "mib_lookup_spherical" -nodeType "mib_lookup_cube1" -nodeType "mib_lookup_cube6"
		 -nodeType "mib_lookup_background" -nodeType "mib_lookup_cylindrical" -nodeType "mib_texture_lookup"
		 -nodeType "mib_texture_lookup2" -nodeType "mib_texture_filter_lookup" -nodeType "mib_texture_checkerboard"
		 -nodeType "mib_texture_polkadot" -nodeType "mib_texture_polkasphere" -nodeType "mib_texture_turbulence"
		 -nodeType "mib_texture_wave" -nodeType "mib_reflect" -nodeType "mib_refract" -nodeType "mib_transparency"
		 -nodeType "mib_continue" -nodeType "mib_opacity" -nodeType "mib_twosided" -nodeType "mib_refraction_index"
		 -nodeType "mib_dielectric" -nodeType "mib_ray_marcher" -nodeType "mib_illum_lambert"
		 -nodeType "mib_illum_phong" -nodeType "mib_illum_ward" -nodeType "mib_illum_ward_deriv"
		 -nodeType "mib_illum_blinn" -nodeType "mib_illum_cooktorr" -nodeType "mib_illum_hair"
		 -nodeType "mib_volume" -nodeType "mib_color_alpha" -nodeType "mib_color_average"
		 -nodeType "mib_color_intensity" -nodeType "mib_color_interpolate" -nodeType "mib_color_mix"
		 -nodeType "mib_color_spread" -nodeType "mib_geo_cube" -nodeType "mib_geo_torus" -nodeType "mib_geo_sphere"
		 -nodeType "mib_geo_cone" -nodeType "mib_geo_cylinder" -nodeType "mib_geo_square"
		 -nodeType "mib_geo_instance" -nodeType "mib_geo_instance_mlist" -nodeType "mib_geo_add_uv_texsurf"
		 -nodeType "mib_photon_basic" -nodeType "mib_light_infinite" -nodeType "mib_light_point"
		 -nodeType "mib_light_spot" -nodeType "mib_light_photometric" -nodeType "mib_cie_d"
		 -nodeType "mib_blackbody" -nodeType "mib_shadow_transparency" -nodeType "mib_lens_stencil"
		 -nodeType "mib_lens_clamp" -nodeType "mib_lightmap_write" -nodeType "mib_lightmap_sample"
		 -nodeType "mib_amb_occlusion" -nodeType "mib_fast_occlusion" -nodeType "mib_map_get_scalar"
		 -nodeType "mib_map_get_integer" -nodeType "mib_map_get_vector" -nodeType "mib_map_get_color"
		 -nodeType "mib_map_get_transform" -nodeType "mib_map_get_scalar_array" -nodeType "mib_map_get_integer_array"
		 -nodeType "mib_fg_occlusion" -nodeType "mib_bent_normal_env" -nodeType "mib_glossy_reflection"
		 -nodeType "mib_glossy_refraction" -nodeType "builtin_bsdf_architectural" -nodeType "builtin_bsdf_architectural_comp"
		 -nodeType "builtin_bsdf_carpaint" -nodeType "builtin_bsdf_ashikhmin" -nodeType "builtin_bsdf_lambert"
		 -nodeType "builtin_bsdf_mirror" -nodeType "builtin_bsdf_phong" -nodeType "cg_amb_light_sampler"
		 -nodeType "cg_data_occlusion" -nodeType "cg_amb_occlusion" -nodeType "cg_amb_occlusion_x"
		 -nodeType "cg_curve_sampler" -nodeType "cg_curve_rand_sampler" -nodeType "cg_shave_color_sampler"
		 -nodeType "cgGeoReplace" -nodeType "cgOcclusionUtility" -nodeType "cgSampleUV" -nodeType "cgOcclusion"
		 -nodeType "cgOcclusionPhen" -nodeType "cgPassSwitcher" -nodeType "cgTexSwitcher"
		 -nodeType "cgFrameSwitcher" -nodeType "cgMaterialUtility" -nodeType "cgMotionVector"
		 -nodeType "cgMaterial" -nodeType "cgMultiplePassGeo" -nodeType "cgMultiplePassEXRWriter"
		 -nodeType "cg_uv_ray_filter" -nodeType "contour_store_function" -nodeType "contour_store_function_simple"
		 -nodeType "contour_contrast_function_levels" -nodeType "contour_contrast_function_simple"
		 -nodeType "contour_shader_simple" -nodeType "contour_shader_silhouette" -nodeType "contour_shader_maxcolor"
		 -nodeType "contour_shader_curvature" -nodeType "contour_shader_factorcolor" -nodeType "contour_shader_depthfade"
		 -nodeType "contour_shader_framefade" -nodeType "contour_shader_layerthinner" -nodeType "contour_shader_widthfromcolor"
		 -nodeType "contour_shader_widthfromlightdir" -nodeType "contour_shader_widthfromlight"
		 -nodeType "contour_shader_combi" -nodeType "contour_only" -nodeType "contour_composite"
		 -nodeType "contour_ps" -nodeType "JS_fisheye" -nodeType "JS_panoramic" -nodeType "latlong_lens"
		 -nodeType "lm2DMV_v2" -nodeType "massive_mray" -nodeType "massive_mray_wrapper" -nodeType "textured_mtl_sh"
		 -nodeType "massive_light_ambient" -nodeType "massive_light_physic" -nodeType "massive_matte"
		 -nodeType "massive_hair" -nodeType "mix8layer" -nodeType "outputNormal" -nodeType "mi_metallic_paint"
		 -nodeType "mi_metallic_paint_x" -nodeType "mi_bump_flakes" -nodeType "mi_car_paint_phen"
		 -nodeType "mi_metallic_paint_output_mixer" -nodeType "mi_car_paint_phen_x" -nodeType "physical_lens_dof"
		 -nodeType "physical_light" -nodeType "dgs_material" -nodeType "dgs_material_photon"
		 -nodeType "dielectric_material" -nodeType "dielectric_material_photon" -nodeType "oversampling_lens"
		 -nodeType "path_material" -nodeType "parti_volume" -nodeType "parti_volume_photon"
		 -nodeType "transmat" -nodeType "transmat_photon" -nodeType "mip_rayswitch" -nodeType "mip_rayswitch_advanced"
		 -nodeType "mip_rayswitch_environment" -nodeType "mip_card_opacity" -nodeType "mip_motionblur"
		 -nodeType "mip_motion_vector" -nodeType "mip_matteshadow" -nodeType "mip_cameramap"
		 -nodeType "mip_mirrorball" -nodeType "mip_grayball" -nodeType "mip_gamma_gain" -nodeType "mip_render_subset"
		 -nodeType "mip_matteshadow_mtl" -nodeType "mip_binaryproxy" -nodeType "mip_rayswitch_stage"
		 -nodeType "mip_fgshooter" -nodeType "mib_ptex_lookup" -nodeType "SpecificObject"
		 -nodeType "misss_physical" -nodeType "misss_physical_phen" -nodeType "misss_fast_shader"
		 -nodeType "misss_fast_shader_x" -nodeType "misss_fast_shader2" -nodeType "misss_fast_shader2_x"
		 -nodeType "misss_skin_specular" -nodeType "misss_lightmap_write" -nodeType "misss_lambert_gamma"
		 -nodeType "misss_call_shader" -nodeType "misss_set_normal" -nodeType "misss_fast_lmap_maya"
		 -nodeType "misss_fast_simple_maya" -nodeType "misss_fast_skin_maya" -nodeType "misss_fast_skin_phen"
		 -nodeType "misss_fast_skin_phen_d" -nodeType "misss_mia_skin2_phen" -nodeType "misss_mia_skin2_phen_d"
		 -nodeType "misss_lightmap_phen" -nodeType "misss_mia_skin2_surface_phen" -nodeType "surfaceSampler"
		 -nodeType "TransparentObject" -nodeType "mib_data_bool" -nodeType "mib_data_int"
		 -nodeType "mib_data_scalar" -nodeType "mib_data_vector" -nodeType "mib_data_color"
		 -nodeType "mib_data_string" -nodeType "mib_data_texture" -nodeType "mib_data_shader"
		 -nodeType "mib_data_bool_array" -nodeType "mib_data_int_array" -nodeType "mib_data_scalar_array"
		 -nodeType "mib_data_vector_array" -nodeType "mib_data_color_array" -nodeType "mib_data_string_array"
		 -nodeType "mib_data_texture_array" -nodeType "mib_data_shader_array" -nodeType "mib_data_get_bool"
		 -nodeType "mib_data_get_int" -nodeType "mib_data_get_scalar" -nodeType "mib_data_get_vector"
		 -nodeType "mib_data_get_color" -nodeType "mib_data_get_string" -nodeType "mib_data_get_texture"
		 -nodeType "mib_data_get_shader" -nodeType "mib_data_get_shader_bool" -nodeType "mib_data_get_shader_int"
		 -nodeType "mib_data_get_shader_scalar" -nodeType "mib_data_get_shader_vector" -nodeType "mib_data_get_shader_color"
		 -nodeType "user_ibl_env" -nodeType "user_ibl_rect" -nodeType "cgsss_skin_x_passes"
		 -nodeType "mia_material_x_passes" -nodeType "mi_metallic_paint_x_passes" -nodeType "mi_car_paint_phen_x_passes"
		 -nodeType "misss_fast_shader_x_passes" -nodeType "cgMassiveShader" -nodeType "phen_fastAO"
		 -nodeType "phen_playblastMayaLambert" -nodeType "phen_playblastMayaLambertTex" -dataType "byteArray"
		 "Mayatomr" "2014.0 - 3.11.1.9 ";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2014";
fileInfo "version" "2014";
fileInfo "cutIdentifier" "201307170459-880822";
fileInfo "osv" "Microsoft Windows 7 Business Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode surfaceShader -n "A_OCC_SG";
createNode mib_amb_occlusion -n "mib_amb_occlusion1";
	setAttr ".S00" 32;
	setAttr ".S04" 30;
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :renderPartition;
	setAttr -s 3 ".st";
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultShaderList1;
	setAttr -s 3 ".s";
select -ne :defaultTextureList1;
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
	setAttr -s 2 ".r";
select -ne :renderGlobalsList1;
select -ne :defaultRenderGlobals;
	setAttr ".edl" no;
	setAttr ".ren" -type "string" "mentalRay";
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 18 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surfaces" "Particles" "Fluids" "Image Planes" "UI:" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 18 0 1 1 1 1 1
		 1 0 0 0 0 0 0 0 0 0 0 0 ;
select -ne :defaultHardwareRenderGlobals;
	setAttr ".fn" -type "string" "im";
	setAttr ".res" -type "string" "ntsc_4d 646 485 1.333";
connectAttr "mib_amb_occlusion1.S11" "A_OCC_SG.oc";
connectAttr "A_OCC_SG.msg" ":defaultShaderList1.s" -na;
connectAttr "mib_amb_occlusion1.msg" ":defaultTextureList1.tx" -na;
// End of occ.ma

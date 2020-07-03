# Blender p3d import-export
Crashday p3d model import-export addon for blender 2.83  

## Usage
### Installation
To install, download latest version from github releases  
In Blender go to Edit->Preferences  
Select Add-ons  
Click "Install..." button at the top and select downloaded zip file  
### Importing
You can import a model in File->Import->Crashday (.p3d)  
When importing you can also add up to four texture path's. If provided, the addon will try to load textures from these folders.  
### Exporting
"Lower top bound" and "Life bottom bound" are working the same as in makep3d.  
Also you can enable export-log which is created in the same folder as the exported file and contains export log as well as meshes list, used in .cca files.
#### Lights
When exporting you have options to turn on coronas, flares, and environment light up for all the lights.  
Though, makep3d sets coronas to off and environment light up to on for every light, which may mean whose values are unused.  

## Moddeling guidelines
CD .p3d format does not support a lot of options available in blender and also uses some old techniques to achieve certain things. Because of that users need to model and structure the scene in a certain way to achieve a good look.
### Lights
Parameters which are exported from light objects are "color" and "power"
### Materials
When importing a model you will see that every imported material has a special name which in general looks like
"type_name.tga". When texturing you might want to use .dds textures which are suported by CD, but in materials list you still should refer to them as .tga.  
CD has different types of materials stored in the .p3d file, but you cant set them in blender in any simple way.
To fix this all materials were given a short type name and if it's present in front of the material name, the appropriate material will be set in .p3d. Available options are:
- Flat: "f_"
- Flat metal: "fm_"
- Gouraud (smooth): "g_"
- Gouraud metal: "gm_"
- Gouraud metal environment: "gme_"
- Shining: "s_"
### Creating hard edges
CD .p3d files do not store any information about normals which means we can not change how smoothing works(only by using pre-set material-types). While Flat materials will show triangles and all the edges will look hard, Gouraud materials will smooth everything. Sometimes it is needed to create a hard edge on smooth surface. The CD way to do this is to split the edge.

## TODO:
- when importing sort car parts into collections
- maybe load .cca and add positions
- check if no uvs or no material
- correctly center meshes
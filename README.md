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
**Object rotation is not applied on export.**  
You can enable export-log which is created in the same folder as the exported file and contains export log as well as meshes list, used in .cca files. This info is also logged in Blender's console.
##### Lights
In Lights tab a panel named "CDRE - Light" was added, which lets you edit Crashday's light settings.  
Though, makep3d sets coronas to off and environment light up to on for every light, which may mean those values are obsolete.  

## Moddeling guidelines
CD .p3d format does not support a lot of options available in blender and also uses some old techniques to achieve certain things. Because of that users need to model and structure the scene in a certain way to achieve a good look.  
Y+ axis in blender is forward direction for cars.
### Materials
For materials a new panel was added named "CDRE - Material". This panel has material type and texture name used by Crashday.
There is no need to add an extension to the texture name, but remember CD uses .dds or .tga.
### Creating hard edges
CD .p3d files do not store any information about normals which means we can not change how smoothing works(only by using pre-set material types). While Flat materials will show triangles and all the edges will look hard, Gouraud materials will smooth everything. Sometimes it is needed to create a hard edge on smooth surface. The CD way to do this is to split the edge.

## TODO:
- dimensions in .p3d mesh are read in the wrong order
- add flags export
- print error when no uv unrap was present, or create a default one
- when importing sort car parts into collections
- save export import settings if possible
- apply obect mode rotation
- correctly center meshes?
- ~~maybe load .cca and add positions~~
- ~~automaticaly set floor~~
- ~~check if no material is on object~~
- ~~option to export models with applied modifiers~~
- ~~correctly set smoothing based on material when importing~~
- ~~error when in edit mode~~
- ~~check material names and .tga automatically~~
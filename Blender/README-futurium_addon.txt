///Why these add ons? ///

Futurium Add-on I created to speed up my sepecifc workflow at work. Currently it has 2 features. 
 - A tool to reset specular, metallic and opacity to default on materials as Maya files, imported into Blender change up these values. This in turn effects the model in the viewport when brought back into Maya.
 - An Exporter to export a model with the correct transform values to match Maya.

Move and Scale plans is to take imported DXF files, set the pivots of each object to be central to the house and then move all to world space 0,0,0.
The outer wall should be called Wall_Trad (upper or lower case). If this is not the case, contact me as I will need to adjust the code and way it is used.


///How to use ///

Futurium Add-on - The material reset button works as is and resets the specified values mentioned above.
The exporter requires some script editing until I implement some UI options for the user. Set the save path on line 104. The name of the file saves as the name of the root mesh.
You can also input objects to be exluded (keep their transforms, e.g. assets originally made in Maya and imported into Blender, without their transforms changed). Do this on Line 83, put in part of the name or the full name.
!!this does reset scale and rotation values on export, if this doesnt work for your situation, don't use!!

Move and scale plans - After converting plans from DWG to DXF and editing to be only one page of the plans. Import into blender at scale 0.001 (Could change with other clients?) and switch off import text.
Once loaded, select all, choose which object you want the pivot to be central of by making it the active object (e.g Outer Walls or Screed for stairs plans), then run the script.


///How to install Blender addons! ///

Load up Blender, go to Edit > Preferences > Add-ons and then click Install in the top left of the window. 
Locate the .py file on your PC and confirm. Ensure the check box is ticked on the add-on window.


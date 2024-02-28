///Why these add ons? ///

To make working between maya and blender as easy as possible. Also new features to work alongside the house generating tool created in geometry nodes.


///How to use ///

Maya Export - Currently a scale bug so beware, comes in maya at 100x scale since changing to adding interiors onto exporter.
Select root of house, choose filepath in the panel, button then exports root and all children, applying correct transforms but leaving child objects specified in the code.

Reset Maya Mats - sets spec and metal to 0 on button press for all materials. Also changes materials to opaque. Prevents shiney materials when brought into Maya, materials in Unity unaffected.

/Plans + House creating tools/
Put in order of use on the add-on

Move DXF Plans - Following the house tool documentation, use this button once seperate componants of plans are selected, set outer wall as active, then run this to move to 0,0,0 with correct pivot on all.

Move DXF Plans Stairs - Same as above but for use on section plans.

Rename by Material - Once the house tool is run, it comes through as one mesh, seperate by material (Select all in edit mode, then 'P'), Then run this to rename each mesh, based on what material is applied.

Square topology - WIP (currently needs a few presses to sqaure off topology). Select outer brick or flooring, use this button to square the topology.

UV Bricks - Once meshes are seperate, click brick meshes and use this to UV to correct scale, still requires manual adjustments at house corners and windows/doors.


///How to install Blender addons! ///

Load up Blender, go to Edit > Preferences > Add-ons and then click Install in the top left of the window. 
Locate the .py file on your PC and confirm. Ensure the check box is ticked on the add-on window.


///Why these add ons? ///

B3D Suffix Remove - Blender adds .001, .002, etc.. to meshes with the same name. Maya is able to have the same name for meshes as long as they are under different parents.
Workflows that use meshes with the same name would not work with a default Blender export as the numbers are added.
On top of this, Maya does not recognise '.' and replaces it with 'FBXASC046'. This add-on removes anything named FBX and past that.

Suffix Add - I created this as I wasn't aware of a way to add suffix to mesh names in Maya and only found a prefix add.
I recently found out if you use a '$' followed by the suffix in searc hand replace names, it then adds a suffix.
I still find using my tool in a custom shelf easier and more straight forward.


///How to use ///

Once the scripts/buttons are on your shelf, select any amount of meshes in the heirachy then press the button on the shelf you wish to use.

!!known bug!! 
if you select from top to bottom and use the b3d suffix remover, it can error, selecting the items from bottom to top instead
in the hierachy does not create this issue, I will be looking into this soon.


///How to install Maya scripts! ///
This is the way I am aware of, let me know if there is an easier way! Go to the script editor in the bottom right of the screen, paste in the 
code into the Python tab (MEL if it is that language but mine are Python). You can then use the button in the top left called save to shelf (4th button from the left), ensure you are on the tab you want it in on the shelf.



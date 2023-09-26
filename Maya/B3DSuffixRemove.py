import maya.cmds as mc

sel=mc.ls(selection=True)

# Take each name and remove anything after 'FBX', useful for removing .001, .002, etc from Blender meshes

for each in sel:
    newname=each.split('FBX')
    mc.rename(newname[0]+'')
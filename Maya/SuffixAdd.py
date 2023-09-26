import maya.cmds as cmds

# Open dialogue box and get the suffix
suffix = cmds.promptDialog(
    title="Suffix",
    message="Enter the suffix to add:",
    button=["OK", "Cancel"],
    defaultButton="OK",
    cancelButton="Cancel",
    dismissString="Cancel"
)

# if not
if suffix == "OK":
    suffix = cmds.promptDialog(query=True, text=True)
else:
    cmds.error("Suffix renaming canceled by user.")

selection = cmds.ls(selection=True)

# Loop through each selected object and add the suffix to its name
for obj in selection:
    old_name = obj
    new_name = old_name + suffix
    cmds.rename(old_name, new_name)
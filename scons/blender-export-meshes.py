# actor-export.py
#
# Purpose:
#   Exports an actor to an .fbx file. When working on complex characters,
#   a .blend file will often contain helpers, backups and other things that
#   should not be exported to .fbx. Furthermore, objects may be on different
#   layers that are not all active (eg. different sets of clothing).
#
#   So to get a clean export of only the desired meshes, each time,
#   all layers will have to be set active, the relevant meshes need to be
#   selected and the exporter needs to be invoked.
#
#   This script automates that process.
#
# Usage:
#   Invoke Blender like this:
#
#   blender master.blend --python actor-export.py -- \
#           target.fbx wildcard1* wildcard2*
#
#   - The first argument (master.blend) is the .blend file containing
#     your character to be exported to .fbx
#
#   - The second argument (--python actor-export.py) runs this script
#
#   - The third argument (--) is a separator behind which the script
#     arguments begin. You can add other Blender arguments before this.
#
#   - The fourth argument (target.fbx) is the output file into which
#     the character meshes will be exported
#
#   - The fifth argument and further (wildcard1*, wildcard2*) are masks
#     against which the meshes in the scene are checked. Any meshes
#     matching one or more of the masks will be exported to the .fbx file.
#
# Conventions:
#   If you have multiple Armatures in your .blend file (very common if you
#   use Rigify and kept the metarig), turn off interaction on them to make
#   this script ignore them. Interaction can be turned off by disabling the
#   little mouse cursor-like symbol in the outliner.
#
import bpy
import sys
import fnmatch
import os

def make_all_layers_visible():
    """
    Makes all layers in the scene visible
    """
    for i in range(len(bpy.context.scene.layers)):
        bpy.context.scene.layers[i] = True

def clear_selection():
    """
    Unselects all selected objects in the scene
    """
    for ob in bpy.data.objects:
        ob.select = False

def select_meshes_matching_masks(masks):
    """
    Selects all meshes matching the specified masks (with wildcards)
    """
    for ob in bpy.data.objects:
        if (ob.type == 'MESH') or (ob.type == "ARMATURE"):
            if ob.hide_select == False:
                matches = [mask for mask in masks if fnmatch.fnmatch(ob.name, mask)]
                if len(matches) > 0:
                    ob.select = True
                    print("Mesh selected for exporting: " + ob.name)

# ----------------------------------------------------------------------

print("actor-export.py running...")

cwd = os.getcwd()
print("base path: " + cwd)

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

# Target path for the .fbx we're going to export
outpath = argv[0]
print("output path: " + outpath)

# Meshes that should be exported
exportmasks = argv[1:]
print("export mask count: " + str(len(exportmasks)))

make_all_layers_visible() # meshes might be on different layers
clear_selection() # deselect everything
select_meshes_matching_masks(exportmasks)

#bpy.context.scene.frame_start = 0
#bpy.context.scene.frame_end = 0

# Figure out which export format the user wants to use
filename, file_extension = os.path.splitext(outpath)
file_extension = file_extension.lower()

# Export the scene
if file_extension == ".fbx":
    bpy.ops.export_scene.fbx(
        filepath=outpath,
        check_existing=False,
        axis_forward='-Z',
        axis_up='Y',
        version='BIN7400',
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=False,
        bake_space_transform=False,
        object_types={'ARMATURE', 'EMPTY', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='EDGE',
        use_mesh_edges=False,
        #use_tspace=True,
        use_custom_props=False,
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        use_armature_deform_only=True,
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=True,
        bake_anim_force_startend_keying=True,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0,
        use_anim=True,
        use_anim_action_all=True,
        use_default_take=False,
        use_anim_optimize=False,
        path_mode='AUTO',
        embed_textures=False,
        batch_mode='OFF',
        use_metadata=True
    )
elif file_extension == ".dae":
    bpy.ops.export_scene.dae(
        filepath=outpath,
        check_existing=False,
        use_export_selected=True,
        object_types={'ARMATURE', 'EMPTY', 'MESH'},
        use_mesh_modifiers=True,
        use_exclude_ctrl_bones=True,
        use_anim=True,
        use_anim_action_all=True,
        use_metadata=True
    )
else:
    die("Only FBX and Collada (.dae) are supported at this time")

# Quit. We do not want to risk keeping the window open,
# which might end up making the user save our patchwork file
# 
quit()

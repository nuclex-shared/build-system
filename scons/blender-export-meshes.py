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
#   blender master.blend --enable-autoexec --python actor-export.py -- \
#           target.fbx wildcard1* wildcard2*
#
#   - The first argument (master.blend) is the .blend file containing
#     your character to be exported to .fbx
#
#   - The second argument enables execution of pyhon script embedded in
#     Blender scenes (some addons, like Rigify, need this)
#
#   - The third argument (--python actor-export.py) runs this script
#
#   - The fourth argument (--) is a separator behind which the script
#     arguments begin. You can add other Blender arguments before this.
#
#   - The fifth argument (target.fbx) is the output file into which
#     the character meshes will be exported
#
#   - The sixth argument and further (wildcard1*, wildcard2*) are masks
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

# ----------------------------------------------------------------------------------------------- #

def _main():

    print('Enabling required add-ons...')
    _enable_required_plugins()


    cwd = os.getcwd()
    print("Base path: " + cwd)

    argv = sys.argv
    argv = argv[argv.index("--") + 1:]  # get all args after "--"

    # Target path for the .fbx we're going to export
    outpath = argv[0]
    print("Output path: " + outpath)

    # Meshes that should be exported
    export_masks = argv[1:]

    _make_all_layers_visible() # meshes might be on different layers
    meshes_to_export = _get_meshes_matching_masks(export_masks)

    print('Selected meshes:')
    for mesh in meshes_to_export:
        print('\t' + mesh.name)

    if len(meshes_to_export) == 0:
        print('\tWARNING: No meshes matching any of the specified names/wildcards')

    _clear_selection() # clear the saved selection
    _select_meshes(meshes_to_export)

    # Apply all modifiers (the Collada exporter has such an option, but it's broken)
    print('Applying modifiers:')
    for mesh in meshes_to_export:
        print('\t' + mesh.name)
        _apply_all_modifiers_except_armature(mesh);

    # Figure out which export format the user wants to use
    filename, file_extension = os.path.splitext(outpath)
    file_extension = file_extension.lower()

    # Export the scene
    if file_extension == ".fbx":
        _export_scene_to_fbx(outpath)
    elif file_extension == ".dae":
        _export_scene_to_collada(outpath)
    else:
        die("Only FBX and Collada (.dae) are supported at this time")

# ----------------------------------------------------------------------------------------------- #

def _enable_required_plugins(require_collada = True):
    """Enables the plugins required to export scenes

    @param  require_collada  Whether the "Better Collada" exporter should be enabled"""

    bpy.ops.wm.addon_enable(module='rigify') # Or are Rigify rigs self-contained after generate?
    bpy.ops.wm.addon_enable(module='io_scene_fbx')

    # The collada exporter should be built-in, but we use the "Better Collada" exporter
    if require_collada:
        bpy.ops.wm.addon_enable(module='io_scene_dae') # Better Collada

# ----------------------------------------------------------------------------------------------- #

def _make_all_layers_visible():
    """Makes all layers in the scene visible"""

    for i in range(len(bpy.context.scene.layers)):
        bpy.context.scene.layers[i] = True

# ----------------------------------------------------------------------------------------------- #

def _clear_selection():
    """Deselects all selected objects in the scene"""

    for ob in bpy.data.objects:
        ob.select = False

# ----------------------------------------------------------------------------------------------- #

def _apply_all_modifiers_except_armature(mesh):
    """Applies all modifiers of a mesh except for the Armature modifier

    @param  mesh  Mesh object on which all enabled modifiers will be applied"""

    bpy.context.scene.objects.active = mesh

    target_obj = bpy.context.active_object
    tool_objs = [o for o in bpy.context.selected_objects if o != target_obj]

    for modifier in target_obj.modifiers:
        if not ('armature' in modifier.name.lower()):
            print('\t\t' + modifier.name)
            bpy.ops.object.modifier_apply(modifier=modifier.name)

# ----------------------------------------------------------------------------------------------- #

def _get_meshes_matching_masks(masks):
    """Finds all meshes matching the specified masks (with wildcards)

    @param  masks  Masks which the names of the meshes must match
    @returns A list of all meshes that match the specified masks"""

    meshes = []

    for ob in bpy.data.objects:
        if (ob.type == 'MESH') or (ob.type == 'ARMATURE'):
            if ob.hide_select == False:
                matches = [mask for mask in masks if fnmatch.fnmatch(ob.name, mask)]
                if len(matches) > 0:
                    meshes.append(ob)

    return meshes

# ----------------------------------------------------------------------------------------------- #

def _select_meshes(meshes):
    """Marks the specified meshes as selected

    @param  meshes  Meshes that will be marked as selected"""

    for mesh in meshes:
        mesh.select = True

# ----------------------------------------------------------------------------------------------- #

def _export_scene_to_fbx(outpath, selected_objects_only = True):
    """Exports the current scene to a FBX file

    @param  outpath                Path under which the exported FBX file will be saved
    @param  selected_objects_only  Whether only selected objects will be exported"""

    bpy.ops.export_scene.fbx(
        filepath=outpath,
        check_existing=False,
        axis_forward='-Z',
        axis_up='Y',
        version='BIN7400',
        use_selection=selected_objects_only,
        global_scale=1.0,
        apply_unit_scale=False,
        bake_space_transform=False,
        object_types={'ARMATURE', 'EMPTY', 'MESH'},
        use_mesh_modifiers=False, # We already hand-applied them
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

# ----------------------------------------------------------------------------------------------- #

def _export_scene_to_collada(outpath, selected_objects_only = True):
    """Exports the current scene to a Collada file

    @param  outpath                Path under which the exported Collada file will be saved
    @param  selected_objects_only  Whether only selected objects will be exported"""

    bpy.ops.export_scene.dae(
        filepath=outpath,
        check_existing=False,
        use_export_selected=selected_objects_only,
        object_types={'ARMATURE', 'EMPTY', 'MESH'},
        use_mesh_modifiers=False, # we hand-apply because Better Collada is buggy here
        use_exclude_ctrl_bones=True,
        use_anim=True,
        use_anim_action_all=True,
        use_metadata=True
    )

# ----------------------------------------------------------------------------------------------- #

print(str())
print("actor-export.py running...")
print("===============================================================================")

_main()

print("===============================================================================")
print(str())

# Quit. We do not want to risk keeping the window open,
# which might end up making the user save our patchwork file
#
quit()

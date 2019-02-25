#!/usr/bin/env python

import os
import shutil

# ----------------------------------------------------------------------------------------------- #

# Path to the Godot executable that will be used for the export
_godot_executable_path = '/opt/godot-3.1/bin/godot_headless.x11.opt.tools.64'

# ----------------------------------------------------------------------------------------------- #

def _enumerate_subdirectories(root_directory, ignored_directories=[]):
    """Enumerates the subdirectories inside a directory

    @param  root_directory       Directory whose direct subdirectories will be enumerated
    @param  ignored_directories  Directories to ignore if encountered"""

    directories = []

    for entry in os.listdir(root_directory):
        if os.path.isdir(entry):
            if not any(entry in s for s in ignored_directories):
                directories.append(entry)

    return directories

# ----------------------------------------------------------------------------------------------- #

def setup_variant_dirs(
    scons_environment, project_directory, intermediate_directory, ignored_directories
):
    """Sets up SCons variant directories for all direct subdirectories in a path

    @param  scons_environment       The SCons environment in which variant dirs will be set up
    @param  project_directory       Directory that contains the Godot project and all assets
    @param  intermediate_directory  Directory into which intermediate files will be placed
    @param  ignored_directories     Directories that will be ignored if encountered"""

    # Set up VariantDirs for all direct subdirectories
    subdirectories = _enumerate_subdirectories(project_directory, ignored_directories)
    for subdirectory in subdirectories:
        build_directory = os.path.join(intermediate_directory, subdirectory)
        scons_environment.VariantDir(build_directory, subdirectory, duplicate = 0)
        #print "VariantDir " + subdirectory + " -> " + build_directory

# ----------------------------------------------------------------------------------------------- #

def enumerate_project_assets(project_directory, ignored_directories, variant_directory = ""):
    """Forms a list of all assets in a project directory

    @param  project_directory    Directory containing the Godot project and its assets
    @param  ignored_directories  Directories that will be ignored if encountered
    @param  variant_directory    Variant directory to which source paths will be rewritten"""

    sources = []

    subdirectories = _enumerate_subdirectories(project_directory, ignored_directories)

    # Form a list of all files in the input directories recursively.
    # This is so that SCons triggers a rebuild if any of these change
    for subdirectory in subdirectories:
        for root, directory_names, file_names in os.walk(subdirectory):
            for file_name in file_names:
                if variant_directory:
                    sources.append(os.path.join(variant_directory, os.path.join(root, file_name)))
                else:
                    sources.append(os.path.join(root, file_name))

    return sources

# ----------------------------------------------------------------------------------------------- #

def enumerate_gdnative_sources(project_directory, ignored_directories, variant_directory = ""):
    """Forms a list of all C/C++ source code files in a project directory

    @param  project_directory    Directory containing the Godot project and its assets
    @param  ignored_directories  Directories that will be ignored if encountered
    @param  variant_directory    Variant directory to which source paths will be rewritten"""

    sources = []
    source_file_extensions = [
        '.c',
        '.C',
        '.cpp',
        '.cc',
        #'.h',
        #'.H',
        #'.hpp',
        #'.hh'
    ]

    subdirectories = _enumerate_subdirectories(project_directory, ignored_directories)

    # Form a list of all files in the input directories recursively.
    # This is so that SCons triggers a rebuild if any of these change
    for subdirectory in subdirectories:
        for root, directory_names, file_names in os.walk(subdirectory):
            for file_name in file_names:
                file_title, file_extension = os.path.splitext(file_name)
                if any(file_extension in s for s in source_file_extensions):
                    if variant_directory:
                        sources.append(os.path.join(variant_directory, os.path.join(root, file_name)))
                    else:
                        sources.append(os.path.join(root, file_name))

    return sources

# ----------------------------------------------------------------------------------------------- #

def _export_godot_project(target, source, env):
    """Exports a single godot project

    @param  target  Path of the game's executable
    @param  source  Source files from which the game will be built
    @param  env     SCons build environment in which the build will take place"""

    export_path = str(target[0])
    print("Exporting Godot project to " + export_path)

    # If the target file already exists, delete it
    if os.path.isfile(export_path):
        os.remove(export_path)

    # Which export profile (from export_presets.cfg) we'll build
    export_profile = env['EXPORT_PROFILE']
    print("Using export profile " + export_profile)

    # Here's the command line with which we will call godot
    command = (
        _godot_executable_path +
        " --verbose" +
        " --path \"./\"" +
        " --export \"" + export_profile + "\"" +
        " \"" + export_path + "\""
    )
    env.Execute(command)

# ----------------------------------------------------------------------------------------------- #

def register_builder(env):
    """Registers the godot builders

    @param  env  Environment the godot builders will be registered in"""

    godot_builder = env.Builder(
        action=_export_godot_project,
        suffix='.x86_64'
    )
    env.Append(BUILDERS={"ExportGodotProject" : godot_builder})

# ----------------------------------------------------------------------------------------------- #

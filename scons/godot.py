#!/usr/bin/env python

import os
import shutil
import platform

# ----------------------------------------------------------------------------------------------- #

# Official download server for the Godot binaries
_download_server = 'https://downloads.tuxfamily.org'

# URLs of the headless server executables
_godot_headless_urls = {
    '3.0': _download_server + '/godotengine/3.0.6/Godot_v3.0.6-stable_linux_headless.64.zip',
    '3.1': _download_server + '/godotengine/3.1/Godot_v3.1-stable_linux_headless.64.zip'
}

# URLs of the export templates
_godot_template_urls = {
    '3.0': _download_server + '/godotengine/3.0.6/Godot_v3.0.6-stable_export_templates.tpz',
    '3.1': _download_server + '/godotengine/3.1/Godot_v3.1-stable_export_templates.tpz'
}

# Name of the Godot executables when using an official build or git build
_godot_executables = {
    '3.0': [
        'Godot_v3.0.6-stable_linux_headless.64',
        'Godot_v3.0.6-stable_x11.64',
        'Godot_v3.0.6-stable_win64.exe'
    ],
    '3.1': [
        'Godot_v3.1-stable_linux_headless.64',
        'Godot_v3.1-stable_x11.64',
        'Godot_v3.1-stable_win64.exe'
    ],
    'git': [
        'godot_headless.x11.opt.tools.64'
    ]
}

# Default version of Godot we will use (good idea? liability for future compatbility?)
_default_godot_version = '3.1'

# ----------------------------------------------------------------------------------------------- #

def register_extension_methods(environment):
    """Registers extensions methods for Godot builds into a SCons environment

    @param  environment  Environment the extension methods will be registered to"""

    environment.AddMethod(_export_project, "export_project")

# ----------------------------------------------------------------------------------------------- #

def _get_all_assets(root_directory):
    """Recursively fetches all assets that might be processed by Godot. Honors
    .gdignore files.

    @param  root_directory  Directory below which all assets will be found
    @return A list of all asset files"""

    assets = []

    for entry in os.listdir(root_directory):
        path = os.path.join(root_directory, entry)
        if os.path.isdir(path):
            _recursively_collect_assets(assets, path)

    #scripts.reverse()

    return assets

# ----------------------------------------------------------------------------------------------- #

def _recursively_collect_assets(assets, directory):
    """Recursively searches for Godot asserts and adds them to the provided list

    @param  assets     List to which any discovered assets will be added
    @param  directory  Directory from which on the method will recursively search"""

    asset_file_extensions = [
        '.tscn',
        '.escn',
        '.scn',
        '.tres',
        '.res',
        '.dae',
        '.obj',
        '.wav',
        '.ogg',
        '.png',
        '.tga',
        '.tif',
        '.jpg',
        '.ttf',
        '.font',
        '.import'
    ]

    # If this directory contains a .gdignore file, don't process it
    gd_ignore_file = os.path.join(directory, ".gdignore")
    if os.path.isfile(gd_ignore_file):
        return

    for entry in os.listdir(directory):
        path = os.path.join(directory, entry)
        if os.path.isdir(path):
            _recursively_collect_build_scripts(scripts, path)
        elif os.path.isfile(path):
            file_title, file_extension = os.path.splitext(file_name)
            if file_extension and any(file_extension in s for s in asset_file_extensions):
                assets.append(path)

# ----------------------------------------------------------------------------------------------- #

def _find_godot_executable(godot_version):
    """Locates a suitable Godot executable on the current system.

    @param  godot_version  Version number of Godot that is requested (i.e. '3.0' or '3.1')
    @returns The absolute path of a Godot executable."""

    candidate_directories = []

    # Build a list of directories in which Godot might be installed on
    # the current platform
    if platform.system() == 'Windows':
        base_directory = os.environ['ProgramFiles']
        for entry in os.listdir(base_directory):
            if 'godot' in entry.lower():
                candidate_directories.append(os.path.join(base_directory, entry))

        base_directory = os.environ['ProgramFiles(x86)']
        for entry in os.listdir(base_directory):
            if 'godot' in entry.lower():
                candidate_directories.append(os.path.join(base_directory, entry))
    else:
        for entry in os.listdir('/opt'):
            if 'godot' in entry.lower():
                candidate_directories.append(os.path.join('/opt', entry))

    # Now check all potential install locations for the Godot executable
    # in the version wanted by the user
    for directory in candidate_directories:

        # Check within the 'bin' directory if one exists
        bin_directory = os.path.join(directory, 'bin')
        if os.path.isdir(bin_directory):
            for executable_name in _godot_executables[godot_version]:
                candidate_path = os.path.join(bin_directory, executable_name)
                if os.path.isfile(candidate_path):
                    return candidate_path

        # Check the candidate directory itself
        for executable_name in _godot_executables[godot_version]:
            candidate_path = os.path.join(directory, executable_name)
            if os.path.isfile(candidate_path):
                return candidate_path

    return None

# ----------------------------------------------------------------------------------------------- #

def _export_project(environment):
    if 'GODOT_VERSION' in environment:
        godot_version = environment['GODOT_VERSION']
    else:
        godot_version = _default_godot_version

    godot_executable_path = _find_godot_executable(godot_version)

    print(godot_executable_path)

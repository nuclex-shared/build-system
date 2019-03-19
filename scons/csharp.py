#!/usr/bin/env python

import os
import shutil
import platform

# ----------------------------------------------------------------------------------------------- #

# Paths in which the 32 bit version of MSBuild can be found on Windows systems
_windows_x86_msbuild_paths = {
    '2.0': [
        '%WinDir%\Microsoft.NET\Framework\v2.0.50727\MSBuild.exe'
    ],
    '3.5': [
        '%WinDir%\Microsoft.NET\Framework\v3.5\MSBuild.exe'
    ],
    '4.0': [
        '%WinDir%\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe'
    ],
    'latest': [
        '%ProgramFiles(x86)%\Microsoft Visual Studio\2017\Community\MSBuild\15.0\Bin\MSBuild.exe',
        '%ProgramFiles(x86)%\Microsoft Visual Studio\2017\Professional\MSBuild\15.0\Bin\MSBuild.exe',
        '%ProgramFiles(x86)%\Microsoft Visual Studio\2017\Enterprise\MSBuild\15.0\Bin\MSBuild.exe',
        'C:\Program Files (x86)\MSBuild\14.0\Bin\MSBuild.exe'
    ]
}

# Paths in which the 64 bit version of MSBuild can be found on Windows systems
_windows_amd64_msbuild_paths = {
    '2.0': [
        '%WinDir%\Microsoft.NET\Framework64\v2.0.50727\MSBuild.exe'
    ],
    '3.5': [
        '%WinDir%\Microsoft.NET\Framework64\v3.5\MSBuild.exe'
    ],
    '4.0': [
        '%WinDir%\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe'
    ],
    'latest': [
        '%ProgramFiles(x86)%\Microsoft Visual Studio\2017\Community\MSBuild\15.0\Bin\amd64\MSBuild.exe',
        '%ProgramFiles(x86)%\Microsoft Visual Studio\2017\Professional\MSBuild\15.0\Bin\amd64\MSBuild.exe',
        '%ProgramFiles(x86)%\Microsoft Visual Studio\2017\Enterprise\MSBuild\15.0\Bin\amd64\MSBuild.exe',
        'C:\Program Files (x86)\MSBuild\14.0\Bin\amd64\MSBuild.exe'
    ]
}

# Possible paths the Visual Studio environment setup batch file can be found in
_windows_visual_studio_batch_paths = [
  '%ProgramFiles(x86)%\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvars32.bat'
]

# Default version of MSBuild we will use
_default_msbuild_version = 'latest'

# ----------------------------------------------------------------------------------------------- #

def register_extension_methods(environment):
    """Registers extensions methods for Godot builds into a SCons environment

    @param  environment  Environment the extension methods will be registered to"""

    #environment.AddMethod(_compile_cli_application, "CliProgram")
    #environment.AddMethod(_compile_cli_library, "CliLibrary")
    pass

# ----------------------------------------------------------------------------------------------- #

def enumerate_sources(source_directory, variant_directory = None):
    """Forms a list of all C# source code files in a source directory

    @param  source_directory     Directory containing the C/C++ source code files
    @param  variant_directory    Variant directory to which source paths will be rewritten"""

    source_file_extensions = [
        '.cs'
    ]

    sources = []

    # Form a list of all files in the input directories recursively.
    for root, directory_names, file_names in os.walk(source_directory):
        for file_name in file_names:
            file_title, file_extension = os.path.splitext(file_name)
            if any(file_extension in s for s in source_file_extensions):
                if variant_directory is None:
                    sources.append(os.path.join(root, file_name))
                else:
                    sources.append(os.path.join(variant_directory, os.path.join(root, file_name)))

    return sources

# ----------------------------------------------------------------------------------------------- #

def _find_msbuild_executable(msbuild_version):
    """Locates a suitable MSBuild executable on the current system.

    @param  msbuild_version  Version number of MSBuild that is requested (i.e. 'latest')
    @returns The absolute path of a MSBuild executable."""

    if platform.system() == 'Windows':

        # If someone uses this script in the far future and the Visual Studio version
        # contained in the expected paths is installed in addition to the newest one,
        # this might result in finding the older Visual Studio's MSBuild executable.
        for candidate in _windows_amd64_msbuild_paths[msbuild_version]:
            if os.path.isfile(candidate):
                return file

        # Only do a scan if we're asked for the latest version as we can't guarantee
        if msbuild_version == 'latest':
            msbuild_directories = _find_msbuild_directories(msbuild_version)
            for msbuild_directory in msbuild_directories:
                for version in os.listdir(msbuild_directory):
                    version_directory = os.path.join(msbuild_directory, version)
                    if os.path.isdir(version_directory):

                        executable_path = os.path.join(version_directory, 'Bin\amd64\MSBuild.exe')
                        if os.path.isfile(executable_path):
                            return executable_path

                        executable_path = os.path.join(version_directory, 'Bin\MSBuild.exe')
                        if os.path.isfile(executable_path):
                            return executable_path

                        executable_path = os.path.join(version_directory, 'amd64\MSBuild.exe')
                        if os.path.isfile(executable_path):
                            return executable_path

                        executable_path = os.path.join(version_directory, 'MSBuild.exe')
                        if os.path.isfile(executable_path):
                            return executable_path

    else:

        if os.path.isfile('/usr/bin/msbuild'):
            return '/usr/bin/msbuild'
        elif os.path.isfile('/usr/bin/xbuild'):
            return '/usr/bin/xbuild'

    return None

# ----------------------------------------------------------------------------------------------- #

def _find_msbuild_directories(msbuild_version):
    """Looks for MSBuild directories on the system

    @returns All MSBuild directories found on the system"""

    msbuild_directories = []

    # Look for directories containing 'Visual Studio' as candidates for
    # to use as the Visual Studio install directory
    visual_studio_directories = []

    # Visual Studio is still an x86 application, so search only here
    program_files_directory = os.environ['ProgramFiles(x86)']
    for directory in os.listdir(program_files_directory):
        if 'visual studio' in directory.lower():
            visual_studio_directories.append(os.path.join(program_files_directory, directory))
        if directory.lower() == 'msbuild':
            msbuild_directories.append(os.path.join(program_files_directory, directory))

    # Up until Visual Studio 2015, MSBuild was in its own directory
    program_files_directory = os.environ['ProgramFiles']
    for directory in os.listdir(program_files_directory):
        if directory.lower() == 'msbuild':
            msbuild_directories.append(os.path.join(program_files_directory, directory))

    # Look for a directory called 'MSBuild' exactly 3 levels deep
    # This looks a bit ugly, but we try to earl-out wherever possible and
    # a Visual Studio directory only has few files in these intermediate levels
    for directory in visual_studio_directories:
        for version in os.listdir(directory):
            version_directory = os.path.join(directory, version)
            if os.path.isdir(version_directory):
                if directory.lower() == 'msbuild':
                    msbuild_directories.add(version_directory)
                else:
                    for edition in os.listdir(version_directory):
                        edition_directory = os.path.join(version_directory, edition)
                        if os.path.isdir(edition_directory):
                            if edition.lower() == 'msbuild':
                                msbuild_direcories.add(edition_directory)
                            else:
                                for msbuild in os.listdir(edition_directory):
                                    msbuild_directory = os.path.join(edition_directory, msbuild)
                                    if os.path.isdir(msbuild_directory):
                                        if msbuild.lower() == 'msbuild':
                                            msbuild_directories.append(msbuild_directory)

    return msbuild_directories

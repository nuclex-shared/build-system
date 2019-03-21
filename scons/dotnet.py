#!/usr/bin/env python

import os
import shutil
import platform
import xml.etree.ElementTree as ET

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
_default_msbuild_version = 'system'

# ----------------------------------------------------------------------------------------------- #

def register_extension_methods(environment):
    """Registers extensions methods for Godot builds into a SCons environment

    @param  environment  Environment the extension methods will be registered to"""

    #environment.AddMethod(_compile_cli_application, "CliProgram")
    #environment.AddMethod(_compile_cli_library, "CliLibrary")
    environment.AddMethod(_call_msbuild, "MSBuild")

# ----------------------------------------------------------------------------------------------- #

def enumerate_sources(source_directory, variant_directory = None):
    """Forms a list of all C# source code files in a source directory

    @param  source_directory     Directory containing the C/C++ source code files
    @param  variant_directory    Variant directory to which source paths will be rewritten"""

    source_file_extensions = [
        '.cs',
        '.vb'
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

def _find_msbuild_executable(environment, msbuild_version):
    """Locates a suitable MSBuild executable on the current system.

    @param  environment      Environment that is used to look for MSBuild
    @param  msbuild_version  Version number of MSBuild that is requested (i.e. 'latest')
    @returns The absolute path of a MSBuild executable."""

    # If we're asked to find *any* MSBuild version, let's start by seeing if it is already
    # in the path. This is the case for Linux systems and may be the case for Windows
    # systems if the user has manually added the Visual Studio environment variables to
    # his standard environment setup (which is not unusual for CI build slaves)
    if (msbuild_version == 'latest') or (msbuild_version == 'system'):

        # Prefer MSBuild (as of 2018, Mono xbuild is being replaced by Open Sourced msbuild)
        msbuild = environment.WhereIs('msbuild')
        if msbuild:
            return msbuild

        # But if we can't get MSBuild, fall back to xbuild (only available on Mono systems)
        xbuild = environment.WhereIs('xbuild')
        if xbuild:
            return xbuild

    if platform.system() == 'Windows':

        # Only do a scan if we're asked for the latest version as we can't guarantee
        # what we'll find and figuring out which version we have is a problem of its own
        if (msbuild_version == 'latest') or (msbuild_version == 'system'):
            msbuild_directories = _find_msbuild_directories()
            for msbuild_directory in msbuild_directories:
                for version in os.listdir(msbuild_directory):
                    version_directory = os.path.join(msbuild_directory, version)
                    if os.path.isdir(version_directory):

                        executable_path = os.path.join(version_directory, 'Bin\amd64\MSBuild.exe')
                        if os.path.isfile(executable_path):
                            return executable_path

                        executable_path = os.path.join(version_directory, 'amd64\MSBuild.exe')
                        if os.path.isfile(executable_path):
                            return executable_path

                        executable_path = os.path.join(version_directory, 'Bin\MSBuild.exe')
                        if os.path.isfile(executable_path):
                            return executable_path

                        executable_path = os.path.join(version_directory, 'MSBuild.exe')
                        if os.path.isfile(executable_path):
                            return executable_path

        # If a specific msbuild version was requested, look for it in its known path
        for candidate in _windows_amd64_msbuild_paths[msbuild_version]:
            if os.path.isfile(candidate):
                return file

    else:

        # Linux systems where msbuild is not in the executable paths (we checked them above).
        # Try msbuild and xbuild in their standard locations, otherwise give up.
        # (we could look for Mono in /opt if we're hardcore...)
        if os.path.isfile('/usr/bin/msbuild'):
            return '/usr/bin/msbuild'
        elif os.path.isfile('/usr/bin/xbuild'):
            return '/usr/bin/xbuild'

    return None

# ----------------------------------------------------------------------------------------------- #

def _find_msbuild_directories():
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

# ----------------------------------------------------------------------------------------------- #

def _call_msbuild(environment, msbuild_project_path, sources, output_path):
    """Invokes MSBuild

    @param  environment           Environment on which MSBuild will be invoked
    @param  msbuild_project_path  Path to the MSBuild project (i.e. *.csproj, *.vcxproj)
    @param  sources               Input files (not used, but for change detection)
    @param  output_path           Path of the build output
    """

    # TODO: Write a .proj 'scanner' and get rid of the 'sources' parameter
    # TODO: 

    msbuild_version = _default_msbuild_version
    if 'MSBUILD_VERSION' in environment:
        msbuild_version = environment['MSBUILD_VERSION']

    msbuild_executable = _find_msbuild_executable(environment, msbuild_version)
    if msbuild_executable is None:
        raise FileNotFoundError('Could not find msbuild executable')

    # Set MSBuild property "OutputPath" to bin
    # Set MSBuild prop
    #return environment.Command(
    return None

# ----------------------------------------------------------------------------------------------- #

def _scan_msbuild_project(node, environment, path):
    """Scans an MSBuild project for other files it is referencing. This is important
    for SCons to detect changes in files that are used within the build.

    @param  node         MSBuild project as a SCons File object
    @param  environment  Environment in which the project is being compiled
    @param  path         Who knows?"""

    sources = []

    xml_namespaces = {
        'msbuild': 'http://schemas.microsoft.com/developer/msbuild/2003'
    }

    contents = node.get_text_contents()
    project_node = ET.fromstring(contents)

    compile_nodes = project_node.findall('./msbuild:ItemGroup/msbuild:Compile', xml_namespaces)
    for compile_node in compile_nodes:
        sources.append(compile_node.attrib.get('Include'))

    print(sources)

    return None

#csccom = "$CSC $CSCFLAGS -out:${TARGET.abspath} $SOURCES"
#csclibcom = "$CSC -t:library $CSCLIBFLAGS $_CSCLIBPATH $_CSCLIBS -out:${TARGET.abspath} $SOURCES"

#!/usr/bin/env python

import os
import shutil
import platform
import subprocess
import re

"""
Helpers for building C/C++ projects with SCons
"""

# ----------------------------------------------------------------------------------------------- #

def enumerate_headers(header_directory, variant_directory = ""):
    """Forms a list of all C/C++ header files in an include directory

    @param  header_directory     Directory containing the headers
    @param  variant_directory    Variant directory to which source paths will be rewritten"""

    source_file_extensions = [
        '.h',
        '.H',
        '.hpp',
        '.hh',
        '.hxx',
        '.inl',
        '.inc'
    ]

    headers = []

    # Form a list of all files in the input directories recursively.
    for root, directory_names, file_names in os.walk(header_directory):
        for file_name in file_names:
            file_title, file_extension = os.path.splitext(file_name)
            if any(file_extension in s for s in source_file_extensions):
                if variant_directory:
                    headers.append(os.path.join(variant_directory, os.path.join(root, file_name)))
                else:
                    headers.append(os.path.join(root, file_name))

    return headers

# ----------------------------------------------------------------------------------------------- #

def enumerate_sources(source_directory, variant_directory = ""):
    """Forms a list of all C/C++ source code files in a source directory

    @param  source_directory     Directory containing the C/C++ source code files
    @param  variant_directory    Variant directory to which source paths will be rewritten"""

    source_file_extensions = [
        '.c',
        '.C',
        '.cpp',
        '.cc',
        '.cxx',
        '.inl',
        '.inc'
    ]

    sources = []

    # Form a list of all files in the input directories recursively.
    for root, directory_names, file_names in os.walk(source_directory):
        for file_name in file_names:
            file_title, file_extension = os.path.splitext(file_name)
            if any(file_extension in s for s in source_file_extensions):
                if variant_directory:
                    sources.append(os.path.join(variant_directory, os.path.join(root, file_name)))
                else:
                    sources.append(os.path.join(root, file_name))

    return sources

# ----------------------------------------------------------------------------------------------- #

def add_include_directory(environment, include_directory):
    """Adds an include directory to a C++ build environment

    @param  environment        Environment the include directory will be added to
    @param  include_directory  Include directory that will be added to the environment"""

    environment.Append(CPPPATH=[include_directory])

# ----------------------------------------------------------------------------------------------- #

def add_library_directory(environment, library_directory):
    """Adds a library directory to a C++ build environment

    @param  environment        Environment the library directory will be added to
    @param  library_directory  Library directory that will be added to the environment"""

    environment.Append(LIBPATH=[library_directory])

# ----------------------------------------------------------------------------------------------- #

def add_library(environment, library_name):
    """Adds a library to a C++ build environment

    @param  environment   Environment the library will be added to
    @param  library_name  Library that will be added to the environment
    @remarks
      The libary name is platform-specific. On Windows systems, the library is usually
      called MyAwesomeThing.lib while on GNU/Linux systems, the convention is
      libMyAwesomeThing.so (the toolchain will automatically try the lib prefix, though)"""

    environment.Append(LIBS=[library_name])

# ----------------------------------------------------------------------------------------------- #

def get_platform_specific_library_name(universal_library_name):
    """Forms the platform-specific library name from a universal library name

    @param  universal_library_name  Universal name of the library that will be converted
    @returns The platform-specific library name
    @remarks
      A universal library name is just the name of the library without extension,
      using dots to separate words - for example My.Awesome.Stuff. Depending on the platform,
      this might get turned into My.Awesome.Stuff.dll or libMyAwesomeStuff.so"""

    if platform.system() == 'Linux':
        return 'lib' + universal_library_name.replace('.', '') + ".so"
    else:
        return universal_library_name + ".dll"

# ----------------------------------------------------------------------------------------------- #

def get_platform_specific_executable_name(universal_executable_name):
    """Forms the platform-specific executable name from a universal executable name

    @param  universal_executable_name  Universal name of the executable that will be converted
    @returns The platform-specific executable name
    @remarks
      A universal executable name is just the name of the executable without extension,
      using dots to separate words - for example My.Awesome.Program. Depending on the platform,
      this might get turned into My.Awesome.Program.exe or MyAwesomeProgram."""

    if platform.system() == 'Linux':
        return universal_executable_name.replace('.', '')
    else:
        return universal_executable_name + ".exe"

# ----------------------------------------------------------------------------------------------- #

def get_platform_library_directory(architecture, build_type):
    """Determines the name of the library directory for the current compiler version
    and output settings (such as platform and whether it's a debug or release build)

    @param  build_type    Type of build, typically either 'debug' or 'release'
                          Microsoft calls this a build configuration
    @param  architecture  CPU architecture the build is targeting, i.e. x86, x64 or arm"""

    if platform.system() == 'Linux':
        gcc_version = _find_gcc_compiler_version()
        if gcc_version is None:
            raise FileNotFoundError('No GCC compiler found')

        return "gcc-" + gcc_version[0] + '-' + architecture + '-' + build_type
    else:
        return 'msvc-14.0-' + architecture + '-' + build_type

# ----------------------------------------------------------------------------------------------- #

def _find_gcc_compiler_version(compiler_executable = 'gcc'):
    """Extracts the version number of a C/C++ compiler (like GCC) as a list of strings.

    @param  compiler_execuable  Executable for the selected compiler (usually just gcc)
    @returns The compiler version number"""

    gcc_process = subprocess.Popen(
        [compiler_executable, '--version'], stdout=subprocess.PIPE
    )
    (stdout, stderr) = gcc_process.communicate()

    match = re.search('[0-9][0-9.]*', stdout)

    # If no match is found the compiler didn't proide the expected output
    # and we have no idea which version it might be
    if match is None:
        return None

    version = match.group().split('.')
    return version

# ----------------------------------------------------------------------------------------------- #

def _find_msvc_compiler_version(compiler_executable = 'cl.exe'):
    pass

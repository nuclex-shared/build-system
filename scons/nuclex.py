#!/usr/bin/env python

import os
import importlib
import platform
import types

from SCons.Environment import Environment
from SCons.Variables import Variables
from SCons.Variables import EnumVariable
from SCons.Variables import PathVariable
from SCons.Variables import BoolVariable
from SCons.Script import ARGUMENTS
from SCons.Script import Dir

# Nuclex SCons libraries
shared = importlib.import_module('shared')
cplusplus = importlib.import_module('cplusplus')
dotnet = importlib.import_module('dotnet')
blender = importlib.import_module('blender')

# Plan:
#   - if TARGET_ARCH is set, use it. For multi-builds,
#     this may result in failure, but that's okay
#   - multi-builds (typical case x86/x64 native + .net anycpu)
#     must control target arch manually anyway.

# ----------------------------------------------------------------------------------------------- #

def create_cplusplus_environment():
    """Creates a new environment with the required variables for building C/C++ projects

    @returns A new scons environment set up for C/C++ builds"""

    environment = Environment(
        variables = _parse_default_command_line_options(),
        SOURCE_DIRECTORY = 'Source',
        HEADER_DIRECTORY = 'Include',
        TESTS_DIRECTORY = 'Tests',
        TESTS_RESULT_FILE = "gtest-results.xml",
        REFERENCES_DIRECTORY = 'References'
    )

    # Extension methods from the C/C== module
    cplusplus.register_extension_methods(environment)

    # Nuclex standard build settings and extensions
    _set_standard_cplusplus_compiler_flags(environment)
    _set_standard_cplusplus_linker_flags(environment)
    _register_cplusplus_extension_methods(environment)

    return environment

# ----------------------------------------------------------------------------------------------- #

def create_dotnet_environment():
    """Creates a new environment with the required variables for building .NET projects

    @returns A new scons environment set up for .NET builds"""

    environment = Environment(
        variables = _parse_default_command_line_options(),
        SOURCE_DIRECTORY = 'Source',
        TESTS_DIRECTORY = 'Tests',
        TESTS_RESULT_FILE = "nunit-results.xml",
        REFERENCES_DIRECTORY = 'References'
    )

    # Register extension methods and additional variables
    dotnet.setup(environment)

    _register_dotnet_extension_methods(environment)

    return environment

# ----------------------------------------------------------------------------------------------- #

def create_blender_environment():
    """Creates a new environment with the required variables for export Blender models

    @returns A new scons environment set up for Blender exports"""

    environment = Environment(
        variables = _parse_default_command_line_options()
    )

    _register_blender_extension_methods(environment)

    return environment

# ----------------------------------------------------------------------------------------------- #

def _parse_default_command_line_options():
    """Parses the command line options controlling various build settings

    @remarks
        This contains variables that work across all builds. Build-specific variables
        are discouraged, but would be irgnored by SCons' Variables class."""

    command_line_variables = Variables(None, ARGUMENTS)

    # Build configuration (also called build type in many SCons examples)
    command_line_variables.Add(
        BoolVariable(
            'DEBUG',
            'Whether to do an unoptimized debug build',
            False
        )
    )

    # Default architecture for the binaries. We follow the Debian practices,
    # which, while clueless and chaotic, are at least widely used.
    default_arch = 'amd64'
    if 'armv7' in platform.uname()[4]:
        default_arch = 'armhf'
    if 'aarch64' in platform.uname()[4]:
        default_arch = 'arm64'

    # CPU architecture to target
    command_line_variables.Add(
        EnumVariable(
            'TARGET_ARCH',
            'CPU architecture the binary will run on',
            default_arch,
            allowed_values=('armhf', 'arm64', 'x86', 'amd64', 'any')
        )
    )

    # Directory for intermediate files
    command_line_variables.Add(
        PathVariable(
            'INTERMEDIATE_DIRECTORY',
            'Directory in which intermediate build files will be stored',
            'obj',
            PathVariable.PathIsDirCreate
        )
    )

    # Directory for intermediate files
    command_line_variables.Add(
        PathVariable(
            'ARTIFACT_DIRECTORY',
            'Directory in which build artifacts (outputs) will be stored',
            'bin',
            PathVariable.PathIsDirCreate
        )
    )

    return command_line_variables

# ----------------------------------------------------------------------------------------------- #

def _register_cplusplus_extension_methods(environment):
    """Registers extension methods for C/C++ builds into a SCons environment

    @param  environment  Environment the extension methods will be registered to"""

    environment.AddMethod(_add_cplusplus_package, "add_package")
    environment.AddMethod(_build_cplusplus_library, "build_library")
    environment.AddMethod(_build_cplusplus_library_with_tests, "build_library_with_tests")
    environment.AddMethod(_build_cplusplus_executable, "build_executable")
    environment.AddMethod(_run_cplusplus_unit_tests, "run_unit_tests")

# ----------------------------------------------------------------------------------------------- #

def _register_dotnet_extension_methods(environment):
    """Registers extension methods for .NET builds into a SCons environment

    @param  environment  Environment the extension methods will be registered to"""

    environment.AddMethod(_build_msbuild_project, "build_project")
    environment.AddMethod(_build_msbuild_project_with_tests, "build_project_with_tests")

# ----------------------------------------------------------------------------------------------- #

def _register_blender_extension_methods(environment):
    """Registers extension methods for Blender exports into a SCons environment

    @param  environment  Environment the extension methods will be registered to"""

    blender.register_extension_methods(environment)

# ----------------------------------------------------------------------------------------------- #

def _is_debug_build(environment):
    """Checks whether a debug build has been requested

    @param  environment  Environment whose settings will be checked for a debug build
    @returns True if a debug build has been requested, otherwise False"""

    if 'DEBUG' in environment:
        return environment['DEBUG']
    else:
        return False

# ----------------------------------------------------------------------------------------------- #

def _set_standard_cplusplus_compiler_flags(environment):
    """Sets up standard flags for the compiler

    @param  environment  Environment in which the C++ compiler flags wlll be set."""

    if platform.system() == 'Windows':
        environment.Append(CXXFLAGS='/EHsc') # Only C++ exceptions, no Microsoft exceptions
        environment.Append(CXXFLAGS='/GF') # String pooling in debug and release
        #environment.Append(CXXFLAGS='/Gv') # Vectorcall for speed
        environment.Append(CXXFLAGS='/utf-8') # Source code and outputs are UTF-8 encoded
        environment.Append(CXXFLAGS='/std:c++14') # Use a widely supported but current C++
        environment.Append(CXXFLAGS='/W4') # Show all warnings
        environment.Append(CXXFLAGS='/GS-') # No buffer security checks (we make games!)
        environment.Append(CXXFLAGS='/GR') # Generate RTTI for dynamic_cast and type_info
        environment.Append(CXXFLAGS='/FS') # Support shared writing to the PDB file

        environment.Append(CFLAGS='/GF') # String pooling in debug and release
        #environment.Append(CFLAGS='/Gv') # Vectorcall for speed
        environment.Append(CFLAGS='/utf-8') # Source code and outputs are UTF-8 encoded
        environment.Append(CFLAGS='/W4') # Show all warnings
        environment.Append(CFLAGS='/GS-') # No buffer security checks (we make games!)
        environment.Append(CFLAGS='/FS') # Support shared writing to the PDB file

        if _is_debug_build(environment):
            environment.Append(CXXFLAGS='/Od') # No optimization for debugging
            environment.Append(CXXFLAGS='/MDd') # Link shared multithreaded debug runtime
            environment.Append(CXXFLAGS='/Zi') # Generate complete debugging information

            environment.Append(CFLAGS='/Od') # No optimization for debugging
            environment.Append(CFLAGS='/MDd') # Link shared multithreaded debug runtime
            environment.Append(CFLAGS='/Zi') # Generate complete debugging information
        else:
            environment.Append(CXXFLAGS='/O2') # Optimize for speed
            environment.Append(CXXFLAGS='/Gy') # Function-level linking for better trimming
            environment.Append(CXXFLAGS='/GL') # Whole program optimizaton (merged build)
            environment.Append(CXXFLAGS='/MD') # Link shared multithreaded release runtime
            environment.Append(CXXFLAGS='/Gw') # Enable whole-program *data* optimization

            environment.Append(CFLAGS='/O2') # Optimize for speed
            environment.Append(CFLAGS='/Gy') # Function-level linking for better trimming
            environment.Append(CFLAGS='/GL') # Whole program optimizaton (merged build)
            environment.Append(CFLAGS='/MD') # Link shared multithreaded release runtime
            environment.Append(CFLAGS='/Gw') # Enable whole-program *data* optimization

    else:
        environment.Append(CXXFLAGS='-std=c++14') # Use a widely supported but current C++
        environment.Append(CXXFLAGS='-fvisibility=hidden') # Default visibility: don't export
        environment.Append(CXXFLAGS='-Wpedantic') # Enable all ISO C++ deviation warnings
        environment.Append(CXXFLAGS='-Wall') # Show all warnings
        environment.Append(CXXFLAGS='-Wno-unknown-pragmas') # Don't warn about #pragma region
        #environment.Append(CXXFLAGS=['-flinker-output=pie']) # Position-independent executable
        environment.Append(CXXFLAGS='-shared-libgcc') # Show all warnings

        environment.Append(CFLAGS='-fvisibility=hidden') # Default visibility: don't export
        environment.Append(CFLAGS='-Wpedantic') # Enable all ISO C++ deviation warnings
        environment.Append(CFLAGS='-Wall') # Show all warnings
        environment.Append(CFLAGS='-Wno-unknown-pragmas') # Don't warn about #pragma region
        #environment.Append(CFLAGS=['-flinker-output=pie']) # Position-independent executable
        environment.Append(CFLAGS='-shared-libgcc') # Show all warnings

        if _is_debug_build(environment):
            environment.Append(CXXFLAGS='-Og') # Tailor code for optimal debugging
            environment.Append(CXXFLAGS='-g') # Generate debugging information

            environment.Append(CFLAGS='-Og') # Tailor code for optimal debugging
            environment.Append(CFLAGS='-g') # Generate debugging information
        else:
            environment.Append(CXXFLAGS='-O3') # Optimize for speed
            environment.Append(CXXFLAGS='-flto') # Merge all code before compiling

            environment.Append(CFLAGS='-O3') # Optimize for speed
            environment.Append(CFLAGS='-flto') # Merge all code before compiling

# ----------------------------------------------------------------------------------------------- #

def _set_standard_cplusplus_linker_flags(environment):
    """Sets up standard flags for the linker

    @param  environment  Environment in which the C++ compiler linker wlll be set."""

    if platform.system() == 'Windows':
        if _is_debug_build(environment):
            pass
        else:
            environment.Append(LINKFLAGS='/LTCG') # Merge all code before compiling
            environment.Append(LIBFLAGS='/LTCG') # Merge all code before compiling

    else:
        environment.Append(LINKFLAGS='-z defs') # Detect unresolved symbols in shared object
        environment.Append(LINKFLAGS='-Bsymbolic') # Prevent replacement on shared object syms

# ----------------------------------------------------------------------------------------------- #

def _add_cplusplus_package(environment, universal_package_name, universal_library_names = None):
    """Adds a precompiled package consisting of some header files and a code library
    to the current build.

    @param  environment              Environment to which a package will be added
    @param  universal_package_name   Name of the package that will be added to the build
    @param  universal_library_names  Names of libraries (inside the package) that need to
                                     be linked.
    @remarks
        If no universal_library_names are given, a library with the same name as
        the package is assumed. The universal_library_name can be used if a package
        offers multiple linkable library (i.e. boost modules, gtest + gtest_main)"""

    references_directory = os.path.join('..', environment['REFERENCES_DIRECTORY'])
    package_directory = os.path.join(references_directory, universal_package_name)

    # Path for the package's headers
    include_directory = cplusplus.find_or_guess_include_directory(package_directory)
    if include_directory is None:
        raise FileNotFoundError('Could not find include directory for package')

    environment.add_include_directory(include_directory)

    # Path for the package's libraries
    library_directory = cplusplus.find_or_guess_library_directory(environment, package_directory)
    if library_directory is None:
        raise FileNotFoundError('Could not find library directory for package')

    environment.add_library_directory(library_directory)

    # Library that needs to be linked
    if universal_library_names is None:
        environment.add_library(universal_package_name)
    elif isinstance(universal_library_names, list):
        for universal_library_name in universal_library_names:
            environment.add_library(universal_library_name)
    else:
        environment.add_library(universal_library_names)

# ----------------------------------------------------------------------------------------------- #

def _build_cplusplus_library(
  environment, universal_library_name, static = False, sources = None
):
    """Creates a shared C/C++ library

    @param  environment             Environment controlling the build settings
    @param  universal_library_name  Name of the library in universal format
                                    (i.e. 'My.Awesome.Stuff')
    @param  static                  Whether to build a static library (default: no)
    @param  sources                 Source files to use (None = auto)
    @remarks
        Assumes the default conventions, i.e. all source code is contained in a directory
        named 'Source' and all headers in a directory named 'Include'.

        See get_platform_specific_library_name() for how the universal_library_name parameter
        is used to produce the output filename on different platforms."""

    environment = environment.Clone()

    # Include directories
    # These will automatically be scanned by SCons for changes
    environment.add_include_directory(environment['HEADER_DIRECTORY'])

    # Recursively search for the source code files or transform the existing file list
    sources = _add_variantdir_and_enumerate_cplusplus_sources(
        environment, environment['SOURCE_DIRECTORY'], sources
    )
    library_path = _put_in_intermediate_path(
        environment, cplusplus.get_platform_specific_library_name(universal_library_name, static)
    )

    if platform.system() == 'Windows':
        environment.Append(
            CXXFLAGS='/Fd"' + os.path.splitext(library_path)[0] + '.pdb"'
        )
        environment.Append(
            CFLAGS='/Fd"' + os.path.splitext(library_path)[0] + '.pdb"'
        )
    else:
        environment.Append(CXXFLAGS='-fpic') # Use position-independent code
        environment.Append(CFLAGS='-fpic') # Use position-independent code

    # Build a shared library
    build_library = None
    if static:
        build_library = environment.StaticLibrary(library_path, sources)
    else:
        build_library = environment.SharedLibrary(library_path, sources)

    # On Windows, a .PDB file is produced when doing a debug build
    if (platform.system() == 'Windows') and _is_debug_build(environment):
        environment.SideEffect(
            os.path.splitext(executable_path)[0] + '.pdb', build_library
        )

    return build_library

# ----------------------------------------------------------------------------------------------- #

def _build_cplusplus_executable(
    environment, universal_executable_name, console = False, sources = None
):
    """Creates a vanilla C/C++ executable

    @param  environment                Environment controlling the build settings
    @param  universal_executable_name  Name of the executable in universal format
                                       (i.e. 'My.Awesome.App')
    @param  console                    Whether to build a shell/command line executable
    @param  sources                    Source files to use (None = auto)
    @remarks
        Assumes the default conventions, i.e. all source code is contained in a directory
        named 'Source' and all headers in a directory named 'Include'.

        See get_platform_specific_executable_name() for how the universal_library_name
        parameter is used to produce the output filename on different platforms."""

    environment = environment.Clone()

    # Include directories
    # These will automatically be scanned by SCons for changes
    environment.add_include_directory(environment['HEADER_DIRECTORY'])

    # Recursively search for the source code files or transform the existing file list
    sources = _add_variantdir_and_enumerate_cplusplus_sources(
        environment, environment['SOURCE_DIRECTORY'], sources
    )
    executable_path = _put_in_intermediate_path(
        environment, cplusplus.get_platform_specific_executable_name(universal_executable_name)
    )

    # On Windows, there is a distinguishment between console (shell) applications
    # and GUI applications. Add the appropriate flag if needed.
    if (platform.system() == 'Windows'):
        if console:
            environment.Append(LINKFLAGS='/SUBSYSTEM:CONSOLE')

        environment.Append(
            CXXFLAGS='/Fd"' + os.path.splitext(executable_path)[0] + '.pdb"'
        )
        environment.Append(
            CFLAGS='/Fd"' + os.path.splitext(executable_path)[0] + '.pdb"'
        )
    else:
        environment.Append(CXXFLAGS='-fpic') # Use position-independent code
        environment.Append(CXXFLAGS='-fpie') # Use position-independent code
        environment.Append(CFLAGS='-fpic') # Use position-independent code
        environment.Append(CFLAGS='-fpie') # Use position-independent code

    # Build the executable
    build_executable = environment.Program(executable_path, sources)

    # On Windows, a .PDB file is produced when doing a debug build
    if (platform.system() == 'Windows') and _is_debug_build(environment):
        environment.SideEffect(
            os.path.splitext(executable_path)[0] + '.pdb', build_executable
        )

    return build_executable

# ----------------------------------------------------------------------------------------------- #

def _build_cplusplus_library_with_tests(
    environment, universal_library_name, universal_test_executable_name,
    sources = None, test_sources = None
):
    """Creates a C/C++ shared library and also builds a unit test executable or it

    @param  environment                Environment controlling the build settings
    @param  universal_executable_name  Name of the library in universal format
                                       (i.e. 'My.Awesome.Stuff')
    @param  sources                    Source files to use (None = auto)
    @param  test_sources               Source files to use for the unit tests (None = auto)
    @remarks
        Assumes the default conventions, i.e. all source code is contained in a directory
        named 'Source' and all headers in a directory named 'Include'.

        In addition to the convenience factor, this method also avoids SCons warnings about
        two environments producing the same intermediate files (or having to compile everything
        twice) by first building a static library, then producing a shared library from it
        and producing the unit test executabel from it together with the unit test sources.

        See get_platform_specific_executable_name() for how the universal_library_name
        parameter is used to produce the output filename on different platforms."""

    # Recursively search for the source code files or transform the existing file list
    sources = _add_variantdir_and_enumerate_cplusplus_sources(
        environment, environment['SOURCE_DIRECTORY'], sources
    )
    test_sources = _add_variantdir_and_enumerate_cplusplus_sources(
        environment, environment['TESTS_DIRECTORY'], test_sources
    )

    intermediate_directory = os.path.join(
        environment['INTERMEDIATE_DIRECTORY'],
        environment.get_build_directory_name()
    )

    base_directory = Dir('.').abspath # Necessary if this is running inside env.SConscript()

    # Build a static library that we can reuse for the shared library and test executable
    if True:
        intermediate_library_name = cplusplus.get_platform_specific_library_name(
            universal_library_name + ".Static", static = True
        )
        intermediate_library_path = _put_in_intermediate_path(
            environment, intermediate_library_name
        )

        staticlib_environment = environment.Clone();
        staticlib_environment.add_include_directory(environment['HEADER_DIRECTORY'])
        #staticlib_environment['PDB'] = os.path.splitext(intermediate_library_path)[0] + '.pdb"'

        if platform.system() == 'Windows':
            staticlib_environment.Append(
                CXXFLAGS='/Fd"' + os.path.join(base_directory, os.path.splitext(intermediate_library_path)[0] + '.pdb"')
            )
            staticlib_environment.Append(
                CFLAGS='/Fd"' + os.path.join(base_directory, os.path.splitext(intermediate_library_path)[0] + '.pdb"')
            )
        else:
            staticlib_environment.Append(CXXFLAGS='-fpic') # Use position-independent code
            staticlib_environment.Append(CFLAGS='-fpic') # Use position-independent code

        compile_static_library = staticlib_environment.StaticLibrary(
            intermediate_library_path, sources
        )

    # Build a shared library using nothing but the static library for sources
    if True:
        sources = [] # We don't use any sources but the static library from above

        library_name = cplusplus.get_platform_specific_library_name(universal_library_name)
        library_path = _put_in_intermediate_path(environment, library_name)

        sharedlib_environment = environment.Clone();
        sharedlib_environment.add_include_directory(environment['HEADER_DIRECTORY'])
        #sharedlib_environment['PDB'] = os.path.splitext(library_path)[0] + '.pdb"'

        sharedlib_environment.add_library_directory(intermediate_directory)
        sharedlib_environment.add_library(intermediate_library_name)

        if platform.system() == 'Windows':
            sharedlib_environment.Append(
                CXXFLAGS='/Fd"' + os.path.join(base_directory, os.path.splitext(library_path)[0] + '.pdb"')
            )
            sharedlib_environment.Append(
                CFLAGS='/Fd"' + os.path.join(base_directory, os.path.splitext(library_path)[0] + '.pdb"')
            )
            dummy_path = _put_in_intermediate_path(environment, 'msvc-dllmain-dummy.cpp')
            sources.append(dummy_path)
            create_dummy_file = sharedlib_environment.Command(
                source = [], action = 'echo // > $TARGET', target = dummy_path
            )

            compile_shared_library = sharedlib_environment.SharedLibrary(library_path, sources)
            sharedlib_environment.Depends(compile_shared_library, create_dummy_file)

            # On Windows, a .PDB file is produced when doing a debug build
            if _is_debug_build(environment):
                environment.SideEffect(
                    os.path.splitext(library_path)[0] + '.pdb', compile_share_library
                )

        else:
            sharedlib_environment.Append(CXXFLAGS='-fpic') # Use position-independent code
            sharedlib_environment.Append(CFLAGS='-fpic') # Use position-independent code
            compile_shared_library = sharedlib_environment.SharedLibrary(library_path, sources)


    if True:
        executable_name = cplusplus.get_platform_specific_executable_name(
            universal_test_executable_name
        )
        executable_path = _put_in_intermediate_path(environment, executable_name)

        executable_environment = environment.Clone()
        executable_environment.add_include_directory(environment['HEADER_DIRECTORY'])
        #executable_environment['PDB'] = os.path.splitext(executable_path)[0] + '.pdb"'

        executable_environment.add_library_directory(intermediate_directory)
        executable_environment.add_library(intermediate_library_name)

        executable_environment.add_package('gtest', [ 'gtest', 'gtest_main' ])

        if platform.system() == 'Windows':
            executable_environment.Append(LINKFLAGS="/SUBSYSTEM:CONSOLE")
            executable_environment.Append(
                CXXFLAGS='/Fd"' + os.path.join(base_directory, os.path.splitext(executable_path)[0] + '.pdb"')
            )
            executable_environment.Append(
                CFLAGS='/Fd"' + os.path.join(base_directory, os.path.splitext(executable_path)[0] + '.pdb"')
            )
        else:
            executable_environment.add_library('pthread') # Needed by googletest
            executable_environment.Append(CXXFLAGS='-fpic') # Use position-independent code
            executable_environment.Append(CXXFLAGS='-fpie') # Use position-independent code
            executable_environment.Append(CFLAGS='-fpic') # Use position-independent code
            executable_environment.Append(CFLAGS='-fpie') # Use position-independent code

        compile_unit_tests = executable_environment.Program(executable_path, test_sources)

    environment.Depends(compile_shared_library, compile_static_library)
    environment.Depends(compile_unit_tests, compile_static_library)

    return [ compile_shared_library, compile_unit_tests ]

# ----------------------------------------------------------------------------------------------- #

def _run_cplusplus_unit_tests(environment, universal_test_executable_name):
    """Runs the unit tests executable comiled from a build_unit_test_executable() call

    @param  environment                     Environment used to locate the unit test executable
    @param  universal_test_executable_name  Name of the unit test executable from the build step
    @remarks
        This executes the unit test executable and produces an XML file detailing
        the test results for CI servers and other processing."""

    environment = environment.Clone()

    # Figure out the path the unit tests executable would have been compiled to
    test_executable_name = cplusplus.get_platform_specific_executable_name(
        universal_test_executable_name
    )
    test_executable_path = _put_in_intermediate_path(
        environment, test_executable_name
    )

    test_results_path = _put_in_artifact_path(
        environment, environment['TESTS_RESULT_FILE']
    )

    return environment.Command(
        source = test_executable_path,
        action = '-$SOURCE --gtest_output=xml:$TARGET',
        target = test_results_path
    )

# ----------------------------------------------------------------------------------------------- #

def _build_msbuild_project(environment, msbuild_project_path):
    """Builds an MSBuild project

    @param  environment           Environment the MSBuild project will be compiled in
    @param  msbuild_project_path  Path to the MSBuild project file that will be built"""

    msbuild_project_file = environment.File(msbuild_project_path)
    dotnet_version_tag = dotnet.detect_msbuild_target_framework(msbuild_project_file)

    build_directory_name = environment.get_build_directory_name(dotnet_version_tag)

    intermediate_build_directory = os.path.join(
        environment['INTERMEDIATE_DIRECTORY'], build_directory_name
    )

    environment.MSBuild(
        msbuild_project_file.srcnode().abspath,
        intermediate_build_directory
    )

# ----------------------------------------------------------------------------------------------- #

def _build_msbuild_project_with_tests(
    environment, msbuild_project_path, tests_msbuild_project_path
):
    _build_msbuild_project(environment, msbuild_project_path)

# ----------------------------------------------------------------------------------------------- #

def _add_variantdir_and_enumerate_cplusplus_sources(environment, directory, sources = None):
    """Sets up a variant directory for a set of sources and enumerates the sources
    with their paths when compiled to the variant directory.

    @param  environment  Environment the variant directory will be set up in
    @param  directory    Directory containing the sources that will be enumerated
    @param  sources      User-provided list of source files to transform instead
                         If this is 'None', the directory will be enumerated.
    @returns The list of source files in their virtual variant dir locations"""

    # Append the build directory. This directory is unique per build setup,
    # so that debug/release and x86/amd64 builds can life side by side or happen
    # in parallel.
    intermediate_build_directory = os.path.join(
        environment['INTERMEDIATE_DIRECTORY'],
        environment.get_build_directory_name()
    )
    variant_directory = os.path.join(intermediate_build_directory, directory)

    # Set up the variant directory so that object files get stored separately
    environment.VariantDir(variant_directory, directory, duplicate = 0)

    if sources is None:

        # Recursively search for the source code files
        return cplusplus.enumerate_sources(directory, intermediate_build_directory)

    else:

        new_sources = []

        for file_path in sources:
            new_sources.append(
                os.path.join(intermediate_build_directory, file_path)
            )

        return new_sources

# ----------------------------------------------------------------------------------------------- #

def _put_in_intermediate_path(environment, filename):
    """Determines the intermediate path for a file with the specified name

    @param  environment  Environment for which the intermediate path will be determined
    @param  filename     Filename for which the intermediate path will be returned
    @returns The intermediate path for a file with the specified name"""

    intermediate_directory = os.path.join(
        environment['INTERMEDIATE_DIRECTORY'],
        environment.get_build_directory_name()
    )

    return os.path.join(intermediate_directory, filename)

# ----------------------------------------------------------------------------------------------- #

def _put_in_artifact_path(environment, filename):
    """Determines the artifact path for a file with the specified name

    @param  environment  Environment for which the artifact path will be determined
    @param  filename     Filename for which the artifact path will be returned
    @returns The artifact path for a file with the specified name"""

    artifact_directory = os.path.join(
        environment['ARTIFACT_DIRECTORY'],
        environment.get_build_directory_name()
    )

    return os.path.join(artifact_directory, filename)

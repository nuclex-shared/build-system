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
#from SCons.Script.SConscript import SConsEnvironment

# Nuclex SCons libraries
shared = importlib.import_module('shared')
cplusplus = importlib.import_module('cplusplus')

# Plan:
#   - if TARGET_ARCH is set, use it. For multi-builds,
#     this may result in failure, but that's okay
#   - multi-builds (typical case x86/x64 native + .net anycpu)
#     must control target arch manually anyway.

# ----------------------------------------------------------------------------------------------- #

def create_cplusplus_environment():
    """Creates a new environment with the required variables for building C/C++ projects

    @returns A new scons environment containing the C/C++ variables"""

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
    _register_cplusplus_extension_methods(environment)

    return environment

# ----------------------------------------------------------------------------------------------- #

def _parse_default_command_line_options():
    """Parses the command line options controlling various build settings

    @remarks
        This contains variables that work across all builds. Build-specific variables
        are discouraged, but would be irgnored by SCons' Variables class."""

    command_line_variables = Variables(None, ARGUMENTS)

    # Build configuration (also called build type in many SCons examples)
#    command_line_variables.Add(
#        BoolVariable(
#            'DEBUG',
#            'Whether to do an unoptimized debug build',
#            'debug'
#        )
#    )

    # CPU architecture to target
    command_line_variables.Add(
        EnumVariable(
            'TARGET_ARCH',
            'CPU architecture the binary will run on',
            'x64',
            allowed_values=('x86', 'x64', 'arm', 'any')
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
    """Registers extensions methods for C/C++ builds into a SCons environment

    @param  environment  Environment the extension methods will be registered to"""

    environment.add_package = types.MethodType(
        _add_cplusplus_package, environment
    )

# ----------------------------------------------------------------------------------------------- #

def _is_debug_build(environment):
    return 'DEBUG' in environment

# ----------------------------------------------------------------------------------------------- #

def _set_standard_cplusplus_compiler_flags(environment):
    """Sets up standard flags for the compiler

    @param  environment  Environment in which the C++ compiler flags wlll be set."""

    if platform.system() == 'Linux':
        environment.Append(CXXFLAGS=['-std=c++14']) # Use a widely supported but current C++
        environment.Append(CXXFLAGS=['-fvisibility=hidden']) # Default visibility: don't export
        environment.Append(CXXFLAGS=['-Wpedantic']) # Enable all ISO C++ deviation warnings
        environment.Append(CXXFLAGS=['-Wall']) # Show all warnings
        #environment.Append(CXXFLAGS=['-flinker-output=pie']) # Position-independent executable
        environment.Append(CXXFLAGS=['-shared-libgcc']) # Show all warnings
        #environment.Append(CXXFLAGS=['-fpic -fpie]') # Position-independent lib/executable

        if _is_debug_build(environment):
            environment.Append(CXXFLAGS=['-Og']) # Tailor code for optimal debugging
            environment.Append(CXXFLAGS=['-g']) # Generate debugging information
        else:
            environment.Append(CXXFLAGS=['-O3']) # Optimize for speed

    else:
        environment.Append(CXXFLAGS=['/EHsc']) # Only C++ exceptions, no Microsoft exceptions
        environment.Append(CXXFLAGS=['/GF']) # String pooling in debug and release
        environment.Append(CXXFLAGS=['/Gv']) # Vectorcall for speed
        environment.Append(CXXFLAGS=['/utf-8']) # Source code and outputs are UTF-8 encoded
        environment.Append(CXXFLAGS=['/std:c++14']) # Use a widely supported but current C++
        environment.Append(CXXFLAGS=['/W4']) # Show all warnings
        environment.Append(CXXFLAGS=['/GS-']) # No buffer security checks (we make games!)
        environment.Append(CXXFLAGS=['/GR']) # Generate RTTI for dynamic_cast and type_info

        if _is_debug_build(environment):
            environment.Append(CXXFLAGS=['/Od']) # No optimization for debugging
            environment.Append(CXXFLAGS=['/MDd']) # Link shared multithreaded debug runtime
            environment.Append(CXXFLAGS=['/Zi']) # Generate complete debugging information
        else:
            environment.Append(CXXFLAGS=['/O2']) # Optimize for speed
            environment.Append(CXXFLAGS=['/Gy']) # Function-level linking for better trimming
            environment.Append(CXXFLAGS=['/GL']) # Whole program optimizaton (merged build)
            environment.Append(CXXFLAGS=['/MD']) # Link shared multithreaded release runtime
            environment.Append(CXXFLAGS=['/Gw']) # Enable whole-program *data* optimization

# ----------------------------------------------------------------------------------------------- #

def _set_standard_cplusplus_linker_flags(environment):
    """Sets up standard flags for the linker

    @param  environment  Environment in which the C++ compiler linker wlll be set."""

    if platform.system() == 'Linux':
        environment.Append(LINKLAGS=['-z defs']) # Detect unresolved symbols in shared object
        environment.Append(LINKLAGS=['-Bsymbolic']) # Prevent replacement on shared object syms

# ----------------------------------------------------------------------------------------------- #

def _add_cplusplus_package(environment, package_name, universal_library_names = None):
    """Adds a precompiled package consisting of some header files and a code library
    to the current build.

    @param  self                     The instance this method should work on
    @param  universal_package_name   Name of the package that will be added to the build
    @param  universal_library_names  Names of libraries (inside the package) that need to
                                     be linked.
    @remarks
        If no universal_library_names are given, a library with the same name as
        the package is assumed. The universal_library_name can be used if a package
        offers multiple linkable library (i.e. boost modules, gtest + gtest_main)"""

    references_directory = os.path.join('..', self._environment['REFERENCES_DIRECTORY'])
    package_directory = os.path.join(references_directory, universal_package_name)

    # Path for the package's headers
    include_directory = self._find_or_guess_include_directory(package_directory)
    if include_directory is None:
        raise FileNotFoundError('Could not find include directory for package')

    self.add_include_directory(include_directory)

    # Path for the package's libraries
    library_directory = self._find_or_guess_library_directory(package_directory)
    if include_directory is None:
        raise FileNotFoundError('Could not find library directory for package')

    self.add_library_directory(library_directory)

    # Library that needs to be linked
    if universal_library_names is None:
        self.add_library(universal_package_name)
    elif isinstance(universal_library_names, list):
        for universal_library_name in universal_library_names:
            self.add_library(universal_library_name)
    else:
        self.add_library(universal_library_names)

# ----------------------------------------------------------------------------------------------- #

def _set_standard_compiler_flags(self):
    """Sets up standard flags for the compiler

    @param  self  The instance this method should work on"""

    self._environment.Append(CXXFLAGS=['-std=c++14'])
    self._environment.Append(CXXFLAGS=['-fvisibility=hidden'])

# ----------------------------------------------------------------------------------------------- #

def build_shared_library(self, universal_library_name):
    """Creates a shared library

    @param  self                    The instance this method should work on
    @param  universal_library_name  Name of the library in universal format
                                        (i.e. 'My.Awesome.Stuff')
    @remarks
        Assumes the default conventions, i.e. all source code is contained in a directory
        named 'Source' and all headers in a directory named 'Include'.

        See get_platform_specific_library_name() for how the universal_library_name parameter
        is used to produce the output filename on different platforms."""

    self._set_standard_compiler_flags()

    # Include directories
    # These will automatically be scanned by SCons for changes
    self.add_include_directory(self._environment['HEADER_DIRECTORY'])

    # Use a separate directory for the object files instead of
    # cluttering up the source tree.
    self._environment.VariantDir(
        os.path.join(
            self._environment['INTERMEDIATE_DIRECTORY'],
            self._environment['SOURCE_DIRECTORY']
        ),
        self._environment['SOURCE_DIRECTORY'],
        duplicate=0
    )

    sources = cplusplus.enumerate_sources(
        self._environment['SOURCE_DIRECTORY'],
        self._environment['INTERMEDIATE_DIRECTORY']
    )

    # Build a shared library
    platform_specific_library_name = cplusplus.get_platform_specific_library_name(
        universal_library_name
    )
    return self._environment.SharedLibrary(
        os.path.join(
            self._environment['INTERMEDIATE_DIRECTORY'],
            platform_specific_library_name
        ),
        sources
    )

# ----------------------------------------------------------------------------------------------- #

def build_unit_test_executable(self, universal_executable_name):
    """Creates a unit test executable

    @param  self                       The instance this method should work on
    @param  universal_executable_name  Name of the library in universal format
                                       (i.e. 'My.Awesome.Library')
    @remarks
        Assumes the default conventions, i.e. all source code is contained in a directory
        named 'Source' and all headers in a directory named 'Include'.

        See get_platform_specific_library_name() for how the universal_executable_name
        parameter is used to produce the output filename on different platforms."""

    self._set_standard_compiler_flags()

    # Include directories
    # These will automatically be scanned by SCons for changes
    self.add_include_directory(self._environment['HEADER_DIRECTORY'])

    # Use a separate directory for the object files instead of
    # cluttering up the source tree.
    self._environment.VariantDir(
        os.path.join(
            self._environment['INTERMEDIATE_DIRECTORY'],
            self._environment['SOURCE_DIRECTORY']
        ),
        self._environment['SOURCE_DIRECTORY'],
        duplicate=0
    )
    self._environment.VariantDir(
        os.path.join(
            self._environment['INTERMEDIATE_DIRECTORY'],
            self._environment['TESTS_DIRECTORY']
        ),
        self._environment['TESTS_DIRECTORY'],
        duplicate=0
    )

    sources = cplusplus.enumerate_sources(
        self._environment['SOURCE_DIRECTORY'],
        self._environment['INTERMEDIATE_DIRECTORY']
    )
    tests = cplusplus.enumerate_sources(
        self._environment['TESTS_DIRECTORY'],
        self._environment['INTERMEDIATE_DIRECTORY']
    )

    self.add_package('gtest', ['gtest', 'gtest_main'])

    # Build the unit test executable
    platform_specific_executable_name = cplusplus.get_platform_specific_executable_name(
        universal_executable_name
    )
    return self._environment.Program(
        os.path.join(
            self._environment['INTERMEDIATE_DIRECTORY'],
            platform_specific_executable_name
        ),
        sources + tests
    )

# ----------------------------------------------------------------------------------------------- #

def run_unit_tests(self, universal_executable_name):
    """Runs the unit tests executable comiled from a build_unit_test_executable() call

    @param  self                       The instance this method should work on
    @param  universal_executable_name  Name of the unit test executable from the build step
    @remarks
        This executes the unit test executable and produces an XML file detailing
        the test results for CI servers and other processing."""

    # Figure out the path the unit tests executable would have been compiled to
    platform_specific_executable_name = cplusplus.get_platform_specific_executable_name(
        universal_executable_name
    )
    test_executable_path = os.path.join(
        self._environment['INTERMEDIATE_DIRECTORY'],
        platform_specific_executable_name
    )

    test_results_path = os.path.join(
        self._environment['ARTIFACT_DIRECTORY'],
        self._environment['TESTS_RESULT_FILE']
    )

    return self._environment.Command(
        source = test_executable_path,
        action = test_executable_path + ' --gtest_output=xml:' + test_results_path,
        target = test_results_path
    )

# ----------------------------------------------------------------------------------------------- #

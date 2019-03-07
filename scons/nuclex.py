#!/usr/bin/env python

import os
import importlib
import platform

from SCons.Environment import Environment
from SCons.Variables import Variables
from SCons.Variables import EnumVariable
from SCons.Variables import PathVariable
from SCons.Script import ARGUMENTS

# Nuclex SCons libraries
shared = importlib.import_module('shared')
cplusplus = importlib.import_module('cplusplus')

# ----------------------------------------------------------------------------------------------- #

class CPlusPlusMaker:
    """Compiles a C/C++ library or executable with SCons"""

    # ------------------------------------------------------------------------------------------- #

    def __init__(self):
        self._environment = Environment(
            variables = self._parse_default_command_line_options(),
            SOURCE_DIRECTORY = 'Source',
            HEADER_DIRECTORY = 'Include',
            TESTS_DIRECTORY = 'Tests',
            TESTS_RESULT_FILE = "gtest-results.xml",
            REFERENCES_DIRECTORY = 'References'
        )

    # ------------------------------------------------------------------------------------------- #

    @staticmethod
    def _parse_default_command_line_options():
        """Parses the command line options controlling various build settings

        @remarks
            This contains variables that work across all builds. Build-specific variables
            are discouraged, but would be irgnored by SCons' Variables class."""

        command_line_variables = Variables(None, ARGUMENTS)

        # Build configuration (also called build type in many SCons examples)
        command_line_variables.Add(
            EnumVariable(
                'CONFIGURATION',
                'Build configuration to use for building',
                'debug',
                allowed_values=('debug', 'release')
            )
        )

        # CPU architecture to target
        command_line_variables.Add(
            EnumVariable(
                'ARCHITECTURE',
                'CPU architecture the binary will run on',
                'x64',
                allowed_values=('x86', 'x64', 'arm')
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

    # ------------------------------------------------------------------------------------------- #

    def select_debug_build(self):
        """Defines the build as a debug build

        @param  self  The instance this method should work on
        @remarks
            Debug builds contain additional checks and disable many compiler optimizations,
            thus they run slower. They are suitable for testing and finding errors while
            a C/C++ project is being developed.

            They should not be shipped because they may depend on libraries only present on
            a developer machine and show assertion messages and other things that are
            not intended for the end user."""

        self._environment['CONFIGURATION'] = 'debug'

    # ------------------------------------------------------------------------------------------- #

    def select_release_build(self):
        """Defines the build as a release build for shipping

        @param  self  The instance this method should work on
        @remarks
            Release builds enable all compiler optimizations and are designed to achieve
            maximum speed + minimum size on the end-users machine.

            They are usually not suitable for debugging because code flow may have been
            rearranged, methods inlined or removed completely and debug information that
            correlates executable addresses with line numbers will have been stripped."""

        self._environment['CONFIGURATION'] = 'release'

    # ------------------------------------------------------------------------------------------- #

    def select_x86_architecture(self):
        """Makes the build produce a 32 bit, Intel x86 executable

        @param  self  The instance this method should work on"""

        self._environment['ARCHITECTURE'] = 'x86'

    # ------------------------------------------------------------------------------------------- #

    def select_x64_architecture(self):
        """Makes the build produce a 64 bit, AMD64 (also called x86_64) executable

        @param  self  The instance this method should work on"""

        self._environment['ARCHITECTURE'] = 'x64'

    # ------------------------------------------------------------------------------------------- #

    def select_arm_architecture(self):
        """Makes the build produce an ARM executable (as needed for i.e. Raspberry PI)

        @param  self  The instance this method should work on"""

        self._environment['ARCHITECTURE'] = 'arm'

    # ------------------------------------------------------------------------------------------- #

    def set_source_directory(self, source_directory):
        """Sets the directory in which source code files will be looked for

        @param  self              The instance this method should work on
        @param  source_directory  Directory in which the source code is found
        @remarks
            Changing the name of the source directory should only be necessary if
            the Nuclex build scripts are used on a non-Nuclex project."""

        self._environment['SOURCE_DIRECTORY'] = source_directory

    # ------------------------------------------------------------------------------------------- #

    def set_header_directory(self, header_directory):
        """Sets the directory in which header files will be looked for

        @param  self              The instance this method should work on
        @param  header_directory  Directory in which the header files are stored
        @remarks
            Changing the name of the header / include directory should only be necessary if
            the Nuclex build scripts are used on a non-Nuclex project."""

        self._environment['HEADER_DIRECTORY'] = header_directory

    # ------------------------------------------------------------------------------------------- #

    def set_tests_directory(self, tests_directory):
        """Sets the directory in which unit test source code files will be looked for

        @param  self             The instance this method should work on
        @param  tests_directory  Directory in which the unit test source code is stored
        @remarks
            Changing the name of the unit test source code directory should only be necessary
            if the Nuclex build scripts are used on a non-Nuclex project."""

        self._environment['TESTS_DIRECTORY'] = tests_directory

    # ------------------------------------------------------------------------------------------- #

    def add_include_directory(self, include_directory):
        """Adds an include directory to the build

        @param  self  The instance this method should work on
        @param  include_directory  Include directory that will be added
        @remarks
            Consider using add_package() instead to automatically set up all include and
            library directories as well as link the libraries themselves."""

        cplusplus.add_include_directory(self._environment, include_directory)

    # ------------------------------------------------------------------------------------------- #

    def add_library_directory(self, library_directory):
        """Adds a library directory to the build

        @param  self  The instance this method should work on
        @param  library_directory  Library directory that will be added
        @remarks
            Consider using add_package() instead to automatically set up all include and
            library directories as well as link the libraries themselves."""

        cplusplus.add_library_directory(self._environment, library_directory)

    # ------------------------------------------------------------------------------------------- #

    def add_library(self, library_name):
        """Adds a library to the build

        @param  self  The instance this method should work on
        @param  library_name  Name of the library that will be linked
        @remarks
            Consider using add_package() instead to automatically set up all include and
            library directories as well as link the libraries themselves."""

        cplusplus.add_library(self._environment, library_name)

    # ------------------------------------------------------------------------------------------- #

    def _find_or_guess_include_directory(self, package_path):
        """Tries to locate the include directory for a package

        @param  self          The instance this method should work on
        @param  package_path  Path to the package"""

        candidate = os.path.join(package_path, 'include')
        if os.path.isdir(candidate):
            return candidate

        candidate = os.path.join(package_path, 'Include')
        if os.path.isdir(candidate):
            return candidate

        package_name = os.path.basename(os.path.normpath(package_path))
        candidate = os.path.join(package_path, package_name)
        if os.path.isdir(candidate):
            return candidate

        return None

    # ------------------------------------------------------------------------------------------- #

    def _find_or_guess_library_directory(self, package_path):
        """Tries to locate the library directory for a package

        @param  self          The instance this method should work on
        @param  package_path  Path to the package"""

        library_directory = os.path.join(
            package_path,
            cplusplus.get_platform_library_directory(
                self._environment['ARCHITECTURE'], self._environment['CONFIGURATION']
            )
        )

        return library_directory

    # ------------------------------------------------------------------------------------------- #

    def add_package(self, universal_package_name, universal_library_names = None):
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

    # ------------------------------------------------------------------------------------------- #

    def _set_standard_compiler_flags(self):
        """Sets up standard flags for the compiler

        @param  self  The instance this method should work on"""

        self._environment.Append(CXXFLAGS=['-std=c++14'])
        self._environment.Append(CXXFLAGS=['-fvisibility=hidden'])

    # ------------------------------------------------------------------------------------------- #

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

    # ------------------------------------------------------------------------------------------- #

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

    # ------------------------------------------------------------------------------------------- #

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

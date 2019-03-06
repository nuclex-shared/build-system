#!/usr/bin/env python

import os
import importlib
import platform

from SCons.Environment import Environment

# Nuclex SCons libraries
shared = importlib.import_module('shared')
cplusplus = importlib.import_module('cplusplus')

# ----------------------------------------------------------------------------------------------- #

def get_cplusplus_platform_specific_name(universal_name, is_executable):
    """Gets the platform-specific name for a build target from its universal name

    @param  universal_name  Universal name to get the the platform-specific name for
    @param  is_executable   Whether the build target is an executable (vs. a library)

    @remarks
      The universal name will be interpreted differently based on the platform,
      Linux systems will, for example, use libMyAwesomeLibrary.so while Windows
      systems will produce My.Awesome.Library.dll."""

    if platform.system() == 'Linux':
        return "lib" + universal_name.replace('.', '')
    elif is_executable:
        return universal_name + ".exe"
    else:
        return universal_name + ".so"

# ----------------------------------------------------------------------------------------------- #

def compile_cplusplus_shared_library(universal_library_name):
    """Creates a shared library

    @param  universal_library_name  Name of the library in universal format
                                    (i.e. 'My.Awesome.Library')
    @remarks
      Assumes the default conventions, i.e. all source code is contained in a directory
      named 'Source' and all headers in a directory named 'Include'.

      See get_platform_specific_library_name() for how the universal_library_name parameter
      is used to produce the output filename on different platforms."""

    # Set up a new build environment definition
    env = Environment(
        intermediate_dir = 'obj'
    )

    env.Append(CXXFLAGS=['-std=c++14', '-fvisibility=hidden'])

    # Include directories
    # These will automatically be scanned by SCons for changes
    env.Append(CPPPATH=['Include'])

    # Use a separate directory for the object files instead of
    # cluttering up the source tree.
    env.VariantDir(
        os.path.join(env['intermediate_dir'], 'Source'), 'Source', duplicate=0
    )
    sources = cplusplus.enumerate_sources('Source', env['intermediate_dir'])

    # Build a shared library
    platform_library_name = get_cplusplus_platform_specific_name(universal_library_name, False)
    return env.SharedLibrary(os.path.join('obj', platform_library_name), sources)

# ----------------------------------------------------------------------------------------------- #

def compile_cplusplus_unit_tests(universal_executable_name):
    """Creates a unit test executable

    @param  universal_executable_name  Name of the library in universal format
                                    (i.e. 'My.Awesome.Library')
    @remarks
      Assumes the default conventions, i.e. all source code is contained in a directory
      named 'Source' and all headers in a directory named 'Include'.

      See get_platform_specific_library_name() for how the universal_library_name parameter
      is used to produce the output filename on different platforms."""

    # Set up a new build environment definition
    env = Environment(
        intermediate_dir = 'obj'
    )

    env.Append(CXXFLAGS=['-std=c++14', '-fvisibility=hidden'])

    # Include directories
    # These will automatically be scanned by SCons for changes
    env.Append(CPPPATH=['Include'])
    env.Append(CPPPATH=['../References/gtest/include'])

    # Use a separate directory for the object files instead of
    # cluttering up the source tree.
    env.VariantDir(
        os.path.join(env['intermediate_dir'], 'Source'), 'Source', duplicate=0
    )
    sources = cplusplus.enumerate_sources('Source', env['intermediate_dir'])

    # Use a separate directory for the object files instead of
    # cluttering up the source tree.
    env.VariantDir(
        os.path.join(env['intermediate_dir'], 'Tests'), 'Tests', duplicate=0
    )
    tests = cplusplus.enumerate_sources('Tests', env['intermediate_dir'])

    # Add GoogleTest
    env.Append(LIBS=['gtest', 'gtest_main'])
    env.Append(LIBPATH=['../References/gcc-x64-pc-linux-gnu'])

    platform_executable_name = get_cplusplus_platform_specific_name(
        universal_executable_name, True
    )
    return env.Program(os.path.join('obj', platform_executable_name), sources + tests)

# ----------------------------------------------------------------------------------------------- #

def run_cplusplus_unit_tests(universal_executable_name):
    env = Environment(
        intermediate_dir = 'obj',
        test_results_file = 'googletest-results.xml'
    )

    # Figure out the path the unit tests executable would have been compiled to
    test_executable_path = os.path.join(
        env['intermediate_dir'],
        get_cplusplus_platform_specific_name(universal_executable_name, True)
    )

    test_results_path = os.path.join(
        os.path.dirname(test_executable_path),
        env['test_results_file']
    )

    return env.Command(
        source = test_executable_path,
        action = test_executable_path + ' --gtest_output=xml:' + test_results_path,
        target = test_results_path
    )

# ----------------------------------------------------------------------------------------------- #

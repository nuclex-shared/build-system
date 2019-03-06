#!/usr/bin/env python

import os
import shutil

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

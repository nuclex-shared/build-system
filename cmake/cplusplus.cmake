#!/usr/bin/cmake
cmake_minimum_required (VERSION 3.8)

# ----------------------------------------------------------------------------------------------- #

# Detect which compiler is being used
#
# This sets one of the following flags
#   CMAKE_COMPILER_IS_INTEL  Intel's special optimizing compiler, exists on multiple platforms
#   CMAKE_COMPILER_IS_CLANG  CLang, an alternative to GCC that's become pretty popular
#   CMAKE_COMPILER_IS_GCC    GNU C/C++ compiler, the standard compiler on Linux systems
#   CMAKE_COMPILER_IS_MSVC   Microsoft Visual C++, the stndard compiler on Windows systems
if(CMAKE_CXX_COMPILER_ID STREQUAL "Intel")
    set(CMAKE_COMPILER_IS_INTEL ON)
elseif(
    (CMAKE_CXX_COMPILER_ID STREQUAL "Clang") OR
    (CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang")
)
    set(CMAKE_COMPILER_IS_CLANG ON)
elseif(
    (CMAKE_CXX_COMPILER_ID STREQUAL "GNU") OR
    CMAKE_COMPILER_IS_GNUCXX
)
    set(CMAKE_COMPILER_IS_GCC ON)
elseif(MSVC)
    set(CMAKE_COMPILER_IS_MSVC ON)
endif()

# ----------------------------------------------------------------------------------------------- #

# Set up common compiler flags depending on the platform used

# Visual C++ flags (matched against Visual C++ 2017)
if(CMAKE_COMPILER_IS_MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /EHsc") # Enable only C++ exceptions
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /GF") # String pooling in debug and release
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /utf-8") # Source code and outputs are UTF-8
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /std:c++14") # Target a specific, recent standard
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4") # Enable all warnings
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /GS-") # No buffer checks (we make games!)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /GR") # Generate RTTI for dynamic_cast/type_info
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /FS") # PDBs can be written from multiple processes

    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /GF") # String pooling in debug and release
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /utf-8") # Source code and outputs are UTF-8
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /W4") # Enable all warnings
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /GS-") # No buffer checks (we make games!)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /FS") # PDBs can be written from multiple processes

    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /MD") # DLL runtime
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /O2") # Optimize for speed
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Gy") # Function-level linking
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /GL") # Whole program optimization
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Gw") # Optimize data across units

    set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} /MD") # DLL runtime
    set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} /O2") # Optimize for speed
    set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} /Gy") # Function-level linking
    set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} /GL") # Whole program optimization
    set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} /Gw") # Optimize data across units

    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /MDd") # Debug runtime
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Od") # No optimization
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Zi") # Debugging information

    set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} /MDd") # Debug runtime
    set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} /Od") # No optimization
    set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} /Zi") # Debugging information
endif()

# GCC flags (matched against GCC 7.3)
if(CMAKE_COMPILER_IS_GCC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14") # Target a specific, recent standard
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fvisibility=hidden") # Don't expose by default
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wpedantic") # Enable pedantic warnings
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall") # Enable all warnings
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-unknown-pragmas") # Don't warn about pragmas
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -shared-libgcc") # Use shared libgcc

    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fvisibility=hidden") # Don't expose by default
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wpedantic") # Enable pedantic warnings
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall") # Enable all warnings
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wno-unknown-pragmas") # Don't warn about pragmas
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -shared-libgcc") # Use shared libgcc

    #set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3") # Optimize for speed
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -flto") # Link-time optimization

    set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -flto") # Link-time optimization

    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -Og") # Optimize for debugging
    #set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g") # Generate debug information

    set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -Og") # Optimize for debugging
endif()

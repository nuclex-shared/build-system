#!/usr/bin/cmake
cmake_minimum_required (VERSION 3.8)

# ----------------------------------------------------------------------------------------------- #

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

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
#
# Visual C++ flags (matched against Visual C++ 2017)
if(CMAKE_COMPILER_IS_MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /EHsc") # Enable only C++ exceptions
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /GF") # String pooling in debug and release
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /utf-8") # Source code and outputs are UTF-8
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /std:c++17") # Target a specific, recent standard
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

# GCC flags (matched against GCC 9.3)
if(CMAKE_COMPILER_IS_GCC || CMAKE_COMPILER_IS_CLANG)

    # C language and build settings
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fvisibility=hidden") # Don't expose by default
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -shared-libgcc") # Use shared libgcc
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -pic") # Use position-independent code
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fmerge-all-constants") # Data deduplication

    # C math routine behavior
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -funsafe-math-optimizations") # Allow optimizations
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fno-trapping-math") # Don't detect 0-div / overflow
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fno-signaling-nans") # NaN never causes exceptions
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fno-errno-math") # Don't set errno for math calls
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fno-rounding-math") # Blindly assume round-to-nearest
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -freciprocal-math") # Allow x/y to become x * (1/y)

    # C compiler warnings
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall") # Enable all warnings
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wextra") # Enable even more warnings
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wpedantic") # Enable standard deviation warnings
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wno-unknown-pragmas") # Don't warn about pragmas

    # C++ language and build settings
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17") # Target a specific, recent standard
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fvisibility=hidden") # Don't expose by default
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -shared-libgcc") # Use shared libgcc
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pic") # Use position-independent code
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fmerge-all-constants") # Data deduplication
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fvisibility-inlines-hidden") # Inline code is hidden

    # C++ math routine behavior
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -funsafe-math-optimizations") # Allow optimizations
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-trapping-math") # Don't detect 0-div / overflow
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-signaling-nans") # NaN never causes exceptions
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-errno-math") # Don't set errno for math calls
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rounding-math") # Blindly assume round-to-nearest
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -freciprocal-math") # Allow x/y to become x * (1/y)

    # C++ compiler warnings
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall") # Enable all warnings
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wextra") # Enable even more warnings
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wpedantic") # Enable standard deviation warnings
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-unknown-pragmas") # Don't warn about pragmas

    # Optimization flags for release builds
    set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -O3") # Optimize for speed
    set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -flto") # Link-time optimization
    set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -fno-stack-protector") # Unprotected

    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3") # Optimize for speed
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -flto") # Link-time optimization
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -fno-stack-protector") # Unprotected

    # Debugger flags for debug builds
    set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -g3") # Generate debug information
    set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -ggdb") # Target the GDB debugger
    #set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -Og") # Optimize for debug (nope!)
    #set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -fbounds-checking") # Array bounds check

    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g3") # Generate debug information
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -ggdb") # Target the GDB debugger
    #set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -Og") # Optimize for debug (nope!)
    #set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fbounds-checking") # Array bounds check

endif()


#        if 'arm' in platform.uname()[4].lower():
#            environment.Append(CXXFLAGS='-march=armv8-a+crc+simd') # Target Raspberry PI 3 CPU
#            environment.Append(CXXFLAGS='-mtune=cortex-a53') # Raspberry PI 3 CPU
#            environment.Append(CXXFLAGS='-mfpu=crypto-neon-fp-armv8') # Raspberry PI 3 CPU
#        else:
#            environment.Append(CXXFLAGS='-march=nocona') # Target CPUs from 2003 and later
#            #environment.Append(CXXFLAGS='-march=bdver1') # Target CPUs from 2011 and later
#            environment.Append(CXXFLAGS='-mtune=generic') # Target CPUs from 2003 and later


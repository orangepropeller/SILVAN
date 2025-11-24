cmake_minimum_required(VERSION 3.10)
project(SILVAN)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Generate compile_commands.json for clangd/IntelliSense
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Find OpenMP
find_package(OpenMP REQUIRED)

# Include directories
include_directories(silvan/include)
include_directories("C:/mingw64/include")
include_directories("C:/mingw64/x86_64-w64-mingw32/include")

# Gather source files
file(GLOB SOURCES "silvan/src/*.cpp")

# Add the executable
add_executable(silvan silvan/main.cpp ${SOURCES})

# Link libraries (OpenMP and Math)
# Note: 'm' is the math library, often implicit on some systems but good to be explicit given previous Makefile
target_link_libraries(silvan PUBLIC OpenMP::OpenMP_CXX m)


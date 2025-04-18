cmake_minimum_required(VERSION 3.20)
project(tri_arbitrage LANGUAGES CXX)

# C++ settings
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Default to Release build for performance
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type (e.g. Debug, Release)" FORCE)
endif()

# Compiler-specific optimizations for low-latency
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  add_compile_options(
    -O3
    -march=native
    -funroll-loops
    -flto           # Link Time Optimization
    -fno-exceptions # Reduce overhead
    -fno-rtti       # If not using RTTI
  )
elseif(MSVC)
  add_compile_options(
    /O2
    /GL  # Whole program optimization
  )
  # Enable LTO on MSVC
  include(CheckIPOSupported)
  check_ipo_supported(RESULT _ipo_supported OUTPUT _ipo_error)
  if(_ipo_supported)
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
  endif()
endif()

# Project-wide options
option(BUILD_TESTS "Build unit and integration tests" ON)
enable_testing()

# Locate external dependencies
find_package(Threads REQUIRED)
find_package(ZeroMQ REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(QuickFIX REQUIRED)
find_package(cpprestsdk REQUIRED)

# WebSocket++ via pkg-config
find_package(PkgConfig REQUIRED)
pkg_check_modules(WEBSOCKETPP REQUIRED websocketpp)

# Include directories for all modules
include_directories(
  ${CMAKE_SOURCE_DIR}/include
  ${ZeroMQ_INCLUDE_DIRS}
  ${OPENSSL_INCLUDE_DIR}
  ${QuickFIX_INCLUDE_DIRS}
  ${CPPRESTSDK_INCLUDE_DIRS}
  ${WEBSOCKETPP_INCLUDE_DIRS}
)

# Subdirectories for modular components
add_subdirectory(signal_generation)
add_subdirectory(execution)
add_subdirectory(risk_management)
add_subdirectory(stat_arbitrage)
add_subdirectory(market_data_adapter)

# Main application target
add_executable(tri_arbitrage_app src/main.cpp)
target_link_libraries(tri_arbitrage_app PRIVATE
  signal_generation
  execution
  risk_management
  stat_arbitrage
  market_data_adapter
  ${ZeroMQ_LIBRARIES}
  OpenSSL::SSL
  OpenSSL::Crypto
  QuickFIX::quickfix
  cpprestsdk::cpprest
  PkgConfig::WEBSOCKETPP
  Threads::Threads
)

target_include_directories(tri_arbitrage_app PRIVATE include)

# Installation rules
install(TARGETS tri_arbitrage_app
        RUNTIME DESTINATION bin)

# Testing
if(BUILD_TESTS)
  add_subdirectory(tests)
endif()

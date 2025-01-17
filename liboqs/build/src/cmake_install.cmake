# Install script for directory: /workspaces/Kyber-API/liboqs/src

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/workspaces/Kyber-API/liboqs/build/src/common/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/workspaces/Kyber-API/liboqs/build/src/kem/bike/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/workspaces/Kyber-API/liboqs/build/src/kem/frodokem/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/workspaces/Kyber-API/liboqs/build/src/kem/ntruprime/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/workspaces/Kyber-API/liboqs/build/src/kem/classic_mceliece/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/workspaces/Kyber-API/liboqs/build/src/kem/hqc/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/workspaces/Kyber-API/liboqs/build/src/kem/kyber/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/workspaces/Kyber-API/liboqs/build/src/kem/ml_kem/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/workspaces/Kyber-API/liboqs/build/src/sig/dilithium/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/workspaces/Kyber-API/liboqs/build/src/sig/ml_dsa/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/workspaces/Kyber-API/liboqs/build/src/sig/falcon/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/workspaces/Kyber-API/liboqs/build/src/sig/sphincs/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/workspaces/Kyber-API/liboqs/build/src/sig/mayo/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/workspaces/Kyber-API/liboqs/build/src/sig/cross/cmake_install.cmake")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/liboqs" TYPE FILE FILES
    "/workspaces/Kyber-API/liboqs/build/src/liboqsConfig.cmake"
    "/workspaces/Kyber-API/liboqs/build/src/liboqsConfigVersion.cmake"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig" TYPE FILE FILES "/workspaces/Kyber-API/liboqs/build/src/liboqs.pc")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "/workspaces/Kyber-API/liboqs/build/lib/liboqs.a")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/liboqs/liboqsTargets.cmake")
    file(DIFFERENT EXPORT_FILE_CHANGED FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/liboqs/liboqsTargets.cmake"
         "/workspaces/Kyber-API/liboqs/build/src/CMakeFiles/Export/lib/cmake/liboqs/liboqsTargets.cmake")
    if(EXPORT_FILE_CHANGED)
      file(GLOB OLD_CONFIG_FILES "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/liboqs/liboqsTargets-*.cmake")
      if(OLD_CONFIG_FILES)
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/liboqs/liboqsTargets.cmake\" will be replaced.  Removing files [${OLD_CONFIG_FILES}].")
        file(REMOVE ${OLD_CONFIG_FILES})
      endif()
    endif()
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/liboqs" TYPE FILE FILES "/workspaces/Kyber-API/liboqs/build/src/CMakeFiles/Export/lib/cmake/liboqs/liboqsTargets.cmake")
  if("${CMAKE_INSTALL_CONFIG_NAME}" MATCHES "^()$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/liboqs" TYPE FILE FILES "/workspaces/Kyber-API/liboqs/build/src/CMakeFiles/Export/lib/cmake/liboqs/liboqsTargets-noconfig.cmake")
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/oqs" TYPE FILE FILES
    "/workspaces/Kyber-API/liboqs/src/oqs.h"
    "/workspaces/Kyber-API/liboqs/src/common/aes/aes_ops.h"
    "/workspaces/Kyber-API/liboqs/src/common/common.h"
    "/workspaces/Kyber-API/liboqs/src/common/rand/rand.h"
    "/workspaces/Kyber-API/liboqs/src/common/sha2/sha2_ops.h"
    "/workspaces/Kyber-API/liboqs/src/common/sha3/sha3_ops.h"
    "/workspaces/Kyber-API/liboqs/src/common/sha3/sha3x4_ops.h"
    "/workspaces/Kyber-API/liboqs/src/kem/kem.h"
    "/workspaces/Kyber-API/liboqs/src/sig/sig.h"
    "/workspaces/Kyber-API/liboqs/src/sig_stfl/sig_stfl.h"
    "/workspaces/Kyber-API/liboqs/src/kem/bike/kem_bike.h"
    "/workspaces/Kyber-API/liboqs/src/kem/frodokem/kem_frodokem.h"
    "/workspaces/Kyber-API/liboqs/src/kem/ntruprime/kem_ntruprime.h"
    "/workspaces/Kyber-API/liboqs/src/kem/classic_mceliece/kem_classic_mceliece.h"
    "/workspaces/Kyber-API/liboqs/src/kem/hqc/kem_hqc.h"
    "/workspaces/Kyber-API/liboqs/src/kem/kyber/kem_kyber.h"
    "/workspaces/Kyber-API/liboqs/src/kem/ml_kem/kem_ml_kem.h"
    "/workspaces/Kyber-API/liboqs/src/sig/dilithium/sig_dilithium.h"
    "/workspaces/Kyber-API/liboqs/src/sig/ml_dsa/sig_ml_dsa.h"
    "/workspaces/Kyber-API/liboqs/src/sig/falcon/sig_falcon.h"
    "/workspaces/Kyber-API/liboqs/src/sig/sphincs/sig_sphincs.h"
    "/workspaces/Kyber-API/liboqs/src/sig/mayo/sig_mayo.h"
    "/workspaces/Kyber-API/liboqs/src/sig/cross/sig_cross.h"
    "/workspaces/Kyber-API/liboqs/build/include/oqs/oqsconfig.h"
    )
endif()


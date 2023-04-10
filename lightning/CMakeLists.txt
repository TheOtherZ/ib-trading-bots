cmake_minimum_required(VERSION 3.16)

project(lightningIB
    VERSION 1.0
    DESCRIPTION "IB API CPP"
    LANGUAGES CXX)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/build)

include_directories(cppclient/client/)

add_executable(main
    main.cpp
    IbAPI.cpp)

target_link_libraries(main ${PROJECT_SOURCE_DIR}/cppclient/client/libTwsSocketClient.so)


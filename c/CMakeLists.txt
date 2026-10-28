cmake_minimum_required(VERSION 3.16)
set(CMAKE_CXX_STANDARD 17)
project(QuartoAmes)

add_executable(QuartoAmes glad.c main.cpp geometry.cpp physics.cpp input_handler.cpp)

# Aponta para a pasta includes
target_include_directories(QuartoAmes PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/includes/GLFW)
target_include_directories(QuartoAmes PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/includes)

# Linka o GLFW e OpenGL
target_link_directories(QuartoAmes PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/includes/GLFW)
find_package(OpenGL REQUIRED)
target_link_libraries(QuartoAmes OpenGL::GL glfw3 gdi32)

# MAGIA NEGRA: Copia a pasta Shaders para a pasta onde o .exe é gerado
add_custom_command(TARGET QuartoAmes POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    ${CMAKE_CURRENT_SOURCE_DIR}/Shaders
    $<TARGET_FILE_DIR:QuartoAmes>/Shaders
)
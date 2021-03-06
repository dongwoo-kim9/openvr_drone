#!/bin/env python

# file hello_glfw.py

from openvr.glframework.glut_app import GlutApp
from openvr.gl_renderer import OpenVrGlRenderer
from openvr.color_cube_actor import ColorCubeActor

"""
Minimal glfw programming example which colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""


if __name__ == "__main__":
    actor = ColorCubeActor()
    renderer = OpenVrGlRenderer(actor)
    with GlutApp(renderer, b"glut OpenVR color cube") as glutApp:
        glutApp.run_loop()

from typing import Dict, Any

import triad_openvr
import matplotlib.pyplot as plt
import threading
import socket
import queue as q
import cv2
import openvr
from openvr import gl_renderer, color_cube_actor
from OpenGL.GL import *  # @UnusedWildImport # this comment squelches IDE warnings
from OpenGL.GLUT import *  # @UnusedWildImport
import numpy
import cam_render
from openvr.glframework.glfw_app import GlfwApp
from openvr.gl_renderer import OpenVrGlRenderer
import glfw


hardware_list = {"hmd": "hmd",
                 "C_L": "controller_L",
                 "C_R": "controller_R"}



class TrackingData:

    def __init__(self, device_name):
        self.device_name = device_name
        self.trigger = None
        self.v = triad_openvr.triad_openvr()


    def dictionary(self, data):
        track = {"device": self.device_name,
                 "yaw": data.yaw,
                 "pitch": data.pitch,
                 "roll": data.roll,
                 "trigger": self.trigger}
        return track

    def tracking(self):

        data = self.v.devices[self.device_name].sample()
        if self.device_name == "controller_L" or self.device_name == "controller_R":
            self.trigger = self.v.devices[self.device_name].controller_state_to_dict()["trigger"]
        else:
            self.trigger = None

        dictionary = self.dictionary(data)
        return dictionary

        # data_to_web: Any = self.trigger(dictionary)
        # return data_to_web


def camera_init(path):
    cpa = cv2.VideoCapture(path)
    (grabbed, frame) = cpa.read()
    return grabbed, frame


def image_render(actor):
    image = gl_renderer.OpenVrGlRenderer(actor=actor)


def make_cube():
    cube = color_cube_actor.ColorCubeActor()
    print("make_cube")
    image_render(cube)


if __name__ == "__main__":
    image = cv2.imread("./images/simple_xcoord_plot.png")
    print("image")
    renderer = cam_render.CamRenderer(image_l=image, image_r=image)
    with GlfwApp(renderer, "glfw OpenVR color cube") as glfwApp:
        glfwApp.run_loop()
        print("image")
# # hmd = TrackingData(device_name="hmd")
# # controller_L = TrackingData(device_name="controller_L")
# # controller_R = TrackingData(device_name="controller_R")
#     with PinkWorld() as pink_world:
#         glutMainLoop()
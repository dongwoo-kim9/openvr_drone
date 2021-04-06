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
from openvr.glframework.glfw_app import GlfwApp

hardware_list = {"hmd": "hmd",
                 "C_L": "controller_L",
                 "C_R": "controller_R"}

# OpenVR is the virtual reality API we are demonstrating here today


class OpenVrGlRenderer(list):
    "Renders to virtual reality headset using OpenVR and OpenGL APIs"

    def __init__(self, actor=None, window_size=(800, 600), multisample=0, left=False, right=False, zNear = 0.2, zFar = 500.0):
        self.vr_system = None
        self.left = left
        self.right = right
        if self.left:
            self.eye = openvr.Eye_Left
        if self.right:
            self.eye = openvr.Eye_Right
        if self.left == False and self.right == False:
            raise Exception("Unable to detect eye display")
        self.zNear = zNear
        self.zFar = zFar

        self.fb = None
        self.window_size = window_size
        poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
        self.poses = poses_t()
        if actor is not None:
            try:
                len(actor)
                self.extend(actor)
            except TypeError:
                self.append(actor)
        self.do_mirror = False
        self.multisample = multisample
        self.compositor = None

    def init_gl(self):
        "allocate OpenGL resources"
        self.vr_system = openvr.init(openvr.VRApplication_Scene)
        w, h = self.vr_system.getRecommendedRenderTargetSize()
        self.fb = gl_renderer.OpenVrFramebuffer(w, h, multisample=self.multisample)
        # self.right_fb = gl_renderer.OpenVrFramebuffer(w, h, multisample=self.multisample)
        self.compositor = openvr.VRCompositor()
        if self.compositor is None:
            raise Exception("Unable to create compositor")
        self.fb.init_gl()
        # self.right_fb.init_gl()
        # Compute projection matrix
        # zNear = 0.2
        # zFar = 500.0
        self.projection = numpy.asarray(gl_renderer.matrixForOpenVrMatrix(self.vr_system.getProjectionMatrix(
           self.eye, self.zNear, self.zFar)))
        self.view = gl_renderer.matrixForOpenVrMatrix(
            self.vr_system.getEyeToHeadTransform(self.eye)).I  # head_X_eye in Kane notation
        # self.view_right = gl_renderer.matrixForOpenVrMatrix(
        #     self.vr_system.getEyeToHeadTransform(openvr.Eye_Right)).I  # head_X_eye in Kane notation
        for actor in self:
            actor.init_gl()

    def render_scene(self):
        if self.compositor is None:
            return
        self.compositor.waitGetPoses(self.poses, None)
        hmd_pose0 = self.poses[openvr.k_unTrackedDeviceIndex_Hmd]
        if not hmd_pose0.bPoseIsValid:
            return
        hmd_pose1 = hmd_pose0.mDeviceToAbsoluteTracking  # head_X_room in Kane notation
        hmd_pose = gl_renderer.matrixForOpenVrMatrix(hmd_pose1).I  # room_X_head in Kane notation
        # Use the pose to compute things
        modelview = hmd_pose
        mv = modelview * self.view  # room_X_eye(left) in Kane notation
        # mvr = modelview * self.view_right  # room_X_eye(right) in Kane notation
        # Repack the resulting matrices to have default stride, to avoid
        # problems with weird strides and OpenGL
        mv = numpy.asarray(numpy.matrix(mv, dtype=numpy.float32))
        # mvr = numpy.asarray(numpy.matrix(mvr, dtype=numpy.float32))
        # 1) On-screen render:
        if self.do_mirror:
            glViewport(0, 0, self.window_size[0], self.window_size[1])
            # Display left eye view to screen
            self.display_gl(mv, self.projection)
        # 2) VR render
        # Left eye view
        glBindFramebuffer(GL_FRAMEBUFFER, self.fb.fb)
        glViewport(0, 0, self.fb.width, self.fb.height)
        self.display_gl(mv, self.projection)
        self.fb.submit(self.eye)
        # self.compositor.submit(openvr.Eye_Left, self.left_fb.texture)
        # Right eye view
        # glBindFramebuffer(GL_FRAMEBUFFER, self.right_fb.fb)
        # self.display_gl(mvr, self.projection_right)
        # self.right_fb.submit(openvr.Eye_Right)
        # self.compositor.submit(openvr.Eye_Right, self.right_fb.texture)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def display_gl(self, modelview, projection):
        glClearColor(0.5, 0.5, 0.5, 0.0)  # gray background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for actor in self:
            actor.display_gl(modelview, projection)

    def dispose_gl(self):
        for actor in self:
            actor.dispose_gl()
        if self.vr_system is not None:
            openvr.shutdown()
            self.vr_system = None
        if self.fb is not None:
            self.fb.dispose_gl()
            # self.right_fb.dispose_gl()

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
    image = cv2.imread("./images/yonsei.jpg")
    image = list(image)
    renderer = gl_renderer.OpenVrGlRenderer(actor=image)
    with GlfwApp(renderer, "glfw OpenVR color cube") as glfwApp:
        glfwApp.run_loop()
# # hmd = TrackingData(device_name="hmd")
# # controller_L = TrackingData(device_name="controller_L")
# # controller_R = TrackingData(device_name="controller_R")
#     with PinkWorld() as pink_world:
#         glutMainLoop()
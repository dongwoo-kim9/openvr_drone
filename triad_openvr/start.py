from typing import Dict, Any

import triad_openvr
import matplotlib.pyplot as plt
import threading
import socket
import queue as q
import msgpack
import argparse
import cv2
import openvr


hardware_list = {"hmd": "hmd",
                 "C_L": "controller_L",
                 "C_R": "controller_R"}


class TrackingData:

    def __init__(self, device_name):
        self.device_name = device_name
        self.trigger = None
        self.v = triad_openvr.triad_openvr()

    def packaging(self, dict):
        packed = msgpack.pack(dict)
        return packed

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


class Image:

    def __init__(self, path):
        self.path = path
        self.vr = openvr.init(openvr.VRApplication_Scene)


    def camera(self):
        cap = cv2.VideoCapture(self.path)
        (grabbed, frame) = cap.read()
        return grabbed, frame

    def Gl_input(self):




if __name__ == "main":
    parser = argparse.ArgumentParser(description="Tracking device")
    hmd = TrackingData(device_name="hmd")
    dict = hmd.tracking()
    controller_L = TrackingData(device_name="controller_L")
    controller_R = TrackingData(device_name="controller_R")

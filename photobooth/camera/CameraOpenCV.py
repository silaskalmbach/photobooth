#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Photobooth - a flexible photo booth software
# Copyright (C) 2018  Balthasar Reuter <photobooth at re - web dot eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging

from PIL import Image

import cv2

from .CameraInterface import CameraInterface


class CameraOpenCV(CameraInterface):

    def __init__(self):

        super().__init__()

        self.hasPreview = True
        self.hasIdle = True

        logging.info('Using OpenCV')

        # Find available cameras
        self._camera_index = self._find_camera()
        logging.info(f'Found camera at index: {self._camera_index}')

        self._cap = cv2.VideoCapture()

    def _find_camera(self, max_cameras=10):
        """Find first available camera index."""
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
            if cap.isOpened():
                logging.info(f'Camera found at index {i}')
                cap.release()
                return i
        logging.error('No cameras found!')
        return 0  # Fallback to default

    def setActive(self):

        if not self._cap.isOpened():
            # Use V4L2 backend explicitly for Linux
            self._cap.open(self._camera_index, cv2.CAP_V4L2)
            if not self._cap.isOpened():
                logging.error(f'Failed to open camera {self._camera_index} with V4L2')
                raise RuntimeError('Camera could not be opened')

            # Set camera properties for better compatibility
            self._cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            logging.info(f'Camera {self._camera_index} opened successfully')

    def setIdle(self):

        if self._cap.isOpened():
            self._cap.release()

    def getPreview(self):

        return self.getPicture()

    def getPicture(self):

        self.setActive()
        status, frame = self._cap.read()
        if not status:
            raise RuntimeError('Failed to capture picture')

        # OpenCV yields frames in BGR format, conversion to RGB necessary.
        # (See https://stackoverflow.com/a/32270308)
        return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

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

import time
import io
import logging

import gphoto2 as gp
from PIL import Image

from .CameraInterface import CameraInterface
from ..StateMachine import RetryEvent  # NEU
from ..Threading import Workers  # NEU


class CameraGphoto2(CameraInterface):

    def __init__(self):

        super().__init__()

        self.hasPreview = True
        self.hasIdle = True

        logging.info('Using python-gphoto2 bindings')

        self._comm = None  # NEU: Wird später gesetzt
        self._setupLogging()
        self._setupCamera()

    # NEU: Methode zum Setzen des Communicators
    def set_communicator(self, comm):
        self._comm = comm

    def cleanup(self):

        self._changeConfig('Shutdown')
        self._cap.exit(self._ctxt)

    def _setupLogging(self):

        gp.error_severity[gp.GP_ERROR] = logging.ERROR
        gp.check_result(gp.use_python_logging())

    def _setupCamera(self):

        self._ctxt = gp.Context()
        self._cap = gp.Camera()
        self._cap.init(self._ctxt)

        logging.info('Camera summary: %s',
                     str(self._cap.get_summary(self._ctxt)))

        # read model specific configuration
        config = self._cap.get_config()
        self.loadConfig(config.get_child_by_name('cameramodel').get_value())

        # set startup configuration
        self._changeConfig('Startup')

        #  print current config
        self._printConfig(self._cap.get_config())

    @staticmethod
    def _configTreeToText(tree, indent=0):

        config_txt = ''

        for chld in tree.get_children():
            config_txt += indent * ' '
            config_txt += chld.get_label() + ' [' + chld.get_name() + ']: '

            if chld.count_children() > 0:
                config_txt += '\n'
                config_txt += CameraGphoto2._configTreeToText(chld, indent + 4)
            else:
                config_txt += str(chld.get_value())
                try:
                    choice_txt = ' ('

                    for c in chld.get_choices():
                        choice_txt += c + ', '

                    choice_txt += ')'
                    config_txt += choice_txt
                except gp.GPhoto2Error:
                    pass
                config_txt += '\n'

        return config_txt

    @staticmethod
    def _printConfig(config):

        config_txt = 'Camera configuration:\n'
        config_txt += CameraGphoto2._configTreeToText(config)
        logging.info(config_txt)

    def _changeConfig(self, state):

        if self.config[state]:
            config = self._cap.get_config()

            for key in self.config[state]:
                val = config.get_child_by_name(key)
                if val.get_value().lower() != self.config[state][key].lower():
                    val.set_value(self.config[state][key])

            try:
                self._cap.set_config(config)
            except BaseException as e:
                logging.warn(('CameraGphoto2: Applying config for state '
                              '"{}" failed: {}').format(state, e))

    def setActive(self):

        self._changeConfig('Active')

    def setIdle(self):

        self._changeConfig('Idle')

    def getPreview(self):

        camera_file = self._cap.capture_preview()
        file_data = camera_file.get_data_and_size()
        return Image.open(io.BytesIO(file_data))

    # def getPicture(self):

    #     file_path = self._cap.capture(gp.GP_CAPTURE_IMAGE)
    #     camera_file = self._cap.file_get(file_path.folder, file_path.name,
    #                                      gp.GP_FILE_TYPE_NORMAL)
    #     file_data = camera_file.get_data_and_size()
    #     return Image.open(io.BytesIO(file_data))


    # def getPicture(self):
    #     try:
    #         # Versuche normale Aufnahme mit Autofokus
    #         file_path = self._cap.capture(gp.GP_CAPTURE_IMAGE)
            
    #     except gp.GPhoto2Error as e:
    #         logging.warning(f'Initial capture failed: {e}')
            
    #         # Warte länger für busy camera
    #         time.sleep(2.0)
            
    #         # Zweiter Versuch ohne Config-Änderung
    #         try:
    #             logging.info('Retry capture without config change')
    #             file_path = self._cap.capture(gp.GP_CAPTURE_IMAGE)
                
    #         except gp.GPhoto2Error as e2:
    #             logging.warning(f'Second capture failed: {e2}')
                
    #             # Jetzt versuche mit Manual Focus
    #             time.sleep(1.0)
                
    #             try:
    #                 config = self._cap.get_config()
    #                 focus_mode = config.get_child_by_name('focusmode')
                    
    #                 logging.info('Setting Manual focus mode')
    #                 focus_mode.set_value('Manual')
    #                 self._cap.set_config(config)
                    
    #                 time.sleep(1.0)
                    
    #                 # Letzter Versuch
    #                 logging.info('Final capture attempt in Manual mode')
    #                 file_path = self._cap.capture(gp.GP_CAPTURE_IMAGE)
                    
    #             except gp.GPhoto2Error as e3:
    #                 logging.error(f'All capture attempts failed: {e3}')
    #                 raise
        
    #     # Lade Bild und gebe es zurück
    #     camera_file = self._cap.file_get(file_path.folder, file_path.name,
    #                                     gp.GP_FILE_TYPE_NORMAL)
    #     file_data = camera_file.get_data_and_size()
    #     return Image.open(io.BytesIO(file_data))


    def getPicture(self):
        max_retries = 10
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                # Bei Retry: Sende Benachrichtigung
                if attempt > 0:
                    message = f'⚠️ Fokussierung fehlgeschlagen \n Versuch {attempt + 1}/{max_retries}'
                    
                    if self._comm:
                        retry_event = RetryEvent(message, attempt + 1, max_retries)
                        self._comm.send(Workers.MASTER, retry_event)
                        logging.warning(message)
                    else:
                        logging.warning(f'{message} (no communicator available)')
                
                # Versuche Bildaufnahme
                logging.info(f'Capture attempt {attempt + 1}/{max_retries}')
                file_path = self._cap.capture(gp.GP_CAPTURE_IMAGE)
                
                # Erfolg!
                if attempt > 0:
                    logging.info('✓ Capture successful after retry')
                break
                
            except gp.GPhoto2Error as e:
                logging.warning(f'Capture attempt {attempt + 1} failed: {e}')
                
                if attempt < max_retries - 1:
                    # Warte vor nächstem Versuch
                    logging.info(f'Waiting {retry_delay}s before retry...')
                    time.sleep(retry_delay)
                    
                    # Versuche Kamera zu "wecken"
                    try:
                        self._cap.capture_preview()
                        logging.debug('Camera: Preview capture successful, camera ready')
                    except gp.GPhoto2Error as preview_error:
                        logging.debug(f'Camera: Preview failed: {preview_error}')
                else:
                    # Alle Versuche fehlgeschlagen
                    logging.error('All capture attempts failed')
                    raise
        
        # Lade Bild und gebe es zurück
        camera_file = self._cap.file_get(file_path.folder, file_path.name,
                                         gp.GP_FILE_TYPE_NORMAL)
        file_data = camera_file.get_data_and_size()
        return Image.open(io.BytesIO(file_data))
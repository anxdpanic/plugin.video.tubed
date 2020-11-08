# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import threading

import pyxbmct.addonwindow as pyxbmct  # pylint: disable=import-error
import xbmc  # pylint: disable=import-error

from ..constants import CREDENTIALS
from ..constants.demo import SIGN_IN_CODES
from ..constants.media import LOGO_SMALL
from ..lib.txt_fmt import bold
from .common import AddonFullWindow

ACTION_STOP = 13


class SignInDialog(AddonFullWindow):

    def __init__(self, context, window, **kwargs):
        self._context = context
        self.window = window

        self.demo = kwargs.get('mode') == 'demo'

        self.title = context.i18n('Sign In')

        super().__init__(self.title)
        self.logo = None
        self.name_label = None

        self.device_code = ''
        self.user_code = ''
        self.verification_url = 'google.com/device'
        self.interval = 5

        self.instructions = None
        self.user_code_label = None
        self.client_id = None

        self.thread = None

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

    def start(self):
        if self.demo:
            data = SIGN_IN_CODES
        else:
            data = self.context.api.request_codes()

        self.device_code = data['device_code']
        self.user_code = data['user_code']

        self.verification_url = \
            data.get('verification_url', 'google.com/device').lstrip('https://www.')
        self.interval = data.get('interval', 5)

        xbmc.executebuiltin('Dialog.Close(all,true)')

        self.setGeometry(680, 300, 30, 68)

        self.set_controls()

        self.set_navigation()

        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
        self.connect(ACTION_STOP, self.close)

        self.thread = DialogThread(self.context, self.device_code,
                                   self.interval, self.close, self.demo)

        self.doModal()

        self.thread.stop()
        self.thread.join()

        return self.thread.signed_in

    def set_controls(self):
        # create instructions here so verification_url is updated
        self.instructions = pyxbmct.Label(
            self.context.i18n('Go to %s and enter the following code:') %
            bold(self.verification_url),
            font='font14',
            alignment=2
        )
        self.placeControl(self.instructions, 3, 2, columnspan=68)

        self.logo = pyxbmct.Image(LOGO_SMALL, aspectRatio=2)
        self.placeControl(self.logo, 9, 2, rowspan=12, columnspan=12)

        self.name_label = pyxbmct.Label(
            bold(self.context.addon.getAddonInfo('name')),
            font='font14',
            alignment=2
        )
        self.placeControl(self.name_label, 20, 2, columnspan=12, rowspan=4)

        # create instructions here so user_code is updated
        self.user_code_label = pyxbmct.Label(
            self.user_code,
            font='font_MainMenu',
            alignment=2
        )
        self.placeControl(self.user_code_label, 12, 2, columnspan=68, rowspan=10)

        self.client_id = pyxbmct.Label(
            self.context.i18n('Client ID: %s') %
            bold(str(CREDENTIALS.ID)),
            font='font10',
            alignment=2
        )
        self.placeControl(self.client_id, 27, 2, columnspan=68)

    def set_navigation(self):
        pass


class DialogThread(threading.Thread):
    def __init__(self, context, device_code, interval, close, demo=False):
        super().__init__()

        self._stopped = threading.Event()
        self._ended = threading.Event()

        self.context = context
        self.device_code = device_code
        self.interval = interval

        self.demo = demo

        self.monitor = xbmc.Monitor()

        self.signed_in = False
        self.close = close

        self.daemon = True
        self.start()

    def abort_now(self):
        return self.monitor.abortRequested() or self.stopped()

    def run(self):
        if self.demo:
            while True:
                if self.abort_now():
                    break

                xbmc.sleep(1000)

        else:
            interval = int(self.interval) * 1000
            if interval > 60000:
                interval = 5000

            steps = ((10 * 60 * 1000) // interval)  # 10 Minutes
            for _ in range(steps):
                # self.update_progress(int(float((100.0 // steps)) * index))

                signed_in = self.context.api.request_access_token(self.device_code)
                if signed_in:
                    self.signed_in = True
                    self.stop()

                if self.abort_now():
                    break

                xbmc.sleep(interval)

        self.close()

        self.end()

    def stop(self):
        self._stopped.set()

    def stopped(self):
        return self._stopped.is_set()

    def end(self):
        if not self._stopped.is_set():
            self._stopped.set()

        self._ended.set()

    def ended(self):
        return self._ended.is_set()

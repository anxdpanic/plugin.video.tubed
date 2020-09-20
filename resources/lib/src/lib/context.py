# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import sys

import xbmcaddon  # pylint: disable=import-error

from .settings import Settings


class Context:

    def __init__(self):
        self._argv = None
        self._mode = None
        self._query = {}

        self._api = None

        self._addon = None

        self._settings = None

    @property
    def argv(self):
        if self._argv is None:
            self._argv = sys.argv
        return self._argv

    @argv.setter
    def argv(self, value):
        self._argv = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    @property
    def api(self):
        return self._api

    @api.setter
    def api(self, value):
        self._api = value

    @property
    def addon(self):
        if not self._addon:
            self._addon = xbmcaddon.Addon()
        return self._addon

    @property
    def settings(self):
        if not self._settings:
            self._settings = Settings(self.addon)
        return self._settings

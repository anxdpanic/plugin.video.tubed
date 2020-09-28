# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmcaddon  # pylint: disable=import-error


class Settings:

    def __init__(self, addon=None):
        self._addon = addon
        self._shallow_cache = {}

    def get_bool(self, setting_id):
        return self._get(setting_id, 'bool')

    def set_bool(self, setting_id, setting_value):
        self._set(setting_id, setting_value, 'bool')

    def get_int(self, setting_id):
        return self._get(setting_id, 'int')

    def set_int(self, setting_id, setting_value):
        self._set(setting_id, setting_value, 'int')

    def get_string(self, setting_id):
        return self._get(setting_id, 'string')

    def set_string(self, setting_id, setting_value):
        self._set(setting_id, setting_value, 'string')

    def get_number(self, setting_id):
        return self._get(setting_id, 'number')

    def set_number(self, setting_id, setting_value):
        self._set(setting_id, setting_value, 'number')

    def get(self, setting_id):
        return self._get(setting_id)

    def set(self, setting_id, setting_value):
        self._set(setting_id, setting_value)

    @property
    def addon(self):
        if not self._addon:
            self._addon = xbmcaddon.Addon()
        return self._addon

    @property
    def shallow_cache(self):
        return self._shallow_cache

    def _get(self, setting_id, setting_type=None):
        if setting_id in self.shallow_cache:
            return self.shallow_cache[setting_id]

        if setting_type == 'bool':
            payload = self.addon.getSettingBool(setting_id)

        elif setting_type == 'int':
            payload = self.addon.getSettingInt(setting_id)

        elif setting_type == 'string':
            payload = self.addon.getSettingString(setting_id)

        elif setting_type == 'number':
            payload = self.addon.getSettingNumber(setting_id)

        else:
            payload = self.addon.getSetting(setting_id)

        self.shallow_cache[setting_id] = payload
        return payload

    def _set(self, setting_id, setting_value, setting_type=None):
        self.shallow_cache[setting_id] = setting_value

        if setting_type == 'bool':
            self.addon.setSettingBool(setting_id, setting_value)
            return

        if setting_type == 'int':
            self.addon.setSettingInt(setting_id, setting_value)
            return

        if setting_type == 'string':
            self.addon.setSettingString(setting_id, setting_value)
            return

        if setting_type == 'number':
            self.addon.setSettingNumber(setting_id, setting_value)
            return

        self.addon.setSetting(setting_id, setting_value)
        return

    @property
    def video_quality(self):
        _map = {
            0: 240,
            1: 360,
            2: 480,
            3: 720,
            4: 1080,
            5: 1440,
            6: 2160,
            7: 4320,
            8: 'mp4',
            9: 'webm'
        }

        return _map.get(self.get_int('quality'), 4)

    @property
    def limit_to_30fps(self):
        return self.get_bool('limit30')

    @property
    def hdr(self):
        return self.get_bool('hdr')

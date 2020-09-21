# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmc  # pylint: disable=import-error
import xbmcaddon  # pylint: disable=import-error

from ..constants import STRINGS


class Translator:

    def __init__(self, addon=None):
        self._addon = addon

    def i18n(self, string_id):
        string_id = STRINGS.get(string_id) or string_id

        try:
            if int(string_id) < 30000:
                return xbmc.getLocalizedString(string_id)

        except ValueError:
            return string_id

        finally:
            return self.addon.getLocalizedString(string_id)  # pylint: disable=lost-exception

    @property
    def addon(self):
        if not self._addon:
            self._addon = xbmcaddon.Addon()
        return self._addon

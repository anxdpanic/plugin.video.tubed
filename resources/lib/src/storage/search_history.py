# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmcvfs  # pylint: disable=import-error

from ..constants import ADDON_ID
from ..lib.sql_storage import Storage


class SearchHistory(Storage):
    def __init__(self):
        filename = xbmcvfs.translatePath(
            'special://profile/addon_data/%s/search/search_history.sqlite' % ADDON_ID
        )

        super().__init__(filename, max_item_count=100)

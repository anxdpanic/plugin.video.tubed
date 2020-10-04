# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmcvfs  # pylint: disable=import-error

from ..constants import ADDON_ID
from ..lib.cache import Cache
from ..lib.context import Context


class DataCache(Cache):
    def __init__(self, context=None):
        filename = xbmcvfs.translatePath(
            'special://profile/addon_data/%s/data/cache.sqlite' % ADDON_ID
        )

        if not context:
            context = Context()

        super().__init__(filename, max_file_size_mb=context.settings.data_cache_limit)

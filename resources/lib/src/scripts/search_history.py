# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from urllib.parse import unquote

import xbmc  # pylint: disable=import-error

from ..storage.search_history import SearchHistory


def invoke(context, action, item=''):  # pylint: disable=unused-argument
    history = SearchHistory()

    if action == 'clear':
        history.clear()

    elif action == 'remove':
        if not item:
            return

        if '%' in item:
            try:
                item = unquote(item)
            except:  # pylint: disable=bare-except
                pass

        history.remove(item)

    xbmc.executebuiltin('Container.Refresh')

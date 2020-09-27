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


def invoke(context):
    history = SearchHistory()

    action = context.query.get('action', '')
    if not action:
        return

    if action == 'clear':
        history.clear()

    elif action == 'remove':
        query = context.query.get('item', '')
        if not query:
            return

        if '%' in query:
            try:
                query = unquote(query)
            except:  # pylint: disable=bare-except
                pass

        history.remove(query)

    xbmc.executebuiltin('Container.Refresh')

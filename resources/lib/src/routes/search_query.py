# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from urllib.parse import quote
from urllib.parse import unquote

import xbmc  # pylint: disable=import-error
import xbmcplugin  # pylint: disable=import-error

from ..constants import MODES
from ..generators.video import video_generator
from ..lib.items.next_page import NextPage
from ..lib.url_utils import create_addon_path
from ..storage.search_cache import SearchCache
from ..storage.search_history import SearchHistory

SEARCH_CACHE = SearchCache()
SEARCH_HISTORY = SearchHistory()


def invoke(context, query='', page_token=''):
    if (not query and
            'mode=%s' % str(MODES.SEARCH_QUERY) in xbmc.getInfoLabel('Container.FolderPath')):
        query = SEARCH_CACHE.item

    if query and '%' in query:
        query = unquote(query)

    if not query:
        keyboard = xbmc.Keyboard()
        keyboard.setHeading(context.i18n('Enter your search term'))
        keyboard.doModal()
        if keyboard.isConfirmed():
            query = keyboard.getText()
            query = query.strip()

    if not query:
        xbmcplugin.endOfDirectory(context.handle, False)
        return

    xbmcplugin.setContent(context.handle, 'videos')
    payload = context.api.search(query=query, page_token=page_token)
    list_items = list(video_generator(payload.get('items', [])))

    quoted_query = quote(query)

    page_token = payload.get('nextPageToken')
    if page_token:
        directory = NextPage(
            label=context.i18n('Next Page'),
            path=create_addon_path({
                'mode': str(MODES.SEARCH_QUERY),
                'query': quoted_query,
                'page_token': page_token
            })
        )
        list_items.append(tuple(directory))

    if not list_items:
        xbmcplugin.endOfDirectory(context.handle, False)
        return

    SEARCH_CACHE.item = quoted_query
    SEARCH_HISTORY.update(query)

    xbmcplugin.addDirectoryItems(context.handle, list_items, len(list_items))

    xbmcplugin.endOfDirectory(context.handle, True)

# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from urllib.parse import quote

import xbmc  # pylint: disable=import-error
import xbmcplugin  # pylint: disable=import-error

from ..constants import MODES
from ..generators.channel import channel_generator
from ..generators.playlist import playlist_generator
from ..generators.video import video_generator
from ..items.next_page import NextPage
from ..items.search_query import SearchQuery
from ..lib.txt_fmt import bold
from ..lib.url_utils import create_addon_path
from ..lib.url_utils import unquote
from ..storage.search_cache import SearchCache
from ..storage.search_history import SearchHistory
from ..storage.users import UserStorage
from .utils import get_sort_order

DEFAULT_ORDER = 'relevance'


def invoke(context, query='', page_token='', search_type='video', order='relevance'):
    if search_type not in ['video', 'channel', 'playlist']:
        return

    uuid = UserStorage().uuid
    search_cache = SearchCache(uuid)
    search_history = SearchHistory(uuid)

    if order == 'prompt':
        order = get_sort_order(context)
        order = order or DEFAULT_ORDER
        if order != DEFAULT_ORDER:
            page_token = ''

    if (not query and
            'mode=%s' % str(MODES.SEARCH_QUERY) in xbmc.getInfoLabel('Container.FolderPath')):
        query = search_cache.item

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

    list_items = []
    quoted_query = quote(query)

    if not page_token and search_type == 'video':

        directory = SearchQuery(
            label=bold(context.i18n('Channels')),
            path=create_addon_path(parameters={
                'mode': str(MODES.SEARCH_QUERY),
                'query': quoted_query,
                'search_type': 'channel'
            })
        )

        list_items.append(tuple(directory))

        directory = SearchQuery(
            label=bold(context.i18n('Playlists')),
            path=create_addon_path(parameters={
                'mode': str(MODES.SEARCH_QUERY),
                'query': quoted_query,
                'search_type': 'playlist'
            })
        )

        list_items.append(tuple(directory))

    payload = context.api.search(query=query, page_token=page_token, search_type=search_type)

    addon_query = {
        'mode': str(MODES.SEARCH_QUERY),
        'query': quoted_query,
        'search_type': search_type
    }

    if search_type == 'video':
        xbmcplugin.setContent(context.handle, 'videos')
        list_items += list(video_generator(context, payload.get('items', [])))
        del addon_query['search_type']

    elif search_type == 'channel':
        list_items += list(channel_generator(context, payload.get('items', [])))

    elif search_type == 'playlist':
        list_items += list(playlist_generator(context, payload.get('items', [])))

    page_token = payload.get('nextPageToken')
    if page_token:
        if order != 'relevance':
            addon_query['order'] = order

        addon_query['page_token'] = page_token

        directory = NextPage(
            label=context.i18n('Next Page'),
            path=create_addon_path(addon_query)
        )
        list_items.append(tuple(directory))

    if not list_items:
        xbmcplugin.endOfDirectory(context.handle, False)
        return

    search_cache.item = quoted_query
    search_history.update(query)

    xbmcplugin.addDirectoryItems(context.handle, list_items, len(list_items))

    xbmcplugin.endOfDirectory(context.handle, True)

# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from urllib.parse import quote

import xbmcplugin  # pylint: disable=import-error

from ..constants import ADDON_ID
from ..constants import MODES
from ..items.directory import Directory
from ..items.search_query import SearchQuery
from ..lib.txt_fmt import bold
from ..lib.url_utils import create_addon_path
from ..storage.search_history import SearchHistory


def invoke(context):
    history = SearchHistory()

    items = []

    directory = SearchQuery(
        label=bold(context.i18n('New Search')),
        path=create_addon_path(parameters={
            'mode': str(MODES.SEARCH_QUERY)
        })
    )
    items.append(tuple(directory))

    for query in history.list():
        directory = Directory(
            label=query,
            path=create_addon_path(parameters={
                'mode': str(MODES.SEARCH_QUERY),
                'query': quote(query)
            })
        )

        context_menus = [
            (context.i18n('Remove...'),
             'RunScript(%s,mode=search_history&action=remove&item=%s)' % (ADDON_ID, quote(query))),

            (context.i18n('Clear history'),
             'RunScript(%s,mode=search_history&action=clear)' % ADDON_ID),
        ]

        directory.ListItem.addContextMenuItems(context_menus)
        items.append(tuple(directory))

    xbmcplugin.addDirectoryItems(context.handle, items, len(items))

    xbmcplugin.endOfDirectory(context.handle, True)

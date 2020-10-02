# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmcplugin  # pylint: disable=import-error

from ..constants import MODES
from ..generators.video import video_generator
from ..items.directory import Directory
from ..items.next_page import NextPage
from ..lib.url_utils import create_addon_path


def invoke(context, page_token='', event_type='live'):
    event_type = event_type.lower()
    if event_type not in ['live', 'completed', 'upcoming']:
        return

    xbmcplugin.setContent(context.handle, 'videos')

    list_items = []

    if not page_token and event_type == 'live':

        directory = Directory(
            label=context.i18n('Upcoming'),
            path=create_addon_path(parameters={
                'mode': str(MODES.LIVE),
                'event_type': 'upcoming'
            })
        )

        list_items.append(tuple(directory))

        directory = Directory(
            label=context.i18n('Completed'),
            path=create_addon_path(parameters={
                'mode': str(MODES.LIVE),
                'event_type': 'completed'
            })
        )

        list_items.append(tuple(directory))

    payload = context.api.live_events(event_type=event_type, page_token=page_token)
    list_items += list(video_generator(context, payload.get('items', [])))

    page_token = payload.get('nextPageToken')
    if page_token:
        directory = NextPage(
            label=context.i18n('Next Page'),
            path=create_addon_path({
                'mode': str(MODES.LIVE),
                'page_token': page_token,
                'event_type': event_type
            })
        )
        list_items.append(tuple(directory))

    xbmcplugin.addDirectoryItems(context.handle, list_items, len(list_items))

    xbmcplugin.endOfDirectory(context.handle, True)

# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmcplugin  # pylint: disable=import-error

from ..generators.video import video_generator


def invoke(context):
    xbmcplugin.setContent(context.handle, 'videos')

    payload = context.api.channel_by_username('mine')
    list_items = list(video_generator(payload.get('items', [])))

    xbmcplugin.addDirectoryItems(context.handle, list_items, len(list_items))

    xbmcplugin.endOfDirectory(context.handle, True)

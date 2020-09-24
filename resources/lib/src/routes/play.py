# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmcplugin  # pylint: disable=import-error

from ..lib.items.stream import Stream


def invoke(context, video_id):
    video = context.api.resolve(video_id=video_id)
    channel = video.get('channel', {})
    license_data = video.get('license', {})
    metadata = video.get('metadata', {})

    stream = Stream(
        label=metadata.get('title', ''),
        label2=channel.get('author', ''),
        path=video.get('url', ''),
        headers=video.get('headers', ''),
        license_key=license_data.get('proxy', '')
    )

    xbmcplugin.setResolvedUrl(context.handle, True, stream.ListItem)

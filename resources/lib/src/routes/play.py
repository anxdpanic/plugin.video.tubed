# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmcplugin  # pylint: disable=import-error

from ..items.stream import Stream


def invoke(context, video_id):
    quality = context.api.quality(
        context.settings.video_quality,
        limit_30fps=context.settings.limit_to_30fps,
        hdr=context.settings.hdr
    )

    video = context.api.resolve(video_id=video_id, quality=quality)
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

    # TODO: Subtitles requires choice logic
    # stream.ListItem.setSubtitles()

    xbmcplugin.setResolvedUrl(context.handle, True, stream.ListItem)

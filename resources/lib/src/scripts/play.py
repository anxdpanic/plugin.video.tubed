# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmc  # pylint: disable=import-error

from ..api.utils import choose_subtitles
from ..items.stream import Stream


def invoke(context, video_id, prompt_subtitles=False):
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

    subtitles = choose_subtitles(
        context,
        subtitles=metadata.get('subtitles', []),
        prompt_override=prompt_subtitles
    )
    stream.ListItem.setSubtitles(subtitles)

    xbmc.Player().play(item=stream.ListItem.getPath(), listitem=stream.ListItem)

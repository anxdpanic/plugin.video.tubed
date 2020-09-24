# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from html import unescape

from ..constants import MODES
from ..lib.items.video import Video
from ..lib.url_utils import create_addon_path


def video_generator(items):
    for item in items:
        video_id = item.get('id', '')
        if isinstance(video_id, dict):
            video_id = video_id.get('videoId', '')

        snippet = item.get('snippet', {})

        payload = Video(
            label=unescape(snippet.get('title', '')),
            label2=unescape(snippet.get('channelTitle', '')),
            path=create_addon_path({
                'mode': str(MODES.PLAY),
                'video_id': video_id
            })
        )

        info_labels = {
            'mediatype': 'video',
            'plot': unescape(snippet.get('description', '')),
            'plotoutline': unescape(snippet.get('description', '')),
            'originaltitle': unescape(snippet.get('title', '')),
            'sorttitle': unescape(snippet.get('title', '')),
            'studio': unescape(snippet.get('channelTitle', ''))
        }
        payload.ListItem.setInfo('video', info_labels)

        thumbnails = snippet.get('thumbnails', {})
        thumbnail = thumbnails.get('standard', thumbnails.get('high', {}))
        if not thumbnail:
            thumbnail = thumbnails.get('medium', thumbnails.get('default', {}))
        thumbnail = thumbnail.get('url', '')

        payload.ListItem.setArt({
            'icon': thumbnail,
            'thumb': thumbnail,
        })

        yield tuple(payload)

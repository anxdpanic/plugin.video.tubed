# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from ..constants import MODES
from ..lib.items.video import Video
from ..lib.url_utils import create_addon_path


def video_generator(items):
    for item in items:
        video_id = item.get('id', '')
        snippet = item.get('snippet', {})

        payload = Video(
            label=snippet.get('title', ''),
            label2=snippet.get('channelTitle', ''),
            path=create_addon_path({
                'mode': str(MODES.PLAY),
                'video_id': video_id
            })
        )

        info_labels = {
            'mediatype': 'video',
            'plot': snippet.get('description', ''),
            'plotoutline': snippet.get('description', ''),
            'originaltitle': snippet.get('title', ''),
            'sorttitle': snippet.get('title', ''),
            'studio': snippet.get('channelTitle', '')
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

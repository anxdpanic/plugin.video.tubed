# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmcgui  # pylint: disable=import-error
import xbmcplugin  # pylint: disable=import-error

from ..constants import SUBTITLE_LANGUAGE
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

    subtitles = choose_subtitles(context, subtitles=metadata.get('subtitles', []))
    stream.ListItem.setSubtitles(subtitles)

    xbmcplugin.setResolvedUrl(context.handle, True, stream.ListItem)


def find_subtitle(subtitles, language, include_asr=True):
    for language_code, _, kind, subtitle_url in subtitles:
        if not include_asr and kind == 'asr':
            continue

        if language_code == language:
            return subtitle_url

    return None


def choose_subtitles(context, subtitles):
    if not subtitles:
        return []

    youtube_language = context.settings.language
    subtitle_language = context.settings.subtitle_language

    payload = []

    if subtitle_language == SUBTITLE_LANGUAGE.NONE:
        return []

    if subtitle_language == SUBTITLE_LANGUAGE.PROMPT:
        selection = [subtitle[1] for subtitle in subtitles]

        result = xbmcgui.Dialog().select(context.i18n('Subtitle language'), selection)
        if result == -1:
            return []

        payload.append(subtitles[result][3])

    elif subtitle_language == SUBTITLE_LANGUAGE.CURRENT_W_FALLBACK:

        payload.append(find_subtitle(subtitles, youtube_language))
        if '-' in youtube_language:
            payload.append(find_subtitle(subtitles, youtube_language.split('-')[0]))
        payload.append(find_subtitle(subtitles, 'en'))
        payload.append(find_subtitle(subtitles, 'en-US'))
        payload.append(find_subtitle(subtitles, 'en-GB'))

    elif subtitle_language == SUBTITLE_LANGUAGE.CURRENT:
        payload.append(find_subtitle(subtitles, youtube_language))
        if '-' in youtube_language:
            payload.append(find_subtitle(subtitles, youtube_language.split('-')[0]))

    elif subtitle_language == SUBTITLE_LANGUAGE.CURRENT_WO_ASR:
        payload.append(find_subtitle(subtitles, youtube_language, include_asr=False))
        if '-' in youtube_language:
            payload.append(
                find_subtitle(subtitles, youtube_language.split('-')[0], include_asr=False)
            )

    return list(set(subtitle for subtitle in payload if subtitle))

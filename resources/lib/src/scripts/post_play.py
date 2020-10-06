# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from html import unescape

from ..generators.data_cache import get_cached
from ..lib.memoizer import reset_cache
from .utils import rate


def invoke(context, video_id):
    if not post_play(context):
        return

    try:
        video = get_cached(context, context.api.videos, [video_id]).get(video_id, {})
    except:  # pylint: disable=bare-except
        video = {}

    video_title = unescape(video.get('snippet', {}).get('title', ''))

    if context.settings.post_play_rate:
        rate(context, video_id, video_title)

    reset_cache()


def post_play(context):
    if context.settings.post_play_rate:
        return True

    return False

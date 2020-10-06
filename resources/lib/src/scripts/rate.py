# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmc  # pylint: disable=import-error

from ..lib.memoizer import reset_cache
from ..lib.url_utils import unquote
from .utils import rate


def invoke(context, video_id, video_title=''):
    if '%' in video_title:
        video_title = unquote(video_title)

    rate(context, video_id, video_title)

    reset_cache()
    xbmc.executebuiltin('Container.Refresh')

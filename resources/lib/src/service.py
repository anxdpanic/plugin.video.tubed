# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error

from .lib.context import Context
from .lib.memoizer import reset_cache
from .lib.playback import CallbackPlayer


def invoke():
    reset_cache()

    sleep_time = 10

    context = Context()
    window = xbmcgui.Window(10000)
    player = CallbackPlayer(context=context, window=window)
    monitor = xbmc.Monitor()

    while not monitor.abortRequested():
        if monitor.waitForAbort(sleep_time):
            break

    player.cleanup_threads(only_ended=False)

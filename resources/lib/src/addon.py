# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from .api import API
from .constants import MODES
from .lib.context import Context
from .lib.routing import Router
from .lib.url_utils import parse_query

# pylint: disable=import-outside-toplevel

CONTEXT = Context()

router = Router()


@router.route(MODES.MAIN)
def _main_menu():
    from .routes import main_menu
    main_menu.invoke(CONTEXT)


@router.route(MODES.MOST_POPULAR, kwargs=['page_token'])
def _most_popular(page_token=''):
    from .routes import most_popular
    most_popular.invoke(CONTEXT, page_token=page_token)


@router.route(MODES.LIKED_VIDEOS, kwargs=['page_token'])
def _liked_videos(page_token=''):
    from .routes import liked_videos
    liked_videos.invoke(CONTEXT, page_token=page_token)


@router.route(MODES.DISLIKED_VIDEOS, kwargs=['page_token'])
def _disliked_videos(page_token=''):
    from .routes import disliked_videos
    disliked_videos.invoke(CONTEXT, page_token=page_token)


@router.route(MODES.PLAY, args=['video_id'])
def _play(video_id):
    from .routes import play
    play.invoke(CONTEXT, video_id=video_id)


def invoke(argv):
    global CONTEXT  # pylint: disable=global-statement

    CONTEXT.argv = argv
    CONTEXT.handle = argv[1]
    CONTEXT.query = parse_query(argv[2])

    CONTEXT.api = API()

    router.invoke(CONTEXT.query)

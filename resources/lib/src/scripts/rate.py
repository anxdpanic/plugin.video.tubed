# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error

from ..lib.memoizer import reset_cache
from ..lib.url_utils import unquote


def invoke(context, video_id, video_title=''):
    if '%' in video_title:
        video_title = unquote(video_title)

    payload = context.api.rating(video_id)
    try:
        payload = payload.get('items', [{}])[0]
    except IndexError:
        return

    rating = payload.get('rating', 'none')

    choices = [
        context.i18n('I like this'),
        context.i18n('I dislike this'),
        context.i18n('Remove rating')
    ]

    choice_map = [
        'like',
        'dislike',
        'none'
    ]

    del choices[choice_map.index(rating)]
    del choice_map[choice_map.index(rating)]

    result = xbmcgui.Dialog().select(context.i18n('Rate'), choices)
    if result == -1:
        return

    rating = choice_map[result]

    payload = context.api.rate(video_id, rating)

    try:
        successful = int(payload.get('error', {}).get('code', 204)) == 204
    except ValueError:
        successful = False

    if successful:
        message = ''

        if video_title:
            if rating == 'none':
                message = context.i18n('Rating removed from %s') % video_title

            elif rating == 'like':
                message = context.i18n('Liked %s') % video_title

            elif rating == 'dislike':
                message = context.i18n('Disliked %s') % video_title

        else:
            if rating == 'none':
                message = context.i18n('Rating removed')

            elif rating == 'like':
                message = context.i18n('Liked')

            elif rating == 'dislike':
                message = context.i18n('Disliked')

        xbmcgui.Dialog().notification(
            context.addon.getAddonInfo('name'),
            message,
            context.addon.getAddonInfo('icon'),
            sound=False
        )

        reset_cache()
        xbmc.executebuiltin('Container.Refresh')

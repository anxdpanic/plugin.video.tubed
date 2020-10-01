# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from html import unescape

import xbmc  # pylint: disable=import-error
import xbmcgui  # pylint: disable=import-error

from ..lib.memoizer import reset_cache
from ..lib.url_utils import unquote


def invoke(context, action, video_id='', video_title='', playlist_id='',
           playlist_title='', playlistitem_id=''):
    if not required_arguments_check(action, video_id, playlist_id, playlistitem_id):
        return

    if '%' in video_title:
        video_title = unquote(video_title)

    if '%' in playlist_title:
        playlist_title = unquote(playlist_title)

    message = ''

    if action == 'add':
        result = add(context, video_id)
        if not result:
            return

        video_title, playlist_title = result
        message = context.i18n('Added %s to %s') % (video_title, playlist_title)

    elif action == 'delete':
        result = delete(context, playlist_id, playlist_title)
        if not result:
            return

        message = context.i18n('Playlist deleted')
        if playlist_title:
            message = context.i18n('%s playlist deleted') % playlist_title

    elif action == 'remove':
        result = remove(context, playlistitem_id)
        if not result:
            return

        message = context.i18n('Removed from playlist')
        if video_title:
            message = context.i18n('Removed %s from playlist') % video_title

    elif action == 'rename':
        result = rename(context, playlist_id)
        if not result:
            return

        message = context.i18n('Playlist renamed to %s') % result
        if playlist_title:
            message = context.i18n('%s renamed to %s') % (playlist_title, result)

    if message:
        xbmcgui.Dialog().notification(
            context.addon.getAddonInfo('name'),
            message,
            context.addon.getAddonInfo('icon'),
            sound=False
        )

        reset_cache()
        xbmc.executebuiltin('Container.Refresh')


def required_arguments_check(action, video_id, playlist_id, playlistitem_id):
    if action == 'add' and not video_id:
        return False

    if action == 'remove' and not playlistitem_id:
        return False

    if action == 'delete' and not playlist_id:
        return False

    return True


def add(context, video_id):
    payload = context.api.playlists_of_channel('mine')
    playlists = [(unescape(item['snippet'].get('title', '')), item['id'])
                 for item in payload['items']]

    if playlists:
        playlist_titles, playlist_ids = zip(*playlists)
    else:
        playlist_ids = []
        playlist_titles = []

    playlist_ids = ['new'] + list(playlist_ids)
    playlist_titles = [context.i18n('New playlist')] + list(playlist_titles)

    result = xbmcgui.Dialog().select(context.i18n('Add to playlist'), playlist_titles)
    if result == -1:
        return None

    playlist_id = playlist_ids[result]
    playlist_title = playlist_titles[result]

    if playlist_id == 'new':
        playlist_title = _get_title_from_user(context)
        if not playlist_title:
            return None

        payload = context.api.create_playlist(playlist_title)
        if payload.get('kind') != 'youtube#playlist':
            return None

        playlist_id = payload['id']
        playlist_title = unescape(payload['snippet'].get('title', ''))

    if not playlist_id:
        return None

    payload = context.api.add_to_playlist(playlist_id, video_id)
    if payload.get('kind') != 'youtube#playlistItem':
        return None

    video_title = unescape(payload['snippet'].get('title', ''))

    return video_title, playlist_title


def delete(context, playlist_id, playlist_title):
    message = context.i18n('You are about to delete a playlist, are you sure?')
    if playlist_title:
        message = context.i18n('You are about to delete %s, are you sure?') % playlist_title

    result = xbmcgui.Dialog().yesno(context.i18n('Delete playlist'), message)
    if not result:
        return False

    payload = context.api.remove_playlist(playlist_id)
    try:
        return int(payload.get('error', {}).get('code', 204)) == 204
    except ValueError:
        return False


def remove(context, playlistitem_id):
    payload = context.api.remove_from_playlist(playlistitem_id)
    try:
        return int(payload.get('error', {}).get('code', 204)) == 204
    except ValueError:
        return False


def rename(context, playlist_id):
    playlist_title = _get_title_from_user(context)
    if not playlist_title:
        return False

    payload = context.api.rename_playlist(playlist_id, playlist_title)
    try:
        success = int(payload.get('error', {}).get('code', 204)) == 204
    except ValueError:
        success = False

    if success:
        return playlist_title

    return False


def _get_title_from_user(context):
    keyboard = xbmc.Keyboard()
    keyboard.setHeading(context.i18n('Enter your playlist title'))
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return None

    playlist_title = keyboard.getText()
    playlist_title = playlist_title.strip()
    if not playlist_title:
        return None

    return playlist_title
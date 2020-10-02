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
from ..lib.txt_fmt import bold
from ..lib.txt_fmt import color
from ..storage.data_cache import DataCache
from ..storage.users import UserStorage

USERS = UserStorage()


def invoke(context):
    reference = []
    choices = []

    for user in USERS.users:
        reference.append(user)

        name = user['name']
        if user['uuid'] == USERS.uuid:
            name = bold(color(name, 'lightgreen'))

        choices.append(name)

    action_count = 2
    action_reference = []

    choices.append(bold(context.i18n('New user...')))
    action_reference.append('new')

    choices.append(bold(context.i18n('Rename user...')))
    action_reference.append('rename')

    if len(reference) > 1:
        action_count = 3
        choices.append(bold(context.i18n('Remove user...')))
        action_reference.append('remove')

    result = xbmcgui.Dialog().select(context.i18n('Manage Users'), choices)
    if result == -1:
        return

    choices = choices[:(len(choices) - action_count)]

    is_user = result <= (len(choices) - 1)
    if is_user:
        choice = reference[result]
        USERS.change_current(choice['uuid'])
        USERS.save()

    else:
        choice = action_reference[result - len(reference)]
        if choice == 'new':

            keyboard = xbmc.Keyboard()
            keyboard.setHeading(context.i18n('New Username'))
            keyboard.doModal()

            if keyboard.isConfirmed():
                new_username = keyboard.getText()
                new_username = new_username.strip()

                if not new_username:
                    return

                USERS.add(new_username)
                USERS.save()

        elif choice == 'rename':
            result = xbmcgui.Dialog().select(context.i18n('Rename user...'), choices)
            if result == -1:
                return

            keyboard = xbmc.Keyboard()
            keyboard.setHeading(context.i18n('New Username'))
            keyboard.doModal()

            if keyboard.isConfirmed():
                new_username = keyboard.getText()
                new_username = new_username.strip()

                if not new_username:
                    return

                choice = reference[result]
                USERS.rename(choice['uuid'], new_username)
                USERS.save()

        elif choice == 'remove':
            result = xbmcgui.Dialog().select(context.i18n('Remove user...'), choices)
            if result == -1:
                return

            choice = reference[result]
            USERS.remove(choice['uuid'])
            USERS.save()

    reset_cache()
    DataCache().clear()
    xbmc.executebuiltin('Container.Refresh')

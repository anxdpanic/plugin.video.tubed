# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import time
from uuid import uuid4
from xml.etree import ElementTree

import xbmcvfs  # pylint: disable=import-error

from ..constants import ADDON_ID


class UserStorage:
    __template_root = \
        '''
<users>
    <user current="true">
        <name>Default</name>
        <uuid>%s</uuid>
        <refresh_token></refresh_token>
        <access_token></access_token>
        <token_expiry>-1</token_expiry>
        <history_playlist></history_playlist>
        <watchlater_playlist></watchlater_playlist>
        <avatar></avatar>
    </user>
</users>
        '''

    __template_user = \
        '''
    <user current="false">
        <name>%s</name>
        <uuid>%s</uuid>
        <refresh_token></refresh_token>
        <access_token></access_token>
        <token_expiry>-1</token_expiry>
        <history_playlist></history_playlist>
        <watchlater_playlist></watchlater_playlist>
        <avatar></avatar>
    </user>
        '''

    def __init__(self):

        self.filename = xbmcvfs.translatePath(
            'special://profile/addon_data/%s/users.xml' % ADDON_ID
        )

        self.root = None

        self._users = None
        self._user = None

        self.load()

    @property
    def users(self):
        if self._users:
            return self._users

        user_elements = self.root.findall('./user')
        payload = []

        for user in user_elements:
            try:
                uuid = user.find('uuid').text
                name = user.find('name').text

                avatar = self._get_elements_text(user, 'avatar')

                refresh_token = self._get_elements_text(user, 'refresh_token')
                access_token = self._get_elements_text(user, 'access_token')
                token_expiry = self._get_elements_text(user, 'token_expiry', -1)

                current = user.attrib.get('current', 'false').lower() == 'true'

                history_playlist = self._get_elements_text(user, 'history_playlist')
                watchlater_playlist = self._get_elements_text(user, 'watchlater_playlist')

                payload.append({
                    'uuid': uuid,
                    'name': name,
                    'current': current,
                    'refresh_token': refresh_token,
                    'access_token': access_token,
                    'token_expiry': token_expiry,
                    'history_playlist': history_playlist,
                    'watchlater_playlist': watchlater_playlist,
                    'avatar': avatar,
                })

            except:  # pylint: disable=bare-except
                pass

        self._users = payload
        return payload

    @property
    def username(self):
        return self._current_user_get('name', '')

    @username.setter
    def username(self, value):
        self._current_user_set('name', value)

    @property
    def avatar(self):
        return self._current_user_get('avatar', '')

    @avatar.setter
    def avatar(self, value):
        self._current_user_set('avatar', value)

    @property
    def uuid(self):
        return self._current_user_get('uuid', '')

    @property
    def refresh_token(self):
        return self._current_user_get('refresh_token', '')

    @refresh_token.setter
    def refresh_token(self, value):
        self._current_user_set('refresh_token', value)

    @property
    def access_token(self):
        return self._current_user_get('access_token', '')

    @access_token.setter
    def access_token(self, value):
        self._current_user_set('access_token', value)

    @property
    def history_playlist(self):
        return self._current_user_get('history_playlist', '')

    @history_playlist.setter
    def history_playlist(self, value):
        self._current_user_set('history_playlist', value)

    @property
    def watchlater_playlist(self):
        return self._current_user_get('watchlater_playlist', '')

    @watchlater_playlist.setter
    def watchlater_playlist(self, value):
        self._current_user_set('watchlater_playlist', value)

    @property
    def token_expiry(self):
        return float(self._current_user_get('token_expiry', -1))

    @token_expiry.setter
    def token_expiry(self, value):
        self._current_user_set('token_expiry', str(value))

    @property
    def token_expired(self):
        if not self.access_token:
            return True

        # in this case no expiration date was set
        if self.token_expiry == -1:
            return False

        return self.token_expiry <= int(time.time())

    def change_current(self, user_uuid):
        user = self.root.find('.//user[@current="true"]')

        user_elements = self.root.findall('./user')
        for user_element in user_elements:
            uuid_element = user_element.find('uuid')

            if not hasattr(uuid_element, 'text'):
                continue

            if uuid_element.text == user_uuid:
                self._reset()

                user.attrib['current'] = 'false'
                user_element.attrib['current'] = 'true'
                break

    def add(self, name):
        self._reset()

        user_template = self.__template_user % (name, str(uuid4()))
        user_element = ElementTree.fromstring(user_template)
        self.root.append(user_element)

    def remove(self, user_uuid):
        self._reset()

        new_uuid = None
        remove = False
        user_elements = self.root.findall('./user')
        for user_element in user_elements:
            uuid_element = user_element.find('uuid')

            if not hasattr(uuid_element, 'text'):
                continue

            if uuid_element.text == user_uuid:
                remove = user_element
            else:
                new_uuid = uuid_element.text

            if remove and new_uuid:
                break

        if remove and new_uuid:
            self.change_current(new_uuid)
            self.root.remove(remove)

    def rename(self, user_uuid, new_name):
        self._reset()

        user_elements = self.root.findall('./user')
        for user_element in user_elements:
            uuid_element = user_element.find('uuid')
            name_element = user_element.find('name')

            if not hasattr(uuid_element, 'text') or not hasattr(name_element, 'text'):
                continue

            if uuid_element.text == user_uuid:
                name_element.text = new_name
                break

    def load(self):
        self._reset()

        try:
            self.root = ElementTree.parse(self.filename).getroot()
        except (ElementTree.ParseError, FileNotFoundError):
            self.root = ElementTree.fromstring(self.__template_root % str(uuid4()))
            self.save()

    def save(self):
        with open(self.filename, 'wb') as file_handle:
            file_handle.write(ElementTree.tostring(self.root,
                                                   short_empty_elements=False,
                                                   method='html'))

    def _current_user_get(self, attrib, default=''):
        if self._user:
            return self._user.get(attrib, default)

        for user in self.users:
            if user.get('current'):
                self._user = user.copy()
                return user.get(attrib, default)

        return default

    def _current_user_set(self, attrib, value):
        user = self.root.find('.//user[@current="true"]')
        if not user:
            return

        element = user.find(attrib)
        if not hasattr(element, 'text'):
            element = None

        self._reset()
        if element is None:
            new_element = ElementTree.SubElement(user, attrib)
            new_element.text = value
        else:
            element.text = value

    def _reset(self):
        self._users = None
        self._user = None

    @staticmethod
    def _get_elements_text(user, element_name, default=''):
        payload = default

        element = user.find(element_name)
        if hasattr(element, 'text'):
            payload = element.text

        return payload

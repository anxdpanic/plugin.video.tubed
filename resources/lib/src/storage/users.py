# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

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
                refresh_token = user.find('refresh_token').text
                access_token = user.find('access_token').text
                current = user.attrib.get('current', 'false').lower() == 'true'

                payload.append({
                    'uuid': uuid,
                    'name': name,
                    'current': current,
                    'refresh_token': refresh_token or '',
                    'access_token': access_token or ''
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

        user_elements = self.root.findall('./user')
        for user_element in user_elements:
            uuid_element = user_element.find('uuid')

            if not hasattr(uuid_element, 'text'):
                continue

            if uuid_element.text == user_uuid:
                self.root.remove(user_element)
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
            return

        self._reset()
        element.text = value

    def _reset(self):
        self._users = None
        self._user = None

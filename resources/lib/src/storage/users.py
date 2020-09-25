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

    def __init__(self):

        self.filename = xbmcvfs.translatePath(
            'special://profile/addon_data/%s/users.xml' % ADDON_ID
        )

        self.tree = None
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
        return self._current_user('name', '')

    @property
    def uuid(self):
        return self._current_user('uuid', '')

    @property
    def refresh_token(self):
        return self._current_user('refresh_token', '')

    @property
    def access_token(self):
        return self._current_user('access_token', '')

    def load(self):
        self.__reset()
        try:
            self.tree = ElementTree.parse(self.filename)
            self.root = self.tree.getroot()
        except (ElementTree.ParseError, FileNotFoundError):
            self.root = ElementTree.fromstring(self.__root_template())
            self.save()
            self.tree = ElementTree.parse(self.filename)
            self.root = self.tree.getroot()

    def save(self):
        self.__reset()
        if not self.tree:
            with open(self.filename, 'wb') as file_handle:
                file_handle.write(ElementTree.tostring(self.root,
                                                       short_empty_elements=False,
                                                       method='html'))
        else:
            self.tree.write(self.filename, short_empty_elements=False, method='html')

    def _current_user(self, attrib, default=''):
        if self._user:
            return self._user.get(attrib, default)

        for user in self.users:
            if user.get('current'):
                self._user = user.copy()
                return user.get(attrib, default)

        return default

    def __reset(self):
        self.tree = None
        self.root = None

        self._users = None
        self._user = None

    def __root_template(self):
        return self.__template_root % str(uuid4())

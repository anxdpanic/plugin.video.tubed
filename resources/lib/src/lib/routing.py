# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""


class Router:

    def __init__(self):
        self._functions = {}
        self._args = {}
        self._kwargs = {}

    def route(self, mode, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = []

        def decorator(func):
            if mode in self._functions:
                message = '%s already registered as %s' % (str(func), mode)
                raise Exception(message)

            self._functions[mode.strip()] = func
            self._args[mode] = args
            self._kwargs[mode] = kwargs

            return func

        return decorator

    def invoke(self, mode, queries):

        if mode not in self._functions:
            message = 'Attempt to invoke an unregistered mode %s' % mode
            raise Exception(message)

        args = []
        kwargs = {}
        unused_args = queries.copy()

        if self._args[mode]:
            for arg in self._args[mode]:
                arg = arg.strip()
                if arg in queries:
                    args.append(self._cast(queries[arg]))
                    del unused_args[arg]
                    continue

                message = 'Mode %s requested argument %s but it was not provided.' % (mode, arg)
                raise Exception(message)

        if self._kwargs[mode]:
            for arg in self._kwargs[mode]:
                arg = arg.strip()
                if arg in queries:
                    kwargs[arg] = self._cast(queries[arg])
                    del unused_args[arg]

        if 'mode' in unused_args:
            del unused_args['mode']

        self._functions[mode](*args, **kwargs)

    @staticmethod
    def _cast(arg):
        lowercase = arg.lower()

        if lowercase == 'true':
            return True

        elif lowercase == 'false':
            return False

        elif lowercase == 'none':
            return None

        return arg

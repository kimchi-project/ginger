# -*- coding: utf-8 -*-
#
# Project Ginger
#
# Copyright IBM Corp, 2015-2017
#
# Code derived from Project Kimchi
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

import json
import time
import unittest
import urllib2
from functools import partial

from wok.asynctask import AsyncTask

from tests.utils import patch_auth, request
from tests.utils import run_server, wait_task

test_server = None


def setUpModule():
    global test_server
    patch_auth()
    test_server = run_server(test_mode=False)


def tearDownModule():
    test_server.stop()


class TaskTests(unittest.TestCase):
    def _async_op(self, cb, opaque):
        time.sleep(1)
        cb('success', True)

    def _except_op(self, cb, opaque):
        time.sleep(1)
        raise Exception("Oops, this is an exception handle test."
                        " You can ignore it safely")
        cb('success', True)

    def _intermid_op(self, cb, opaque):
        time.sleep(1)
        cb('in progress')

    def setUp(self):
        self.request = partial(request)

    def _task_lookup(self, taskid):
        return json.loads(
            self.request('/plugins/ginger/tasks/%s' % taskid).read()
        )

    def test_tasks(self):
        id1 = AsyncTask('/plugins/ginger/tasks/1', self._async_op).id
        id2 = AsyncTask('/plugins/ginger/tasks/2', self._except_op).id
        id3 = AsyncTask('/plugins/ginger/tasks/3', self._intermid_op).id

        target_uri = urllib2.quote('^/plugins/ginger/tasks/*', safe="")
        filter_data = 'status=running&target_uri=%s' % target_uri
        tasks = json.loads(
            self.request('/plugins/ginger/tasks?%s' % filter_data).read()
        )
        self.assertEquals(3, len(tasks))

        tasks = json.loads(self.request('/plugins/ginger/tasks').read())
        tasks_ids = [t['id'] for t in tasks]
        self.assertEquals(set([id1, id2, id3]) - set(tasks_ids), set([]))
        wait_task(self._task_lookup, id2)
        foo2 = json.loads(
            self.request('/plugins/ginger/tasks/%s' % id2).read()
        )
        keys = ['id', 'status', 'message', 'target_uri']
        self.assertEquals(sorted(keys), sorted(foo2.keys()))
        self.assertEquals('failed', foo2['status'])
        wait_task(self._task_lookup, id3)
        foo3 = json.loads(
            self.request('/plugins/ginger/tasks/%s' % id3).read()
        )
        self.assertEquals('in progress', foo3['message'])
        self.assertEquals('running', foo3['status'])

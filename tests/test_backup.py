#
# Project Ginger
#
# Copyright IBM, Corp. 2016
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

import mock
import os
import tempfile
import unittest

from wok.objectstore import ObjectStore
from wok.plugins.ginger.models.backup import ArchivesModel, ArchiveModel


class BackupArchiveTests(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        objstore_loc = self.temp_file.name
        self._objstore = ObjectStore(objstore_loc)

        ArchivesModel._archive_dir = '/tmp'
        ArchivesModel._default_include = []
        ArchivesModel._default_exclude = []

    def tearDown(self):
        self.temp_file.close()
        os.remove(self.temp_file.name)

    @mock.patch('wok.plugins.ginger.models.backup.run_command')
    @mock.patch('wok.plugins.ginger.models.backup.get_tar_create_timeout')
    @mock.patch('wok.plugins.ginger.models.backup._sha256sum')
    def test_create_and_lookup_backup_file(self, mock_sha256sum,
                                           mock_timeout, mock_run_command):
        include = []
        exclude = []
        descr = 'test_create_lookup_bkp_file'
        mock_run_command.return_value = ["", "", 0]
        mock_timeout.return_value = 10
        mock_sha256sum.return_value = 'sha256sum'

        params = {'include': [], 'exclude': [], 'description': descr}
        archive_id = ArchivesModel(objstore=self._objstore).create(params)

        archive_file = os.path.join('/tmp', archive_id + '.tar.gz')

        cmd = ['tar', '--create', '--gzip', '--absolute-names',
               '--file', archive_file, '--selinux', '--acl',
               '--xattrs'] + exclude + include

        mock_run_command.asert_called_once_with(cmd)
        mock_sha256sum.asert_called_once_with(archive_file)

        lookup = ArchiveModel(objstore=self._objstore).lookup(archive_id)

        self.assertEqual(lookup.get('identity'), archive_id)
        self.assertEqual(lookup.get('include'), [])
        self.assertEqual(lookup.get('exclude'), [])
        self.assertEqual(lookup.get('description'), descr)
        self.assertEqual(lookup.get('file'), archive_file)

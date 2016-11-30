#
# Project Ginger
#
# Copyright IBM Corp, 2016
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

import fs_utils

from wok.exception import NotFoundError, OperationFailed
from wok.exception import InvalidParameter, MissingParameter
from wok.rollbackcontext import RollbackContext


class FileSystemsModel(object):
    """
    Model class for listing filesystems (df -hT) and mounting a filesystem
    """

    def create(self, params):

        if not params.get('type'):
            raise MissingParameter("GINFS00016E")

        if params['type'] == 'local':

            if not params.get('blk_dev'):
                raise MissingParameter("GINFS00009E")

            blk_dev = params['blk_dev']

            if not params.get('mount_point'):
                raise MissingParameter("GINFS00010E")

            mount_point = params['mount_point']

            mount_options = params.get('mount_options', '')

            try:
                with RollbackContext() as rollback:
                    fs_utils._mount_a_blk_device(blk_dev, mount_point,
                                                 mount_options)
                    rollback.prependDefer(
                        fs_utils._umount_partition, mount_point)
                    fs_utils.make_persist(blk_dev, mount_point, mount_options)
                    rollback.commitAll()
            except Exception as e:
                raise InvalidParameter("GINFS00007E", {"err": e.message})

            return mount_point

        elif params['type'] == 'nfs':

            if not params.get('server'):
                raise MissingParameter("GINFS00014E")

            server = params['server']

            if not params.get('share'):
                raise MissingParameter("GINFS00015E")

            share = params['share']

            if not params.get('mount_point'):
                raise MissingParameter("GINFS00010E")

            mount_point = params['mount_point']

            mount_options = params.get('mount_options', '')

            try:
                with RollbackContext() as rollback:
                    fs_utils.nfsmount(
                        server, share, mount_point, mount_options)
                    rollback.prependDefer(
                        fs_utils._umount_partition, mount_point)
                    dev_info = server + ':' + share
                    fs_utils.make_persist(
                        dev_info, mount_point, mount_options)
                    rollback.commitAll()
            except Exception as e:
                raise InvalidParameter("GINFS00018E", {"err": e})
            return mount_point
        else:
            raise InvalidParameter("GINFS00017E")

    def get_list(self):
        try:
            fs_names = fs_utils._get_fs_names()

        except OperationFailed as e:
            raise OperationFailed("GINFS00013E",
                                  {'err': e.message})

        return fs_names


class FileSystemModel(object):
    """
    Model for viewing and unmounting the filesystem
    """

    def lookup(self, name):
        try:
            fs = fs_utils._get_fs_info(name)

            # if not empty: return
            if len(fs) > 0:
                return fs

            # empty: return NotFound
            raise ValueError

        except ValueError:
            raise NotFoundError("GINFS00001E", {'name': name})

    def delete(self, name):
        try:
            fs_utils._umount_partition(name)
            fs_utils.remove_persist(name)
        except OperationFailed as e:
            raise OperationFailed("GINFS00002E",
                                  {'name': name, 'err': e.message})

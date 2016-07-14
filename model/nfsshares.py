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
from wok.utils import patch_find_nfs_target


class NFSSharesModel(object):
    """
    Model to represent the list of NFS shares/exports
    """

    def get_list(self, model_args):
        try:
            name = model_args
            nfsshares = patch_find_nfs_target(name)
            if not nfsshares:
                raise NotFoundError("GINNFS00002E")
            fs_details = fs_utils._get_df_output()
            fs_name_list = [d['filesystem'] for d in fs_details]
            sharepoints = []
            for nfs_share in nfsshares:
                nfsmount = nfs_share['host_name']+':'+nfs_share['target']
                if nfsmount not in fs_name_list:
                    sharepoints.append(nfs_share['target'])

            return {'NFSShares': sharepoints}

        except ValueError:
            raise OperationFailed("GINNFS00001E", {'name': name})

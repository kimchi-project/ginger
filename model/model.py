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

from wok import config as wok_config
from wok.basemodel import BaseModel
from wok.objectstore import ObjectStore
from wok.utils import get_all_model_instances, get_model_instances
from wok.utils import upgrade_objectstore_schema


class GingerModel(BaseModel):

    def __init__(self):

        objstore_loc = wok_config.get_object_store() + '_ginger'
        self._objstore = ObjectStore(objstore_loc)
        # Some paths or URI's present in the objectstore have changed after
        # Wok 2.0.0 release. Check here if a schema upgrade is necessary.
        upgrade_objectstore_schema(objstore_loc, 'version')

        kargs = {'objstore': self._objstore}
        models = get_all_model_instances(__name__, __file__, kargs)

        # Import task model from Wok
        instances = get_model_instances('wok.model.tasks')
        for instance in instances:
            models.append(instance(**kargs))

        super(GingerModel, self).__init__(models)

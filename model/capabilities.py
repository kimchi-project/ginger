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

import os

from wok.utils import get_model_instances, listPathModules


class CapabilitiesModel(object):
    def __init__(self):
        self.features = {}

        pckg_namespace = __name__.rsplit('.', 1)[0]

        for mod_name in listPathModules(os.path.dirname(__file__)):
            if mod_name.startswith("_") or mod_name == 'capabilities':
                continue

            instances = get_model_instances(pckg_namespace + '.' + mod_name)
            for instance in instances:
                feat_name = instance.__name__.replace('Model', '')
                try:
                    self.features[feat_name] = instance.is_feature_available
                except AttributeError:
                    self.features[feat_name] = None

    def lookup(self, *ident):
        current_feature_state = {}

        for feat_name, is_avail_method in self.features.items():
            if not is_avail_method:
                current_feature_state[feat_name] = True
            else:
                current_feature_state[feat_name] = is_avail_method()

        return current_feature_state

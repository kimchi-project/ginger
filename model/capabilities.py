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


class CapabilitiesModel(object):
    def __init__(self, features):
        self.features_enabled = {}
        self._set_capabilities(features)

    def lookup(self, *ident):
        return self.features_enabled

    def _set_capabilities(self, features):
        for feat in features:
            feat_name = type(feat).__name__.replace('Model', '')
            try:
                self.features_enabled[feat_name] = \
                    feat.is_feature_available()
            except AttributeError:
                self.features_enabled[feat_name] = True

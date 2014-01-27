#
# Project Kimchi
#
# Copyright IBM, Corp. 2014
#
# Authors:
#  Daniel H Barboza <danielhb@linux.vnet.ibm.com>
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

from kimchi.exception import OperationFailed
from kimchi.utils import kimchi_log
from kimchi.utils import run_command


class PowerProfilesModel():
    """
    The model class for power saving profiles of the host
    """
    def get_list(self):
        profiles = []
        tuned_cmd = ["tuned-adm", "list"]
        output, error, returncode = run_command(tuned_cmd)
        if returncode != 0:
            kimchi_log.error('Could not retrieve power profiles, error: %s',
                             error)
            raise OperationFailed('Error while retrieving power saving '
                                  'profiles.')
        lines_output = output.rstrip("\n").split("\n")
        for line in lines_output:
            if line.startswith('-'):
                line = line.strip("- ")
                profiles.append(line)
        return profiles


class PowerProfileModel():
    """
    The model class to represent a single power saving profile.
    """
    def _get_active_powersaving_profile(self):
        tuned_cmd = ["tuned-adm", "active"]
        output, error, returncode = run_command(tuned_cmd)
        if returncode != 0:
            kimchi_log.error('Could not retrieve active power profile, '
                             'error: %s', error)
            raise OperationFailed('Error while retrieving active '
                                  'power saving profiles.')
        output = output.split()
        return output[-1].rstrip()

    def __init__(self):
        self.active_powerprofile = self._get_active_powersaving_profile()

    def lookup(self, powerprofile):
        is_active = self.active_powerprofile == powerprofile
        return {"name": powerprofile, "active": is_active}

    def update(self, profile, params):
        if params['active'] and self.active_powerprofile != profile:
            self.active_powerprofile = profile
            tuned_cmd = ["tuned-adm", "profile", profile]
            output, error, returncode = run_command(tuned_cmd)
            if returncode != 0:
                kimchi_log.error('Could not activate power profile %s, '
                                 'error: %s', powerprofile, error)
                raise OperationFailed('Error while activating power '
                                      'saving profile %s.', powerprofile)
        return profile

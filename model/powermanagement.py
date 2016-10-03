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

from wok.exception import InvalidOperation, OperationFailed
from wok.utils import run_command
from psutil import pid_exists


def parse_tunedadm_list(tuned_output):
    profiles = []
    lines = tuned_output.rstrip("\n").split("\n")
    for line in lines:
        if line.startswith('-'):
            line = line.strip("- ").split()
            profiles.append(line[0])

    return profiles


def get_tuned_profiles():
    tuned_cmd = ["tuned-adm", "list"]
    output, error, returncode = run_command(tuned_cmd)
    if returncode == 2:
        raise InvalidOperation('GINPOWER0002E')
    return parse_tunedadm_list(output)


def get_active_tuned_profile():
    tuned_cmd = ["tuned-adm", "active"]
    output, error, returncode = run_command(tuned_cmd)
    # This is a possible scenario where tuned is running
    # but there is no active profile yet. No need to
    # report/issue an error.
    if returncode != 0:
        return None
    output = output.split()
    return output[-1].rstrip()


def activate_tuned_profile(powerprofile):
    tuned_cmd = ["tuned-adm", "profile", powerprofile]
    output, error, returncode = run_command(tuned_cmd)
    if returncode != 0:
        raise OperationFailed("GINPOWER0001E",
                              {'profile': powerprofile, 'err': error})


class PowerProfilesModel(object):
    """
    The model class for power saving profiles of the host
    """
    @staticmethod
    def is_feature_available():
        # To make this feature available we need tuned service
        # running.
        try:
            with open('/run/tuned/tuned.pid', 'r') as file:
                tunedpid = int(file.read().rstrip('\n'))
                if pid_exists(tunedpid):
                    return True
        # Don't need to handle any possible exception raised
        # in the code above. If that fails for any reason we
        # assume the service is not running.
        except:
            pass

        return False

    def get_list(self):
        return get_tuned_profiles()


class PowerProfileModel(object):
    """
    The model class to represent a single power saving profile.
    """
    def __init__(self):
        self.active_powerprofile = get_active_tuned_profile()

    def lookup(self, powerprofile):
        is_active = self.active_powerprofile == powerprofile
        return {"name": powerprofile, "active": is_active}

    def update(self, powerprofile, params):
        if params['active'] and self.active_powerprofile != powerprofile:
            activate_tuned_profile(powerprofile)
            self.active_powerprofile = powerprofile
        return powerprofile

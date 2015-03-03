#
# Project Ginger
#
# Copyright IBM, Corp. 2014
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

import gettext


_ = gettext.gettext


messages = {
    "GINNET0001E": _("Failed to read /etc/resolv.conf because %(reason)s"),
    "GINNET0002E": _("Failed to write /etc/resolv.conf because %(reason)s"),
    "GINNET0003E": _("Invalid network parameters. Details: %(err)s"),
    "GINNET0004E": _("Unable to update interface configuration. "
                     "Details: %(err)s"),
    "GINNET0005E": _("Invalid parameter for DNS servers"),
    "GINNET0006E": _("Invalid parameter for interface ip address"),
    "GINNET0007E": _("Invalid parameter for interface netmask"),
    "GINNET0008E": _("Invalid parameter for network gateway"),
    "GINNET0009E": _("Unable to get default gateway: %(err)s"),
    "GINNET0010E": _("Unable to delete default gateway: %(err)s"),
    "GINNET0011E": _("Unable to set default gateway: %(err)s"),
    "GINNET0012E": _("Invalid ip/netmask inputs. Both fields must be valid "
                     "ip/netmask values or both must be blank (will erase "
                     "the current IP/netmask)."),
    "GINNET0013E": _("Interface %(name)s is not editable because it belongs "
                     "to a vlan or bridge"),

    "GINUSER0001E": _("Specify name, password, group and profile for the new "
                      "user."),
    "GINUSER0002E": _("User name is a required string."),
    "GINUSER0003E": _("User password is a required string."),
    "GINUSER0004E": _("User group is a required string."),
    "GINUSER0005E": _("User profile is required and should be one among "
                      "kimchiuser, virtuser or admin."),
    "GINUSER0006E": _("Could not add user '%(user)s' to kvm group."),
    "GINUSER0007E": _("Could not add user '%(user)s' to sudoers list."),
    "GINUSER0008E": _("The user name '%(user)s' is already in use'."),
    "GINUSER0009E": _("Could not create user '%(user)s'."),
    "GINUSER0010E": _("Could not delete user '%(user)s'."),
    "GINUSER0011E": _("User '%(user)s' does not exist."),
    "GINUSER0012E": _("Could not delete group '%(group)s'"),
    "GINUSER0013E": _("Group for user '%(user)s' does not exist for removal."),

    "GINFW0001E": _("Cannot update system firmware while running VMs."),
    "GINFW0002E": _("Firmware image unpack failed: rc = %(rc)s. "
                    "Details: %(err)s"),
    "GINFW0003E": _("FW update failed: "
                    "No image file found in the package file."),
    "GINFW0004E": _("Error flashing firmware. rc = %(rc)s. \
                     Please see /usr/sbin/update_flash for rc reasons."),
    "GINFW0005E": _("Error commiting firmware. rc = %(rc)s. \
                     Ensure you are booted to the temporary side."),
    "GINFW0006E": _("Error rejecting firmware. rc = %(rc)s. \
                     Ensure you are booted to the permanent side."),

    "GINHBK0001E": _('Failed to create tar archive "%(name)s", cmd: '
                     '"%(cmd)s". Inspect error log for more information.'),
    "GINHBK0002E": _('Failed to delete archive file "%(name)s".'),
    "GINHBK0003E": _('Failed to create archive dir "%(dir)s". '
                     'Inspect error log for more information.'),
    "GINHBK0004E": _('Description too long.'),
    "GINHBK0005E": _('Please check the uniqueness of the paths or patterns.'),
    "GINHBK0006E": _('Path or pattern is too long or too short.'),
    "GINHBK0007E": _('Invalid days_ago number.'),
    "GINHBK0008E": _('Invalid counts_ago number.'),
    "GINHBK0009E": _('Failed to create archive "%(identity)s". '
                     'Inspect error log for more information.'),
    "GINHBK0010E": _('Timeout while creating archive "%(identity)s", the '
                     'files might be too large for a configuration backup.'),

    "GINADAP0001E": _("SAN adapter '%(adapter)s' does not exist in the system."
                      ),

    "GINSEP0001E": _("System hostname is a required parameter."),
    "GINSEP0002E": _("System port number is a required parameter."),
    "GINSEP0003E": _("SNMP community is a required parameter."),
    "GINSEP0004E": _("SEP command execution error: '%(cmd)s' - rc: '%(rc)s' \
                     - error: '%(error)s'."),

    "GINPOWER001E": _("Failed to retrieve power management profiles: \
                       Host OS does not support the tuned-adm package."),
    "GINPOWER002E": _("Failed to retrieve power management profiles: \
                       Daemon 'tuned-adm' is not active."),
    "GINPOWER003E": _("Failed to retrieve power management profiles: \
                       Package 'tuned-adm' is not installed."),
    "GINPOWER004E": _("Error activating power saving profile %(profile)s.")
}

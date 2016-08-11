# -*- coding: utf8 -*-

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

import re
import cherrypy

from collections import OrderedDict

from wok.utils import wok_log
from wok.utils import run_command


class SensorsModel(object):
    """
    The model class for polling host sensor data
    """

    def _get_default_temperature_unit(self):
        return cherrypy.request.app.config['unit']['temperature']

    def lookup(self, params):
        def convert_units(dev_name, sensor_line, temperature_unit):
            """
            Do three things:
            1. Convert from C to F if needed.
            2. Make all numbers floats.
            3. Make sure no 'max' temp is 0.
            """
            fallback_max = 100.0 if temperature_unit == 'C' else 212.0
            name = sensor_line[0]
            val = float(sensor_line[1])
            if 'fan' not in dev_name and \
                    'power' not in dev_name:
                if(abs(val) < 1):
                    if "max" in name:
                        val = fallback_max
                    elif "alarm" in name:
                        # unwise to modify '0' alarm val
                        val = 0.0
                elif(temperature_unit == 'F'):
                    val = 9.0/5.0 * val + 32
            return (name, val)

        def parse_sensors(temperature_unit):
            command = ['sensors', '-u']
            sens_out, error, rc = run_command(command)
            if rc:
                wok_log.error("Error retrieving sensors data: %s: %s." %
                              (error, rc))

            devices = []
            for section in sens_out.split('\n\n'):
                """
                    A device consists of possibly multiple sensors, each
                    with a possible current, max, alarm, and critical temp,
                    or just a current and max (for fans, for example).
                    Each is broken into sections separated by a blank line,
                    and will have two headings:
                        amb-temp-sensor-isa-0000
                        Adapter: ISA adapter
                """
                # The first line of each device section is the device name,
                #   e.g., amb-temp-sensor-isa-0000
                dev_name, sep, section = section.partition('\n')
                sub_devices = {"cores": [], "fans": [], "power": [], "pci": [],
                               "ambient": [], "others": []}
                """
                    Two sub-devices of a CPU device:
                    Physical id 0:
                        temp1_input: 48.000
                        temp1_max: 87.000
                        temp1_crit: 105.000
                        temp1_crit_alarm: 0.000
                    Core 0:
                        temp2_input: 48.000
                        temp2_max: 87.000
                        temp2_crit: 105.000
                        temp2_crit_alarm: 0.000

                """
                if dev_name is not '':
                    # The second line, e.g. Adapter: ISA adapter, isn't
                    #   unique, so it is discarded.
                    throw_away, sep, section = section.partition('\n')
                    # A device may have multiple sub-devices, listed
                    #   in separate groups. Split this section/device
                    #   into lines to parse each sub-device.
                    # Each sub-device (e.g. Core 0) has a unique sensor.
                    device = section.splitlines()
                    sensor_name = ''
                    sensor = []
                    # Parse backwards, because you don't want to add a
                    #   new device to the dict until you have all sub-
                    #   device sensors.
                    for line in reversed(device):
                        try:
                            # Get all ':'-separated elements from a line.
                            # This may be the name of the sub-device,
                            # or a name:value pair for a temp.
                            data_line = line.split(': ')
                            data_line = [x.strip().strip(':')
                                         for x in data_line]

                            if len(data_line) > 1:  # name:value pair

                                # this case gets this statement:
                                # ['ERROR', "Can't ... <sensor>", 'I/O error']
                                # so, will be added <sensor> with value 0
                                if len(data_line) == 3:
                                    data_line = [data_line[1].split()[5], 0]

                                data_line = convert_units(
                                    dev_name, data_line, temperature_unit)

                                # sensors come with :
                                # <sensor_name>_<min,fault,input>
                                data_splitted = data_line[0].split("_")
                                data_splitted.pop(0)
                                key = '_'.join(data_splitted)

                                sensor.append((key, data_line[1]))

                                # unit already present: skip
                                if True in ["unit" in pair for pair in sensor]:
                                    continue

                                # add unit
                                if "fan" in data_line[0]:
                                    sensor.append(("unit", "RPM"))
                                elif "power" in data_line[0]:
                                    sensor.append(("unit", "W"))
                                elif "temp" in data_line[0]:
                                    sensor.append(
                                        ("unit",
                                         self._get_default_temperature_unit())
                                    )

                            else:  # Sub-device name
                                sensor_name = data_line[0]
                                sensor.append(("name", sensor_name))
                                sensor = OrderedDict(reversed(sensor))

                                # add to category
                                if "core" in sensor_name.lower():
                                    sub_devices["cores"].append(sensor)

                                elif "fan" in sensor_name.lower():
                                    sub_devices["fans"].append(sensor)

                                elif "ambient" in sensor_name.lower():
                                    sub_devices["ambient"].append(sensor)

                                elif "pci" in sensor_name.lower():
                                    sub_devices["pci"].append(sensor)

                                elif "power" in sensor_name.lower():
                                    sub_devices["power"].append(sensor)

                                else:
                                    sub_devices["others"].append(sensor)

                                sensor = []
                        except Exception:
                            pass
                    """
                        Add the entire device (e.g. all cores and their
                        max, min, crit, alarm) as one dict. Reverse it
                        so that fans, CPUs, etc. are in order.
                    """
                    devices.append(
                        {"adapter": dev_name,
                         "inputs": OrderedDict(reversed(sub_devices.items()))}
                    )
            return devices

        def parse_hdds(temperature_unit):
            # hddtemp will strangely convert a non-number (see error case
            #   below) to 32 deg F. So just always ask for C and convert later.
            out, error, rc = run_command(['hddtemp'])
            if rc:
                wok_log.error("Error retrieving HD temperatures: rc %s."
                              "output: %s" % (rc, error))
                return None

            hdds = OrderedDict()

            for hdd in out.splitlines():
                # This error message occurs when the HDD does not
                # have S.M.A.R.T (Self-Monitoring, Analysis, and
                # Reporting Technology) available. Skip the hdd line
                # in this case.
                if 'S.M.A.R.T. not available' in hdd:
                    continue

                hdd_name = ''
                hdd_temp = 0.0
                try:
                    hdd_items = hdd.split(':')
                    hdd_name, hdd_temp = hdd_items[0], hdd_items[2]
                    hdd_temp = re.sub('°[C|F]', '', hdd_temp).strip()
                except Exception as e:
                    wok_log.error('Sensors hdd parse error: %s' % e.message)
                    continue
                try:
                    # Try to convert the number to a float. If it fails,
                    # don't add this disk to the list.
                    hdd_temp = float(hdd_temp)
                    if(temperature_unit == 'F'):
                        hdd_temp = 9.0/5.0 * hdd_temp + 32
                    hdds[hdd_name] = hdd_temp
                except ValueError:
                    # If no sensor data, parse float will fail.
                    wok_log.warning("Sensors hdd: %s" % hdd)
            hdds['unit'] = temperature_unit
            return hdds

        # Don't store the unit parameter passed in permanently so that
        #   the setting stored in the config file is what everyone will
        #   see, and the UI will not bounce between 'C' and 'F' if
        #   a lot of querying is going on from different sources.
        self.temperature_unit = self._get_default_temperature_unit()
        override_unit = None
        if params is not None:
            override_unit = params.get('temperature_unit')
        cur_unit = self.temperature_unit if override_unit is None \
            else override_unit
        sensors = parse_sensors(cur_unit)
        hdds = parse_hdds(cur_unit)
        return {'sensors': sensors, 'hdds': hdds}

    @staticmethod
    def is_feature_available():
        _, _, rc1 = run_command(['sensors', '-u'])
        _, _, rc2 = run_command(['hddtemp'])

        return rc1 == 0 | rc2 == 0

# -*- coding: utf-8 -*-
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

import mock
import unittest

from wok.plugins.ginger.model.sensors import SensorsModel


class SensorsTests(unittest.TestCase):

    @mock.patch('wok.plugins.ginger.model.sensors.run_command')
    @mock.patch('wok.plugins.ginger.model.sensors.SensorsModel.'
                '_get_default_temperature_unit')
    def test_sensors_output(self, mock_temperature, mock_run_command):
        sensors_output = """acpitz-virtual-0
Adapter: Virtual device
temp1:
  temp1_input: 46.000
  temp1_crit: 200.000

thinkpad-isa-0000
Adapter: ISA adapter
fan1:
  fan1_input: 3768.000

coretemp-isa-0000
Adapter: ISA adapter
Physical id 0:
  temp1_input: 47.000
  temp1_max: 87.000
  temp1_crit: 105.000
  temp1_crit_alarm: 0.000
Core 0:
  temp2_input: 44.000
  temp2_max: 87.000
  temp2_crit: 105.000
  temp2_crit_alarm: 0.000
Core 1:
  temp3_input: 47.000
  temp3_max: 87.000
  temp3_crit: 105.000
  temp3_crit_alarm: 0.000

        """

        hddtemp_output = "/dev/sda: ST320LT007-9ZV142: 38°C"

        sensors_cmd_output = [sensors_output, "", 0]
        hddtemp_cmd_output = [hddtemp_output, "", 0]
        mock_run_command.side_effect = \
            [sensors_cmd_output, hddtemp_cmd_output]

        mock_temperature.return_value = 'C'

        lookup = SensorsModel().lookup(None)

        self.assertEqual(lookup.get('hdds'), {'/dev/sda': 38.0, 'unit': 'C'})

        self.assertIsNotNone(lookup.get('sensors'))
        self.assertIsNotNone(lookup['sensors'][0])
        self.assertIsNotNone(
            lookup['sensors'][0]['inputs']['others'][0]
        )
        self.assertEqual(
            lookup['sensors'][0]['inputs']['others'][0]['input'],
            46.0
        )
        self.assertEqual(
            lookup['sensors'][0]['inputs']['others'][0]['crit'],
            200.0
        )
        self.assertIsNotNone(lookup['sensors'][1])
        self.assertIsNotNone(
            lookup['sensors'][1]['inputs']['fans'][0]
        )
        self.assertEqual(
            lookup['sensors'][1]['inputs']['fans'][0]['input'],
            3768.0
        )
        self.assertIsNotNone(lookup['sensors'][2])
        self.assertIsNotNone(
            lookup['sensors'][2]['inputs']['cores']
        )
        self.assertEqual(
            lookup['sensors'][2]['inputs']['cores'][0]['input'],
            47.0
        )
        self.assertEqual(
            lookup['sensors'][2]['inputs']['cores'][0]['max'],
            87.0
        )
        self.assertEqual(
            lookup['sensors'][2]['inputs']['cores'][0]['crit'],
            105.0
        )
        self.assertEqual(
            lookup['sensors'][2]['inputs']['cores'][0]['crit_alarm'],
            0.0
        )

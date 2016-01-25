#
# Project Ginger
#
# Copyright IBM, Corp. 2015-2016
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

import wok.plugins.ginger.model.sysmodules as sysmodules
from wok.plugins.ginger.model.sysmodules import SysModuleModel
from wok.plugins.ginger.model.sysmodules import SysModulesModel


class SysmodulesTests(unittest.TestCase):

    def test_lsmod_parser(self):
        lsmod_sample_output = \
            """
Module                  Size  Used by
vfio_pci               32768  0
vfio_iommu_type1       20480  0
vfio_virqfd            16384  1 vfio_pci
vfio                   24576  2 vfio_iommu_type1,vfio_pci
loop                   28672  0
rfcomm                 69632  14
            """
        output_array = sysmodules.parse_lsmod_output(
            lsmod_sample_output
        )
        self.assertEqual(len(output_array), 6)

        modules = ['vfio_pci', 'vfio_iommu_type1', 'vfio_virqfd', 'vfio',
                   'loop', 'rfcomm']
        for module in output_array:
            module_name = module['name']
            self.assertIn(module_name, modules)
            if module_name == 'vfio_iommu_type1':
                self.assertEqual(module['size'], '20480')
            if module_name == 'rfcomm':
                self.assertEqual(module['used_by'], '14')
            if module_name == 'vfio':
                self.assertEqual(
                    module['used_by_loaded'],
                    ['vfio_iommu_type1', 'vfio_pci']
                )

    def test_modinfo_parser(self):
        modinfo_sample_output = """filename: /lib/modules/4.2.8-300.fc23.\
x86_64/kernel/net/tipc/tipc.ko.xz\0version=2.0.0\0license=Dual BSD/GPL\0\
description=TIPC: Transparent Inter Process Communication\0\
srcversion=D8C4AF100F6EA6984637AD1\0depends=udp_tunnel,ip6_udp_tunnel\0\
intree=Y\0vermagic=4.2.8-300.fc23.x86_64 SMP mod_unload \0\
signer=Fedora kernel signing key\0\
sig_key=89:CE:AF:53:80:B1:D1:50:40:56:CB:00:AA:3C:46:34:6B:EB:2E:05\0\
sig_hashalgo=sha256\0"""

        modinfo_dict = sysmodules.parse_modinfo_0_output(
            modinfo_sample_output
        )

        self.assertEqual(
             modinfo_dict['filename'],
             '/lib/modules/4.2.8-300.fc23.x86_64/kernel/net/tipc/tipc.ko.xz'
        )
        self.assertEqual(modinfo_dict['version'], '2.0.0')
        self.assertEqual(modinfo_dict['license'], 'Dual BSD/GPL')
        self.assertEqual(
            modinfo_dict['description'],
            'TIPC: Transparent Inter Process Communication'
        )
        self.assertEqual(
            modinfo_dict['srcversion'],
            'D8C4AF100F6EA6984637AD1'
        )
        self.assertEqual(
            modinfo_dict['depends'],
            ['udp_tunnel', 'ip6_udp_tunnel']
        )
        self.assertEqual(modinfo_dict['intree'], 'Y')
        self.assertEqual(
            modinfo_dict['vermagic'],
            '4.2.8-300.fc23.x86_64 SMP mod_unload'
        )
        self.assertEqual(modinfo_dict['signer'], 'Fedora kernel signing key')
        self.assertEqual(
            modinfo_dict['sig_key'],
            '89:CE:AF:53:80:B1:D1:50:40:56:CB:00:AA:3C:46:34:6B:EB:2E:05'
        )
        self.assertEqual(modinfo_dict['sig_hashalgo'], 'sha256')

        self.assertEqual(modinfo_dict['aliases'], [])
        self.assertEqual(modinfo_dict['parms'], {})
        self.assertEqual(modinfo_dict['features'], {})

    def test_modinfo_parser_with_aliases_parms(self):
        modinfo_sample_output = """filename:  /lib/modules/4.2.8-300.fc23.\
x86_64/kernel/drivers/block/loop.ko.xz\0alias=devname:loop-control\0\
alias=char-major-10-237\0alias=block-major-7-*\0license=GPL\0depends=\0\
intree=Y\0vermagic=4.2.8-300.fc23.x86_64 SMP mod_unload \0\
signer=Fedora kernel signing key\0\
sig_key=89:CE:AF:53:80:B1:D1:50:40:56:CB:00:AA:3C:46:34:6B:EB:2E:05\0\
sig_hashalgo=sha256\0\
parm:           max_loop:Maximum number of loop devices (int)\0\
parm:           max_part:Maximum number of partitions per loop \
device (int)\0"""

        modinfo_dict = sysmodules.parse_modinfo_0_output(
            modinfo_sample_output
        )

        self.assertEqual(
             modinfo_dict['filename'],
             '/lib/modules/4.2.8-300.fc23.x86_64/kernel/drivers'
             '/block/loop.ko.xz'
        )
        self.assertEqual(modinfo_dict['license'], 'GPL')
        self.assertEqual(modinfo_dict['depends'], [])
        self.assertEqual(modinfo_dict['intree'], 'Y')
        self.assertEqual(
            modinfo_dict['vermagic'],
            '4.2.8-300.fc23.x86_64 SMP mod_unload'
        )
        self.assertEqual(modinfo_dict['signer'], 'Fedora kernel signing key')
        self.assertEqual(
            modinfo_dict['sig_key'],
            '89:CE:AF:53:80:B1:D1:50:40:56:CB:00:AA:3C:46:34:6B:EB:2E:05'
        )
        self.assertEqual(modinfo_dict['sig_hashalgo'], 'sha256')

        self.assertEqual(
            modinfo_dict['aliases'],
            ['devname:loop-control', 'char-major-10-237', 'block-major-7-*']
        )

        self.assertEqual(
            modinfo_dict['parms'],
            {
                'max_loop': 'Maximum number of loop devices (int)',
                'max_part': 'Maximum number of partitions per loop '
                            'device (int)'
            }
        )
        self.assertEqual(modinfo_dict['features'], {})

    def test_modinfo_parser_multiple_author(self):
        modinfo_sample_output = """filename:       /lib/modules/4.2.8-300.\
fc23.x86_64/kernel/drivers/net/wireless/rtlwifi/rtl_pci.ko.xz\0\
description=PCI basic driver for rtlwifi\0license=GPL\0author=Larry \
Finger	<Larry.FInger@lwfinger.net>\0author=Realtek WlanFAE	\
<wlanfae@realtek.com>\0author=lizhaoming	<chaoming_li@realsil.\
com.cn>\0depends=mac80211,rtlwifi\0intree=Y\0vermagic=4.2.8-300.fc23.\
x86_64 SMP mod_unload \0signer=Fedora kernel signing key\0sig_key=89:\
CE:AF:53:80:B1:D1:50:40:56:CB:00:AA:3C:46:34:6B:EB:2E:05\0\
sig_hashalgo=sha256\0"""

        modinfo_dict = sysmodules.parse_modinfo_0_output(
            modinfo_sample_output
        )

        self.assertEqual(
            modinfo_dict['authors'],
            [
                'Larry Finger	<Larry.FInger@lwfinger.net>',
                'Realtek WlanFAE	<wlanfae@realtek.com>',
                'lizhaoming	<chaoming_li@realsil.com.cn>'
            ]
        )
        self.assertEqual(
             modinfo_dict['filename'],
             '/lib/modules/4.2.8-300.fc23.x86_64/kernel/drivers'
             '/net/wireless/rtlwifi/rtl_pci.ko.xz'
        )
        self.assertEqual(modinfo_dict['license'], 'GPL')
        self.assertEqual(modinfo_dict['depends'], ['mac80211', 'rtlwifi'])
        self.assertEqual(modinfo_dict['intree'], 'Y')
        self.assertEqual(
            modinfo_dict['vermagic'],
            '4.2.8-300.fc23.x86_64 SMP mod_unload'
        )
        self.assertEqual(modinfo_dict['signer'], 'Fedora kernel signing key')
        self.assertEqual(
            modinfo_dict['sig_key'],
            '89:CE:AF:53:80:B1:D1:50:40:56:CB:00:AA:3C:46:34:6B:EB:2E:05'
        )
        self.assertEqual(modinfo_dict['sig_hashalgo'], 'sha256')
        self.assertEqual(modinfo_dict['aliases'], [])
        self.assertEqual(modinfo_dict['parms'], {})
        self.assertEqual(modinfo_dict['features'], {})

    @mock.patch('wok.plugins.ginger.model.sysmodules.run_command')
    def test_model_list_loaded_modules(self, mock_run_command):
        mock_run_command.return_value = ["", "", 0]
        SysModulesModel().get_list()
        mock_run_command.assert_called_once_with(['lsmod'])

    @mock.patch('wok.plugins.ginger.model.sysmodules.run_command')
    def test_model_load_module(self, mock_run_command):
        mock_run_command.return_value = ["", "", 0]
        module_name = "fake_test_kernel_module"
        params = {'name': module_name}
        cmd = ['modprobe', module_name]
        SysModulesModel().create(params)
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.sysmodules.run_command')
    def test_model_load_module_with_parms(self, mock_run_command):
        mock_run_command.return_value = ["", "", 0]
        module_name = "fake_test_kernel_module"
        parms = "parameter1=value1 parameter2=100 parameter3=true"
        params = {'name': module_name, 'parms': parms}
        cmd = [
            'modprobe',
            module_name,
            'parameter1=value1',
            'parameter2=100',
            'parameter3=true'
        ]
        SysModulesModel().create(params)
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.sysmodules.parse_modinfo_0_output')
    @mock.patch('wok.plugins.ginger.model.sysmodules.run_command')
    def test_model_get_module_info(self, mock_run_command, mock_parser):
        mock_run_command.return_value = ["", "", 0]
        mock_parser.return_value = {}
        module_name = "fake_test_kernel_module"
        cmd = ['modinfo', '-0', module_name]
        SysModuleModel().lookup(module_name)
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.sysmodules.run_command')
    def test_model_unload_module(self, mock_run_command):
        mock_run_command.return_value = ["", "", 0]
        module_name = "fake_test_kernel_module"
        cmd = ['modprobe', '-r', module_name]
        SysModuleModel().delete(module_name)
        mock_run_command.assert_called_once_with(cmd)

    def get_modinfo_mlx4core_output(self):
        return """filename:       /lib/modules/\
3.18.22-354.el7_1.pkvm3_1_0.3600.1.ppc64le/kernel/drivers/net/\
ethernet/mellanox/mlx4/mlx4_core.ko\0version=2.2-1\0license=Dual BSD/GPL\0\
description=Mellanox ConnectX HCA low-level driver\0author=Roland Dreier\0\
srcversion=AB5AB33578ABBAE854E905B\0\
alias=pci:v000015B3d00001010sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d0000100Fsv*sd*bc*sc*i*\0\
alias=pci:v000015B3d0000100Esv*sd*bc*sc*i*\0\
alias=pci:v000015B3d0000100Dsv*sd*bc*sc*i*\0\
alias=pci:v000015B3d0000100Csv*sd*bc*sc*i*\0\
alias=pci:v000015B3d0000100Bsv*sd*bc*sc*i*\0\
alias=pci:v000015B3d0000100Asv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00001009sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00001008sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00001007sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00001006sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00001005sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00001004sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00001003sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00001002sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d0000676Esv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00006746sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00006764sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d0000675Asv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00006372sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00006750sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00006368sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d0000673Csv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00006732sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00006354sv*sd*bc*sc*i*\0\
alias=pci:v000015B3d0000634Asv*sd*bc*sc*i*\0\
alias=pci:v000015B3d00006340sv*sd*bc*sc*i*\0\
depends=\0intree=Y\0vermagic=3.18.22-354.el7_1.pkvm3_1_0.3600.1\
.ppc64le SMP mod_unload \0\
parm:           debug_level:Enable debug tracing if > 0 (int)\0\
parm:           msi_x:attempt to use MSI-X if nonzero (int)\0\
parm:           num_vfs:enable #num_vfs functions if num_vfs > 0
num_vfs=port1,port2,port1+2 (array of byte)\0\
parm:           probe_vf:number of vfs to probe by pf driver (num_vfs > 0)
probe_vf=port1,port2,port1+2 (array of byte)\0\
parm:           log_num_mgm_entry_size:log mgm size, that defines the num \
of qp per mcg, for example: 10 gives 248.range: 7 <= log_num_mgm_entry_size \
<= 12. To activate device managed flow steering when available, \
set to -1 (int)\0\
parm:           enable_64b_cqe_eqe:Enable 64 byte CQEs/EQEs when the FW \
supports this (default: True) (bool)\0\
parm:           log_num_mac:Log2 max number of MACs per ETH port \
(1-7) (int)\0\
parm:           log_num_vlan:Log2 max number of VLANs per ETH port \
(0-7) (int)\0\
parm:           use_prio:Enable steering by VLAN priority on ETH ports \
(deprecated) (bool)\0\
parm:           log_mtts_per_seg:Log2 number of MTT entries per segment \
(1-7) (int)\0\
parm:           port_type_array:Array of port types: HW_DEFAULT (0) is \
default 1 for IB, 2 for Ethernet (array of int)\0\
parm:           enable_qos:Enable Quality of Service support in the HCA \
(default: off) (bool)\0\
parm:           internal_err_reset:Reset device on internal errors if \
non-zero (default 1) (int)\0"""

    def test_modinfo_parser_mlx4core(self):
        modinfo_dict = sysmodules.parse_modinfo_0_output(
            self.get_modinfo_mlx4core_output()
        )

        self.assertEqual(modinfo_dict['authors'], ['Roland Dreier'])
        self.assertEqual(modinfo_dict['license'], 'Dual BSD/GPL')
        self.assertEqual(modinfo_dict['depends'], [])
        self.assertEqual(modinfo_dict['intree'], 'Y')
        self.assertEqual(len(modinfo_dict['aliases']), 27)
        self.assertEqual(len(modinfo_dict['parms']), 13)
        self.assertIn('num_vfs', modinfo_dict['parms'].keys())
        self.assertIn('probe_vf', modinfo_dict['parms'].keys())

    @mock.patch('wok.plugins.ginger.model.sysmodules.run_command')
    def test_model_get_mxl4core_info_returns_SRIOV(self, mock_run_command):
        mock_run_command.return_value = [
            self.get_modinfo_mlx4core_output(),
            "",
            0
        ]
        module_name = "mlx4-core"
        cmd = ['modinfo', '-0', module_name]
        lookup = SysModuleModel().lookup(module_name)
        mock_run_command.assert_called_once_with(cmd)

        self.assertEqual(lookup['authors'], ['Roland Dreier'])
        self.assertEqual(lookup['license'], 'Dual BSD/GPL')
        self.assertEqual(lookup['depends'], [])
        self.assertEqual(lookup['intree'], 'Y')

        self.assertEqual(len(lookup['aliases']), 27)
        self.assertEqual(len(lookup['parms']), 13)
        self.assertIn('num_vfs', lookup['parms'].keys())
        self.assertIn('probe_vf', lookup['parms'].keys())

        self.assertIn('SR-IOV', lookup['features'].keys())
        sriov_dic = lookup['features']['SR-IOV']
        self.assertIsNotNone(sriov_dic.get('desc'))
        self.assertEqual(sriov_dic['parms'], ['num_vfs', 'probe_vf'])

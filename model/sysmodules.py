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


from wok.exception import InvalidOperation, NotFoundError, OperationFailed
from wok.utils import run_command, wok_log


def parse_lsmod_output(lsmod_output):
    """
    Sample lsmod output:

Module                  Size  Used by
vfio_pci               32768  0
vfio_iommu_type1       20480  0
vfio_virqfd            16384  1 vfio_pci
vfio                   24576  2 vfio_iommu_type1,vfio_pci
loop                   28672  0
rfcomm                 69632  14
    """
    lines = lsmod_output.strip().split('\n')
    lines = lines[1:]
    modules_array = []
    for line in lines:
        tokens = line.split()
        module_stats = {
            'name': tokens[0],
            'size': tokens[1],
            'used_by': tokens[2],
        }
        if len(tokens) == 4:
            used_by_loaded = tokens[3].split(',')
            module_stats['used_by_loaded'] = used_by_loaded

        modules_array.append(module_stats)
    return modules_array


def parse_modinfo_0_output(modinfo_output):
    """
    Sample modinfo -0 output (single line output, lines are separated by
\0):

filename:  /lib/modules/4.2.8-300.fc23.x86_64/kernel/net/tipc/tipc.ko.xz\0
version=2.0.0\0 license=Dual BSD/GPL\0
description=TIPC: Transparent Inter Process Communication\0
srcversion=D8C4AF100F6EA6984637AD1depends=udp_tunnel,ip6_udp_tunnel\0
intree=Yvermagic=4.2.8-300.fc23.x86_64 SMP mod_unload\0
signer=Fedora kernel signing key\0
sig_key=89:CE:AF:53:80:B1:D1:50:40:56:CB:00:AA:3C:46:34:6B:EB:2E:05\0
sig_hashalgo=sha256\0
    """
    lines = modinfo_output.strip().split('\0')
    modinfo_dict = {}

    filename_line = lines[0].split()
    modinfo_dict['filename'] = filename_line[1]

    modinfo_dict['aliases'] = []
    modinfo_dict['authors'] = []
    modinfo_dict['parms'] = {}
    dict_attr_to_array = {'alias': 'aliases',
                          'author': 'authors',
                          'parm': 'parms'}

    lines = lines[1:]
    for line in lines:
        tokens = line.split('=', 1)
        attr_name = tokens[0]

        if attr_name == '':
            continue

        if 'parm:' in attr_name:
            tokens = line.split(':', 1)
            attr_name = tokens[0]

        attr_value = None
        if len(tokens) == 2:
            attr_value = tokens[1]

        if attr_name in ['alias', 'author', 'parm']:
            attr_name = dict_attr_to_array[attr_name]
            if attr_name == 'parms':
                parm_values = attr_value.split(':', 1)
                parm_name = parm_values[0].strip()
                parm_desc = '' if len(parm_values) != 2 else parm_values[1]
                modinfo_dict['parms'][parm_name] = parm_desc

            else:
                modinfo_dict[attr_name].append(attr_value.strip())

        elif attr_name == 'depends':
            deps = []
            if len(tokens) == 2:
                deps = attr_value.split(',')
                if deps == ['']:
                    deps = []
            modinfo_dict['depends'] = deps

        else:
            modinfo_dict[attr_name] = attr_value.rstrip()

    modinfo_dict['features'] = {}

    return modinfo_dict


def get_lsmod_output():
    out, err, returncode = run_command(['lsmod'])
    if returncode != 0:
        raise OperationFailed('GINSYSMOD00001E', {'err': err})
    else:
        return out


def get_modinfo_0_output(module_name):
    out, err, returncode = run_command(['modinfo', '-0', module_name])
    if returncode != 0:
        if 'not found' in err:
            raise NotFoundError('GINSYSMOD00002E', {'module': module_name})
        else:
            raise OperationFailed(
                'GINSYSMOD00003E',
                {'err': err, 'module': module_name}
            )
    else:
        return out


def get_loaded_modules_list():
    modules = parse_lsmod_output(get_lsmod_output())
    mod_names = []
    for mod in modules:
        mod_names.append(mod['name'])
    return mod_names


def load_kernel_module(module_name, parms=None):
    cmd = ['modprobe', module_name]
    if parms:
        cmd += parms
    out, err, returncode = run_command(cmd)
    if returncode != 0:
        if 'not found' in err:
            raise NotFoundError('GINSYSMOD00002E', {'module': module_name})
        else:
            raise OperationFailed(
                'GINSYSMOD00004E',
                {'err': err, 'module': module_name}
            )


def list_kernel_modules():
    result, err, returncode = run_command(["modprobe", "-c"])
    text = result.splitlines()

    modules = []

    # remove blacklist modules
    for i in range(len(text)):
        if text[i].startswith("#"):
            text = text[i+1:]
            break

    # get running modules
    loaded_modules = get_loaded_modules_list()

    # get modules
    for i in text:
        split = i.split()
        if len(split) > 0:
            mod_name = i.split().pop()
        else:
            continue
        if mod_name not in modules and mod_name not in loaded_modules:
            modules.append(mod_name)

    return modules


def unload_kernel_module(module_name):
    out, err, returncode = run_command(['modprobe', '-r', module_name])
    if returncode != 0:
        if 'not found' in err:
            raise NotFoundError('GINSYSMOD00002E', {'module': module_name})
        else:
            raise OperationFailed(
                'GINSYSMOD00005E',
                {'err': err, 'module': module_name}
            )


class SysModulesModel(object):

    def create(self, params):
        module_name = params['name']
        if module_name in get_loaded_modules_list():
            raise InvalidOperation('GINSYSMOD00006E', {'module': module_name})

        parms = None
        if 'parms' in params:
            parms = params['parms'].split()
        module_name = params['name']
        load_kernel_module(module_name, parms)
        wok_log.info('Kernel module %s loaded.' % module_name)
        return module_name

    def get_list(self, _all=None):
        if _all == "true":
            return list_kernel_modules()

        return get_loaded_modules_list()


class SysModuleModel(object):

    def get_features_per_module(self):
        mlx4_core_SRIOV = {
            'desc': 'SR-IOV: Single Root I/O Virtualization',
            'parms': ['num_vfs', 'probe_vf']
        }
        features_mod = {
            'mlx4-core': {'SR-IOV': mlx4_core_SRIOV},
            'mlx4_core': {'SR-IOV': mlx4_core_SRIOV}
        }
        return features_mod

    def __init__(self):
        self.features_mod = self.get_features_per_module()

    def lookup(self, name):
        modinfo_dict = parse_modinfo_0_output(get_modinfo_0_output(name))

        if self.features_mod.get(name) is not None:
            modinfo_dict['features'] = self.features_mod.get(name)

        modinfo_dict['name'] = name

        return modinfo_dict

    def delete(self, name):
        unload_kernel_module(name)
        wok_log.info('Kernel module %s unloaded.' % name)

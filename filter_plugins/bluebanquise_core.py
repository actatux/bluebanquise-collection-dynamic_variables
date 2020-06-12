# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 Bruno Travouillon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
'''Ansible Filter Plugins for BlueBanquise Core'''

import re

from ansible.errors import AnsibleFilterError

def icebergs_groups_list(groups, iceberg_naming):
    '''Get the list of icebergs groups.'''
    data = []

    for group in groups:
        if re.match('^'+iceberg_naming+'[0-9]+', group):
            data.append(group)

    return data

def number_of_icebergs(groups, iceberg_naming):
    '''Get the number of icebergs groups.'''
    return len(icebergs_groups_list(groups, iceberg_naming))

def current_iceberg(host):
    '''Get the iceberg of the target host.'''
    data = None

    if not host['icebergs_system']:
        data = host['iceberg_naming']+'1'
    else:
        for group in host['group_names']:
            m = re.match('^'+host['iceberg_naming']+'[0-9]+', group)
            # Return first match
            if m:
                data = group
                break

    if not data:
        raise AnsibleFilterError("Could not find any iceberg definition for host.")

    return data

def current_iceberg_number(host):
    '''Get the iceberg number of the target host.'''
    iceberg = current_iceberg(host)
    idx = re.sub(host['iceberg_naming'], '', iceberg)
    return idx

def current_iceberg_network(host):
    '''Get the name of the management network of the target host.'''
    return host['management_networks_naming'] + current_iceberg_number(host)

def equipment_groups_list(groups, equipment_naming):
    '''Get the list of equipment groups.'''
    data = []

    for group in groups:
        if re.match('^'+equipment_naming+'_.*', group):
            data.append(group)

    if not data:
        raise AnsibleFilterError(f"Could not find any groups that match equipment naming. (groups={groups})", equipment_naming)

    return sorted(set(data))

def master_groups_list(groups, master_groups_naming):
    '''Get the list of master groups.'''
    data = []

    for group in groups:
        if re.match('^'+master_groups_naming+'_.*', group):
            data.append(group)

    if not data:
        raise AnsibleFilterError(f"Could not find any groups that match master groups naming. (groups={groups})", master_groups_naming)

    return sorted(set(data))

def node_main_network(host):
    '''Get the management network of the target host.'''
    main_ntw = []
    netif = host['network_interfaces']
    iceberg_network = current_iceberg_network(host)

    for nic in netif:
        if (netif[nic]['network'] and
            re.match(iceberg_network+'-[a-zA-Z0-9]+', netif[nic]['network'])):
            main_ntw.append(netif[nic]['network']);

    if not main_ntw:
        raise AnsibleFilterError("Could not find the main network for host.")

    # list | unique | sort | first
    return sorted(set(main_ntw))[0]

def node_main_network_interface(host):
    '''Get the name of the interface connected to the management network for the target host.'''
    main_ntw_nic = []
    netif = host['network_interfaces']

    for nic in netif:
        if (netif[nic]['network'] and netif[nic]['network'] == node_main_network(host)):
            main_ntw_nic.append(nic)

    if not main_ntw_nic:
        raise AnsibleFilterError("Could not find the main network interface for host.")

    # The unique in j2_node_main_network makes me believe it is allowed to
    # define the same network several times, with one network interface each.
    # However, this may return as much network interfaces, which seems
    # unexpected for j2_node_main_network_interface.
    #
    # msg: filter={'eth1', 'eth3'} | j2=eth1eth3
    #
    # list | unique | join | trim
    # Note: not sure about the join | trim neither
    # Note: may miss a sort if possible if are valid
    return (''.join(sorted(set(main_ntw_nic)))).strip()

def _get_host_aliases(host):
    aliases = []

    if 'global_alias' in host:
        for alias in host['global_alias']:
            aliases.append(alias)

    # TODO {% if host_dict['alias'] is defined and host_iceberg == j2_current_iceberg %}
    if 'alias' in host:
        for alias in host['alias']:
            aliases.append(alias)

    return aliases

def get_hosts(inventory, domain_name):
    # TODO implement global_network_settings tests
    # TODO range group multi iceberg
    hosts = []

    for hostname in inventory:
        host = inventory[hostname]

        if 'network_interfaces' in host:
            main_ntw_itf = node_main_network_interface(host)
            aliases = _get_host_aliases(host)
            for itf in host['network_interfaces']:
                network = host['network_interfaces'][itf]
                if itf == main_ntw_itf:
                    hosts.append(
                        {'ip4': network['ip4'],
                         'hostname': [hostname,
                                      f"{hostname}.{domain_name}",
                                      f"{hostname}-{network['network']}"],
                         'aliases': aliases})
                else:
                    hosts.append({'ip4': network['ip4'],
                                'hostname': [f"{hostname}-{network['network']}"]})

        if 'bmc' in host:
            bmc = host['bmc']
            aliases = _get_host_aliases(bmc)
            hosts.append({'ip4': bmc['ip4'],
                          'hostname': [bmc['name']],
                          'aliases': aliases})

    return hosts

class FilterModule(object):
    ''' BlueBanquise Core filters. '''

    def filters(self):
        return {
            'icebergs_groups_list': icebergs_groups_list,
            'number_of_icebergs': number_of_icebergs,
            'current_iceberg': current_iceberg,
            'current_iceberg_number': current_iceberg_number,
            'current_iceberg_network': current_iceberg_network,
            'equipment_groups_list': equipment_groups_list,
            'master_groups_list': master_groups_list,
            'node_main_network': node_main_network,
            'node_main_network_interface': node_main_network_interface,
            'get_hosts': get_hosts,
        }

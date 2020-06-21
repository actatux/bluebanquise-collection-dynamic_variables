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
'''Ansible Filter plugin to extract data from BlueBanquise inventories'''

from ansible.errors import AnsibleFilterError
from ansible_collections.bluebanquise.dynamic_variables.plugins.filter.core import node_main_network_interface

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

def extract_hosts(inventory, domain_name):
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
    ''' BlueBanquise extract filters. '''

    def filters(self):
        return {
            'extract_hosts': extract_hosts,
        }

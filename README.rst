dynamic_variables
-----------------

Description
^^^^^^^^^^^

This role allows to define the dynamic variables for `BlueBanquise`_ with
custom Ansible filters instead of relying on the inventory.

By default, the j2 variables are defined in the inventory which is managed by
the end-user. A user might manage the inventory in a different way than the
core roles of BlueBanquise (e.g., SCM vs. rpm). Moreover, if the core should
add some new j2 variables or update some logic in existing variables, the
end-user would need to be very careful when upgrading to apply the new logic in
the inventory files.

Installation
^^^^^^^^^^^^

Clone this role to your BlueBanquise custom roles directory:

.. code-block::

  $ cd /etc/bluebanquise
  $ git clone https://github.com/actatux/bluebanquise-role-dynamic_variables \
      roles/custom/dynamic_variables

If you don't want to mind with core-logic in your inventory, you should
definitely consider including this role at the beginning of your playbooks.

.. code-block:: yaml

  ---
  - name: My playbook
    hosts: "{{ target }}"

    roles:
      - role: dynamic_variables

Tests
^^^^^

There is a task file `tests.yml` which is included if `check_filters: True`.
Its purpose is to run the filters against the inventory and compare the results
with these of the j2 variables from the inventory. In other words, it allows to
ensure the logic of the filters match the logic in the inventory and won't
break the core. To run these tests, you must keep the j2 definitions in your
inventory. This is primarily intended for non-regression tests.

Example playbook to run the tests:

.. code-block:: yaml

  ---
  - name: Use filters to set j2 variables from the inventory
    # So we don't need to rely on the j2 variables which are defined
    # in the user's inventory.
    hosts: "{{ target }}"
    vars:
      check_filters: True

    roles:
      - name: dynamic_variables
        role: dynamic_variables

    tasks:
      - name: Print j2 variables from the filters
        debug:
          msg: |
            j2_icebergs_groups_list={{ j2_icebergs_groups_list }}
            j2_number_of_icebergs={{ j2_number_of_icebergs }}
            j2_current_iceberg={{ j2_current_iceberg }}
            j2_current_iceberg_number={{ j2_current_iceberg_number }}
            j2_current_iceberg_network={{ j2_current_iceberg_network }}
            j2_equipment_groups_list={{ j2_equipment_groups_list }}
            j2_master_groups_list={{ j2_master_groups_list }}
            j2_node_main_network={{ j2_node_main_network }}
            j2_node_main_network_interface={{ j2_node_main_network_interface }}

If you don't plan to check the logic, you can discard the j2_* definitions from
your inventory.

Changelog
^^^^^^^^^

* 1.0.0: Role creation. Bruno Travouillon <devel@travouillon.fr>

.. _`BlueBanquise`: http://www.bluebanquise.com/

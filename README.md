# Ansible Collection - bluebanquise.dynamic_variables

## Description

This Ansible collection provides plugins and roles to define and use the
dynamic variables for [BlueBanquise](http://www.bluebanquise.com) with custom
filters instead of relying on the inventory.

By default, the j2 variables are defined in the inventory which is managed by
the end-user. A user might manage the inventory in a different way than the
core roles of BlueBanquise (e.g., SCM vs. rpm). Moreover, if the core should
add some new j2 variables or update some logic in existing variables, the
end-user would need to be very careful when upgrading to apply the new logic in
the inventory files.

## Installation

Clone this project:

  ```
  $ git clone https://github.com/actatux/bluebanquise-collection-dynamic_variables.git
  ```

Build and install the collection:

  ```
  $ ansible-galaxy collection build
  $ ansible-galaxy collection install bluebanquise-dynamic_variables-1.0.0.tar.gz
  ```

Include this collection at the beginning of your playbooks and add the role
`j2_variables`:

  ```
  ---
  - name: My playbook
    hosts: all
    collections:
      - bluebanquise.dynamic_variables
    roles:
      - role: j2_variables
  ```

## Tests

To test the filters, run the playbook `tests/main.yml` with your inventory. The
purpose of this playbook is to run the filters against the inventory and
compare the results with these of the j2 variables from the same inventory. In
other words, it allows to ensure the logic of the filters match the logic in
the inventory and won't break the core. To run these tests, you must keep the
j2 definitions in your inventory. This is primarily intended for non-regression
tests.

To run the tests, you can build and install the collection locally:

  ```
  $ ansible-galaxy collection build --output-path /tmp/tests
  $ ansible-galaxy collection install -p /tmp/tests/collections \
      /tmp/tests/bluebanquise-dynamic_variables-1.0.0.tar.gz
  $ ANSIBLE_COLLECTIONS_PATHS=/tmp/tests/collections/ ansible-playbook \
      tests/main.yml -i /path/to/your/inventory/
  ```

If you don't plan to check the logic, you can discard the j2_* definitions from
your inventory.

## Changelog

* 1.0.0: Migrate role to collection. Bruno Travouillon <devel@travouillon.fr>
* 0.1.0: Role creation. Bruno Travouillon <devel@travouillon.fr>

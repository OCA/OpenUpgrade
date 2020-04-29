# Copyright 2020 Tecnativa - Jairo Llopis
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Let action direct to the tree view by default, as expected
    env.ref('auth_ldap.action_ldap_installer').view_id = False

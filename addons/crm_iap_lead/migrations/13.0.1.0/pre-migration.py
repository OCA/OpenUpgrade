# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

to_install = [
    'crm_iap_lead_website',
]


def install_new_modules(cr):
    sql = """
    UPDATE ir_module_module
    SET state='to install'
    WHERE name in %s AND state='uninstalled'
    """ % (tuple(to_install),)
    openupgrade.logged_query(cr, sql)


@openupgrade.migrate()
def migrate(env, version):
    install_new_modules(env.cr)

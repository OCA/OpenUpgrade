# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

to_install = [
    "sale_coupon",
]


def install_new_modules(cr):
    sql = """
    UPDATE ir_module_module
    SET state='to install'
    WHERE name = {} AND state='uninstalled'
    """.format(
        tuple(to_install),
    )
    openupgrade.logged_query(cr, sql)


@openupgrade.migrate()
def migrate(env, version):
    install_new_modules(env.cr)

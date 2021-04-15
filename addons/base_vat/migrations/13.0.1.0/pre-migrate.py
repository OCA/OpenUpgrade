# Copyright 2021 Demolium BV <http://www.demolium.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def merge_base_vat_sanitized_column(env):
    openupgrade.logged_query(
        env.cr,
        "UPDATE res_partner "
        "SET vat = sanitized_vat "
        "WHERE vat != sanitized_vat")


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "res_partner", "sanitized_vat"):
        merge_base_vat_sanitized_column(env)

# Copyright 2024 Coop IT Easy <https://coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_fields_renames = [
    (
        "res.partner",
        "res_partner",
        "implemented_count",
        "implemented_partner_count",
    ),
]


def _fill_res_partner_activation_active(env):
    """Fill active for res.partner.activation"""
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE res_partner_activation
        ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT true
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE res_partner_activation ALTER COLUMN active DROP DEFAULT
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_renames)
    _fill_res_partner_activation_active(env)

# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from openupgradelib import openupgrade


def remove_res_country_state_ir_model_data(env):
    """
    remove obsolete ir.model.data entries, without removing the data itself,
    in case it is used.
    """
    openupgrade.logged_query(
        env.cr,
        """
        delete from ir_model_data
        where
            module = 'l10n_be' and
            model = 'res.country.state'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    remove_res_country_state_ir_model_data(env)

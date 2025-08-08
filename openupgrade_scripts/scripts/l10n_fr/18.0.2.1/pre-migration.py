# Copyright 2025 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_model_data
        SET module = 'l10n_fr_account'
        WHERE module = 'l10n_fr' AND model IN (
            'account.account.tag', 'account.report', 'account.report.column',
            'account.report.expression', 'account.report.line',
            'ir.config_parameter', 'res.bank')
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_module_module
        SET state='to upgrade'
        WHERE name = 'l10n_fr_account' AND state='uninstalled'""",
    )

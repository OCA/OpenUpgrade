# Copyright 2026 Le Filament
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _remove_autocreated_expression(env):
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM account_report_expression
        WHERE label='balance'
        AND report_line_id IN (
            SELECT res_id FROM ir_model_data
            WHERE module='l10n_fr'
            AND name in (
                'tax_report_16', 'tax_report_23', 'tax_report_TIC_total',
                'tax_report_X4', 'tax_report_Y1', 'tax_report_Y2',
                'tax_report_Y3', 'tax_report_Z4', 'tax_report_32')
            AND model='account.report.line')
        AND id NOT IN (
            SELECT res_id FROM ir_model_data
            WHERE module='l10n_fr' AND model='account.report.expression'
        )
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _remove_autocreated_expression(env)

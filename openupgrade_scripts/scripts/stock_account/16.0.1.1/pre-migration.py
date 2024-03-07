# Copyright 2023 Coop IT Easy - Robin Keunen
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _account_move_line_fill_cogs_display_type(env):
    """
    Fill the display type for journal items corresponding to Cost of Good Sold
    lines (COGS) for customer invoices.
    In v15, the lines were set to is_anglo_saxon_line == True, in v16
    field display_display is used.

    openupgrade account migration script already sets display_type
    in _account_move_fast_fill_display_type (pre-migration)

    cf _stock_account_prepare_anglo_saxon_out_lines_vals
    :param env:
    :return:
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line
           SET display_type = 'cogs'
        WHERE is_anglo_saxon_line;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _account_move_line_fill_cogs_display_type(env)

# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(
        env.cr, [("board.access_board_board all", "board.access_board_board_all")]
    )
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "board",
        ["menu_board_my_dash"],
        False,
    )

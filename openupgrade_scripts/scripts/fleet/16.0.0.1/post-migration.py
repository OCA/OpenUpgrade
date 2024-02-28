# Copyright 2023 Viindoo - Nguyễn Việt Lâm
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "fleet", "16.0.0.1/noupdate_changes.xml")

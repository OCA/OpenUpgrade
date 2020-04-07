# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Fill empty code field in link_tracker_code to later
    # replace with computed function in pre-migration
    openupgrade.logged_query(
        env.cr, """
        UPDATE link_tracker_code
        SET code = 'openupgrade_temp_code'
        WHERE code IS NULL
        """
    )

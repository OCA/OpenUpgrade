# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_link_tracker_code(env):
    tracker_codes = env['link.tracker.code'].search([('code', '=', 'openupgrade_temp_code')])
    for tracker in tracker_codes:
        tracker.code = tracker.get_random_code_string()


@openupgrade.migrate()
def migrate(env, version):
    fill_link_tracker_code(env)

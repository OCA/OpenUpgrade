# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _discuss_channel_computation(env):
    rating_last_discuss = (
        env["discuss.channel"].with_context(active_test=False).search([])
    )
    rating_last_discuss._compute_rating_last_value()


@openupgrade.migrate()
def migrate(env, version):
    _discuss_channel_computation(env)

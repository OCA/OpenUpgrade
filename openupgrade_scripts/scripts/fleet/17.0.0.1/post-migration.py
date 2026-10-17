# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _compute_image_128(env):
    """The vehicle models and the vehicles now inherit avatar.mixin, so their
    image_128, related to the brand image, is now stored as an attachment, which is
    not computed when the field is created. Compute it, the models first, as the
    vehicle image is the one of its model.
    """
    for model_name in ("fleet.vehicle.model", "fleet.vehicle"):
        records = env[model_name].with_context(active_test=False).search([])
        env.add_to_compute(records._fields["image_128"], records)
        records._recompute_recordset(["image_128"])


@openupgrade.migrate()
def migrate(env, version):
    _compute_image_128(env)

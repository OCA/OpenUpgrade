# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _onboarding_step_convert_field_m2o_to_m2m(env):
    # Convert m2o to m2m in 'onboarding.onboarding.step'
    openupgrade.m2o_to_x2m(
        env.cr,
        env["onboarding.onboarding.step"],
        "onboarding_onboarding_step",
        "onboarding_ids",
        "onboarding_id",
    )


def _onboarding_progress_step_convert_field_m2o_to_m2m(env):
    """
    Convert m2o to m2m in 'onboarding.progress.step'
    """
    openupgrade.m2o_to_x2m(
        env.cr,
        env["onboarding.progress.step"],
        "onboarding_progress_step",
        "progress_ids",
        "progress_id",
    )


@openupgrade.migrate()
def migrate(env, version):
    _onboarding_step_convert_field_m2o_to_m2m(env)
    _onboarding_progress_step_convert_field_m2o_to_m2m(env)

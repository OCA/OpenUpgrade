# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def hr_candidate2hr_applicant(env):
    """
    Prepare merging hr.candidate into hr.applicant:
    Merge models
    Rename hr_candidate to legacy table
    Lift constraints on hr_candidate.id
    """
    openupgrade.merge_models(env.cr, "hr.candidate", "hr.applicant", "candidate_id")
    openupgrade.rename_tables(env.cr, [("hr_candidate", None)])
    openupgrade.lift_constraints(
        env.cr, openupgrade.get_legacy_name("hr_candidate"), "id", cascade=True
    )
    openupgrade.remove_tables_fks(env.cr, [openupgrade.get_legacy_name("hr_candidate")])


@openupgrade.migrate()
def migrate(env, version):
    hr_candidate2hr_applicant(env)

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
    legacy_table = openupgrade.get_legacy_name("hr_candidate")
    # PostgreSQL >= 17 catalogs NOT NULL as a named constraint and refuses to
    # drop it while the column is still part of a primary key, even when the
    # pkey drop is queued in the same ALTER TABLE statement (as
    # openupgrade.lift_constraints does). Drop the pkey first, on its own, so
    # the remaining lift_constraints() call only has the not-null constraint
    # left to lift.
    env.cr.execute(
        "alter table {} drop constraint if exists {} cascade".format(
            legacy_table, legacy_table + "_pkey"
        )
    )
    openupgrade.lift_constraints(env.cr, legacy_table, "id", cascade=True)
    openupgrade.remove_tables_fks(env.cr, [legacy_table])


@openupgrade.migrate()
def migrate(env, version):
    hr_candidate2hr_applicant(env)

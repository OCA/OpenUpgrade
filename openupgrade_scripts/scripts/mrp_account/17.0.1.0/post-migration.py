# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _fill_account_analytic_account_mrp_bom_rel(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_analytic_account_mrp_bom_rel
        (mrp_bom_id, account_analytic_account_id)
        SELECT mb.id, SUBSTRING(ip.value_reference, 26)::int
        FROM mrp_bom mb
        JOIN ir_model_fields imf
            ON imf.model = 'mrp.bom' AND imf.name = 'analytic_account_id'
        JOIN ir_property ip
            ON ip.fields_id = imf.id AND ip.res_id = 'mrp.bom,' || mb.id::varchar
        """,
    )


def _fill_account_analytic_account_mrp_production_rel(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_analytic_account_mrp_production_rel
        (mrp_production_id, account_analytic_account_id)
        SELECT DISTINCT mp.id, aaa.id
        FROM mrp_production mp
        CROSS JOIN LATERAL jsonb_object_keys(mp.analytic_distribution) AS dist(key)
        JOIN account_analytic_account aaa ON aaa.id = dist.key::int
        WHERE mp.analytic_distribution IS NOT NULL
        """,
    )


def _fill_account_analytic_account_mrp_workcenter_rel(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_analytic_account_mrp_workcenter_rel
        (mrp_workcenter_id, account_analytic_account_id)
        SELECT id, costs_hour_account_id
        FROM mrp_workcenter
        WHERE costs_hour_account_id IS NOT NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_account_analytic_account_mrp_bom_rel(env)
    _fill_account_analytic_account_mrp_production_rel(env)
    _fill_account_analytic_account_mrp_workcenter_rel(env)
    openupgrade.m2o_to_x2m(
        env.cr,
        env["mrp.workorder"],
        "mrp_workorder",
        "mo_analytic_account_line_ids",
        "mo_analytic_account_line_id",
    )
    openupgrade.m2o_to_x2m(
        env.cr,
        env["mrp.workorder"],
        "mrp_workorder",
        "wc_analytic_account_line_ids",
        "wc_analytic_account_line_id",
    )

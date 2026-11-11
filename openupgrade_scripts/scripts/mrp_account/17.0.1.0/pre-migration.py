# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade, openupgrade_160


def _fill_production_analytic_distribution(env):
    """The OCA module mrp_stock_analytic already stores an analytic distribution
    on the production in 16.0: keep it, and only convert the analytic account of
    the productions that do not have one.
    """
    existing = openupgrade.column_exists(
        env.cr, "mrp_production", "analytic_distribution"
    )
    legacy = openupgrade.get_legacy_name("analytic_distribution")
    if existing:
        openupgrade.rename_columns(
            env.cr, {"mrp_production": [("analytic_distribution", legacy)]}
        )
    openupgrade_160.fill_analytic_distribution(env, "mrp_production", m2m_rel=False)
    if existing:
        openupgrade.logged_query(
            env.cr,
            f"""
            UPDATE mrp_production
            SET analytic_distribution = {legacy}
            WHERE {legacy} IS NOT NULL
            """,
        )


@openupgrade.migrate()
def migrate(env, version):
    _fill_production_analytic_distribution(env)
    openupgrade_160.fill_analytic_distribution(
        env,
        "mrp_workcenter",
        m2m_rel=False,
        analytic_account_column="costs_hour_account_id",
    )

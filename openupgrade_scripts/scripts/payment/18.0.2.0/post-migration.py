# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade, openupgrade_merge_records


def merge_ogone_sips_into_worldline(env):
    ogone = env["payment.provider"].search([("code", "=", "ogone")])
    sips = env["payment.provider"].search([("code", "=", "sips")])
    worldline = env.ref("payment.payment_provider_worldline")
    to_merge = []
    if ogone:
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE payment_provider
            SET state = 'disabled'
            WHERE code = 'ogone'
            """,
        )
        to_merge.extend(ogone.ids)
    if sips:
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE payment_provider
            SET state = 'disabled'
            WHERE code = 'sips'
            """,
        )
        to_merge.extend(sips.ids)
    if to_merge:
        openupgrade_merge_records.merge_records(
            env,
            "payment.provider",
            to_merge,
            worldline.id,
            {"openupgrade_other_fields": "preserve"},
            delete=False,
        )


@openupgrade.migrate()
def migrate(env, version):
    merge_ogone_sips_into_worldline(env)
    openupgrade.load_data(env, "payment", "18.0.2.0/noupdate_changes_manual.xml")
    openupgrade.load_data(env, "payment", "18.0.2.0/noupdate_changes.xml")
    imd = env["ir.model.data"].search(
        [("module", "=", "payment_ogone"), ("name", "=", "payment_provider_ogone")]
    )
    if imd:
        imd.unlink()
    imd = env["ir.model.data"].search(
        [("module", "=", "payment"), ("name", "=", "payment_provider_sips")]
    )
    if imd:
        imd.unlink()

# Copyright 2025 Tecnativa - Carlos Roca
# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _pre_create_and_fill_l10n_es_is_simplified(env):
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE account_move ADD COLUMN l10n_es_is_simplified BOOL DEFAULT false",
    )
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE account_move ALTER COLUMN l10n_es_is_simplified DROP DEFAULT",
    )
    # The field is filled with the first part of the compute without considering the
    # partner_simplified part, as this record is created during the installation.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET l10n_es_is_simplified = (
            partner_id IS NULL
            AND move_type IN ('in_receipt', 'out_receipt')
        )
        """,
    )


def _xml_id_renaming_account_tax_template(env):
    """In 17.0, some tax templates XML-ID have been changed. With this method, the
    XML-IDs are set correctly.
    """
    for src, dest in [
        ("s_iva0_e", "s_iva0_g_e"),
        ("s_iva0_ic", "s_iva0_g_i"),
        ("s_iva0", "s_iva0_nsd"),
    ]:
        imds = env["ir.model.data"].search(
            [
                ("module", "=", "account"),
                ("model", "=", "account.tax"),
                ("name", "=like", f"%_account_tax_template_{src}"),
            ]
        )
        for imd in imds:
            imd.name = imd.name.replace(
                f"account_tax_template_{src}", f"account_tax_template_{dest}"
            )


def _remove_xml_id_account_fiscal_position(env):
    # In 17.0 account.fiscal.position.tax and account.fiscal.position.account don't have
    # xml_id. With this method they are removed.
    for company in env["res.company"].search([]):
        openupgrade.logged_query(
            env.cr,
            f"""
            DELETE FROM ir_model_data
            WHERE module='l10n_es'
            AND model IN (
                'account.fiscal.position.tax', 'account.fiscal.position.account'
            ) AND name LIKE '{company.id}_%'
            """,
        )


def _handle_dua_transition(env):
    """Handle if you had l10n_es_dua module from OCA/l10n-spain installed."""
    openupgrade.rename_xmlids(
        env.cr,
        [
            ("l10n_es.producto_dua_valoracion_21", "l10n_es.product_dua_valuation_21"),
            ("l10n_es.producto_dua_valoracion_10", "l10n_es.product_dua_valuation_10"),
            ("l10n_es.producto_dua_valoracion_4", "l10n_es.product_dua_valuation_4"),
            (
                "l10n_es.producto_dua_valoracion_21_product_template",
                "l10n_es.product_dua_valuation_21_product_template",
            ),
            (
                "l10n_es.producto_dua_valoracion_10_product_template",
                "l10n_es.product_dua_valuation_10_product_template",
            ),
            (
                "l10n_es.producto_dua_valoracion_4_product_template",
                "l10n_es.product_dua_valuation_4_product_template",
            ),
        ],
    )
    record = env.ref("l10n_es.producto_dua_compensacion", False)
    if record:
        record.active = False
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_model_data
        WHERE module='l10n_es'
        AND name IN (
            'producto_dua_compensacion',
            'producto_dua_compensacion_product_template'
        )
        """,
    )
    # Tax groups
    imds = env["ir.model.data"].search(
        [
            ("name", "=like", "%_tax_group_dua_exento"),
            ("model", "=", "account.tax.group"),
        ]
    )
    for imd in imds:
        imd.name = imd.name.replace("tax_group_dua_exento", "tax_group_dua_exempt")
    # Taxes
    imds = env["ir.model.data"].search(
        [
            ("name", "=like", "%_account_tax_template_p_dua0"),
            ("module", "=", "account"),
            ("model", "=", "account.tax"),
        ]
    )
    for imd in imds:
        imd.name = imd.name.replace(
            "account_tax_template_p_dua0", "account_tax_template_p_dua_exempt"
        )


@openupgrade.migrate()
def migrate(env, version):
    _pre_create_and_fill_l10n_es_is_simplified(env)
    _xml_id_renaming_account_tax_template(env)
    _remove_xml_id_account_fiscal_position(env)
    _handle_dua_transition(env)

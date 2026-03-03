# Copyright 2026 Tecnativa - David Bañón Gil
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _compute_new_tax_type(env):
    openupgrade.logged_query(
        env.cr,
        """
    UPDATE account_tax t
    SET l10n_mx_tax_type =
        CASE
            WHEN c.code = 'MX' THEN 'iva'
            ELSE NULL
        END
    FROM res_country c
    WHERE t.country_id = c.id;
    """,
    )


def _delete_analytic_tags(env):
    l10n_mx_xmlids = [
        "tag_iva",
        "tag_isr",
        "tag_ieps",
        "tag_diot_0",
        "tag_diot_16_refund",
        "tag_diot_16",
        "tag_diot_16_imp",
        "tag_diot_16_imp_non_cre",
        "tag_diot_16_imp_refund",
        "tag_diot_16_non_cre",
        "tag_diot_8",
        "tag_diot_8_non_cre",
        "tag_diot_8_refund",
        "tag_diot_8_south",
        "tag_diot_8_south_non_cre",
        "tag_diot_8_south_refund",
        "tag_diot_16_imp_int",
        "tag_diot_16_imp_int_non_cre",
        "tag_diot_16_imp_int_refund",
        "tag_diot_ret",
        "tag_diot_exento",
        "tag_diot_exento_imp",
        "tag_diot_no_obj",
    ]
    openupgrade.delete_records_safely_by_xml_id(
        env, [f"l10n_mx.{x}" for x in l10n_mx_xmlids]
    )


@openupgrade.migrate()
def migrate(env, version):
    _delete_analytic_tags(env)
    _compute_new_tax_type(env)

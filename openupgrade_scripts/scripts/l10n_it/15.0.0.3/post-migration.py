from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    to_delete_xml_ids = [
        "l10n_it.tax_group_iva_10_de_50",
        "l10n_it.tax_group_iva_20_de_10",
        "l10n_it.tax_group_iva_20_de_15",
        "l10n_it.tax_group_iva_20_de_40",
        "l10n_it.tax_group_iva_20_de_50",
        "l10n_it.tax_group_iva_21_de_10",
        "l10n_it.tax_group_iva_21_de_15",
        "l10n_it.tax_group_iva_21_de_40",
        "l10n_it.tax_group_iva_21_de_50",
        "l10n_it.tax_group_iva_21_inde",
        "l10n_it.tax_group_iva_22_de_10",
        "l10n_it.tax_group_iva_22_de_15",
        "l10n_it.tax_group_iva_22_de_40",
        "l10n_it.tax_group_iva_22_de_50",
        "l10n_it.tax_group_iva_22_inde",
        "l10n_it.tax_group_iva_4_de_50",
    ]
    openupgrade.delete_records_safely_by_xml_id(env, to_delete_xml_ids)

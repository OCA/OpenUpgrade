from openupgradelib import openupgrade

# List of XML IDs of tax reports defined in l10n_it
# These include the generic VAT report and the annual reports
ITALIAN_REPORT_XML_IDS = [
    "l10n_it.tax_report_vat",
    "l10n_it.tax_annual_report_vat_va",
    "l10n_it.tax_annual_report_vat_ve",
    "l10n_it.tax_annual_report_vat_vf",
    "l10n_it.tax_annual_report_vat_vh",
    "l10n_it.tax_annual_report_vat_vj",
    "l10n_it.tax_annual_report_vat_vl",
]


@openupgrade.migrate()
def migrate(env, version):
    """
    Remove existing reports and related records to avoid duplications.
    """
    if not version:
        return

    # Try standard cleanup first, this usually isn't enough
    openupgrade.delete_records_safely_by_xml_id(
        env, ITALIAN_REPORT_XML_IDS, delete_childs=True
    )

# Copyright 2025 Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openupgradelib import openupgrade

IRNR_TAX_GROUP_MAP = {
    "l10n_es.%s_account_tax_template_s_irpfnrnue24": "l10n_es.tax_group_retenciones_24",
    "l10n_es.%s_account_tax_template_p_irpfnrnue24p": "l10n_es.tax_group_retenciones_24",
    "l10n_es.%s_account_tax_template_s_irpfnrue19": "l10n_es.tax_group_retenciones_19",
    "l10n_es.%s_account_tax_template_p_irpfnrue19p": "l10n_es.tax_group_retenciones_19",
    "l10n_es.%s_account_tax_template_s_irpfnrnue0": "l10n_es.tax_group_retenciones_0",
    "l10n_es.%s_account_tax_template_p_irpfnrnue0p": "l10n_es.tax_group_retenciones_0",
    "l10n_es.%s_account_tax_template_s_irpfnrue0": "l10n_es.tax_group_retenciones_0",
    "l10n_es.%s_account_tax_template_p_irpfnrue0p": "l10n_es.tax_group_retenciones_0",
}


@openupgrade.migrate()
def migrate(env, version):
    for company in env["res.company"].search([]):
        for irnr_tax_ref in IRNR_TAX_GROUP_MAP:
            irnr_tax = env.ref(irnr_tax_ref % company.id, raise_if_not_found=False)
            if irnr_tax:
                irnr_tax.tax_group_id = env.ref(IRNR_TAX_GROUP_MAP[irnr_tax_ref])

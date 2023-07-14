# Copyright 2023 Tecnativa - Víctor Martínez
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    for company in env["res.company"].search([]):
        wizard = env["base.document.layout"].with_company(company).create({})
        company.write(
            {
                "report_footer": wizard.report_footer,
                "company_details": wizard.company_details,
            }
        )

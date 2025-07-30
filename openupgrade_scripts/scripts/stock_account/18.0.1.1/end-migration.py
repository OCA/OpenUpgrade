# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    for company in env["res.company"].search([("chart_template", "!=", False)]):
        if not company.country_id.code:
            continue
        module_name = "l10n_" + company.country_id.code.lower()
        l10n_module = env["ir.module.module"].search(
            [
                ("name", "=", module_name),
                ("state", "=", "installed"),
            ]
        )
        if not l10n_module:
            continue
        template_code = company.chart_template
        ChartTemplate = env["account.chart.template"].with_company(company)
        full_data = ChartTemplate._get_chart_template_data(template_code)
        try:
            ChartTemplate._load_wip_accounts(company, full_data["res.company"])
        except ValueError:
            _logger.info("Cannot load wip accounts for %s", module_name)
            continue

from markupsafe import Markup
from openupgradelib import openupgrade


def account_move_line_is_storno(env):
    """
    Compute is_storno on lines of companies with storno accounting
    """
    lines_to_recompute = env["account.move.line"].search(
        [("company_id.account_storno", "=", True)]
    )
    lines_to_recompute._compute_is_storno()


def res_company(env):
    """
    Set fields expense_account_id, income_account_id, price_difference_account_id
    from localization if not set elsewhere and the localization sets it
    """
    admin_channel = env.ref("mail.channel_admin", False)
    for company in env["res.company"].search([]):
        AccountChartTemplate = env["account.chart.template"].with_context(
            default_company_id=company.id,
            allowed_company_ids=company.ids,
            tracking_disable=True,
            delay_account_group_sync=True,
            lang="en_US",
            chart_template_load=True,
        )
        if company.chart_template not in AccountChartTemplate._template_register:
            if admin_channel:
                admin_channel.message_post(
                    body=Markup(
                        "<h1>Openupgrade v18: account</h1>"
                        f"<p>Chart template {company.chart_template} unknown "
                        "(not yet migrated?)</p>"
                    )
                )
            continue
        template_data = AccountChartTemplate._get_chart_template_data(
            company.chart_template
        )
        company_template_data = {
            company_id: {
                key: value
                for key, value in company_data.items()
                if key
                in (
                    "expense_account_id",
                    "income_account_id",
                    "price_difference_account_id",
                )
                and not company[key]
            }
            for company_id, company_data in template_data["res.company"].items()
        }
        AccountChartTemplate._load_data({"res.company": company_template_data})


@openupgrade.migrate()
def migrate(env, version):
    account_move_line_is_storno(env)
    # res_company(env)

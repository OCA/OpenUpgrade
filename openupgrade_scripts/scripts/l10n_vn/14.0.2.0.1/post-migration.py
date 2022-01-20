from openupgradelib import openupgrade


def create_account_account(env, company):
    """Create new accounts in v14"""
    vn_template = env.ref("l10n_vn.vn_template", raise_if_not_found=False)
    query = """INSERT INTO account_account
        ( name, code, user_type_id, company_id, reconcile)
        SELECT name, code, user_type_id, %s, reconcile
        FROM account_account_template
        WHERE chart_template_id = %s AND
            code IN ('1541', '1542', '1543', '1544', '911')"""
    openupgrade.logged_query(
        env.cr,
        query,
        (company.id, vn_template.id),
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "l10n_vn", "14.0.2.0.1/noupdate_changes.xml")
    for company in env["res.company"].search(
        [("chart_template_id", "=", env.ref("l10n_vn.vn_template").id)]
    ):
        create_account_account(env, company)

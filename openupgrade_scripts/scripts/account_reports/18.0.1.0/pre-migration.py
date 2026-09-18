from openupgradelib import openupgrade


XMLID_RENAMES = [
    (
        'account_reports.account_financial_report_totalincome0',
        'account_reports.account_financial_report_operating_income0',
    ),
    (
        'account_reports.account_financial_report_totalincome0_balance',
        'account_reports.account_financial_report_operating_income0_balance',
    ),
]


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.rename_xmlids(cr, XMLID_RENAMES)

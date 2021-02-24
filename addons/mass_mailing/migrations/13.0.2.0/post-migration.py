# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    # mail.mass_mailing.list
    'mass_mailing.mass_mail_list_1',
]


def update_mailing_domain_filter(env):
    if openupgrade.table_exists(env.cr, 'account_invoice'):
        openupgrade.logged_query(
            env.cr, """
            UPDATE mailing_mailing
            SET mailing_domain = replace(mailing_domain,
                '''customer''', '''customer_rank''')
            WHERE mailing_domain LIKE '%''customer''%'""",
        )
        openupgrade.logged_query(
            env.cr, """
            UPDATE mailing_mailing
            SET mailing_domain = replace(mailing_domain,
                '''supplier''', '''supplier_rank''')
            WHERE mailing_domain LIKE '%''supplier''%'""",
        )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    update_mailing_domain_filter(env)
    openupgrade.load_data(env.cr, 'mass_mailing', 'migrations/13.0.2.0/noupdate_changes.xml')

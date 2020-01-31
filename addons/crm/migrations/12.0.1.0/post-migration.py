# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def fill_mail_blacklist_crm_lead(cr):
    cr.execute(
        """
        INSERT INTO mail_blacklist (email, active,
            create_uid, create_date, write_uid, write_date)
        SELECT email_from, active, create_uid, create_date,
            write_uid, write_date
        FROM crm_lead cl
        WHERE cl.%s
            AND COALESCE(cl.email_from, '') != ''
        ON CONFLICT DO NOTHING
        """, (AsIs(openupgrade.get_legacy_name('opt_out')), ),
    )


def map_crm_team_dashboard_graph_model(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('dashboard_graph_model'),
        'dashboard_graph_model',
        [('crm.opportunity.report', 'crm.lead')],
        table='crm_team', write='sql')


@openupgrade.migrate()
def migrate(env, version):
    fill_mail_blacklist_crm_lead(env.cr)
    map_crm_team_dashboard_graph_model(env.cr)
    openupgrade.load_data(
        env.cr, 'crm', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.load_data(
        env.cr, 'crm', 'migrations/12.0.1.0/noupdate_changes2.xml',
        mode='init_no_create')
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'crm.crm_rule_all_lead_report',
            'crm.crm_rule_personal_lead_report',
            'crm.opp_report_multi_company',
            'crm.email_template_opportunity_reminder_mail',
            'crm.mail_template_data_module_install_crm',
        ],
    )

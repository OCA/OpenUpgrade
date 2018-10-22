# Copyright 2018 Eficent <http://www.eficent.com>
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
        WHERE cl.%s = TRUE
            AND cl.email_from NOT IN (SELECT email FROM mail_blacklist)
        """, (AsIs(openupgrade.get_legacy_name('opt_out')), ),
    )


def map_crm_team_dashboard_graph_model(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('dashboard_graph_model'),
        'dashboard_graph_model',
        [('crm.opportunity.report', 'crm.lead')],
        table='crm_team', write='sql')


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    fill_mail_blacklist_crm_lead(cr)
    map_crm_team_dashboard_graph_model(cr)
    openupgrade.load_data(
        cr, 'crm', 'migrations/12.0.1.0/noupdate_changes.xml')

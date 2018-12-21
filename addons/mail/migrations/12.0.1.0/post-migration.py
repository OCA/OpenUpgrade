# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def fill_mail_blacklist_res_partner(cr):
    cr.execute(
        """
        INSERT INTO mail_blacklist (email, active,
            create_uid, create_date, write_uid, write_date)
        SELECT email, active, create_uid, create_date,
            write_uid, write_date
        FROM res_partner
        WHERE %s AND email IS NOT NULL
        ON CONFLICT DO NOTHING
        """, (AsIs(openupgrade.get_legacy_name('opt_out')), ),
    )


def fill_mail_notification_mail_id(cr):
    cr.execute(
        """
        UPDATE mail_message_res_partner_needaction_rel mmrpnr
        SET mail_id = mm.id
        FROM mail_mail mm
        WHERE mmrpnr.mail_message_id = mm.mail_message_id
        """
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    fill_mail_blacklist_res_partner(cr)
    fill_mail_notification_mail_id(cr)
    openupgrade.load_data(
        cr, 'mail', 'migrations/12.0.1.0/noupdate_changes.xml')

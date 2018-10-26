# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def fill_mail_blacklist_mass_mailing_contact(cr):
    cr.execute(
        """
        INSERT INTO mail_blacklist (email, active,
            create_uid, create_date, write_uid, write_date)
        SELECT email, TRUE as active, create_uid, create_date,
            write_uid, write_date
        FROM mail_mass_mailing_contact mmmc
        WHERE mmmc.%s
        ON CONFLICT DO NOTHING
        """, (AsIs(openupgrade.get_legacy_name('opt_out')), ),
    )


def fill_mass_mailing_list_contact_rel_unsubscription_date(cr):
    cr.execute(
        """
        UPDATE mail_mass_mailing_contact_list_rel mmmclr
        SET unsubscription_date = mmmc.%s
        FROM mail_mass_mailing_contact mmmc
        WHERE mmmclr.contact_id = mmmc.id
        """, (AsIs(openupgrade.get_legacy_name('unsubscription_date')), ),
    )


def fill_mass_mailing_user_id(cr):
    cr.execute(
        """
        UPDATE mail_mass_mailing
        SET user_id = create_uid
        WHERE user_id IS NULL
        """
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    fill_mail_blacklist_mass_mailing_contact(cr)
    fill_mass_mailing_list_contact_rel_unsubscription_date(cr)
    fill_mass_mailing_user_id(cr)

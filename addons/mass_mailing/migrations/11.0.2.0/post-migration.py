# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_list_id_to_list_ids(cr):
    """Set the list_ids for the list_id in mail.mass_mailing.contact"""
    cr.execute(
        """
        SELECT id, list_id FROM mail_mass_mailing_contact;
        """)
    rows = cr.fetchall()
    for r in rows:
        cr.execute(
            """
            INSERT INTO mail_mass_mailing_contact_list_rel (contact_id,
            list_id) values(%s,%s)
            """, (r[0], r[1],))


def map_mailing_model_to_mailing_model_id(cr):
    """Set the mailing_model_id for the mailing_model in mail.mass_mailing"""
    cr.execute(
        """
        SELECT mm.id, m.id FROM mail_mass_mailing AS mm
        LEFT JOIN ir_model AS m ON m.model = mm.mailing_model;
        """)
    rows = cr.fetchall()
    for r in rows:
        cr.execute(
            """
            UPDATE mail_mass_mailing SET mailing_model_id = %s WHERE id = %s
            """, (r[1], r[0],))


@openupgrade.migrate()
def migrate(env, version):
    map_list_id_to_list_ids(env.cr)
    map_mailing_model_to_mailing_model_id(env.cr)

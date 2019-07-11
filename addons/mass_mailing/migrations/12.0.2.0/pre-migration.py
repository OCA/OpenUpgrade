# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    'mail_mass_mailing_contact': [
        ('opt_out', None),
        ('unsubscription_date', None),
    ],
}
_xmlid_renames = [
    ("website_mass_mailing.page_unsubscribe",
     "mass_mailing.page_unsubscribe"),
    ("website_mass_mailing.page_unsubscribed",
     "mass_mailing.page_unsubscribed"),
    ("website_mass_mailing.unsubscribe",
     "mass_mailing.unsubscribe"),
    ("website_mass_mailing.unsubscribed",
     "mass_mailing.unsubscribed"),
]


def complete_mail_mass_mailing_contact_list_rel_db_layout(cr):
    """Add 'id' column to table mail_mass_mailing_contact_list_rel, as this
    table comes from v11 many2many relation table, so now that has been
    promoted to regular model table, it doesn't autopopulate this field.
    """
    openupgrade.logged_query(
        cr, """
        CREATE SEQUENCE mail_mass_mailing_contact_list_rel_id_seq
        INCREMENT 1
        MAXVALUE 2147483647
        """,
    )
    openupgrade.logged_query(
        cr, """
        ALTER TABLE mail_mass_mailing_contact_list_rel
        ADD id int4
        NOT NULL
        DEFAULT(
            nextval('mail_mass_mailing_contact_list_rel_id_seq'::regclass)
        )""",
    )
    openupgrade.logged_query(
        cr, """
        ALTER SEQUENCE mail_mass_mailing_contact_list_rel_id_seq
        OWNED BY mail_mass_mailing_contact_list_rel.id""",
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.rename_columns(cr, _column_renames)
    complete_mail_mass_mailing_contact_list_rel_db_layout(cr)
    openupgrade.rename_xmlids(cr, _xmlid_renames)

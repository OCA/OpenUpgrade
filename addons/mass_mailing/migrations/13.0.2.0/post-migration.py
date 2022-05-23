# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    # mail.mass_mailing.list
    'mass_mailing.mass_mail_list_1',
]


def fill_several_campaign_id(env):
    tables = ["mailing_mailing", "mailing_trace", "link_tracker", "link_tracker_click"]
    for table in tables:
        openupgrade.logged_query(
            env.cr, """
            UPDATE {} AS tt
            SET campaign_id = mmc.campaign_id
            FROM mail_mass_mailing_campaign mmc
            WHERE tt.mass_mailing_campaign_id = mmc.id
                AND tt.campaign_id IS NULL""".format(table))


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    fill_several_campaign_id(env)
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'mass_mailing', 'migrations/13.0.2.0/noupdate_changes.xml')

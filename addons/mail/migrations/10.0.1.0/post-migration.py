# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    # the table exists already, so the ORM doesn't create an id column
    cr.execute(
        'alter table mail_message_res_partner_needaction_rel '
        'add column id serial not null primary key'
    )
    # as 9.0 deleted notifications for read messages, all existing
    # notifications are unread by definition
    cr.execute(
        'update mail_message_res_partner_needaction_rel set is_read=False'
    )
    # set email properties
    cr.execute(
        """update mail_message_res_partner_needaction_rel rel
        set is_email=True, email_status=case
            when m.state in ('sent', 'exception') then m.state
            else 'ready'
        end
        from mail_mail m
        where rel.mail_message_id=m.mail_message_id"""
    )
    openupgrade.load_data(
        cr, 'mail', 'migrations/10.0.1.0/noupdate_changes.xml')

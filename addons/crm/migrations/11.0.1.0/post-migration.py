# -*- coding: utf-8 -*-
# Copyright 2017 Bloopark <http://bloopark.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute("""
         INSERT INTO mail_activity(res_id, res_model_id, res_model,
         res_name, activity_type_id, summary,
         date_deadline, user_id, create_uid, create_date, write_uid, write_date)
         SELECT cl.id,  im.id, 'crm.lead',cl.title_action, cl.next_activity_id,
         cl.title_action, cl.date_action,cl.user_id, cl.create_uid, cl.create_date,
         cl.write_uid, cl.write_date
         FROM crm_lead as cl, ir_model as im
         WHERE next_activity_id IS NOT NULL  AND  date_action IS NOT NULL  AND im.model='crm.lead'
         """)
    openupgrade.load_data(
        env.cr, 'crm', 'migrations/11.0.1.0/noupdate_changes.xml',
    )

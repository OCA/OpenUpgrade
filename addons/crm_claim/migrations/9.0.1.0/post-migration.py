# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import AsIs
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    cr.execute(
        "alter table crm_claim_category add column lead_tag_id int")
    cr.execute(
        "insert into crm_claim_category (name, team_id, lead_tag_id) "
        "select t.name, t.team_id, t.id "
        "from crm_lead_tag t "
        "join ir_model m on t.object_id=m.id and m.model='crm.claim'")
    cr.execute(
        "update crm_claim c set categ_id=cc.id "
        "from crm_claim_category cc where c.%(categ_id)s=cc.lead_tag_id",
        {
            'categ_id': AsIs(openupgrade.get_legacy_name('categ_id')),
        })
    openupgrade.logged_query(
        cr,
        "UPDATE ir_model_data imd "
        "SET res_id = ccc.id, model = 'crm.claim.category' "
        "FROM crm_claim_category ccc "
        "WHERE res_id = ccc.lead_tag_id "
        "AND module = 'crm_claim' "
        "AND imd.name LIKE 'categ_claim%%'")
    openupgrade.load_data(
        cr, 'crm_claim', 'migrations/9.0.1.0/noupdate_changes.xml',
    )

# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(cr, version):
    # Converts the m2m to o2m (but there would be data loss)
    cr.execute("""UPDATE res_users SET 
    sale_team_id = r.section_id FROM 
    sale_member_rel r WHERE id = r.member_id
    """)

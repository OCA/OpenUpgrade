# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, an open source suite of business apps
# This module copyright (C) 2015-Today GRAP (<http://www.grap.coop>).
# @author: Sylvain LE GAL (<http://twitter.com/legalsylvain>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')


def migrate_crm_lead_sale_order(cr):
    """Set new sale_order fields with value found in crm_lead, if
    sale_order.origin field mentions the crm_lead;
    - retrieve crm_lead.type_id to set sale_order.campaign_id;
    - retrieve crm_lead.channel_id to set sale_order.medium_id;
    """
    openupgrade.logged_query(cr, """
        UPDATE sale_order sale
        SET campaign_id = lead.campaign_id, medium_id = lead.medium_id
        FROM crm_lead lead
        WHERE sale.partner_id = lead.partner_id
        AND sale.origin like '%% '||lead.id;
        """)


@openupgrade.migrate()
def migrate(cr, version):
    migrate_crm_lead_sale_order(cr)

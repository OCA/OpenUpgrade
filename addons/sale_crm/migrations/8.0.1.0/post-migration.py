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

import re
import logging

from openerp.openupgrade import openupgrade
from openerp.modules.registry import RegistryManager

logger = logging.getLogger('OpenUpgrade')


def migrate_crm_lead_sale_order(cr):
    """Get the id of the crm that had generated a sale.order
    If found:
    - retrieve crm_lead.type_id to set sale_order.campaign_id;
    - retrieve crm_lead.channel_id to set sale_order.medium_id;
    """
    execute = openupgrade.logged_query

    # Get all sale orders with an origin value
    execute(cr,
            'SELECT id as so_id, origin, partner_id'
            ' FROM sale_order'
            ' WHERE origin IS NOT NULL')

    for so_id, origin, partner_id in cr.fetchall():
        # Try to get the crm_id from origin value
        crm_id = re.findall("([0-9]+)$", origin)
        if crm_id:
            crm_id = int(crm_id[-1])
            # if found, get campaign_id and medium_id
            execute(cr,
                    'SELECT id, campaign_id, medium_id'
                    ' FROM crm_lead'
                    ' WHERE id=%s'
                    ' AND partner_id=%s' % (crm_id, partner_id))
            res = cr.fetchone()
            if not res:
                logger.warning(
                    "Cannot retrieve crm_lead.id '%s' "
                    "found in sale_order origin '%s'" % (crm_id, origin))
            else:
                execute(
                    cr,
                    'UPDATE sale_order'
                    ' SET campaign_id = %s,'
                    ' medium_id = %s'
                    ' WHERE id = %s' % (
                        res[1], res[2], so_id))


@openupgrade.migrate()
def migrate(cr, version):
    registry = RegistryManager.get(cr.dbname)
    migrate_crm_lead_sale_order(cr)

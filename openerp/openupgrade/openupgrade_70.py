# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# This migration script copyright (C) 2013-today Sylvain LE GAL
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

# This module provides simple tools for openupgrade migration, specific for the
# 6.1 -> 7.0.

def get_partner_id_from_partner_address_id(cr, partner_address_id):
    """
        Get the new partner_id from old partner_address_id.
        :param partner_address_id : res_partner_address previously used.
    """
    cr.execute("""
        SELECT openupgrade_7_migrated_to_partner_id 
        FROM res_partner_address
        WHERE id=%s""",
        (partner_address_id,))
    return cr.fetchone()[0]
    
def get_partner_id_from_user_id(cr, user_id):
    """
        Get the new partner_id from user_id.
        :param user_id : user previously used.
    """
    cr.execute("""
        SELECT partner_id 
        FROM res_users 
        WHERE id=%s""",
        (user_id,))
    return cr.fetchone()[0]

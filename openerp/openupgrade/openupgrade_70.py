# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# This module copyright (C) 2013 Sylvain LE GAL
#                       (C) 2013 Therp BV
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

# This module provides simple tools for openupgrade migration, specific for
# the 6.1 -> 7.0 migration. It is kept in later editions to keep all the API
# docs in the latest release.
import openupgrade


def set_partner_id_from_partner_address_id(
        cr, pool, model_name, partner_field, address_field, table=None):
    """
    Set the new partner_id on any table with migrated contact ids

    :param model_name: the model name of the target table
    :param partner_field: the column in the target model's table \
                          that will store the new partner when found
    :param address_field: the legacy field in the model's table \
                    that contains the old address in the model's table
    :param table: override the target model's table name in case it was renamed
    :returns: nothing
    """
    model = pool.get(model_name)
    table = table or model._table
    openupgrade.logged_query(
        cr,
        """
        UPDATE %(table)s
        SET %(partner_field)s=address.openupgrade_7_migrated_to_partner_id
        FROM res_partner_address address
        WHERE %(table)s.%(address_field)s=address.id
        """ % {'table': table,
               'partner_field': partner_field,
               'address_field': address_field})


def get_partner_id_from_user_id(cr, user_id):
    """
        Get the new partner_id from user_id.
        :param user_id : user previously used.
    """
    cr.execute("""
        SELECT partner_id
        FROM res_users
        WHERE id=%s""", (user_id,))
    return cr.fetchone()[0]

# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, an open source suite of business apps
# This module copyright (C) 2015-Today Akretion.
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

from openerp.openupgrade import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.date_to_datetime_tz(
        cr, 'sale_order', 'user_id',
        openupgrade.get_legacy_name('commitment_date'),
        'commitment_date')
    openupgrade.date_to_datetime_tz(
        cr, 'sale_order', 'user_id',
        openupgrade.get_legacy_name('requested_date'),
        'requested_date')

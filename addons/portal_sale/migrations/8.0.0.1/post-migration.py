# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Onestein SL,
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.openupgrade import openupgrade


def load_data(cr):
    '''
    Update the references to base.group_portal
    :param cr:
    '''
    openupgrade.load_data(cr, 'portal_sale', 'migrations/8.0.0.1/modified_data.xml', mode='init')


@openupgrade.migrate()
def migrate(cr, version):
    load_data(cr)

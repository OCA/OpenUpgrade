# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Sylvain LE GAL
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

from openupgrade import openupgrade

column_renames = {
    'hr_employee': [
        ('address_home_id', None),
        ('address_id', None),
        ('photo', 'image'),
    ]
}


def clean_hr_employee_image(cr):
    """
    Remove odd non-binary image data
    """
    openupgrade.logged_query(cr, """
        UPDATE hr_employee
        SET image = NULL
        WHERE image like '/openerp/image%%';""")


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    clean_hr_employee_image(cr)

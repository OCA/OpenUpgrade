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

from openerp.openupgrade import openupgrade

xmlid_renames = [
    ('l10n_fr.tva_acq_normale_inclue', 'l10n_fr.tva_acq_normale_TTC'),
    ('l10n_fr.tva_acq_specifique_inclue', 'l10n_fr.tva_acq_specifique_TTC'),
    ('l10n_fr.tva_acq_specifique_1_inclue', 'l10n_fr.tva_acq_specifique_1_TTC'),
    ('l10n_fr.tva_acq_reduite_inclue', 'l10n_fr.tva_acq_reduite_TTC'),
    ('l10n_fr.tva_acq_super_reduite_inclue', 'l10n_fr.tva_acq_super_reduite_TTC'),
]

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_xmlids(cr, xmlid_renames)

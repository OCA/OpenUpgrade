##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2009 Smile.fr. All Rights Reserved
#    authors: Raphaël Valyi, Xavier Fernandez
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import fields, osv

class bom_customization_configurator(osv.osv_memory):
    _name = "bom_customization.configurator"
    
    _columns = {
                #TODO wrong def form demo!!!!
                'bom_option': fields.many2one('bom_customization.bom_customization_groups', "BoM Option", required = True),
                'bom_key_values': fields.one2many("bom_customization.bom_customization_values", 'group_id', "Bom Options"),
              }
    
bom_customization_configurator()
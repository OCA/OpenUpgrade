# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 CCILV ASBL. (http://www.ccilv.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields, osv

class cci_country(osv.osv):
    _name = "cci.country"
    _description = "Country or Area for CCI"
    _columns = {
        'code' : fields.char('Code',size=3,required=True),
        'name' : fields.char('Name',size=64,required=True),
        'official_name' : fields.char('Official Name',size=120),
        'postalabbrev' : fields.char('Postal Abbreviation',size=4),
        'phoneprefix' : fields.integer('Phone Prefix'),
        'description' : fields.text('Description'),
        'iscountry' : fields.boolean('Country',help='Indicates if this code designates a country; if False, designates an area'),
        'active' : fields.boolean('Active',help='Indicates if we can still use this country-area code'),
        'valid4certificate' : fields.boolean('Certificates',help='Indicates if this code can be used for certificates'),
        'valid4ata' : fields.boolean('ATA',help='Indicates if this code can be used for carnets ATA'),
        'valid4embassy' : fields.boolean('Embassy',help='Indicates if this code can be used for Embassies'),
        'cci_country_ids' : fields.many2many('cci.country','cci_country_rel','country_id','current_country_id','Linked Countries-Areas'),
    }
    _defaults = {
        'iscountry' : lambda *a: True,
        'active' : lambda *a : True,
        'valid4certificate' : lambda *a : True,
        'valid4ata' : lambda *a: False,
        'valid4embassy' : lambda *a: True,
    }
cci_country()



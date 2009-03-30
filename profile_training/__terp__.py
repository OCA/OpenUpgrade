# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

{
    'name' : 'Profile Training',
    'version' : '0.0.1',
    'author' : 'Tiny SPRL',
    'website' : 'http://www.openerp.com',
    'description' : """Profile for the training management.
With this profile the training management will be installed and you can have 
the choice to install the examn management and the room management""",
    'depends' : [
        'training',
        'document_lock',
    ],
    'init_xml' : [
    ],
    'demo_xml' : [
    ],
    'update_xml' : [
        'profile_training.xml',
    ],
    'active' : False,
    'installable' : True,
    'category' : 'Profile',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

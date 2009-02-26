#!/usr/bin/env python
#coding: utf-8
#
# (c) 2008 Sednacom <http://www.sednacom.fr>
#
# authors :
#  - Brice < brice@sednacom.fr >
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import wizard
import pooler

init_form_desc = """<?xml version="1.0" ?>
<form string="Zarafa">
    <label string="Import contacts (Zarafa)" />
</form>
"""

end_form_desc = """<?xml version="1.0" ?>
<form string="Zarafa">
    <label string="Import OK !" />
</form>
"""

class wizard_zarafa_contact_import( wizard.interface ):

    def _do_import( wiz, cr, uid, data, context ):
        pooloo = pooler.get_pool(cr.dbname)
        obj = pooloo.get('zarafa.contact')

        obj._import(cr, uid, context)

        return {}

    states = {
        'init' : {
            'actions' : [ ],
            'result' : {
                'type' : 'form' ,
                'arch': init_form_desc ,
                'fields': {} ,
                'state': [ ( 'doit', 'Import' ), ],
                }
            },
        'doit' : {
            'actions' : [_do_import, ],
            'result' : {
                'type' : 'state' ,
                'state': 'done' ,
                }
            },
        'done' : {
            'actions' : [  ],
            'result' : {
                'type' : 'form' ,
                'arch': end_form_desc ,
                'fields': {} ,
                'state': [( 'end', 'Ok' ),  ],
            },
        },
    }

wizard_zarafa_contact_import( 'zarafa.contact.import' )

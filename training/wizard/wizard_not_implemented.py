# -*- coding: UTF-8 -*-
# openacademy/wizard/wizard_spam.py

import wizard
import pooler
import tools

class wizard_not_implemented(wizard.interface):

    first_screen_fields = { }

    first_screen_form = '''<?xml version="1.0"?>
    <form string="Not Implemented" colspan="4">
        <label string="This wizard is not implented !" />
    </form>'''

    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'form',
                'arch': first_screen_form,
                'fields': first_screen_fields,
                'state':[('end','Ok', 'gtk-close')],
            }
        },
    }


wizard_not_implemented('wizard_not_implemented')

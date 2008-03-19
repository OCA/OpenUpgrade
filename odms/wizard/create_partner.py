
# The different libraries to import

import wizard
import pooler

def _create_partner(self,cr,uid,data,context):
	print "DEBUG - accessing _create_partner"
	return pooler.get_pool(cr.dbname).get('odms.subscription').create_partner(cr,uid,data['id'],context)


class create_partner(wizard.interface):
        """Creates a partner from a OD partner"""
        states = {
                # The initialisation state (mandatory) called when the wizard is launched
                'init': {
                        'actions': [_create_partner],
                        'result': {'type': 'state', 'state':'end'}
                },
        }

# Instanciate the wizard object with the defined wizard (see .xml file) as parameter
create_partner('odms.create_partner')


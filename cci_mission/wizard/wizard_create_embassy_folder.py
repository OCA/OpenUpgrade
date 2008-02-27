import wizard
import pooler

form = """<?xml version="1.0"?>
<form string="Create Embassy Folder">
    <separator string="Create Embassy Folder" />
</form>
"""

fields = {}

class create_embassy_folder(wizard.interface):
    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form' ,   'arch' : form,
                    'fields' : fields,
                    'state' : [('end','Ok')]}
        },

    }
create_embassy_folder("cci_mission.create_embassy_folder")

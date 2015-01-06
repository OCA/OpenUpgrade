""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    'mail_gateway': 'mail',
    'outlook': 'plugin_outlook',
    'thunderbird': 'plugin_thunderbird',
    }

renamed_models = {
    'mailgate.message': 'mail.message',
    'mailgate.thread': 'mail.thread',
    }

# -*- encoding: utf-8 -*-
#####################################################################
#Created By     : Eiffel Consultancy Pvt. Ltd.
#Created Date   : 14/02/2007
#####################################################################


{
    'name' : 'Report for timesheet',
    'version' :'1.0',
    'author' : 'Tiny',
    'depends' : ['hr_timesheet','multi_company'],
    'description': 'New report for timesheet',
    'init_xml' : [],
    'update_xml': [
        'report_timesheet_user_view.xml',
    ],
    'installable': True
}



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


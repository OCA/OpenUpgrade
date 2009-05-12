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
    'name': 'ETL system',
    'version': '1.0',
    'category': 'Generic Modules/Others',
    'description': """
	ETL system- Extract Transfer Load system
	    """,
    'author': 'Tiny',
    'website': 'http://openerp.com',
    'depends': ['base'],
    'init_xml': [
         'etl_connector/etl_connector_data.xml',
         'etl_component/control/control_data.xml',
         'etl_component/input/input_data.xml',
         'etl_component/output/output_data.xml',
         'etl_component/transform/transform_data.xml'
     ],
    'update_xml': [
         'etl_interface_sequence.xml',
         'etl_interface_view.xml',
         'etl_component/etl_component_view.xml',
         'etl_connector/etl_connector_view.xml',
         'etl_interface_workflow.xml',
         'etl_connector/localfile_view.xml',
         'etl_connector/openobject_connector_view.xml',
         'etl_connector/sql_connector_view.xml',
         'etl_connector/facebook_connector_view.xml',
         'etl_component/control/data_count_view.xml',
         'etl_component/control/sleep_view.xml',
         'etl_component/input/csv_in_view.xml',
         'etl_component/input/vcard_in_view.xml',
         'etl_component/input/facebook_in_view.xml',
         'etl_component/input/sql_in_view.xml',
         'etl_component/input/excel_in_view.xml',
         'etl_component/input/xml_in_view.xml',
         'etl_component/input/openobject_in_view.xml',
        'etl_component/input/xmlrpc_in_view.xml',
	     'etl_component/input/gmail_in_view.xml',

	     'etl_component/output/csv_out_view.xml',
         'etl_component/output/sql_out_view.xml',
         'etl_component/output/openobject_out_view.xml',
         'etl_component/output/excel_out_view.xml',
         'etl_component/output/xml_out_view.xml',
         'etl_component/output/vcard_out_view.xml',

         'etl_component/transform/data_filter_view.xml',
         'etl_component/transform/sort_view.xml',
         'etl_component/transform/map_view.xml',
         'etl_component/transform/logger_view.xml',
         'etl_component/transform/logger_bloc_view.xml',
         'etl_component/transform/merge_view.xml', # To be check
         'etl_component/transform/schema_validator_view.xml',
         'etl_component/transform/unique_view.xml',

         ],
     'demo_xml': ['etl_interface_demo.xml'],
    'installable': True,
    'active': False,
}

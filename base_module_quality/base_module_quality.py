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
import pooler
import os
from tools import config

class abstract_quality_check(object):
    '''
        This Class provide...
    '''

    def __init__(self):
        '''
        this method should initialize the var
        '''
        #This float have to store the rating of the module.
        #Used to compute the final score (average of all scores).
        #0 <= self.score <= 1
        self.score = 0.0

        #This char have to store the name of the test.
        self.name = ""

        #This char have to store the result.
        #Used to display the result of the test.
        self.result = ""

        #This char have to store the result with more details.
        #Used to provide more details if necessary.
        self.result_details = ""

        #This bool defines if the test can be run only if the module is installed.
        #True => the module have to be installed.
        #False => the module can be uninstalled.
        self.bool_installed_only = True

        #This variable is use to make result of test should have more weight (Some tests are more critical than others)
        self.ponderation = 1.0

        #Specify test got an error on module
        self.error = False

        #The tests have to subscribe itselfs in this list, that contains all the test that have to be performed. 
        self.tests = []
        self.list_folders = os.listdir(config['addons_path']+'/base_module_quality/')
        for item in self.list_folders:
            self.item = item
            path = config['addons_path']+'/base_module_quality/'+item
            if os.path.exists(path+'/'+item+'.py') and item not in ['report', 'wizard', 'security']:
                item2 = 'base_module_quality.' + item +'.' + item
                x = __import__(item2)
                x2 = getattr(x, item)
                x3 = getattr(x2, item)
                self.tests.append(x3)
#        raise 'Not Implemented'

    def run_test(self, cr, uid, module_path=""):
        '''
        this method should do the test and fill the score, result and result_details var
        '''
        raise 'Not Implemented'

    def get_objects(self, cr, uid, module):
        # This function returns all object of the given module..
        pool = pooler.get_pool(cr.dbname)
        ids2 = pool.get('ir.model.data').search(cr, uid, [('module','=', module), ('model','=','ir.model')])
        model_list = []
        model_data = pool.get('ir.model.data').browse(cr, uid, ids2)
        for model in model_data:
            model_list.append(model.res_id)
        obj_list = []
        for mod in pool.get('ir.model').browse(cr, uid, model_list):
            obj_list.append(str(mod.model))
        return obj_list

    def get_ids(self, cr, uid, object_list):
        #This method return dictionary with ids of records of object for module
        pool = pooler.get_pool(cr.dbname)
        result_ids = {}
        for obj in object_list:
            ids = pool.get(obj).search(cr, uid, [])
            result_ids[obj] = ids
        return result_ids

    def format_table(self, header=[], data_list=[]):
        detail = ""
        if header[0]=='method':
            detail += ('{| border="1" cellspacing="0" cellpadding="5" align="left" \n! %-40s \n! %-16s \n! %-20s \n! %-16s ') % (header[1].ljust(40), header[2].ljust(16), header[3].ljust(20), header[4].ljust(16))
            for res in data_list[0]:
                detail += ('\n|-\n| %s \n| %s \n| %s \n| %s ') % (res, data_list[0][res][0], data_list[0][res][1], data_list[0][res][2])
            detail = detail + '\n|}'
        elif header[0]=='speed':
            detail += ('{| border="1" cellspacing="0" cellpadding="5" align="left" \n! %-40s \n! %-10s \n! %-10s \n! %-10s \n! %-10s \n! %-20s') % (header[1].ljust(40), header[2].ljust(10), header[3].ljust(10), header[4].ljust(10), header[5].ljust(10), header[6].ljust(20))
            for data in data_list[0]:
                detail +=  ('\n|-\n| %s \n| %s \n| %s \n| %s \n| %s \n| %s ') % (data[0], data[1], data[2], data[3], data[4], data[5])
                detail = detail  + '\n|}\n'
        return detail

    def add_quatation(self, x, y):
        return x/y

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


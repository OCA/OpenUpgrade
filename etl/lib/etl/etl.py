# -*- encoding: utf-8 -*-
##############################################################################
#
#    ETL system- Extract Transfer Load system
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
""" ETL Process.

    This is the main file of ETL which includes several test functions

"""
# TODO :      
#     - make good documentation and test with doctest
#     - Integrate profiler in the job code: cProfile
#     - do a unittest system and implement unit tests on components file                
        
        

def test1():    
    #TODO : avoid using .CSV files, povide stringIO with string directly in the __main__
    fileconnector=etl.connector.localfile('demo/data/invoice.csv')
    transformer.description= {'id':etl.transformer.LONG,'name':etl.transformer.STRING,'invoice_date':etl.transformer.DATE,'invoice_amount':etl.transformer.FLOAT,'is_paid':etl.transformer.BOOLEAN}    
    transformer=etl.transformer(transformer.description)
    csv_in1= etl.component.input.csv_in.csv_in(fileconnector=fileconnector,transformer=transformer)
    log1=etl.component.transform.logger.logger(name='Read Invoice File')
    tran=etl.etl.transition(csv_in1,log1)
    job1=etl.etl.job([log1])
    job1.run()


if __name__ == '__main__':
    #TODO : make perfect testing method
    pass







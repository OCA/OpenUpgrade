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
""" ETL Component.

    This file should be spread in different files in component's subdirs.

"""

import etl
import csv
import sys
import time


class csv_in(etl.component):
    """
        This is an ETL Component that use to read data from csv file.
       
		Type: Data Component
		Computing Performance: Streamline
		Input Flows: 0
		* .* : nothing
		Output Flows: 0-x
		* .* : return the main flow with data from csv file
    """
    def __init__(self, filename, *args, **argv):
        super(csv_in, self).__init__(*args, **argv)
        self.filename = filename

    def process(self):
        fp = csv.DictReader(file(self.filename))
        for row in fp:
            yield row, 'main'

class csv_out(etl.component):
    """
        This is an ETL Component that use to write data to csv file.

		Type: Data Component
		Computing Performance: Streamline
		Input Flows: 0-x
		* .* : the main data flow with input data
		Output Flows: 0-1
		* main : return all data
    """
    def __init__(self, filename, *args, **argv):
        super(csv_out, self).__init__(*args, **argv)
        self.filename=filename

    def process(self):
        fp2=None
        datas = []
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:                    
                    if not fp2:
                        fp2 = file(self.filename, 'wb+')
                        fieldnames = d.keys()
                        fp = csv.DictWriter(fp2, fieldnames)
                        fp.writerow(dict(map(lambda x: (x,x), fieldnames)))
                    fp.writerow(d)
                    yield d, 'main'

class sort(etl.component):
    """
        This is an ETL Component that use to perform sort operation.
 
		Type: Data Component
		Computing Performance: Semi-Streamline
		Input Flows: 1
		* .* : the main data flow with input data
		Output Flows: 0-x
		* .* : return the main flow with sort result
    """
    def __init__(self, fieldname, *args, **argv):
        super(sort, self).__init__(*args, **argv)
        self.fieldname = fieldname

    # Read all input channels, sort and write to 'main' channel
    def process(self):
        datas = []
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    datas.append(d)

        datas.sort(lambda x,y: cmp(x[self.fieldname],y[self.fieldname]))
        for d in datas:
            yield d, 'main'

class logger_bloc(etl.component):
    """
        This is an ETL Component that use to display log detail in end of process.
       
	    Type: Data Component
		Computing Performance: Bloc
		Input Flows: 0-x
		* .* : the main data flow with input data
		Output Flows: 0-y
		* .* : return the main flow 
    """
    def __init__(self, name, output=sys.stdout, *args, **argv):
        self.name = name
        self.output = output
        self.is_end = 'main'
        super(logger_bloc, self).__init__(*args, **argv)

    def process(self):
        datas=[]
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    datas.append(d)
        for d in datas:
            self.output.write('\tBloc Log '+self.name+str(d)+'\n')
            yield d, 'main'


class sleep(etl.component):
    """
       This is an ETL Component that use to sleep process.
    """
    def __init__(self, delay=1, *args, **argv):
        self.delay = delay
        super(sleep, self).__init__(*args, **argv)

    def process(self):
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    time.sleep(self.delay)
                    yield d, 'main'

class logger(etl.component):
    """
        This is an ETL Component that use to display log detail in streamline.
 
	    Type: Data Component
		Computing Performance: Streamline
		Input Flows: 0-x
		* .* : the main data flow with input data
		Output Flows: 0-y
		* .* : return the main flow 
    """
    def __init__(self, name, output=sys.stdout, *args, **argv):
        self.name = name
        self.output = output
        self.is_end = 'main'
        super(logger, self).__init__(*args, **argv)

    def process(self):
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:                    
                    self.output.write('\tLog '+self.name+str(d)+'\n')
                    yield d, 'main'

class diff(etl.component):
    """
        This is an ETL Component that use to find diff.
        Takes 2 flows in input and detect a difference between these two flows
        using computed keys (based on data records) to compare elements that may not
        have to be in the same order.

        Type: Data Component
        Computing Performance: Semi-Streamline
        Input Flows: 2
        * main: The main flow
        * .*: the second flow
        Output Flows: 0-x
        * same: return all elements that are the same in both input flows
        * updated: return all updated elements
        * removed: return all elements that where in main and not in the second flow
        * added: return all elements from the second flow that are not in main channel
    """
    def __init__(self, keys, *args, **argv):
        self.keys = keys
        self.row = {}
        self.diff = []
        self.same = []
        super(diff, self).__init__(*args, **argv)

    # Return the key of a row
    def key_get(self, row):
        result = []
        for k in self.keys:
            result.append(row[k])
        return tuple(result)

    def process(self):  
        self.row = {}      
        for channel,transition in self.input_get().items():            
            if channel not in self.row:
                self.row[channel] = {}
            other = None            
            for key in self.row.keys():
                if key<>channel:
                    other = key
                    break
            for iterator in transition:
                for r in iterator: 
                    key = self.key_get(r)
                    if other and (key in self.row[other]):
                        if self.row[other][key] == r:
                            yield r, 'same'                            
                        else:
                            yield r, 'update' 
                        del self.row[other][key]
                    else:
                        self.row[channel][key] = r         
        todo = ['add','remove']
        for k in self.row:     
            channel= todo.pop()                   
            for v in self.row[k].values():
                yield v,channel               
    




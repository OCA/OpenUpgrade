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
""" 
 Provides statistic info of ETL process.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.

"""
import datetime

class statistic(object):
    """
    This class computes basic statistics and return them at the end of the process like data in a channel called     
    "statistics".
    Input Channel | # of Records | Time To Process | Time/Record | Memory Usage
    main          | 1244         | 123 sec         | 0.1 sec     | 1Mb
    other         | 144          | 12 sec          | 0.1 sec     | 1Mb
    """
    
    statistics = {}
    def statistic(self, source_component, destination_component, source_channel, destination_channel, total_record, stat_time):
        #TODO : improvement
        input_channel = (source_component, destination_component, source_channel, destination_channel)
        if input_channel not in self.statistics:
            self.statistics.setdefault(input_channel, {                   
                       'input_channel': input_channel,
                       'total_records': 0,
                       'total_time': 0,
                       'record_time': 0,
                       'memory': 0,
                       'start': stat_time
            })
        stat = self.statistics[input_channel]        
        stat['end'] = stat_time
        stat['total_time'] = stat['end'] - stat['start']
        if total_record:    
            stat['total_records'] += total_record
            stat['record_time'] = stat['total_time'] / stat['total_records']
            stat['memory'] += 0 # TODO : Calculate size of data

    def statistics_get(self):
        for stat in self.statistics:
            yield stat, 'statistics'


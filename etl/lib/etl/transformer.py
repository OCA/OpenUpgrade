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
 ETL Process.

 The class provides transformeration process.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.

"""
import datetime
import logger

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class transformer(object):
    """
        Transfer data into different type.
        Pass description like :-
          - INTEGER  : convert string to Integer object.
          - FLOAT    : convert string to float object.
          - LONG     : convert string to long integer object.
          - COMPLEX  : convert string to complex number.
          - STRING   : convert string to string.
          - DATE     : convert string to datetime.date object.
          - DATETIME : convert string to datetime.datetime object.
          - TIME     : convert string to datetime.time object.
          - BOOLEAN  : convert string to boolean object.
        Example :-
           datas = [{'id': '1', 'name': 'abc', 'invoice_date': '2009-10-20', 'invoice_amount': '200.00', 'is_paid': '1'}]
           description= {'id': etl.transformer.LONG, 'name': etl.transformer.STRING, 'invoice_date': etl.transformer.DATE, 'invoice_amount': etl.transformer.FLOAT, 'is_paid': etl.transformer.BOOLEAN}
           return = [{'id': 1, 'name': 'abc', 'invoice_date': datetime.date object (2009, 10, 20), 'invoice_amount': 200.00, 'is_paid': True}]
    """
    INTEGER = 'int'
    STRING = 'str'
    DATE = 'date'
    DATETIME = 'datetime'
    TIME = 'time'
    FLOAT = 'float'
    LONG = 'long'
    COMPLEX = 'complex'
    BOOLEAN = 'bool'

    _transform_method = {
        'int': int,
        'str': unicode,
        'date': lambda x: datetime.datetime.strptime(x, DATE_FORMAT).date(),
        'time': lambda x: datetime.datetime.strptime(x, TIME_FORMAT).time(),
        'datetime':lambda x: datetime.datetime.strptime(x, DATETIME_FORMAT),
        'float': float,
        'long': long,
        'complex': complex,
        'bool': bool
    }

    def __init__(self, description):
        self.description = description
        self.logger = logger.logger()

    def __getstate__(self):
       pass

    def __setstate__(self, state):
        pass


    def action_error(self, e):
        print e
        self.logger.notifyChannel("transformer", logger.LOG_ERROR,
                     str(self) + ' : ' + str(e))
        return None

    def transform(self, data):
        # TODO : TO check : data and description should have same keys.
        try:
            for column in data:
                if column in self.description:
                    transform_method = self.description[column] and self._transform_method[self.description[column]]
                    data[column] = data[column] and transform_method(data[column]) or data[column]
            return data
        except UnicodeEncodeError, e:
            return self.action_error(e)
        except UnicodeDecodeError, e:
            return self.action_error(e)
        except TypeError, e:
            return self.action_error(e)
        except ValueError, e:
            return self.action_error(e)


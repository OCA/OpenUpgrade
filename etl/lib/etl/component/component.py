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
 ETL Component.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""
import datetime
from etl import signal
import pickle

class component(signal):
    """
    Base class of ETL Component.
    """

    def __init__(self, name='', connector=None, transformer=None, row_limit=0):
        super(component, self).__init__()
        self._type = 'component'
        self._cache = {}
        self.trans_in = []
        self.trans_out = []
        self.data = {}
        self.job = False
        self.generator = None
        self.name = name
        self.connector = connector
        self.transformer = transformer
        self.row_limit = row_limit
        self.row_count = 0
        self.status = 'open'

    def __str__(self):
        res='<Component job="%s" name="%s" type="%s" status="%s"'% (self.job and self.job.name or '', self.name, self._type, self.status)
        if self.is_start():
            res += ' is_start = "True"'
        if self.is_end():
            res += ' is_end = "True"'
        res += ">"
        return res

    def __getstate__(self):
        res = super(component, self).__getstate__()
        res.update({'transformet':self.transformer, 'row_limit':self.row_limit, 'row_count':self.row_count, 'name':self.name,'status':self.status, 'trans_in' : [], 'trans_out' : [], 'connector': pickle.dumps(self.connector),'_type':self._type })
        return res

    def __setstate__(self, state):
        super(component, self).__setstate__(state)
        state['connector'] = pickle.loads(state['connector'])
        state['_signal__connects'] = {}
        state['data'] = {}
        state['_cache'] = {}
        state['generator'] = None
        state['transformer'] = None
        self.__dict__ = state

    def __copy__(self):
        res = component(name=self.name, connector=self.connector, transformer=self.transformer, row_limit=self.row_limit)
        return res

    def copy(self):
        res = self.__copy__()
        res.name += '(copy)'
        return res

    def is_start(self):
        if not len(self.trans_in):
            return True
        return False

    def is_end(self):
        if not len(self.trans_out):
            return True
        return False

    def pause(self):
        self.status = 'pause'
        self.signal('pause', {'date': datetime.datetime.today()})

    def stop(self):
        self.status = 'stop'
        self.signal('stop', {'date': datetime.datetime.today()})

    def end(self):
        self.status = 'end'
        self.signal('end', {'date': datetime.datetime.today()})

    def start(self):
#        print "component start status.............",self.status
#        if self.status == 'end':
#            print "No need to start component again"
#            pass
        self.status = 'start'
        self.signal('start', {'date': datetime.datetime.today()})

    def warning(self, message):
        self.signal('warning', {'message': message})

    def error(self, message):
        self.signal('error', {'message': message})

    def generator_get(self, transition):
        """
        Get generator list of transition.
        """
        if self.generator:
            return self.generator
        self.generator = self.process()
        return self.generator

    def channel_get(self, trans=None):
        """
        Get channel list of transition.
        """
        #if self.status in ('end','stop') or (trans and trans.type=='trigger' and trans.status in ('end','stop','close')):
        #    return
        self.data.setdefault(trans, [])
        self._cache['start_output'] = {trans:False}
        self._cache['start_input'] = {trans:False}
        gen = self.generator_get(trans) or None
        if trans:
            trans.start()
        self.start()
        try:
#            row_count = 0
            self.row_count = 0
            while True:
                if self.data[trans]:
                    if not self._cache['start_output'][trans]:
                        self._cache['start_output'][trans] = datetime.datetime.today()
                        self.signal('start_output', {'trans': trans, 'date': datetime.datetime.today()})

                    data = self.data[trans].pop(0)
                    self.signal('send_output', {'trans':trans,'data':data, 'date': datetime.datetime.today()})
                    yield data
                    continue
                elif self.data[trans] is None:
                    self.signal('no_input')
                    raise StopIteration
                data, chan = gen.next()
#                row_count += 1
                self.row_count += 1
                if self.row_limit and row_count > self.row_limit:
                     raise StopIteration
                if data is None:
                    self.signal('no_input')
                    raise StopIteration
                if self.transformer:
                    data = self.transformer.transform(data)

                if not self._cache['start_input'][trans]:
                    self._cache['start_input'][trans] = datetime.datetime.today()
                    self.signal('start_input', {'trans': trans,'channel':chan, 'date': datetime.datetime.today()})

                self.signal('get_input', {'trans': trans,'channel':chan,'data':data, 'date': datetime.datetime.today()})
                for t, t2 in self.trans_out:
                    if (t == chan) or (not t) or (not chan):
                        self.data.setdefault(t2, [])
                        if not t:
                            self.data[t2].append((chan,data))
                        else:
                             self.data[t2].append(data)
        except StopIteration, e:
            if trans:
                trans.end()
            self.end()
        #except Exception, e:
        #    self.signal('error', {'data': self.data, 'type': 'exception', 'error': str(e)})

    def process(self):
        """
        Process method of ETL component.
        """
        pass

    def get_trigger_data(self, channel, trigger):
        return None

    def input_get(self):
        """
        Get input iterator of ETL component.
        """
        result = {}
        for channel, trans in self.trans_in:
            result.setdefault(channel, [])
            if trans == 'trigger':
                data = trans.source.get_trigger_data(channel, trans.trigger)
            else:
                data = trans.source.channel_get(trans)
            result[channel].append(data)
        return result

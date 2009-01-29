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

    The module provides process of ETL.

"""

class component(object):
    """
       Base class of ETL Component.
    """
    is_end = False
    def __init__(self,*args, **argv):
        self.trans_in = []
        self.trans_out = []
        self.is_output = False
        self.data = {}
        self.generator = None

    def __str__(self):
        return self.data

    def generator_get(self, transition):
        """ Get generator list of transition
        """
        if self.generator:
            return self.generator
        self.generator = self.process()
        return self.generator

    def channel_get(self, trans=None):
        """ Get channel list of transition
        """
        self.data.setdefault(trans, [])
        gen = self.generator_get(trans) or []
        while True:
            if self.data[trans]:
                yield self.data[trans].pop(0)
                continue
            elif self.data[trans] is None:
                raise StopIteration
            data, chan = gen.next()
            if data is None:
                raise StopIteration
            for t,t2 in self.trans_out:
                if (t == chan) or (not t) or (not chan):
                    self.data.setdefault(t2, [])
                    self.data[t2].append(data)

    def process(self):
        """ process method of ETL component
        """
        raise 'Should be override'


    def input_get(self):
        """ Get input iterator of ETL component
        """
        result = {}
        for channel,trans in self.trans_in:
            result.setdefault(channel, [])
            result[channel].append(trans.source.channel_get(trans))
        return result


class transition(object):
    """
       Base class of ETL transition.
    """
    def __init__(self, source, destination, channel_source='main', channel_destination='main', type='data'):
        self.type = type
        self.source = source
        self.destination = destination
        self.channel_source = channel_source
        self.channel_destination = channel_destination
        self.destination.trans_in.append((channel_destination,self))
        self.source.trans_out.append((channel_source,self))

class job(object):
    """
       Base class of ETL job.
    """
    def __init__(self,outputs=[]):
        self.outputs=outputs
    def __str__(self):
		pass

    def run(self):
        for c in self.outputs:
            for a in c.channel_get():
                pass

class connector(object):
    """
        Base class of ETL Connector.
    """
    def __init__(self,*args,**argv):
        self.host=argv.get('host',False)
        self.port=argv.get('port',False)
        self.uid=argv.get('uid',False)
        self.pwd=argv.get('pwd',False)
        self.connection_string=argv.get('connection_string',False)
        self.connection_type=argv.get('connection_type',False)
    def open(self,mode=False):
        return True
    def __str__(self):        
        return self.connection_string
    def close(self):
        return True


def test1():
    fileconnector=etl.connector.file_connector.file_connector('demo/data/partner.csv')
    csv_in1= etl.component.input.csv_in.csv_in(fileconnector=fileconnector)
    log1=etl.component.transform.logger.logger(name='Read Partner File')
    tran=etl.etl.transition(csv_in1,log1)
    job1=etl.etl.job([log1])
    job1.run()


if __name__ == '__main__':
    test1()







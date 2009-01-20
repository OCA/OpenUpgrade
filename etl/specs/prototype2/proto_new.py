#csv_in ---> logger
import csv
import sys

class component(object):
    def __init__(self,*args, **argv):
        self.trans_in = {}
        self.is_output = False
        self.data = {}
        self.is_end = False
        self.generator = None

    def generator_get(self, channel):
        if self.generator:
            return self.generator
        self.generator = self.process()

    def channel_get(self, channel):
        self.data.setdefault(channel, [])
        gen = self.generator_get() or []
        for data, chan in gen:
            if data is None:
                self.data[chan] = None
            if self.data[channel]:
                yield self.data[channel].pop(0)
            elif self.data[channel] is None:
                raise StopIteration
            elif chan==channel:
                yield data
            else:
                self.data.setdefault(chan, [])
                self.data[chan].append( data )

    def process(self): 
        pass

    def run(self):
        gen = self.channel_get(self.is_end)
        for a in gen:
            pass

class csv_in(component):
    def __init__(self, filename, *args, **argv):
        super(csv_in, self).__init__(*args, **argv)
        self.filename = filename

    def process(self):
        fp = csv.DictReader(file(self.filename))
        for row in fp:
            yield row, 'main'


class sort(component):
    def __init__(self, fieldname, *args, **argv):
        super(sort, self).__init__(*args, **argv)
        self.fieldname = fieldname

    # Read all input channels, sort and write to 'main' channel
    def process(self):
        datas = []
        for channel,iterator in self.trans_in.items():
            for d in iterator:
                datas.append(d)
        datas.sort(lambda x,y: cmp(x[self.fieldname],y[self.fieldname]))
        for d in datas:
            yield d, 'main'

class logger(component):
    def __init__(self, name, output=sys.stdout, *args, **argv):
        self.name = name
        self.output = output
        self.is_end = 'main'
        super(logger, self).__init__(*args, **argv) 

    def process(self): 
        self.output.write('Logger : '+(self.name or '')+'\n')
        for channel,iterator in self.trans_in.items():
            for data in iterator:
                self.output.write('\tLog '+self.name+str(data)+'\n')

class transition(object):
    def __init__(self, source, destination,type='data_transition', status='open', channel_source='main', channel_destination='main'):
        self.type=type
        self.source = source
        self.destination = destination
        self.channel_source = channel_source
        self.channel_destination = channel_destination

        self.destination.trans_in[channel_destination] = source.channel_get(channel_source)

class job(object):
    def __init__(self,outputs=[]):
        self.outputs=outputs

    def run(self):
        for c in self.outputs:
            c.run()

csv_in1= csv_in('partner.csv')
log1=logger(name='After Sort')
sort1=sort('name')

tran=transition(csv_in1,sort1)
tran=transition(sort1,log1)

job1=job([log1])
job1.run()


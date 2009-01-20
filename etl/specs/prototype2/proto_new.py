#csv_in ---> logger
import csv
import sys
import time

class component(object):
    is_end = False
    def __init__(self,*args, **argv):
        self.trans_in = []
        self.is_output = False
        self.data = {}
        self.generator = None

    def generator_get(self, channel):
        #if self.generator:
        #    return self.generator
        self.generator = self.process()
        return self.generator

    def channel_get(self, channel):
        self.data.setdefault(channel, [])
        gen = self.generator_get(channel) or []
        while True:                
            if self.data[channel]:
                yield self.data[channel].pop(0)
                continue
            elif self.data[channel] is None:
                raise StopIteration
            data, chan = gen.next()            
            if data is None:
                raise StopIteration
            elif chan==channel:
                yield data
            else:
                self.data.setdefault(chan, [])
                self.data[chan].append( data )
        
    def process(self):
        pass

class csv_in(component):
    def __init__(self, filename, *args, **argv):
        super(csv_in, self).__init__(*args, **argv)
        self.filename = filename

    def process(self):
        fp = csv.DictReader(file(self.filename))            
        for row in fp:
            yield row, 'main'

class csv_out(component):
    def __init__(self, filename, *args, **argv):
        super(csv_out, self).__init__(*args, **argv)
        self.filename=filename
        self.fp=None        
  
    def process(self):       
        datas = []
        for trans in self.trans_in:
            for channel,iterator in trans.items():
                for d in iterator:
                    datas.append(d)        
        self.fp=file(self.filename, 'wb+') 
        fieldnames = datas[0].keys()
        fp = csv.DictWriter(self.fp, fieldnames)
        fp.writerow(dict(map(lambda x: (x,x), fieldnames)))
        fp.writerows(datas)                 
        for d in datas:
            yield d, 'main'

class sort(component):
    def __init__(self, fieldname, *args, **argv):
        super(sort, self).__init__(*args, **argv)
        self.fieldname = fieldname

    # Read all input channels, sort and write to 'main' channel
    def process(self):
        datas = []                
        for trans in self.trans_in:            
            for channel,iterator in trans.items():                
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
        datas=[]
        for trans in self.trans_in:
            for channel,iterator in trans.items():
                for d in iterator:
                    datas.append(d)
        for d in datas:
            self.output.write('\tLog '+self.name+str(d)+'\n')
            yield d, 'main'

class transition(object):
    def __init__(self, source, destination,type='data_transition', status='open', channel_source='main', channel_destination='main'):
        self.type=type
        self.source = source
        self.destination = destination
        self.channel_source = channel_source
        self.channel_destination = channel_destination
        self.destination.trans_in.append({channel_destination:source.channel_get(channel_source)})

class job(object):
    def __init__(self,outputs=[]):
        self.outputs=outputs

    def run(self, t):
        for c in self.outputs:
            gen = c.channel_get(c.is_end)
            for a in gen:
                if t:
                    time.sleep(t)

csv_in1= csv_in('partner.csv')
log1=logger(name='After Sort')
sort1=sort('name')

tran=transition(csv_in1,sort1)
tran=transition(sort1,log1)

#job1=job([log1])
#job1.run(1)

csv_in1= csv_in('partner.csv')
csv_in2= csv_in('partner1.csv')
csv_out1= csv_out('partner2.csv')
sort1=sort('name')
log1=logger(name='Read Partner File')
log2=logger(name='After Sort')

tran=transition(csv_in1,log1)
tran1=transition(csv_in2,log1)
tran2=transition(csv_in1,sort1)
tran3=transition(csv_in2,sort1)
tran4=transition(sort1,log2)
tran5=transition(sort1,csv_out1)


job1=job([log1,sort1,csv_out1]) # thsi is work
job1.run(0)

# this is not work, log2 can not get data

#job2=job([log1,sort1,csv_out1,log2]) 
#job2.run(0)


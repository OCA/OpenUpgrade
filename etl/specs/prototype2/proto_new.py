
import csv
import sys
import time

class component(object):
    is_end = False
    def __init__(self,*args, **argv):
        self.trans_in = []
        self.trans_out = []
        self.is_output = False
        self.data = {}
        self.generator = None

    def generator_get(self, transition):
        if self.generator:
            return self.generator
        self.generator = self.process()
        return self.generator

    def channel_get(self, trans=None):
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
        pass

    def input_get(self):
        result = {}
        for channel,trans in self.trans_in:
            result.setdefault(channel, [])
            result[channel].append(trans.source.channel_get(trans))
        return result

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

class control_count(component):
    def process(self):
        datas = {}
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    datas.setdefault(channel, 0)
                    datas[channel] += 1

        for d in datas:
            yield {'channel': d, 'count': datas[d]}, 'main'

class sort(component):
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

class logger_bloc(component):
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


class sleep(component):
    def __init__(self, delay=1, *args, **argv):
        self.delay = delay
        super(sleep, self).__init__(*args, **argv)

    def process(self):
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    time.sleep(self.delay)
                    yield d, 'main'

class logger(component):
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

class diff(component):
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



class transition(object):
    def __init__(self, source, destination,type='data_transition', status='open', channel_source='main', channel_destination='main'):
        self.type=type
        self.source = source
        self.destination = destination
        self.channel_source = channel_source
        self.channel_destination = channel_destination
        self.destination.trans_in.append((channel_destination,self)) #:source.channel_get(self)})
        self.source.trans_out.append((channel_source,self))

class job(object):
    def __init__(self,outputs=[]):
        self.outputs=outputs

    def run(self):
        for c in self.outputs:
            for a in c.channel_get():
                pass

csv_in1= csv_in('partner.csv')
csv_in2= csv_in('partner1.csv')
csv_out1= csv_out('partner2.csv')
sort1=sort('name')
log1=logger(name='Read Partner File')
log2=logger(name='After Sort')
sleep1=sleep(1)

tran=transition(csv_in1,sort1)
tran1=transition(csv_in2,sort1)
tran4=transition(sort1,sleep1)
tran4=transition(sleep1,log2)
tran5=transition(sort1,csv_out1)


#job1=job([csv_out1,log2])
#job1.run()


in1 = csv_in('partner.csv')
in2 = csv_in('partner2.csv')
in3 = csv_in('partner3.csv')
in4 = csv_in('add.csv')
diff1 = diff(['id'])

log_1 = logger_bloc(name="Original Data")
log_2 = logger_bloc(name="Modified Data")

log1 = logger(name="Log Same")
log2 = logger(name="Log Add")
log3 = logger(name="Log Remove")
log4 = logger(name="Log Update")


csv_out1 = csv_out('add.csv')

#transition(in1, log_1)
#transition(in2, log_2)
#
#transition(in1, diff1, channel_destination='original')
#transition(in2, diff1, channel_destination='modified')
#
#transition(diff1, log1, channel_source="same")
#transition(diff1, log3, channel_source="remove")
#transition(diff1, log2, channel_source="add")
#transition(diff1, csv_out1, channel_source="add")
#transition(diff1, log4, channel_source="update")
#
#job = job([log1,log2,log3,log4,csv_out1])
#job.run()

transition(in3, log1)
transition(in4, log1)

c1 = control_count()
transition(in3, c1)
transition(in4, c1)
transition(log1, c1, channel_destination='end')

log10=logger(name='Count')
transition(c1, log10)

job = job([log10])
job.run()



#class a(object):
#    def test(self, hello):
#        print hello
#b=a()
#
#import pickle
#pickle.dump(b,file('result.pickle','wb+'))




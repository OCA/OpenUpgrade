
import csv
import etl

class etl_csv_input(etl.node):
    def __init__(self, filename, *args, **argv):
        super(etl_csv_input, self).__init__(*args, **argv)
        self.filename = filename

    def run(self):
        self.start()
        fp = csv.DictReader(file(self.filename))
        for row in fp:
            self.input([row])
        return self.stop()

class etl_csv_output(etl.node):
    def __init__(self, filename, *args, **argv):
        super(etl_csv_output, self).__init__(*args, **argv)
        self.fp = file(filename, 'wb+')

    def input(self, rows, transition=None):
        fieldnames = rows[0].keys()
        fp = csv.DictWriter(self.fp, fieldnames)
        fp.writerow(dict(map(lambda x: (x,x), fieldnames)))
        fp.writerows(rows)
        self.output(rows)
        return True

class etl_operator_sort(etl.node):
    def __init__(self, fieldname, *args, **argv):
        self.fieldname = fieldname
        super(etl_operator_sort, self).__init__(*args, **argv)

    def start(self, transition=None):
        self.data = []

    def stop(self, transition=None):
        self.data.sort(lambda x,y: cmp(x[self.fieldname],y[self.fieldname]))
        self.output(self.data)
        return super(etl_operator_sort, self).stop(transition)

    def input(self, rows, transition=None):
        self.data += rows

class etl_operator_log(etl.node):
    def input(self, rows, transition=None):
        print 'Data Logger:', self.name
        for row in rows:
            print '\t', row
        super(etl_operator_log, self).input(rows, transition)

class etl_operator_log_bloc(etl.node):
    def __init__(self, *args, **argv):
        self.data = []
        super(etl_operator_log_bloc, self).__init__(*args, **argv)

    def input(self, rows, transition=None):
        self.data += rows
        return super(etl_operator_log_bloc, self).input(rows, transition)

    def stop(self, transition=None):
        ok = super(etl_operator_log_bloc, self).stop(transition)
        if ok:
            print 'Data Bloc Logger:', self.name
            for row in self.data:
                print '\t', row
        return ok

class etl_operator_diff(etl.node):
    def __init__(self, keys, *args, **argv):
        self.keys = keys
        self.data = {}
        self.diff = []
        self.same = []
        super(etl_operator_diff, self).__init__(*args, **argv)

    # Return the key of a row
    def key_get(self, row):
        result = []
        for k in self.keys:
            result.append(row[k])
        return tuple(result)

    def stop(self, transition=None):
        ok = super(etl_operator_diff, self).stop(transition)
        if ok:
            self.output(self.diff, 'update')
            self.output(self.same, 'same')
            todo = ['remove','add']
            for k in self.data:
                self.output(self.data[k].values(), todo.pop())
        return ok

    def input(self, rows, transition=None):
        if transition not in self.data:
            self.data[transition] = {}
        other = None
        for key in self.data.keys():
            if key<>transition:
                other = key
                break
        for r in rows:
            key = self.key_get(r)
            if other and (key in self.data[other]):
                if self.data[other][key] == r:
                    self.same.append(r)
                else:
                    self.diff.append(r)
                del self.data[other][key]
            else:
                self.data[transition][key] = r

class etl_merge(etl.node):
    pass

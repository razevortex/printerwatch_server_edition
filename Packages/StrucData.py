from Packages.SubPkg.csv_handles import *
from Packages.SubPkg.foos import *

db_dict_template = {}
db_keys = ['TonerBK', 'TonerC', 'TonerM', 'TonerY', 'Printed_BW', 'Printed_BCYM', 'Copied_BW', 'Copied_BCYM']
for key in db_keys:
    db_dict_template[key] = 'NaN'

class DataSet(object):
    def __init__(self, ID, headless=False):
        if headless is not True:
            self.Const = {}
            self.Static = {}
            # Data is struc [(index/TimeStamp, {key, val}), (...), ... ]
            self.get_device_data(ID)
        self.Data = []
        self.get_struc_data(ID)
        self.processing = False
        self.ProcessedData = []

    def get_device_data(self, id):
        cli = dbClient()
        cli.updateData()
        for line in cli.ClientData:
            if line['Serial_No'] == id:
                self.Const['Serial_No'] = line['Serial_No']
                self.Const['Device'] = f"{line['Manufacture']} {line['Model']}"
                self.Static['IP'] = line['IP']
        spec = dbClientSpecs()
        spec.updateData()
        for line in spec.ClientData:
            if line['Serial_No'] == id:
                # Get and Add User / Location data
                string = user = loc = ''
                if line['Contact'] != 'NaN':
                    user = line['Contact']
                if line['Location'] != 'NaN':
                    loc = line['Location']
                string += user
                if loc != user:
                    string += f' {loc}'
                self.Static['UserLoc'] = string
                # Get and Add a string with the used Cartidges
                string = ''
                for cart in ['CartBK', 'CartC', 'CartM', 'CartY']:
                    if line[cart] != 'NaN':
                        if string != '':
                            string += ';'
                        string += line[cart]
                self.Static['Carts'] = string

    def get_struc_data(self, id):
        db = dbRequest(id)
        self.Data = []
        for line in db.ClientData:
            dic_t = copy.deepcopy(db_dict_template)
            index = line['Time_Stamp']
            for key in db_keys:
                if line[key] != 'NaN':
                    dic_t[key] = int(line[key])
            self.Data.append((index, dic_t))

    def light_Data(self, reduce='time', key=''):
        if self.processing is not False:
            data = self.ProcessedData
        else:
            data = self.Data
        arr_t = []
        if reduce == 'time':
            dates = []
            for index, dic in data:
                date = index.split(' ')
                date = date[0]
                if date not in dates:
                    arr_t.append((date, dic))
                    dates.append(date)
            #self.processing = True
            #self.ProcessedData = arr_t
        elif reduce == 'keys':
            if type(key) == list:
                for index, dic in data:
                    dic_t = {}
                    for k in key:
                        dic_t[k] = dic[k]
                    arr_t.append((index, dic_t))
            else:
                for index, dic in data:
                    arr_t.append((index, {key: dic[key]}))
        self.processing = True
        self.ProcessedData = arr_t

    def diff_Data(self):
        if self.processing is not False:
            data = self.ProcessedData
        else:
            data = self.Data
        t, v = data[0]
        template = {}
        for key in v.keys():
            template[key] = 0
        '''        template = {'TonerBK': 0, 'TonerC': 0, 'TonerM': 0, 'TonerY': 0, 'Printed_BW': 0, 'Printed_BCYM': 0,
                    'Copied_BW': 0, 'Copied_BCYM': 0}
        '''
        index, dic_1 = data[0]
        arr_t = [(index, template)]
        hold = dic_1
        for index, dic in data[1:]:
            diff = copy.deepcopy(template)
            for key in dic.keys():
                if hold[key] != 'NaN':
                    hold, diff = calculate_diff(key, hold, dic, diff)
            arr_t.append((index, diff))
        self.processing = True
        self.ProcessedData = arr_t

    def combine_keys(self, combine, to):
        if self.processing is not False:
            data = self.ProcessedData
        else:
            data = self.Data
        arr_t = []
        for index, dic in data:
            dic_t = {to: 0}
            for key in dic.keys():
                if key in combine:
                    if dic[key] != 'NaN':
                        dic_t[to] += dic[key]
                else:
                    dic_t[key] = dic[key]
            arr_t.append((index, dic_t))
        self.processing = True
        self.ProcessedData = arr_t

    def sum_data(self):
        if self.processing is not False:
            data = self.ProcessedData
        else:
            data = self.Data
        first = data[0][1]
        dic_t = {}
        for key in first.keys():
            dic_t[key] = 0
        arr_t = []
        for index, dic in data:
            for key in dic.keys():
                dic_t[key] += dic[key]
            arr_t.append((index, copy.deepcopy(dic_t)))
        self.processing = True
        self.ProcessedData = arr_t

    def table_data(self):
        if self.processing is not False:
            data = self.ProcessedData
        else:
            data = self.Data
        arr_t = []
        for index, dic in data:
            dic_t = {'Time_Stamp': index}
            dic_t.update(dic)
            arr_t.append(dic_t)
        return arr_t

    def head_data(self, line='1'):
        if line == '1':
            return f"{self.Const['Serial_No']}, {self.Const['Device']}"
        if line == '2':
            return f"{self.Static['UserLoc']}, {self.Static['IP']}"

fuse = [('TonerC', 'TonerM', 'TonerY'),
         ('Printed_BW', 'Copied_BW'),
         ('Printed_BCYM', 'Copied_BCYM')]
to = ['TonerCYM', 'BW', 'BCYM']
ttt = {'BCYM': 0, 'BW': 0, 'TonerCYM': 0, 'TonerBK': 0}

def get_global_timeline():
    cli = dbClient()
    cli.updateData()
    time_index = []
    for line in cli.ClientData:
        id = line['Serial_No']
        container = DataSet(id, headless=True)
        container.light_Data()

        for day in container.ProcessedData:
            time_index.append(day[0])
    time_index = list(set(time_index))
    time_index = sorted(time_index)
    return time_index

def neutral_timeline():
    arr_t = []
    for i in get_global_timeline():
        arr_t.append((i, 0))
    return arr_t

def get_group_id_set(filter='', filter_for='Manufacture'):
    cli = dbClient()
    cli.updateData()
    arr_t = []
    dic_t = {}
    if filter == '':
        clients = cli.ClientData
    else:
        arr_t = []
        for line in cli.ClientData:
            for key, val in line.items():
                for v in val:
                    if filter in str(v):
                        arr_t.append(line)
                        break
        clients = arr_t
    arr_t = []
    for line in clients:
        arr_t.append(line[filter_for])
    arr_t = list(set(arr_t))
    arr_t = sorted(arr_t)
    for key in arr_t:
        grouped = []
        for line in cli.ClientData:
            if line[filter_for] == key:
                grouped.append(line['Serial_No'])
        dic_t[key] = grouped
    return dic_t

def create_group_data(id_set, data_key, time_line):
    if data_key == 'BW':
        fuse = ('Printed_BW', 'Copied_BW')
        to = 'BW'
    elif data_key == 'BCYM':
        fuse = ('Printed_BCYM', 'Copied_BCYM')
        to = 'BCYM'
    else:
        fuse = ('TonerC', 'TonerM', 'TonerY')
        to = ['TonerCYM', 'BW', 'BCYM']
    for id in id_set:
        container = DataSet(id, headless=True)
        container.light_Data()
        container.combine_keys(fuse, to)
        container.light_Data(reduce='keys', key=to)
        container.diff_Data()
        #for i in range(len(fuse)):
        #    container.combine_keys(fuse, to)
        arr_t = []
        for time, val in time_line:
            for index, dic in container.ProcessedData:
                if index == time:
                    val += dic[data_key]
            arr_t.append((time, val))
        time_line = arr_t
    arr_t = []
    for time, val in time_line:
        arr_t.append(val)
    return arr_t

colors = ['#0000FF','#00FF00','#FF0000','#990000','#009900','#000099','#990099','#009999','#999900','#ffff00','#00ffff','#ff00ff']

def create_plot_data(group, filter, data_key):
    id_set = get_group_id_set(filter=filter, filter_for=group)
    time_line = neutral_timeline()
    arr_t = []
    for key in id_set.keys():
        dic_t = {}
        group_data = create_group_data(id_set[key], data_key, time_line)
        print(key, group_data)
        val = 0
        data = []
        for i in group_data:
            val += i
            data.append(val)
        dic_t['data'] = data
        dic_t['label'] = key
        arr_t.append(dic_t)
    data = []
    for i in range(len(arr_t)):
        dic = arr_t[i]
        dic['borderColor'] = colors[i % len(colors)]
        dic['pointRadius'] = 1
        dic['lineTension'] = 0.2
        data.append(dic)
    return data

if __name__ == '__main__':
    id_set = get_group_id_set(filter_for='Model')
    time_line = neutral_timeline()
    print(id_set)
    for key in id_set.keys():
        print(len(id_set[key]))
        group_data = create_group_data(id_set[key], 'BW', time_line)
        print(key, group_data)
        val = 0
        data = []
        for i in group_data:
            val += i
            data.append(val)
        print(key)
        print(data)
        print(len(data))


    '''
        #print(len(container.ProcessedData))
        container.diff_Data()
        for i in range(len(fuse)):
            container.combine_keys(fuse[i], to[i])
        container.sum_data()
        for line in container.ProcessedData:
            print(line)

            all.append(line)
        dates = []
        for line in all:
            dates.append(line[0])
        data = []
        for date in list(set(dates)):
            dic_t = copy.deepcopy(ttt)
            for index, dic in all:
                if date == index:
                    for key in dic.keys():
                        dic_t[key] += dic[key]
            data.append((date, dic_t))
    for line in sorted(data):
        print(line)'''
import time

class Cache:

    def __init__(self, default_ttl):
        self.default_ttl = default_ttl
        self.entrys = []
        for i in range(100):
            self.entrys.append(Entry(i,'','','',0,0,0.0))

    def insert_DB(self,file):
        f = open(file, 'r')
        lines = f.readlines()
        for line in lines:
            list = line.split(' ')
            if line.startswith('#') or line == '\n':
                continue
            if self.search_available() != -1:
                ind = self.search_available()
                self.entrys[ind] = Entry(ind,list[0],list[1],list[2],list[3],list[4][:-1],'FILE',True)
            else:
                self.remove_entry_last()
                self.entrys[self.search_available()] = Entry(ind,list[0],list[1],list[2],list[3],list[4][:-1],'FILE',True)
        
    def insert_cache(self,string):
        list = string.split(',')
        if self.search_available() != -1:
            ind = self.search_available()
            self.entrys[ind] = Entry(ind,list[0],list[1],list[2],list[3],list[3],'OTHERS',True)
        else:
            self.remove_entry_last()
            ind = self.search_available()
            self.entrys[ind] = Entry(ind,list[0],list[1],list[2],list[3],list[3],'OTHERS',True)

    def remove_entry_last(self):
        for entry in self.entrys:
            if entry.origin == 'OTHERS':
                if (time.time() - entry.timeStamp) > entry.ttl:
                    self.entrys.remove(entry)
        last = -1
        last_time = 0
        for entry in self.entrys:
            if entry.timeStamp > last_time and entry.origin != 'FILE':
                last = entry.index
        self.entrys[last] = Entry(last,'','',0,0,0.0)

    def search_available(self):
        for entry in self.entrys:
            if entry.state == False:
                return entry.index
        return -1

    def get_entry(self,name,type):
        list = []
        for entry in self.entrys:
            if entry.name.endswith(name) and entry.type == type:
                list.append(entry.__str__())
        return list

    def get_extra_values(self,name,type):
        list = []
        for entry in self.entrys:
            if entry.name.endswith(name) and (entry.type == 'NS' or entry.type == type):
                for entry2 in self.entrys:
                    if entry2.name == entry.value and entry2.type == 'A':
                        list.append(entry2.__str__())
        return list

    def get_entries_for_domain(self,domain):
        list = []
        for entry in self.entrys:
            if entry.name.endswith(domain):
                list.append(entry.__str__())
                #if entry.type == 'SOAREFRESH' or entry.type == 'SOASERIAL' or entry.type == 'SOARETRY' or entry.type == 'SOAEXPIRE':
                #    list.append((entry.__str__(),int(entry.value)))
                #else:
                #    list.append((entry.__str__(),0))
        return list

    def get_query(self,name,type):
        extra_tags = []
        default = []
        for entry in self.entrys:
            if entry.name==name and entry.type == type:
                default.append(entry.__str__())
                extra_tags.append(entry.value)
        auto_values = []
        for entry in self.entrys:
            if entry.name==name and entry.type == 'NS':
                auto_values.append(entry.__str__())
                extra_tags.append(entry.value)
        extra_values = []
        for entry in self.entrys:
            if entry.name in extra_tags and entry.type == 'A':
                extra_values.append(entry.__str__())
        return [default,auto_values,extra_values]
    
    def get_refresh(self):
        num = 0
        for entry in self.entrys:
            if entry.type == 'SOAREFRESH':
                num = entry.value
                break
        return num

    def get_serial(self):
        num = 0
        for entry in self.entrys:
            if entry.type == 'SOASERIAL':
                num = entry.value
                break
        return num

    def get_retry(self):
        num = 0
        for entry in self.entrys:
            if entry.type == 'SOARETRY':
                num = entry.value
                break
        return num
    
    def get_expire(self):
        num = 0
        for entry in self.entrys:
            if entry.type == 'SOAEXPIRE':
                num = entry.value
                break
        return num

    def __str__(self):
        string = ''
        for entry in self.entrys:
            string += str(entry.index)
            string += ','
            string += str(entry)
            string += ','
            string += str(entry.origin)
            string += ','
            string += str(entry.timeStamp)
            string += ','
            string += str(entry.state)
            string += '\n'
        
        return string

            
class Entry:

    def __init__(self,index,name,type,value,ttl,priority,origin,state=False):
        self.index = index
        self.name = name
        self.type = type
        self.value = value
        self.ttl = ttl
        self.priority = priority
        self.origin = origin
        self.timeStamp = time.time()
        self.state = state

    def __str__(self):
        return str(self.name+' '+self.type+' '+self.value+' '+str(self.ttl)+' '+str(self.priority))


def main():
    cache = Cache(86400)
    cache.insert_DB('./test_configs/cam.db') 
    print(cache)
    print(cache.get_entries_for_domain('cam.'))

if __name__=='__main__':
    main()
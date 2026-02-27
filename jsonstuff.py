import json, os

class DBObject():
    def __init__(self) -> None:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        if 'json' not in os.listdir():
            os.mkdir('json')
        os.chdir('json')
        try:
            with open('server.json','r') as f:
                data = json.load(f)
        except json.decoder.JSONDecodeError:
            data = {'server_ct':0, 'server_ids':[], 'data':{}}
            print('b')
        except FileNotFoundError:
            open('server.json','x').close()
            data = {'server_ct':0, 'server_ids':[], 'data':{}}
            print('c')

        self.ct = data['server_ct']
        self.ids = data['server_ids']
        self.data = data['data']

    def add_server(self, name: str, guid: int, chid:int, ip: str, port=25565):
        if guid not in self.ids:
            self.data[str(guid)] = {'server_name': name, 
                            'server_id': guid,
                            'channel_id': chid, 
                            'mc_server_ip':ip, 
                            'mc_server_port':port}
            self.ids.append(guid)
            self.ct = len(self.ids)
    
    def rm_server(self, id:int):
        del self.data[str(id)]
        self.ids.remove(id)
        self.ct -= 1

    def format_data(self):
        return {'server_ct':self.ct, 'server_ids':self.ids, 'data':self.data}

    def __str__(self):
        return json.dumps(self.format_data(),indent=4)

    def save_db(self):
        with open('server.json','w') as f:
            json.dump(self.format_data(),f)

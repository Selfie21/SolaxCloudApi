import requests, json
import sched, time


class Inverter:

    __sensor_map = {
        'PV1 Current':                (0, 'A'),
        'PV1 Voltage':                (2, 'V'),

        'Output Current Phase 1':     (4, 'A'),
        'Network Voltage Phase 1':    (5, 'V'),
        'AC Power':                   (6, 'W'),

        'Inverter Temperature':       (7, 'C'),
        'Today\'s Energy':            (8, 'kWh'),
        'Total Energy':               (9, 'kWh'),
        'Exported Power':             (10, 'W'),
        'PV1 Power':                  (11, 'W'),
        'PV2 Power':                  (12, 'W'),

        'Battery Voltage':            (13, 'V'),
        'Battery Current':            (14, 'A'),
        'Battery Power':              (15, 'W'),
        'Battery Temperature':        (16, 'C'),
        'Battery Remaining Capacity': (21, '%'),

        'Total Feed-in Energy':       (41, 'kWh'),
        'Total Consumption':          (42, 'kWh'),

        'Power Now Phase 1':          (43, 'W'),
        'Power Now Phase 2':          (44, 'W'),
        'Power Now Phase 3':          (45, 'W'),
        'Output Current Phase 2':     (46, 'A'),
        'Output Current Phase 3':     (47, 'A'),
        'Network Voltage Phase 2':    (48, 'V'),
        'Network Voltage Phase 3':    (49, 'V'),

        'Grid Frequency Phase 1':     (50, 'Hz'),
        'Grid Frequency Phase 2':     (51, 'Hz'),
        'Grid Frequency Phase 3':     (52, 'Hz'),

        'EPS Voltage':                (53, 'V'),
        'EPS Current':                (54, 'A'),
        'EPS Power':                  (55, 'W'),
        'EPS Frequency':              (56, 'Hz'),
    }


class DataHandler:

    def __init__(self, url):
        self.url = url

    def make_request(self):
        response = None
        try:
            response = requests.post(self.url)
            return response.content
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as err:
            print(err)
        finally:
            response.close()

    def start_looping_requests(self, sc):
        data = currentHandler.make_request()
        data_string = data.decode('utf8').replace("'", '"')
        data_json = json.loads(data_string)['Data']
        self.print_data(data_json)
        s.enter(5, 1, self.start_looping_requests, (sc,))

    def print_data(self, arrData):
        index = 0
        for dataset in arrData:
            print(int(index), int(dataset))
            index += 1

solaxurl = 'http://5.8.8.8:80/?optType=ReadRealTimeData'
currentHandler = DataHandler(solaxurl)

s = sched.scheduler(time.time, time.sleep)
s.enter(5, 1, currentHandler.start_looping_requests, (s,))
s.run()

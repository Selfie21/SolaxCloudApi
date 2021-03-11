import requests
import json
from datetime import datetime


class SolaxCrawler():

    def __init__(self):
        date_today = datetime.now().strftime('%Y-%m-%d')
        core_url = 'https://www.solaxcloud.com'
        self.original_url = core_url + '/#/overview'
        self.login_url = core_url + '/phoebus/login/loginNew'
        self.data_url = core_url + '/phoebus/userIndex/getSiteInfo'
        self.logout_url = core_url + '/phoebus/websiteLocation/getLocation'

        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/80.0.3987.132 Safari/537.36'
        }

        self.data_params = {
            'siteId': '710029268595245056'
        }



    def get_data(self, session):
        data_response = session.post(self.data_url, params=self.data_params, headers=self.headers, verify=False)

        if not self.is_json(data_response.text):
            return 0, 0, 0

        data = json.loads(data_response.text)
        daily_yield = data['todayYield']
        yearly_yield = data['yearYield']
        current_power = data['gridPower']

        # close session
        requests.get(self.logout_url, verify=False)
        requests.post(self.logout_url, verify=False, headers={'Connection': 'close'})

        return current_power, daily_yield, yearly_yield

    def initiate_login_session(self, username, password):
        login_data = {'roletype': '5'}
        login_data.update({'username': username, 'userpwd': password})

        session = requests.session()
        session.post(self.login_url, data=login_data, headers=self.headers, verify=False)
        session.get(self.original_url, headers=self.headers, verify=False)
        return session

    def is_json(self, json_file):
        try:
            json.loads(json_file)
        except ValueError as e:
            return False
        return True

    def find_year_data(self, list_data, year):
        for dataset in list_data:
            if dataset['time'] == year:
                return dataset['yieldtoday']
        return 0


username = 'test'
password = 'cc03e747a6afbbcbf8be7668acfebee5'

solaxretriever = SolaxCrawler()
solax_session = solaxretriever.initiate_login_session(username, password)
data = solaxretriever.get_data(solax_session)
print(data)
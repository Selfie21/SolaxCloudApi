import requests
import json
from datetime import datetime


class SolaxCrawler():

    def __init__(self):
        date_today = datetime.now().strftime('%Y-%m-%d')
        core_url = 'https://www.solaxcloud.com'
        self.original_url = core_url + '/i18n/language.do?language=en_US&url=/views/index.jsp'
        self.login_url = core_url + '/login/login.do'
        self.data_url = core_url + '/userIndex/getCurrentData.do'
        self.backup_url = core_url + '/userIndex/getYield.do'
        self.logout_url = core_url + '/login/loginOut.do'

        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/80.0.3987.132 Safari/537.36'
        }

        self.data_params = {
            ('currentTime', date_today + ' 12:01:42')
        }

        self.backup_params = {
            ('reportType', '4'),
            ('day', str(datetime.now().day)),
            ('month', str(datetime.now().month)),
            ('year', str(datetime.now().year)),
            ('webTime', datetime.now().strftime('%Y,%m,%d'))
        }



    def get_data(self, session):
        data_response = session.post(self.data_url, params=self.data_params, headers=self.headers, verify=False)

        if not self.is_json(data_response.text):
            return 0, 0, 0

        data = json.loads(data_response.text)
        daily_yield = data['todayYield']
        yearly_yield = data['yearYield']
        current_power = data['gridpower']

        # the solax website sometimes has the bug where it shows the daily yield as yearly yield
        # if that happens i take the yearly yield from another source
        if daily_yield == yearly_yield:
            data_response = session.post(self.backup_url, params=self.backup_params, headers=self.headers, verify=False)
            data = json.loads(data_response.text)
            yearly_yield = self.find_year_data(data['returnList'], 2020)

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
password = '098f6bcd4621d373cade4e832627b4f6'

solaxretriever = SolaxCrawler()
solax_session = solaxretriever.initiate_login_session(username, password)
data = solaxretriever.get_data(solax_session)
print(data)
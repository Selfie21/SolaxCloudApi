import requests
import json
from datetime import datetime


class SolaxCrawler():

    def __init__(self):
        date_today = datetime.now().strftime('%Y-%m-%d')
        self.original_url = 'https://www.solaxcloud.com/i18n/language.do?language=en_US&url=/views/index.jsp'
        self.login_url = 'https://www.solaxcloud.com/login/login.do'
        self.data_url = 'https://www.solaxcloud.com/userIndex/getCurrentData.do?currentTime=' + date_today + '+12%3A01%3A42'
        self.logout_url = 'https://www.solaxcloud.com/login/loginOut.do'

        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/80.0.3987.132 Safari/537.36'
        }


    def get_data(self, session):
        data_response = session.post(self.data_url, headers=self.headers, verify=False)
        data = json.loads(data_response.text)

        daily_yield = data['todayYield']
        monthly_yield = data['monthYield']
        yearly_yield = data['yearYield']
        total_yield = data['totalYield']
        current_power = data['gridpower']

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


username = 'user'
password = '5f4dcc3b5aa765d61d8327deb882cf99'

solaxretriever = SolaxCrawler()
solax_session = solaxretriever.initiate_login_session(username, password)
data = solaxretriever.get_data(solax_session)

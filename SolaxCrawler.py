import requests
import json
import time
from datetime import datetime


class SolaxCrawler():

    def get_data(self):
        date_today = datetime.now().strftime('%Y-%m-%d')
        original_url = 'https://www.solaxcloud.com/i18n/language.do?language=en_US&url=/views/index.jsp'
        login_url = 'https://www.solaxcloud.com/login/login.do'
        logout_url = 'https://www.solaxcloud.com/login/loginOut.do'

        power_url = 'https://www.solaxcloud.com/userIndex/getPower.do'
        yield_url = 'https://www.solaxcloud.com/device/getPage.do?enableFlag=&SN=&siteId=&siteName=&loginName=&currentTime=' + date_today + '+21%3A28%3A24&wifiSN=&inverterType=&nation=&size=10&current=1'

        #you should use your own here (just inspect your browser and copy it)
        headers = {
             'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
        }

        login_data = {
            'username': 'Username',
            'userpwd': 'Password', #the password should be encrypted with md5
            'roletype': '5'        #password = 5f4dcc3b5aa765d61d8327deb882cf99
        }

        solax_session = requests.session()
        # if you want to verify the Certificate you have to install the Certificate from the solax site
        # and run refer to it in the verify param
        solax_session.post(login_url, data=login_data, headers=headers, verify=False)

        solax_session.get(original_url, headers=headers, verify=False)
        time.sleep(1)
        response_power = solax_session.get(power_url, headers=headers, verify=False)
        current_power = json.loads(response_power.text)['gridPower']

        response_yield = solax_session.get(yield_url, headers=headers, verify=False)
        yield_data = json.loads(response_yield.text)['rows'][0]
        daily_yield = yield_data['todayYield']
        total_yield = yield_data['totalYield']

        # close session
        r = requests.get(logout_url, verify=False)
        q = requests.post(logout_url, verify=False, headers={'Connection': 'close'})

        return current_power, daily_yield, total_yield

solaxretriever = SolaxCrawler()
data = solaxretriever.get_data()
print(data)
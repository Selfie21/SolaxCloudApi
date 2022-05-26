from Client import Client

if __name__ == "__main__":

    token_id = '20220524015936043146470'
    site_id = 'SWBBCCDVNZ'
    ENDPOINT = r'https://www.solaxcloud.com:9443/proxy/api/getRealtimeInfo.do'

    kwargs = {'tokenId': token_id,
              'sn': site_id}

    data = Client.request('GET', ENDPOINT, **kwargs)
    speech = ''

    if data is None:
        speech = 'Wrong token data entered. At least did not receive a valid response from Solax Server. Please try again!'

    acpower = data['acpower']
    today_kwh = data['yieldtoday']
    total_kwh = data['yieldtotal']
    bat_pow = data['batPower']
    speech = 'Total Yield today is: ' + str(int(today_kwh)) + 'kwh. Total Yield is: ' + str(int(total_kwh)) + 'kwh. Current Battery Power is: ' + str(int(bat_pow))


"""
ac power: erzeugte Leistung (AC) von Wechselrichter
yield: Energie PV Anlage
feedinpower:  Leistung P
feedinenergy: Gesamte ins Netz eingespeiste Energie
consumeenergy: Gesamte vom Netz benutze Energie
'batterie': Power Battery
"""








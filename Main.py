from Client import Client

if __name__ == "__main__":

    token_id = '20220524015936043146470'
    site_id = 'SWBBCCDVNZ'
    ENDPOINT = r'https://www.solaxcloud.com:9443/proxy/api/getRealtimeInfo.do'

    kwargs = {'tokenId': token_id,
              'sn': site_id}

    data = Client.request('GET', ENDPOINT, **kwargs)

    acpower = data['acpower']
    today_kwh = data['yieldtoday']
    total_kwh = data['yieldtotal']
    bat_pow = data['batPower']
    print(today_kwh)


"""
ac power: erzeugte Leistung (AC) von Wechselrichter
yield: Energie PV Anlage
feedinpower:  Leistung P
feedinenergy: Gesamte ins Netz eingespeiste Energie
consumeenergy: Gesamte vom Netz benutze Energie
'batterie': Power Battery
"""








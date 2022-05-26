from requests import Request, Session


class Client:

    session = Session()

    @staticmethod
    def send_request(method, adress, **kwargs):
        request = Request(method, adress, params=kwargs)
        prepared = request.prepare()
        return Client.session.send(prepared)

    @staticmethod
    def process_request(response):
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                return None
            return data['result']

    @staticmethod
    def request(method, adress, **kwargs):
        response = Client.send_request(method, adress, **kwargs)
        content = Client.process_request(response)
        return content

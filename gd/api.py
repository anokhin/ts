import requests

__author__ = 'Nikolay Anokhin'


class Api(object):

    endpoint = ''

    def __init__(self, access_token):
        self.access_token = access_token

    def call(self, method, **params):
        request_params = params.copy()
        request_params["access_token"] = self.access_token
        try:
            response = requests.get(self.endpoint.format(method=method), params=request_params)
            if response.status_code != 200:
                raise requests.exceptions.RequestException("Bad status code {}".format(response.status_code))
            return response.json()
        except requests.exceptions.RequestException as re:
            print "A n API call failed with exception {}".format(re)
            raise

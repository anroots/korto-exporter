from json import JSONDecodeError

import requests
import sys


class Korto:
    def __init__(self, logger, api_url, auth_token):
        self.api_url = api_url
        self.logger = logger
        self.jar = requests.cookies.RequestsCookieJar()
        self.jar.set('auth_token', auth_token)

    def get_meter_readings(self, apartment_id):
        request_data = {
            'operationName': 'GetMetersData',
            'variables': {
                'id': apartment_id
            },
            'query': '''
          query GetMetersData($id: ID!, $ignore_date_limits: Boolean) {
  viewer {
    id
    apartment(id: $id) {
      id
      meters(ignore_date_limits: $ignore_date_limits) {
        id
        type
        description
        unit
        step
        precision
        reading
        reading_date
        reading_origin
        consumption
        __typename
      }
      readings_allowed
      readings_start
      readings_end
      __typename
    }
    __typename
  }
}
          '''
        }
        self.logger.debug('Starting collection of Korto meters')
        meters = self.make_request(request_data).get('data').get('viewer').get('apartment').get('meters')
        self.logger.debug('Received {} metrics from Korto'.format(len(meters)))

        return meters

    @staticmethod
    def get_request_headers():
        return {
            'Accept': '*/*',
            'Accept-Language': 'en',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
        }

    def make_request(self, request_payload):
        self.logger.debug('Sending request to Korto API')
        try:
            r = requests.post(url=self.api_url, cookies=self.jar, json=request_payload, headers=self.get_request_headers())
        except requests.exceptions.RequestException as e:
            self.logger.fatal(e)
            self.logger.fatal('Received error from HTTP request, exiting')
            sys.exit(1)
        try:
            response = r.json()
        except JSONDecodeError as e:
            self.logger.fatal('Korto HTTP endpoint returned invalid JSON, can not parse it')
            self.logger.fatal(r.text)
            sys.exit(1)
        if r.json().get('errors'):
            self.logger.fatal(response.get('errors')[0].get('message'))
            self.logger.fatal('Received error from Korto, exiting')
            sys.exit(1)
        return response

    def get_apartment_balance(self,apartment_id):
        request_data = {
            'operationName': 'GetApartmentBalance',
            'variables': {
                'id': apartment_id
            },
            'query': '''
                  query GetApartmentBalance($id: ID!) {
  viewer {
    id
    apartment(id: $id) {
      id
      balance {
        balance
        balance_date
        last_payment
        last_payment_date
        __typename
      }
      __typename
    }
    __typename
  }
}
                  '''
        }

        self.logger.debug('Starting collection of Korto balances')
        balance = self.make_request(request_data).get('data').get('viewer').get('apartment').get('balance')
        self.logger.debug('Received balance info from Korto')
        return balance

import sys
import datetime
from prometheus_client import start_http_server, Summary
import time
from prometheus_client.core import REGISTRY
import logging
import os
from prometheus_client.metrics_core import GaugeMetricFamily

from src.lib.korto import Korto

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'))
logger = logging.getLogger('korto-exporter')


class KortoCollector(object):
    def __init__(self, api_url, apartment_id, auth_token):
        self.apartment_id = apartment_id
        self.korto = Korto(logger, api_url, auth_token)

    def date_format(self, date):
        if date is None:
            return '1970-01-01'
        return str(datetime.datetime.strptime(date, '%d.%m.%Y').date())

    @REQUEST_TIME.time()
    def collect(self):
        logger.info('Scraping Korto for new metrics...')

        meter_readings = self.korto.get_meter_readings(self.apartment_id)

        for meter in meter_readings:
            gauge = GaugeMetricFamily("korto_meter_reading", 'Reading value of a single utility meter',
                                      labels=['meter_id', 'type', 'unit', 'reading_origin', 'reading_date',
                                              'apartment_id'])
            gauge.add_metric([meter.get('id'), meter.get('type'), meter.get('unit'), meter.get('reading_origin'),
                              self.date_format(meter.get('reading_date')), str(self.apartment_id)],
                             meter.get('reading'))
            yield gauge

            gauge = GaugeMetricFamily("korto_meter_consumption", 'Consumption value of a single utility meter',
                                      labels=['meter_id', 'type', 'unit', 'apartment_id'])
            gauge.add_metric([meter.get('id'), meter.get('type'), meter.get('unit'), str(self.apartment_id)],
                             meter.get('consumption'))
            yield gauge

        balance = self.korto.get_apartment_balance(apartment_id)
        gauge = GaugeMetricFamily("korto_apartment_balance", 'Balance of the apartment in EUR',
                                  labels=['date', 'apartment_id'])
        gauge.add_metric([self.date_format(balance.get('balance_date')), str(self.apartment_id)],
                         balance.get('balance') or 0)
        yield gauge

        gauge = GaugeMetricFamily("korto_apartment_last_payment", 'Last payment value in EUR',
                                  labels=['date', 'apartment_id'])
        gauge.add_metric([self.date_format(balance.get('last_payment_date')), str(self.apartment_id)],
                         balance.get('last_payment') or 0)
        yield gauge

        logger.info('Scraping completed')


if __name__ == '__main__':
    logger.info('korto-exporter (https://github.com/anroots/korto-exporter) starting up...')
    api_url = os.environ.get('KORTO_API_URL', 'https://pro.korto.ee/api/')
    apartment_id = os.environ.get('KORTO_APARTMENT_ID')
    auth_token = os.environ.get('KORTO_AUTH_TOKEN')
    if not auth_token or not apartment_id:
        logger.fatal('You need to set required env variables before starting the exporter')
        sys.exit(1)
    REGISTRY.register(KortoCollector(api_url, apartment_id, auth_token))
    start_http_server(8080)
    logger.info('Collector started, listening on port :8080; waiting for scrapes...')

    while True:
        time.sleep(1)

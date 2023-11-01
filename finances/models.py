import requests
from django.db import models
from djmoney.models.fields import MoneyField
from decimal import Decimal
import datetime

#class SpentStats(class):
#    type_ref_hash = models.CharField(max_length=64, blank=True)


class HistoricalPrice(models.Model):
    timestamp = models.IntegerField(unique=True)
    usd_price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    eur_price = MoneyField(max_digits=14, decimal_places=2, default_currency='EUR')
    gbp_price = MoneyField(max_digits=14, decimal_places=2, default_currency='GBP')
    cad_price = MoneyField(max_digits=14, decimal_places=2, default_currency='CAD')
    chf_price = MoneyField(max_digits=14, decimal_places=2, default_currency='CHF')
    aud_price = MoneyField(max_digits=14, decimal_places=2, default_currency='AUD')
    jpy_price = MoneyField(max_digits=14, decimal_places=2, default_currency='JPY')
    usd_to_eur = models.DecimalField(max_digits=10, decimal_places=4)
    usd_to_gbp = models.DecimalField(max_digits=10, decimal_places=4)
    usd_to_cad = models.DecimalField(max_digits=10, decimal_places=4)
    usd_to_chf = models.DecimalField(max_digits=10, decimal_places=4)
    usd_to_aud = models.DecimalField(max_digits=10, decimal_places=4)
    usd_to_jpy = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return f"{self.usd_price} @ {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']


    @classmethod
    def get_or_create_from_api(cls, timestamp=-1):
        if timestamp == -1:
            current_datetime = datetime.datetime.now()
            timestamp = int(current_datetime.timestamp())

        cached_data = cls.objects.filter(timestamp=timestamp).first()

        if cached_data:
            return cached_data, False

        url = f"https://mempool.space/api/v1/historical-price?timestamp={timestamp}"
        response = requests.get(url)
        api_response = response.json()

        obj, created = cls.objects.get_or_create(timestamp=timestamp, defaults={
            'usd_price': Decimal(str(api_response['prices'][0]['USD'])),
            'eur_price': Decimal(str(api_response['prices'][0]['EUR'])),
            'gbp_price': Decimal(str(api_response['prices'][0]['GBP'])),
            'cad_price': Decimal(str(api_response['prices'][0]['CAD'])),
            'chf_price': Decimal(str(api_response['prices'][0]['CHF'])),
            'aud_price': Decimal(str(api_response['prices'][0]['AUD'])),
            'jpy_price': Decimal(str(api_response['prices'][0]['JPY'])),
            'usd_to_eur': Decimal(str(api_response['exchangeRates']['USDEUR'])),
            'usd_to_gbp': Decimal(str(api_response['exchangeRates']['USDGBP'])),
            'usd_to_cad': Decimal(str(api_response['exchangeRates']['USDCAD'])),
            'usd_to_chf': Decimal(str(api_response['exchangeRates']['USDCHF'])),
            'usd_to_aud': Decimal(str(api_response['exchangeRates']['USDAUD'])),
            'usd_to_jpy': Decimal(str(api_response['exchangeRates']['USDJPY']))
        })
        return obj, created

import requests
from django.db import models
from django.contrib import messages
from djmoney.models.fields import MoneyField
from decimal import Decimal
import datetime
from pymempool import MempoolAPI
from labelbase.receivers import compute_type_ref_hash
from django.conf import settings
from jsonfield import JSONField
import json
from django.contrib.auth.models import User
from shared.encryption import get_fernet_key, cipher_suite
import logging
logger = logging.getLogger('labelbase')


class OutputStat(models.Model):
    """
    These fields are unencrypted. Why?

    Glad you asked.

    Encrypting everything always would be better, but...

    * We use a hash for each output and not the output itself.

    * There is no sensitive information stored in these records.


    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    type_ref_hash = models.CharField(max_length=64,
                                     blank=True,
                                     help_text="Reflects type + ref, where type is Output")
    spent = models.BooleanField(
        help_text=(""),
        default=None,
        null=True
    )
    value = models.IntegerField()  # tx output, in sats
    confirmed_at_block_height = models.IntegerField(default=0)
    confirmed_at_block_time = models.IntegerField(default=0)

    last_error = JSONField(default={})
    next_enc_input_attrs = models.TextField(default=None, null=True)  # will be used for fee estimation

    def set_next_input_attributes(self, data):
        json_data = json.dumps(data).encode('utf-8')
        encrypted_data = cipher_suite.encrypt(json_data)
        self.next_enc_input_attrs = encrypted_data.decode('utf-8')

    def next_input_attributes(self):
        if self.next_enc_input_attrs:
            encrypted_data = self.next_enc_input_attrs.encode('utf-8')
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        return json.loads("{}")

    MAINNET = 'mainnet'
    TESTNET = 'testnet'

    NETWORK_CHOICES = [
        (MAINNET, 'Mainnet'),
        (TESTNET, 'Testnet'),
    ]

    network = models.CharField(
        max_length=10,
        choices=NETWORK_CHOICES,
        default='mainnet',
        help_text="Choose the network for this labelbase's label output."
    )

    class Meta:
        unique_together = (("user", "type_ref_hash"),)

    @property
    def get_spent_status(self):
        if self.confirmed_at_block_time == 0:
            return "unconfirmed"
        if self.spent:
            return "spent"
        if not self.spent:
            return "unspent"

    def output_metrics_dict(self, tracked_fiat_value=0, fiat_currency="USD"):
        """
        Get output metrics dictionary for the current instance.

        Args:
            tracked_fiat_value (float): The tracked fiat value (default: None).
            fiat_currency (str): The fiat currency code (default: "USD").

        Returns:
            dict: Output metrics dictionary.
        """
        old_output_value = tracked_fiat_value
        is_tracked = False
        if not fiat_currency:
            fiat_currency = "USD"
        # Check if the block time is confirmed
        if self.confirmed_at_block_time:
            # Get or create HistoricalPrice instance for the confirmed block time
            obj, created = HistoricalPrice.get_or_create_from_api(self.user,
                                        timestamp=self.confirmed_at_block_time
            )
            if obj is None:
                logger.error("No price info found for {}".format(self.confirmed_at_block_time))
                return {}
            print ("obj, created  = {} {}, self.confirmed_at_block_time {}".format(
                obj, created, self.confirmed_at_block_time))

            # Use tracked fiat value if available, otherwise estimate using past price
            if Decimal(tracked_fiat_value) > Decimal(0):
                old_output_value = tracked_fiat_value
                is_tracked = True
            else:
                # Get historical price at the confirmed block time
                old_output_value = (Decimal(self.value)/Decimal("100000000.0"))*obj.get_currency_price(fiat_currency)
            print ("\old_output_value: {} @ timestamp {}".format(old_output_value, self.confirmed_at_block_time))
        else:
            print ("no self.confirmed_at_block_time")

        current_datetime = datetime.datetime.now()
        timestamp = int(current_datetime.timestamp())

        # Get or create HistoricalPrice instance for the current time in UTC
        obj_now, created = HistoricalPrice.get_or_create_from_api(self.user,
                                                        timestamp=timestamp
        )

        # Calculate the current price
        current_price = (Decimal(self.value)/Decimal("100000000.0"))*obj_now.get_currency_price(fiat_currency)

        # Calculate performance
        performance = 0
        if current_price:
            performance = ((current_price - old_output_value) / old_output_value) * 100

        return {
            "value": self.value,
            "type_ref_hash": self.type_ref_hash,
            "spent": self.spent,
            "confirmed_at_block_height": self.confirmed_at_block_height,
            "confirmed_at_block_time": self.confirmed_at_block_time,
            "network": self.network,
            "fiat_value_old": old_output_value,
            "fiat_value": current_price,
            "fiat_cur": fiat_currency,
            "performance": performance,
            "current_price": current_price,
            "is_tracked": is_tracked,
        }

    def output_metrics_dict_OLD(self, tracked_fiat_value=0, fiat_currency="USD"):
        """
        Parses 'tracked_fiat_value' and 'fiat_currency' information from the given label.
        """
        if self.confirmed_at_block_time:
            obj, created = HistoricalPrice.get_or_create_from_api(self.user,
                                        timestamp=self.confirmed_at_block_time)

        performance = 0
        current_output_value = self.value  # TODO: * fiat at time X
        if fiat_value and fiat_cur:
            # Compute or estimate perfomance
            # sats * price = value
            if fiat_value < current_output_value:
                performance = -1
            elif fiat_value > current_output_value:
                performance = 1
            else:
                performance = 0

        return {
            "value": self.value,
            "type_ref_hash": self.type_ref_hash,
            "spent": self.spent,
            "confirmed_at_block_height": self.confirmed_at_block_height,
            "confirmed_at_block_time": self.confirmed_at_block_time,
            "network": self.network,
            "fiat_value": fiat_value,
            "fiat_cur": fiat_cur,
            "performance": performance,
        }

    @classmethod
    def get_or_create_from_api(cls,
                               user,
                               type_ref_hash=None,
                               network='mainnet',
                               txid=None,
                               vout=None,
                               force_reload=False):

        obj = None
        created = False
        if type_ref_hash is None:
            type_ref_hash = compute_type_ref_hash(
                                        "tx", "{}:{}".format(txid, vout))
        if force_reload:
            cached_data = None
        else:
            cached_data = cls.objects.filter(type_ref_hash=type_ref_hash,
                                             network=network).last()

        if cached_data:
            return cached_data, False

        def get_value_and_spent(txid, vout):
            mempool_api = MempoolAPI()
            res0 = mempool_api.get_transaction(txid)
            vouts = res0.get("vout", [])
            if vouts:
                value = vouts[int(vout)].get("value", 0)
                res1 = mempool_api.get_transaction_outspend(txid, str(vout))
                return (value,
                        res1.get('spent', False) in [True, "true"],
                        res0.get('status', {}).get('block_height', 0),
                        res0.get('status', {}).get('block_time', 0))

        if txid and vout:
            res = get_value_and_spent(txid, vout)

            if res:
                value, spent, confirmed_at_block_height, confirmed_at_block_time = res
                obj, created = cls.objects.get_or_create(user=user,
                        type_ref_hash=type_ref_hash, network=network,
                                defaults={
                                'spent': spent,
                                'value': value,
                                'confirmed_at_block_height': confirmed_at_block_height,
                                'confirmed_at_block_time': confirmed_at_block_time,
                            })
        return obj, created


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

    def get_currency_price(self, currency):
        """
        Get the price for the specified currency.

        Args:
            currency (str): The currency code (e.g., 'USD', 'EUR', 'GBP').

        Returns:
            decimal.Decimal: The price for the specified currency.
        """
        if currency not in settings.CURRENCIES:
            raise ValueError(f"Invalid currency code: {currency}")

        currency_lower = currency.lower()
        price_field = getattr(self, f"{currency_lower}_price")
        return price_field.amount

    def __str__(self):
        return f"{self.usd_price} @ {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

    @classmethod
    def get_or_create_from_api(cls, user=None, timestamp=-1):
        if timestamp == -1:
            current_datetime = datetime.datetime.now()
            timestamp = int(current_datetime.timestamp())
        cached_data = cls.objects.filter(timestamp=timestamp).first()
        if cached_data:
            return cached_data, False
        try:
            if user:
                mempool_endpoint = user.profile.mempool_endpoint
            else:
                mempool_endpoint = "https://mempool.space"
            url = f"{mempool_endpoint}/api/v1/historical-price?timestamp={timestamp}"
            response = requests.get(url)
            api_response = response.json()
        except Exception as ex:
            logger.error(ex, exc_info=True)
            try:
                from threadlocals.threadlocals import get_current_request
                request = get_current_request()
                if request:
                    messages.error(request, "<strong>Connection Error:</strong> Could not connect to Mempool to retrieve historical price.")
            except Exception as ex2:
                logger.error(ex2, exc_info=True)
            return None, None
        try:
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
        except:
            return None, None

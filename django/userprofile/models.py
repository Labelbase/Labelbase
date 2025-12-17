from django.db import models
from django.contrib.auth.models import User
from labelbase.models import Labelbase


CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('CAD', 'Canadian Dollar'),
        ('CHF', 'Swiss Franc'),
        ('AUD', 'Australian Dollar'),
        ('JPY', 'Japanese Yen'),
    ]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mempool_endpoint = models.CharField(
        max_length=160,
        default="https://mempool.space",
        blank=True,
    )

    # electrum
    electrum_hostname = models.CharField(max_length=255, default="electrum.emzy.de", blank=True)
    electrum_ports = models.CharField(max_length=6, default="s50002", blank=True)

    # electrum testnet
    electrum_hostname_test = models.CharField(max_length=255, default="testnet.qtornado.com", blank=True)
    electrum_ports_test = models.CharField(max_length=6, default="s51002", blank=True)

    avatar_url = models.CharField(max_length=160,
                                  default="/static/avatar.jpg",
                                  blank=True,
                                  help_text="")
    # switches
    merge_identical = models.BooleanField(default=False)
    auto_cleanup = models.BooleanField(default=False)
    use_hashtags = models.BooleanField(default=True)
    use_treemap = models.BooleanField(default=True)
    use_attachments = models.BooleanField(default=True)
    use_sentry = models.BooleanField(default=True)
    use_chatwoot = models.BooleanField(default=False)
    use_fiatfinances = models.BooleanField(default=True)
    update_utxo_on_login = models.BooleanField(default=True)

    my_currency = models.CharField(max_length=3,
                                   choices=CURRENCY_CHOICES,
                                   default='USD')

    my_fee = models.IntegerField(default=1, help_text="Fee used when broadcasting transactions")
    my_fee_rate_threshold = models.IntegerField(default=1, help_text="Adjust fee health thresholds (percentage points). Default: 0 = no adjustment, +1 = more lenient, -1 = more strict")

    has_seen_welcome_popup = models.BooleanField(default=False)

    @property
    def my_fee_threshold_healthy(self):
        """Calculate healthy threshold with user adjustment"""
        return 1.0 + self.my_fee_rate_threshold

    @property
    def my_fee_threshold_warning(self):
        """Calculate warning threshold with user adjustment"""
        return 3.0 + self.my_fee_rate_threshold

    def labelbases(self):
        return Labelbase.objects.filter(user_id=self.user_id)

    def __str__(self):
        return self.user.username

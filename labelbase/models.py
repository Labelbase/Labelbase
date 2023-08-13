from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django_cryptography.fields import encrypt


class Labelbase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = encrypt(
        models.CharField(
            max_length=160,
            default="",
            blank=True,
        )
    )
    fingerprint = encrypt(models.CharField(max_length=8, default="", blank=True))
    about = encrypt(models.CharField(max_length=200, default="", blank=True))

    def get_absolute_url(self):
        return reverse("labelbase", args=[self.id])


class Label(models.Model):
    """
    Reference:
    https://github.com/bitcoin/bips/blob/master/bip-0329.mediawiki
    """
    TYPE_TX = "tx"
    TYPE_ADDR = "addr"
    TYPE_PUBKEY = "pubkey"
    TYPE_INPUT = "input"
    TYPE_OUTPUT = "output"
    TYPE_XPUT = "xpub"

    TYPE_CHOICES = [
        (TYPE_TX, "tx"),
        (TYPE_ADDR, "addr"),
        (TYPE_PUBKEY, "pubkey"),
        (TYPE_INPUT, "input"),
        (TYPE_OUTPUT, "output"),
        (TYPE_XPUT, "xpub"),
    ]
    type = models.CharField(
        max_length=16,
        choices=TYPE_CHOICES,
        default=TYPE_ADDR,
    )
    ref = encrypt(
        models.CharField(
            max_length=160,
            default="",
            blank=True,
        )
    )
    label = encrypt(
        models.CharField(
            max_length=160,
            default="",
            blank=True,
        )
    )
    origin = encrypt(
        models.CharField(
            help_text=("Optional key origin information referencing the wallet "
                       "associated with the label. The origin property should "
                       "only appear where type is 'tx'."),
            max_length=160,
            default="",
            blank=True,
        )
    )
    spendable = encrypt(
        models.NullBooleanField(
            help_text=("One of true or false, denoting if an output should be "
                       "spendable by the wallet. The spendable property only "
                       "where type is 'output'."),
            default=None,
        )
    )

    labelbase = models.ForeignKey(Labelbase, on_delete=models.CASCADE)

    def get_absolute_url(self):
        """
        Is used by "edit label" functionality.
        This brings us back to the labelbase once the lable was saved.
        """
        return self.labelbase.get_absolute_url()

    def get_mempool_url(self):
        mempool_endpoint = self.labelbase.user.profile.mempool_endpoint
        if self.type == "addr":
            return "{}/address/{}".format(mempool_endpoint, self.ref)
        if self.type == "tx":
            return "{}/tx/{}".format(mempool_endpoint, self.ref)
        return ""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django_cryptography.fields import encrypt
from django.utils.safestring import mark_safe

from pymempool import MempoolAPI

from labellabor.utils import extract_fiat_value
from labelbase.utils import compute_type_ref_hash
from finances.models import OutputStat
from attachments.models import LabelAttachment

class Labelbase(models.Model):
    """
    NOTE: Currently not available, see
    https://github.com/Labelbase/Labelbase/issues/46

    Labelbase Operation Modes
    =========================

    (this should be only choosable when creating a labelbase, not afterwards.)
    ( this affects entries when changing entries - maybe, depending on the change)

    A) Combine Identical Entries: When enabled, if you add a label with the same
       type and reference as an existing entry, the label attribute of the entries
       will be combined. This allows you to aggregate information.
       If the spendable attribute is provided, the last value given will overwrite
       the value of the "combined" entry.

    B) Create Duplicate Entries: Enabling this option will create duplicate entries
       for labels with the same type and reference. This is useful when you want to
       keep separate entries for identical labels (e.g., to track a history).
       Each duplicate entry retains its own attributes, including spendable.
       Please note that when labels are exported, they will be sorted in ascending
       order by their ID, with older entries appearing first and newer entries later.
       When importing labels into a wallet or system, it may retain only the latest
       record and overwrite previous ones during the import process.

    C) Replace Previous Entries: With this option enabled, when you add a label with
       the same type and reference as an existing entry, the previous entry will be
       replaced with the new one. The spendable and all other attributes of the new
       entry will overwrite the value of the previous entry.

    Choose the operation mode that best suits your needs for managing entries with
    the same 'type' and 'ref' within this Labelbase.
    """
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

    COMBINE = 'combine'
    DUPLICATE = 'duplicate'
    REPLACE = 'replace'
    SKIP = 'skip'

    OPERATION_MODE_CHOICES = [
        (COMBINE, 'Combine Identical Entries'),
        (DUPLICATE, 'Create Duplicate Entries (Default)'),
        (REPLACE, 'Replace Previous Entries'),
        (SKIP, 'Skip Identical Entries')
    ]

    operation_mode = models.CharField(
        max_length=10,
        choices=OPERATION_MODE_CHOICES,
        default='duplicate',
        help_text=("Choose the operation mode for handling entries with the same"
                   "'type' and 'ref'. The default mode is to create duplicate entries.")
    )

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
        help_text="Choose the network for this labelbase."
    )

    @property
    def is_mainnet(self):
        return self.network == self.MAINNET

    @property
    def is_testnet(self):
        return self.network == self.TESTNET

    def get_mempool_api(self):
        if self.network != "mainnet":
            mempool_endpoint = \
                "{}/{}".format(self.user.profile.mempool_endpoint, self.network)
        else:
            mempool_endpoint = self.user.profile.mempool_endpoint
        return MempoolAPI(api_base_url="{}{}".format(mempool_endpoint, "/api/"))

    def get_absolute_url(self):
        return reverse("labelbase", args=[self.id])

    def get_hashtags_url(self):
        return reverse('labelbase_hashtags', kwargs={'labelbase_id': self.id})

    def get_xpub_url(self):
        for label in self.label_set.all():
            if label.type == "xpub": # and is_valid_xpub() ...
                # returns the first xpub, works for single signature only at the moment.
                return reverse('edit_label', kwargs={'pk': label.id})
        return None


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
    TYPE_XPUB = "xpub"

    TYPE_CHOICES = [
        (TYPE_TX, "tx"),
        (TYPE_ADDR, "addr"),
        (TYPE_PUBKEY, "pubkey"),
        (TYPE_INPUT, "input"),
        (TYPE_OUTPUT, "output"),
        (TYPE_XPUB, "xpub"),
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
            max_length=1000,
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
        models.BooleanField(
            help_text=("One of true or false, denoting if an output should be "
                       "spendable by the wallet. The spendable property only "
                       "where type is 'output'."),
            default=None,
            null=True
        )
    )

    labelbase = models.ForeignKey(
        Labelbase,
        on_delete=models.CASCADE
    )

    type_ref_hash = models.CharField(
        max_length=64,
        blank=True)

    # All additional fields (from the BIP-329 upgrade) encrypted for maximum privacy
    height = encrypt(
        models.CharField(
            max_length=16,
            null=True,
            blank=True,
            help_text="Block height where transaction was confirmed"
        )
    )
    time = encrypt(
        models.CharField(
            max_length=64,
            null=True,
            blank=True,
            help_text="ISO-8601 timestamp of the block"
        )
    )
    fee = encrypt(
        models.CharField(
            max_length=32,
            null=True,
            blank=True,
            help_text="Transaction fee in satoshis (stored as string)"
        )
    )
    value = encrypt(
        models.CharField(
            max_length=32,
            null=True,
            blank=True,
            help_text="Transaction value in satoshis, signed (stored as string)"
        )
    )
    rate = encrypt(
        models.TextField(
            null=True,
            blank=True,
            help_text="Exchange rate at transaction time (JSON string)"
        )
    )
    keypath = encrypt(
        models.CharField(
            max_length=256,
            null=True,
            blank=True,
            help_text="Key derivation path (e.g., /1/123)"
        )
    )
    fmv = encrypt(
        models.TextField(
            null=True,
            blank=True,
            help_text="Fair market value (JSON string)"
        )
    )
    heights = encrypt(
        models.TextField(
            null=True,
            blank=True,
            help_text="Block heights for address activity (JSON array as string)"
        )
    )

    def get_extracted_fiat_value(self):
        return extract_fiat_value(self.label)

    def get_finance_output_metrics_dict(self):
        type_ref_hash = compute_type_ref_hash(self.type, self.ref)
        output, _ = OutputStat.get_or_create_from_api(
                                user=self.labelbase.user,
                                type_ref_hash=type_ref_hash,
                                network=self.labelbase.network)

        val, cur = extract_fiat_value(self.label)
        return output.output_metrics_dict(tracked_fiat_value=val, fiat_currency=cur)

    def get_label_attachment(self):
        type_ref_hash = compute_type_ref_hash(self.type, self.ref)
        label_attachment, _ = LabelAttachment.objects.get_or_create(
                                    user=self.labelbase.user,
                                    type_ref_hash=type_ref_hash,
                                    network=self.labelbase.network)
        return label_attachment

    def get_absolute_url(self):
        """
        Is used by "edit label" functionality.
        This brings us back to the labelbase once the label was saved.
        """
        return self.labelbase.get_absolute_url()


    def get_mempool_url(self):
        if self.labelbase and self.labelbase.network != "mainnet":
            mempool_endpoint = \
                "{}/{}".format(self.labelbase.user.profile.mempool_endpoint,
                               self.labelbase.network)
        else:
            mempool_endpoint = self.labelbase.user.profile.mempool_endpoint
        try:
            if self.type == "addr":
                return "{}/address/{}".format(mempool_endpoint, self.ref)
            elif self.type == "tx":
                return "{}/tx/{}".format(mempool_endpoint, self.ref)
            elif self.type == "output":
                return "{}/tx/{}".format(mempool_endpoint, self.ref.split(":")[0])
        except:
            pass
        return ""


    def get_fee_health_status(self):
        """
        Calculate fee health status for this label if it's a spendable unspent output.
        """
        # Only calculate for spendable outputs
        if self.type != self.TYPE_OUTPUT or not self.spendable:
            return {
                'status': None,
                'fee_sats': None,
                'value_sats': None,
                'fee_percentage': None,
                'threshold_healthy': None,
                'threshold_warning': None,
                'threshold_high': None
            }

        try:
            value_sats = int(self.value) if self.value else None
        except (ValueError, TypeError):
            value_sats = None

        if not value_sats or value_sats <= 0:
            return {
                'status': None,
                'fee_sats': None,
                'value_sats': value_sats,
                'fee_percentage': None,
                'threshold_healthy': None,
                'threshold_warning': None,
                'threshold_high': None
            }

        # Get user's fee rate from profile
        user_fee_rate = self.labelbase.user.profile.my_fee  # sats per vbyte
        threshold_adjustment = self.labelbase.user.profile.my_fee_rate_threshold  # percentage points

        # Use P2WPKH as default - most common modern type
        # Simple 1-in, 2-out transaction
        from finances.tx_math import calculate_transaction_size, calculate_fee

        inputs = [{'input_script': 'P2WPKH'}]
        output_counts = {'p2wpkh': 2}

        tx_size = calculate_transaction_size(inputs, output_counts)
        fee_sats = calculate_fee(tx_size['txVBytes'], user_fee_rate)

        # Calculate fee as percentage of output value
        fee_percentage = (fee_sats / value_sats) * 100

        # Define thresholds (base + user adjustment)
        threshold_healthy = 1.0 + threshold_adjustment
        threshold_warning = 3.0 + threshold_adjustment

        # Determine status
        if fee_percentage < threshold_healthy:
            status = 'green'
        elif fee_percentage < threshold_warning:
            status = 'yellow'
        else:
            status = 'red'

        return {
            'status': status,
            'fee_sats': fee_sats,
            'value_sats': value_sats,
            'fee_percentage': round(fee_percentage, 3),
            'threshold_healthy': threshold_healthy,
            'threshold_warning': threshold_warning,
            'threshold_high': threshold_warning
        }


    @property
    def get_fee_health_status_display(self):
        """
        Returns text representation of fee health status for DataTables display.
        """
        health = self.get_fee_health_status()

        if not health['status']:
            return ''

        status_map = {
            'green': '🟢',
            'yellow': '🟡',
            'red': '🔴'
        }
        # FIXME: escaping in data tables
        #status_map = {
        #    'green': '<span data-feather="circle-check" class="align-text-bottom"></span>',
        #    'yellow': '<span data-feather="alert-circle" class="align-text-bottom"></span>',
        #    'red': '<span color:red; data-feather="alert-triangle" class="align-text-bottom"></span>'
        #}

        emoji = status_map.get(health['status'], '')

        return f"{emoji} {health['fee_percentage']}%"

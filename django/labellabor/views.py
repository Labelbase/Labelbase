import os
import time
import tempfile
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, resolve_url
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, TemplateView
from django.views import View
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.http import FileResponse
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib import messages
from django_datatables_view.base_datatable_view import BaseDatatableView
from two_factor.views import OTPRequiredMixin
from two_factor.views.utils import class_view_decorator
from rest_framework.authtoken.models import Token
from bip329.bip329_writer import BIP329JSONLWriter, BIP329JSONLEncryptedWriter
from labelbase.models import Label, Labelbase
from labelbase.forms import LabelForm, LabelbaseForm
from labelbase.forms import ExportLabelsForm
from finances.models import OutputStat
from finances.tasks import check_all_outputs
from .utils import hashtag_to_badge, extract_fiat_value





from embit import bip32, script
from embit.networks import NETWORKS

from django.http import JsonResponse
from django_datatables_view.base_datatable_view import BaseDatatableView
from embit import bip32, script
from embit.networks import NETWORKS

DEFAULT_DERIVE_ADDRESS_COUNT = 100

class BitcoinAddressDatatableView(BaseDatatableView):
    label_id = None  # Variable to store label ID and verify if all is okay.


    def get(self, request, *args, **kwargs):
        self.label_id = kwargs.get('label_id')
        return super().get(request, *args, **kwargs)

    def get_initial_queryset(self):
        return self.initialize_addresses()

    def initialize_addresses(self):
        addresses = []
        if self.label_id is not None:
            # Verify if the label belongs to the current user and get xpub
            try:
                label = Label.objects.get(id=self.label_id,
                                          labelbase__user_id=self.request.user.id)
            except Label.DoesNotExist:
                return []
            if label.type == "xpub":
                xpub = label.ref
                #policy_type = self.request.GET.get('policy_type', 'Single Signature')
                derivation = self.request.GET.get('derivation', 'm/84')
                offset = int(self.request.GET.get('offset', 0))
                addresses = []

                supported_policy_types = ['Single Signature']
                supported_derivations = ['m/44', 'm/49', 'm/84']

                #if policy_type not in supported_policy_types:
                #    return []
                if derivation not in supported_derivations:
                    return []

                if not xpub:
                    return []

                key = bip32.HDKey.from_base58(xpub)

                for i in range(int(self.request.GET.get('address_count', DEFAULT_DERIVE_ADDRESS_COUNT))):
                    idx = i + offset
                    if derivation == 'm/44' and xpub.startswith("xpub"):
                        # BIP 44 - Legacy Addresses (P2PKH)
                        pub = key.derive(f"m/0/{idx}").key
                        sc = script.p2pkh(pub)
                        address = sc.address(NETWORKS["main"])
                    elif derivation == 'm/49' and xpub.startswith("ypub"):
                        # BIP 49 - SegWit Addresses (P2SH-P2WPKH)
                        pub = key.derive(f"m/0/{idx}").key
                        witness_script = script.p2wpkh(pub)
                        sc = script.p2sh(witness_script)
                        address = sc.address(NETWORKS["main"])
                    elif derivation == 'm/84' and xpub.startswith("zpub"):
                        # BIP 84 - Native SegWit Addresses (P2WPKH)
                        pub = key.derive(f"m/0/{idx}").key
                        sc = script.p2wpkh(pub)
                        address = sc.address(NETWORKS["main"])
                    elif derivation == 'm/44' and xpub.startswith("tpub"):
                        # BIP 44 - Legacy Addresses (P2PKH)
                        pub = key.derive(f"m/0/{idx}").key
                        sc = script.p2pkh(pub)
                        address = sc.address(NETWORKS["test"])
                    elif derivation == 'm/49' and xpub.startswith("upub"):
                        # BIP 49 - SegWit Addresses (P2SH-P2WPKH)
                        pub = key.derive(f"m/0/{idx}").key
                        witness_script = script.p2wpkh(pub)
                        sc = script.p2sh(witness_script)
                        address = sc.address(NETWORKS["test"])
                    elif derivation == 'm/84' and xpub.startswith("vpub"):
                        # BIP 84 - Native SegWit Addresses (P2WPKH)
                        pub = key.derive(f"m/0/{idx}").key
                        sc = script.p2wpkh(pub)
                        address = sc.address(NETWORKS["test"])
                    else:
                        continue

                    addresses.append({
                        'index': idx,
                        'path': f"{derivation}'/0'/0'/0/{idx}",
                        'address': address
                    })


        return addresses


    def filter_queryset(self, qs):
        query = self.request.GET.get('search[value]', '').lower()
        q_qs = []
        if query:
            for item in qs:
                if query in item['address'].lower():
                    q_qs.append(item)
            return q_qs
        return qs


    def ordering(self, qs):
        # not supported right now
        return qs

    def paging(self, qs):
        start = int(self.request.GET.get('start', 0))
        length = int(self.request.GET.get('length', 10))
        return qs[start:start + length]

    def prepare_results(self, qs):
        return qs

    def count_total_records(self, qs=None):
        return int(self.request.GET.get('address_count', DEFAULT_DERIVE_ADDRESS_COUNT))

    def count_records(self, qs):
        return len(qs)

    def count_filtered_records(self, qs=None):
        return len(qs)

    def render_to_response(self, context, **response_kwargs):
        qs = self.get_initial_queryset()
        filtered_qs = self.filter_queryset(qs)
        ordered_qs = self.ordering(filtered_qs)
        page_qs = self.paging(ordered_qs)
        return JsonResponse({
            "draw": int(self.request.GET.get('draw', 1)),
            "recordsTotal": self.count_total_records(qs),
            "recordsFiltered": self.count_filtered_records(filtered_qs),
            "data": page_qs
        })


class AboutView(TemplateView):
    template_name = "about.html"


class EncryptionView(TemplateView):
    template_name = "encryption.html"


class InteroperationalView(TemplateView):
    template_name = "interoperational.html"


class CloudView(TemplateView):
    template_name = "cloud.html"


class HomeView(TemplateView):
    template_name = "home.html"


class PrivacyView(TemplateView):
    template_name = "privacy.html"


class TermsView(TemplateView):
    template_name = "terms.html"


class DonationView(TemplateView):
    template_name = "donate.html"


class LabelDeleteView(DeleteView):
    model = Label
    success_url = "/"
    error_url = "/#failed"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.labelbase.user != self.request.user:
            return redirect(self.error_url)
        return super().post(request, *args, **kwargs)


class LabelbaseDeleteView(DeleteView):
    model = Labelbase
    success_url = "/"
    error_url = "/#failed"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user != self.request.user:
            return redirect(self.error_url)
        return super().post(request, *args, **kwargs)


class LabelbaseDatatableView(BaseDatatableView):
    model = Label

    columns = ["id", "type", "ref", "label", "origin", "spendable"]

    order_columns = ["id", "type", "ref", "label", "origin", "spendable"]

    max_display_length = 100

    def get_initial_queryset(self):
        labelbase_id = self.kwargs["labelbase_id"]

        search_tag = self.request.GET.get('tag', None)

        qs = Label.objects.filter(labelbase__user_id=self.request.user.id,
                                  labelbase_id=labelbase_id).order_by("id")

        if search_tag:
            # Due to encryption, we need to use a super slow process here...
            res_ids = []
            search = f'#{search_tag}'
            print(search)
            for record in qs:
                if record.label and search in record.label:
                    res_ids.append(record.id)
                    continue
            qs = qs.filter(id__in=res_ids)
        return qs

    def render_column(self, row, column):
        if column == 'id':
            return f'<tt><a href="{reverse("edit_label", args=[row.id])}">{row.id}</a></tt>'
        elif column == 'type':
            return "<tt>{}</tt>".format(row.get_type_display())
        elif column == 'ref':
            ctx = {
                'row': row,
                'mempool_url': row.get_mempool_url(),
            }
            return render_to_string('labelbase_dt_ref.html', context=ctx, request=self.request)
        elif column == 'label':
            if row.label is None:
                return ""
            if row.labelbase.user.profile.use_hashtags:
                return hashtag_to_badge(f'<tt>{row.label}</tt>')
            else:
                return f'<tt>{row.label}</tt>'
        elif column == 'origin':
            if row.origin is None:
                return ""
            return f'<tt>{row.origin}</tt>'
        elif column == 'spendable':
            spendable_value = row.spendable
            if spendable_value is None:
                spendable_formatted = ''
            else:
                spendable_formatted = 'true' if spendable_value else 'false'
            # if spendable_formatted == 'true':
            #    return f'<span class="badge badge-spendable fs--2 "><svg xmlns="http://www.w3.org/2000/svg" width="16px" height="16px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-check ms-1" style="height:12.8px;width:12.8px;"><polyline points="20 6 9 17 4 12"></polyline></svg> <span class="badge-label"><tt>{spendable_formatted }</tt></span></span>' # noqa
            # elif spendable_formatted == 'false':
            #    return f'<span class="badge badge-unspendable fs--2 "><svg xmlns="http://www.w3.org/2000/svg" width="12.4" height="12.4" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 6L6 18M6 6l12 12"/></svg><span class="badge-label"><tt>{spendable_formatted }</tt></span></span>' # noqa
            return f'<tt>{spendable_formatted}</tt>'
        else:
            return super(LabelbaseDatatableView, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            # Due to encryption, we need to use a super slow process here...
            res_ids = []
            search = search.lower()
            for record in qs:
                if record.type and search in record.type.lower():
                    res_ids.append(record.id)
                    continue
                if record.ref and search in record.ref.lower():
                    res_ids.append(record.id)
                    continue
                if record.label and search in record.label.lower():
                    res_ids.append(record.id)
                    continue
                if record.origin and search in record.origin.lower():
                    res_ids.append(record.id)
                    continue
            return qs.filter(id__in=res_ids)
        return qs



class LabelbaseHealthDatatableView(BaseDatatableView):
    columns = ["id", "ref", "label", "value"]

    order_columns = ["id", "ref", "label"]

    def get_initial_queryset(self):
        labelbase_id = self.kwargs["labelbase_id"]

        search_tag = self.request.GET.get('tag', None)

        qs = Label.objects.filter(type=Label.TYPE_OUTPUT,
                                  labelbase__user_id=self.request.user.id,
                                  labelbase_id=labelbase_id).order_by("id")

        if search_tag:
            # Due to encryption, we need to use a super slow process here...
            res_ids = []
            search = f'#{search_tag}'

            for record in qs:
                if record.label and search in record.label:
                    res_ids.append(record.id)
                    continue
            qs = qs.filter(id__in=res_ids)
        return qs

    def render_column(self, row, column):
        if column == 'id':
            return f'<tt><a href="{reverse("edit_label", args=[row.id])}">{row.id}</a></tt>'
        elif column == 'type':
            return "<tt>{}</tt>".format(row.get_type_display())
        elif column == 'ref':
            ctx = {
                'row': row,
                'mempool_url': row.get_mempool_url(),
            }
            return render_to_string('labelbase_dt_ref.html', context=ctx, request=self.request)
        elif column == 'label':
            if row.label is None:
                return ""
            if row.labelbase.user.profile.use_hashtags:
                return hashtag_to_badge(f'<tt>{row.label}</tt>')
            else:
                return f'<tt>{row.label}</tt>'
        elif column == 'value':
            try:
                return row.get_finance_output_metrics_dict().get('value')
            except Exception as ex:
                return "{}".format(ex)
        else:
            return super(LabelbaseHealthDatatableView, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            # Due to encryption, we need to use a super slow process here...
            res_ids = []
            search = search.lower()
            for record in qs:
                if record.type and search in record.type.lower():
                    res_ids.append(record.id)
                    continue
                if record.ref and search in record.ref.lower():
                    res_ids.append(record.id)
                    continue
                if record.label and search in record.label.lower():
                    res_ids.append(record.id)
                    continue
                if search in "{}".format(record.get_finance_output_metrics_dict().get('value')):
                    res_ids.append(record.id)
                    continue
            return qs.filter(id__in=res_ids)
        return qs


class LabelbaseViewActionView(View):
    def get(self, request, *args, **kwargs):
        labelbase = get_object_or_404(
            Labelbase, id=self.kwargs["labelbase_id"], user_id=self.request.user.id
        )
        if self.kwargs["action"] == "update-spent-outputs":
            check_all_outputs(self.request.user.id, labelbase_id=labelbase.id)
        return HttpResponseRedirect(labelbase.get_absolute_url())


class LabelbaseView(ListView):
    template_name = "labelbase.html"
    context_object_name = "label_list"

    def get_queryset(self):
        qs = Label.objects.filter(
            labelbase__user_id=self.request.user.id,
            labelbase_id=self.kwargs["labelbase_id"],
        )
        return qs.order_by("id")

    def get_context_data(self, **kwargs):
        labelbase_id = self.kwargs["labelbase_id"]
        context = super(LabelbaseView, self).get_context_data(**kwargs)
        context["labelbase"] = get_object_or_404(
            Labelbase, id=labelbase_id, user_id=self.request.user.id
        )
        context["active_labelbase_id"] = labelbase_id
        context["labelform"] = LabelForm(
            request=self.request, labelbase_id=labelbase_id
        )
        context["api_token"] = Token.objects.get(user_id=self.request.user.id)
        return context

    def post(self, request, *args, **kwargs):
        labelbase_id = self.kwargs["labelbase_id"]
        labelform = LabelForm(request.POST, request=request, labelbase_id=labelbase_id)
        if labelform.is_valid():
            label = labelform.save()
            return HttpResponseRedirect(label.labelbase.get_absolute_url())



class UTXOsHealthView(ListView):
    template_name = "utxos_health.html"
    context_object_name = "label_list"

    def get_queryset(self):
        qs = Label.objects.filter(
            type=Label.TYPE_OUTPUT,
            labelbase__user_id=self.request.user.id,
            labelbase_id=self.kwargs["labelbase_id"],
        )
        return qs.order_by("id")

    def get_context_data(self, **kwargs):
        labelbase_id = self.kwargs["labelbase_id"]
        context = super(UTXOsHealthView, self).get_context_data(**kwargs)
        context["labelbase"] = get_object_or_404(
            Labelbase, id=labelbase_id, user_id=self.request.user.id
        )
        context["active_labelbase_id"] = labelbase_id
        context["labelform"] = LabelForm(
            request=self.request, labelbase_id=labelbase_id
        )
        context["api_token"] = Token.objects.get(user_id=self.request.user.id)
        return context

class LabelbaseMergeView(LabelbaseView):
    template_name = "labelbase_merge.html"

    def get_queryset(self):
        labels = []
        qs = Label.objects.filter(
            labelbase__user_id=self.request.user.id,
            labelbase_id=self.kwargs["labelbase_id"],
        )
        lbl_type = self.request.GET.get("type", None)
        lbl_ref = self.request.GET.get("ref", None)
        lbl_label = self.request.GET.get("label", None)

        for l in qs:
            if lbl_type and lbl_ref and lbl_label:
                if l.type == lbl_type and l.ref == lbl_ref and l.label == lbl_label:
                    labels.append(l)
            elif lbl_type and lbl_ref:
                if l.type == lbl_type and l.ref == lbl_ref:
                    labels.append(l)
            elif lbl_type and lbl_label:
                if l.type == lbl_type and l.label == lbl_label:
                    labels.append(l)
            elif lbl_ref and lbl_label:
                if l.ref == lbl_ref and l.label == lbl_label:
                    labels.append(l)
            elif lbl_type:
                if l.type == lbl_type:
                    labels.append(l)
            elif lbl_ref:
                if l.ref == lbl_ref:
                    labels.append(l)
            elif lbl_label or lbl_label == '':
                if l.label == lbl_label:
                    labels.append(l)
        label_ids = []
        for l in labels:
            label_ids.append(l.id)
        if label_ids:
            qs = Label.objects.filter(id__in=label_ids,
                                      labelbase__user_id=self.request.user.id,
                                      labelbase_id=self.kwargs["labelbase_id"])
        else:
            qs = Label.objects.none()
        return qs.order_by("id")


class StatsAndKPIView(View):
    template_name = "labelbase_stats_and_kpi.html"

    def get(self, request, *args, **kwargs):
        labelbase_id = self.kwargs["labelbase_id"]
        labelbase = get_object_or_404(
            Labelbase, id=labelbase_id, user_id=self.request.user.id
        )
        return render(request, self.template_name, {
            "labelbase": labelbase,
            "active_labelbase_id": labelbase_id})


class TreeMapsView(ListView):
    context_object_name = "label_list"

    def get_template_names(self):
        # TODO: "action" has no at the moment, it's all redundend code.
        # The template processes each output and adds or drops it.

        #if 'action' in self.kwargs:
        #    action = self.kwargs['action']
        #    if action == 'unspent-outputs':
        #        return "labelbase_tree_maps_unspent_outputs.html"
        #    elif action == 'unspent-spendable-outputs':
        #        return "labelbase_tree_maps_unspent_outputs.html"
        return "labelbase_tree_maps_unspent_outputs.html"

    def get_context_data(self, **kwargs):


        # Store nearest price information.
        # TODO: This should (or could) be done on new blocks too.
        from finances.models import HistoricalPrice
        HistoricalPrice.get_or_create_from_api(self.request.user, -1)

        context = super().get_context_data(**kwargs)

        labelbase_id = self.kwargs["pk"]
        labelbase = get_object_or_404(
            Labelbase, id=labelbase_id, user_id=self.request.user.id
        )
        context['labelbase'] = labelbase
        context['active_labelbase_id'] = labelbase.id
        context['action'] = self.kwargs.get('action', 'unspent-outputs')
        return context

    def get_queryset(self):
        #action = self.kwargs.get('action', 'unspent-outputs')
        label_ids = []

        qs = Label.objects.filter(
            labelbase__user_id=self.request.user.id,
            labelbase_id=self.kwargs["pk"],
        )

        for l in qs:
            if l.type == "output":
                output = OutputStat.objects.filter(
                                            user=l.labelbase.user,
                                            type_ref_hash=l.type_ref_hash,
                                            network=l.labelbase.network).last()
                if output and output.spent is False:
                    # FIXME: redundend code.
                    # The template processes each output and adds or drops it,
                    # depending of its state.

                    #if action == 'unspent-spendable-outputs' and l.spendable is True:
                    #    label_ids.append(l.id)
                    #else:
                    label_ids.append(l.id)
        if label_ids:
            qs = qs.filter(id__in=label_ids,
                           labelbase__user_id=self.request.user.id,
                           labelbase_id=self.kwargs["pk"])
        else:
            qs = Label.objects.none()
        return qs.order_by("id")


class LabelbasePortfolioView(LabelbaseView):
    template_name = "labelbase_portfolio.html"

    def get_queryset(self):
        self.balances = {}
        label_ids = []
        qs = Label.objects.filter(
            labelbase__user_id=self.request.user.id,
            labelbase_id=self.kwargs["labelbase_id"],
        )
        for l in qs:
            if l.type == "output":
                val, cur = extract_fiat_value(l.label)
                if val > 0:
                    if self.balances.get(cur, None) is None:
                        self.balances[cur] = 0
                    self.balances[cur] += val
                label_ids.append(l.id)
        if label_ids:
            qs = Label.objects.filter(id__in=label_ids,
                                      labelbase__user_id=self.request.user.id,
                                      labelbase_id=self.kwargs["labelbase_id"])
        else:
            qs = Label.objects.none()
        return qs.order_by("id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['balances'] = self.balances
        return context


class FixAndMergeLabelsView(View):
    template_name = "label_fix_and_merge.html"

    def get(self, request, *args, **kwargs):
        labelbase_id = self.kwargs["labelbase_id"]
        labelbase = get_object_or_404(
            Labelbase, id=labelbase_id, user_id=self.request.user.id
        )

        # Fetch all records for the specified Labelbase
        records = Label.objects.filter(labelbase_id=labelbase_id)

        # Create a dictionary to store records grouped by type, ref, and label
        record_groups_type_and_ref = {}
        record_groups_type_and_ref_and_label = {}
        record_groups_all_identical = {}

        resulting_duplicates_type_and_ref = []
        resulting_duplicates_type_and_ref_and_label = []
        resulting_duplicates_all_identical = []
        resulting_empty_label_records = []
        resulting_too_long_label_records = []

        all_identical_records = []

        # Iterate through the records and group them
        for record in records:
            key_type_and_ref = (record.type, record.ref)
            key_type_and_ref_label = (record.type, record.ref, record.label)
            key_all_identical = (record.type, record.ref, record.label, record.origin, record.spendable)

            if record.label in [None, ""]:
                resulting_empty_label_records.append(record)
            elif len(record.label) > 255:
                resulting_too_long_label_records.append(record)

            if key_type_and_ref in record_groups_type_and_ref:
                record_groups_type_and_ref[key_type_and_ref].append(record)
            else:
                record_groups_type_and_ref[key_type_and_ref] = [record]

            if key_type_and_ref_label in record_groups_type_and_ref_and_label:
                record_groups_type_and_ref_and_label[key_type_and_ref_label].append(record)
            else:
                record_groups_type_and_ref_and_label[key_type_and_ref_label] = [record]

            if key_all_identical in record_groups_all_identical:
                record_groups_all_identical[key_all_identical].append(record)
            else:
                record_groups_all_identical[key_all_identical] = [record]

        # Iterate through the grouped records and identify duplicates
        for key_type_and_ref, duplicates in record_groups_type_and_ref.items():
            if len(duplicates) > 1:
                type_val, ref_val = key_type_and_ref
                resulting_duplicates_type_and_ref.append({'type': type_val, 'ref': ref_val})

        for key_type_and_ref_and_label, duplicates in record_groups_type_and_ref_and_label.items():
            if len(duplicates) > 1:
                type_val, ref_val, label_val = key_type_and_ref_and_label
                resulting_duplicates_type_and_ref_and_label.append(
                    {'type': type_val, 'ref': ref_val, 'label': label_val})

        for key_all_identical, duplicates in record_groups_all_identical.items():
            if len(duplicates) > 1:
                type_val, ref_val, label_val, origin_val, spendable_cal = key_all_identical
                for record in duplicates:
                    if record not in all_identical_records:
                        all_identical_records.append(record)
                res_rec = {
                    'type': type_val,
                    'ref': ref_val,
                    'label': label_val,
                    'origin': origin_val,
                    'spendable': spendable_cal
                }
                resulting_duplicates_all_identical.append(res_rec) # nonsense, but counts
        fix_suggestions = sum(map(len, [#resulting_duplicates_type_and_ref,
                                        #resulting_duplicates_type_and_ref_and_label,
                                        #resulting_duplicates_all_identical,
                                        resulting_empty_label_records,
                                        #resulting_too_long_label_records
                                        ]))
        return render(request, self.template_name, {
            "labelbase": labelbase,
            "fix_suggestions": fix_suggestions,
            "resulting_duplicates_all_identical_final_record_count": len(resulting_duplicates_all_identical),

            "resulting_duplicates_all_identical_current_record_count": len(all_identical_records),
            "all_identical_records": all_identical_records, # the unique identical records where all fields are the same

            "resulting_duplicates_type_and_ref": resulting_duplicates_type_and_ref,
            "resulting_duplicates_type_and_ref_and_label": resulting_duplicates_type_and_ref_and_label,
            "resulting_empty_label_records": resulting_empty_label_records,
            "resulting_too_long_label_records": resulting_too_long_label_records,

            "active_labelbase_id": labelbase_id,
            })


class ExportLabelsView(View):
    def post(self, request, *args, **kwargs):
        labelbase_id = self.kwargs["labelbase_id"]
        labelbase = get_object_or_404(
            Labelbase, id=labelbase_id, user_id=self.request.user.id
        )
        form = ExportLabelsForm(request.POST)
        if form.is_valid():
            # Retrieve data from the form
            tx_checkbox = form.cleaned_data['tx_checkbox']
            addr_checkbox = form.cleaned_data['addr_checkbox']
            pubkey_checkbox = form.cleaned_data['pubkey_checkbox']
            input_checkbox = form.cleaned_data['input_checkbox']
            output_checkbox = form.cleaned_data['output_checkbox']
            xpub_checkbox = form.cleaned_data['xpub_checkbox']

            encrypt_checkbox = form.cleaned_data['encrypt_checkbox']

            # Use request.POST, not form.cleaned_data['passphrase']
            passphrase = request.POST.get('passphrase', '')

            # Export labels based on selected checkboxes
            selected_type_attributes = []
            if tx_checkbox:
                selected_type_attributes.append('tx')
            if addr_checkbox:
                selected_type_attributes.append('addr')
            if pubkey_checkbox:
                selected_type_attributes.append('pubkey')
            if input_checkbox:
                selected_type_attributes.append('input')
            if output_checkbox:
                selected_type_attributes.append('output')
            if xpub_checkbox:
                selected_type_attributes.append('xpub')

            timestamp = time.strftime('%Y%m%d%H%M%S')

            # Define the prefix and file extension for the temporary file
            prefix = f'labelbase-{labelbase.id}-{timestamp}-'
            suffix = '.jsonl'

            # Create a temporary file with the specified prefix and file extension
            with tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix=suffix) as temp_file:
                # Create a BIP329JSONLWriter instance
                if encrypt_checkbox and passphrase:
                    label_writer = BIP329JSONLEncryptedWriter(temp_file.name, passphrase, remove_existing=True)
                else:
                    label_writer = BIP329JSONLWriter(temp_file.name, remove_existing=True)
                labels = Label.objects.filter(labelbase_id=labelbase_id,
                                              labelbase__user_id=request.user.id,
                                              type__in=selected_type_attributes
                                             ).order_by("id")
                for label in labels:
                    label_entry = {
                        "type": label.type,
                        "ref": label.ref,
                        "label": label.label,
                    }

                    if label.origin and label.type == "tx":
                        label_entry["origin"] = label.origin
                    if label.spendable in [True, False] and label.type == "output":
                        label_entry["spendable"] = label.spendable

                    # Write the label entry to the file
                    label_writer.write_label(label_entry)

                final_filename = f"labelbase-{labelbase.id}-{timestamp}.jsonl"
                if encrypt_checkbox and passphrase:
                    if label_writer.is_closed is False:
                        # Close the encrypted writer when finished
                        label_writer.close()
                    final_filename = final_filename.replace(".jsonl", ".7z")

            response = FileResponse(open(temp_file.name, 'rb'))
            response['Content-Type'] = 'application/json'

            response['Content-Disposition'] = f'attachment; filename="{final_filename}"'
            os.remove(temp_file.name)
            return response

        messages.add_message(
            request,
            messages.ERROR,
            "Could not export labels. Please try again."
        )
        return HttpResponseRedirect(labelbase.get_absolute_url())


class LabelUpdateView(UpdateView):
    model = Label
    fields = ["type", "ref", "label", "origin", "spendable"]

    def get_object(self):
        user_id = self.request.user.id
        pk = self.kwargs["pk"]
        return get_object_or_404(Label, labelbase__user_id=self.request.user.id, pk=pk)

    def get_template_names(self):
        if 'action' in self.kwargs:
            action = self.kwargs['action']
            if action == 'labeling':
                return "label_edit_labeling.html"
            elif action == 'attachments' and settings.SELF_HOSTED and \
                self.object.labelbase.user.profile.use_attachments:
                return "label_edit_attachments.html"
            elif action == "derive-addresses":
                return "label_derive_addresses.html"
            elif action == 'output-details':
                return "label_edit_output_details.html"
        return "label_edit_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_labelbase_id"] = self.object.labelbase.id
        context["labelbase"] = self.object.labelbase
        context["action"] = self.kwargs.get('action', 'update')
        if context["action"] in ["labeling", "derive-addresses"]:
            context["labelform"] = LabelForm(
                request=self.request, labelbase_id=self.object.labelbase.id
            )
            if self.object.type == "tx":
                # used by "labeling"
                mempool_api = self.object.labelbase.get_mempool_api()
                context["res_tx"] = mempool_api.get_transaction(self.object.ref)


        if self.object.type == "xpub":
            context["address_count"] = self.request.GET.get("address_count", DEFAULT_DERIVE_ADDRESS_COUNT)
            context["offset"] = int(self.request.GET.get("offset", 0))

        if self.object.type == "output":
            context["output"] = OutputStat.objects.filter(
                                    user=self.object.labelbase.user,
                                    type_ref_hash=self.object.type_ref_hash).last()

        return context


class LabelbaseUpdateView(UpdateView):
    def post(self, request, *args, **kwargs):
        labelbase_id = self.kwargs["labelbase_id"]
        labelbase = get_object_or_404(
            Labelbase, id=labelbase_id, user_id=self.request.user.id
        )
        labelbase.name = request.POST.get("name", "")
        labelbase.fingerprint = request.POST.get("fingerprint", "")
        labelbase.about = request.POST.get("about", "")
        labelbase.operation_mode = request.POST.get("operation_mode", "")
        labelbase.network = request.POST.get("network", "")

        labelbase.save()
        return HttpResponseRedirect(labelbase.get_absolute_url())


class LabelbaseFormView(FormView):
    template_name = "labelbase_new.html"
    form_class = LabelbaseForm

    def get(self, request, *args, **kwargs):
        return redirect(resolve_url("home"))

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return redirect(form.instance.get_absolute_url())


class RegistrationView(FormView):
    template_name = "registration.html"
    form_class = UserCreationForm

    def form_valid(self, form):
        form.save()
        return redirect("registration_complete")


class RegistrationCompleteView(TemplateView):
    template_name = "registration_complete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_url"] = resolve_url(settings.LOGIN_URL)
        return context


@class_view_decorator(never_cache)
class ExampleSecretView(OTPRequiredMixin, TemplateView):
    template_name = "secret.html"


class OutputStatUpdateRedirectView(View):
    def get(self, request, output_stats_id, label_id):
        if not output_stats_id:
            messages.add_message(
                request,
                messages.ERROR,
                "<strong>Hmmmm....</srong> Not ready yet. Please retry in a few seconds."
            )
            return redirect('edit_label', pk=label_id)
        try:
            output_stat = OutputStat.objects.get(id=output_stats_id)
        except OutputStat.DoesNotExist:
            messages.add_message(
                request,
                messages.ERROR,
                "<strong>Hmmmm....</srong> Could not modify label data."
            )
            return redirect('edit_label', pk=label_id)
        try:
            label = Label.objects.get(id=label_id, labelbase__user_id=self.request.user.id)
        except Label.DoesNotExist:
            messages.add_message(
                request,
                messages.ERROR,
                "Can't find what you are looking for.."
            )
            return redirect("home")

        spent = request.GET.get('force-spent', None)

        if spent not in ["true", "false", "none"]:
            messages.add_message(
                request,
                messages.ERROR,
                "<strong>Hmmmm....</srong> This action is unknown."
            )
            return redirect('edit_label', pk=label_id)
        if spent == "true":
            spent = True
        elif spent == "false":
            spent = False
        elif spent == "none":
            spent = None
        OutputStat.objects.filter(id=output_stat.id).update(spent=spent, last_error={})
        messages.add_message(
            request,
            messages.SUCCESS,
            "<strong>Okay!</strong> Verifying output status now."
        )
        label.save() # will trigger a check agains Electrum
        return redirect('edit_label', pk=label_id)

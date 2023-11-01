from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
import json
from labelbase.models import Labelbase
from labelbase.serializers import LabelSerializer
from django.shortcuts import get_object_or_404
from django.contrib import messages
import decimal


from .forms import UploadFileForm
from tempfile import NamedTemporaryFile

EOLSTOP = [b"", "", None, "\n"]


def handle_uploaded_file(f):
    fp = NamedTemporaryFile(delete=False)
    for chunk in f.chunks():
        fp.write(chunk)
    return fp


@login_required
def upload_labels(request):
    """
    Used to import labels manually using files.
    """

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            imported_lables = 0
            labelbase = get_object_or_404(
                Labelbase,
                id=form.cleaned_data.get("labelbase_id", ""),
                user_id=request.user.id,
            )
            fp = handle_uploaded_file(request.FILES["file"])
            fp.seek(0)
            # BIP-0329
            if form.cleaned_data.get("import_type", "") == "BIP-0329":
                while True:
                    buf = fp.readline()
                    if buf in EOLSTOP:
                        break
                    data = json.loads(buf)
                    data["labelbase"] = labelbase.id
                    serializer = LabelSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        imported_lables += 1
            elif form.cleaned_data.get("import_type", "") == "BIP-0329-7z-enc":
                # TODO: Implement
                pass
            # Bitbox App
            elif form.cleaned_data.get("import_type", "") == "csv-bitbox":
                while True:
                    buf = fp.readline()
                    if buf in EOLSTOP:
                        break
                    try:
                        buf = str(buf.decode("utf-8"))
                        sbuf = buf.split(",")
                        # Time,Type,Amount,Unit,Fee,Address,Transaction ID,Note
                        for elem in [("tx", 6), ("addr", 5)]:
                            data = {
                                "type": elem[0],
                                "ref": sbuf[elem[1]],
                                "label": " ".join(sbuf[7:]),
                            }
                            data["labelbase"] = labelbase.id
                            serializer = LabelSerializer(data=data)
                            if serializer.is_valid():
                                serializer.save()
                                imported_lables += 1
                            else:
                                messages.add_message(
                                    request,
                                    messages.ERROR,
                                    'Could not process line "{}".'.format(buf),
                                )
                    except Exception as ex:
                        messages.add_message(
                            request,
                            messages.ERROR,
                            'Could not process line "{}", {}.'.format(buf, ex),
                        )
            # Pocket Accointing
            elif form.cleaned_data.get("import_type", "") == "pocket-accointing":
                fp.close()
                csv_file_path = fp.name
                mempool_api = labelbase.get_mempool_api()
                from .pocket import validate_csv_format, parse_csv_to_json
                if validate_csv_format(csv_file_path):
                    for item in parse_csv_to_json(csv_file_path):
                        #label = "Got {} {} for {} {} in tx=\"{}\" ref=\"{} #Pocket\" ".format(item[0].get('outSellAmount'), item[1].get('inBuyAsset') , item[2].get('inBuyAmount'), item[2].get('inBuyAsset') , item[0].get('operationId'), item[1].get('operationId'))

                        label = "Got {} {} for {:.2f} {} with reference: {} #Pocket".format(item[0].get('outSellAmount'), item[1].get('inBuyAsset'), decimal.Decimal(item[2].get('inBuyAmount')), item[2].get('inBuyAsset'), item[1].get('operationId'))
                        txid = item[0].get('operationId')
                        tx = mempool_api.get_transaction(txid)
                        potential_utxos = []
                        vouts = tx.get("vout", [])
                        for i in range(len(vouts)):
                            if vouts[i].get('value', 0) == decimal.Decimal(item[0].get('outSellAmount'))*100000000:
                                potential_utxos.append("{}:{}".format(txid, i ))
                        data = {}
                        if len(potential_utxos) == 1:
                            # label UTXO/output of tx
                            data = {
                                "type": "output",
                                "ref": potential_utxos[0],
                                "label": label,
                            }
                        if len(potential_utxos) > 1:
                            # mark tx, add warning tag
                            data = {
                                "type": "tx",
                                "ref": txid,
                                "label": "{} {}".format(label, "#W001_UTXO_NOT_FOUND"),
                            }
                        if data:
                            data["labelbase"] = labelbase.id
                            serializer = LabelSerializer(data=data)
                            if serializer.is_valid():
                                serializer.save()
                                imported_lables += 1
                            else:
                                messages.add_message(
                                    request,
                                    messages.ERROR,
                                    'Could not process record "{}".'.format(item),
                                )
                else:
                    print("ERROR") # TODO
            # BlueWallet
            elif form.cleaned_data.get("import_type", "") == "csv-bluewallet":
                while True:
                    buf = fp.readline()
                    if buf in EOLSTOP:
                        break
                    try:
                        buf = str(buf.decode("utf-8"))
                        sbuf = buf.split(",")
                        data = {
                            "type": "tx",
                            "ref": sbuf[1],
                            "label": " ".join(sbuf[3:]),
                        }
                        data["labelbase"] = labelbase.id
                        serializer = LabelSerializer(data=data)
                        if serializer.is_valid():
                            serializer.save()
                            imported_lables += 1
                        else:
                            messages.add_message(
                                request,
                                messages.ERROR,
                                'Could not process line "{}".'.format(buf),
                            )
                    except Exception as ex:
                        messages.add_message(
                            request,
                            messages.ERROR,
                            'Could not process line "{}", {}.'.format(buf, ex),
                        )
            else:
                fp.close()
                os.unlink(fp.name)
                return HttpResponseRedirect("/failed/url/")
            fp.close()
            os.unlink(fp.name)
            if imported_lables:
                messages.add_message(
                    request,
                    messages.INFO,
                    "Processed and imported {} labels.".format(imported_lables),
                )
            return HttpResponseRedirect(labelbase.get_absolute_url())
    else:
        form = UploadFileForm()
    return render(request, "upload.html", {"form": form})

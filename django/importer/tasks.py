from background_task import background

import json
import decimal
from labelbase.serializers import LabelSerializer

import logging
logger = logging.getLogger('labelbase')

from .models import UploadedData

EOLSTOP = [b"", "", None, "\n"]


@background(schedule=1)
def process_uploaded_data(uploaded_data_id, passphrase=None, loop=None):
    try:
        uploaded_data = UploadedData.objects.get(pk=uploaded_data_id)
        imported_lables = 0
        labelbase = uploaded_data.labelbase
        fp = uploaded_data.file.open()

        # BIP-0329
        if uploaded_data.import_type == "BIP-0329":
            while True:
                buf = fp.readline()
                if buf in EOLSTOP:
                    break
                data = json.loads(buf)

                logger.info(f"Parsed data: {data}")

                data["labelbase"] = labelbase.id
                serializer = LabelSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    imported_lables += 1
        elif uploaded_data.import_type  == "BIP-0329-7z-enc":
            # TODO: Implementation needed.
            pass
        elif uploaded_data.import_type == "samourai":
            buf = fp.read()
            logger.info(buf)
            print(buf)
            from .samourai import import_samourai_labels
            import_samourai_labels(labelbase, buf, passphrase)
        # Bitbox App
        elif uploaded_data.import_type  == "csv-bitbox":
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
        elif uploaded_data.import_type  == "pocket-accointing":
            fp.close()
            csv_file_path = fp.name
            mempool_api = labelbase.get_mempool_api()
            from .pocket import validate_csv_format, parse_csv_to_json
            if validate_csv_format(csv_file_path):
                for item in parse_csv_to_json(csv_file_path):
                    label = "Got {} {} for {:.2f} {} with reference: {} #Pocket".format(item[0].get('outSellAmount'), item[1].get(
                        'inBuyAsset'), decimal.Decimal(item[2].get('inBuyAmount')), item[2].get('inBuyAsset'), item[1].get('operationId'))
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
                            # messages.add_message(
                            #    request,
                            #    messages.ERROR,
                            #    'Could not process record "{}".'.format(item),
                            # )
                            pass
            else:
                print("ERROR")  # TODO
        # BlueWallet
        elif uploaded_data.import_type == "csv-bluewallet":
            header_row = True
            while True:
                buf = fp.readline()
                if buf in EOLSTOP:
                    break
                if header_row:
                    header_row = False
                    continue
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
                        # messages.add_message(
                        #    request,
                        #    messages.ERROR,
                        #    'Could not process line "{}".'.format(buf),
                        # )
                        pass
                except Exception as ex:
                    # messages.add_message(
                    #    request,
                    #    messages.ERROR,
                    #    'Could not process line "{}", {}.'.format(buf, ex),
                    # )
                    pass
        # Clean up – Note: Currently we delete the upload from the file system,
        # later we can store the messages.add_message messages, the state and the
        # amount of importet labels in it to propagate the messages to the
        # frontend/user interface.
        uploaded_data.delete()
    except Exception as ex:
        logger.error(ex, exc_info=True)

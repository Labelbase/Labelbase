from connectrum.client import StratumClient
from connectrum.svr_info import ServerInfo
from connectrum import ElectrumErrorResponse
import json
import asyncio
import threading

from labelbase.models import Label
#from labelbase.utils import compute_type_ref_hash
from finances.models import OutputStat, HistoricalPrice

import logging
logger = logging.getLogger('labelbase')


async def interact(conn, server_info, method, utxo):
    try:
        await conn.connect(server_info, "s", use_tor=server_info.is_onion,
                           disable_cert_verify=True, short_term=True)
        txid, index = utxo.split(":")
        try:
            txn = await conn.RPC(method, txid, True)
            if txn:
                try:
                    blocktime = int(txn.get('blocktime', 0))
                    logger.debug("blocktime: {}".format(blocktime))

                except Exception as ex:
                    blocktime = 0
                    logger.error("Can't get blocktime: {}".format(ex))
                print(txn.get('vout'))
                address = txn.get('vout')[int(index)].get('scriptPubKey', {}).get('address')
                value = txn.get('vout')[int(index)].get('value')*100000000
                return (txid, index, address, value, blocktime)
            else:
                print("Failed to fetch transaction.")
        except ElectrumErrorResponse as ex:
            print(ex)
    finally:
        conn.close()


async def interact_addr(conn, server_info, method, addr):
    try:
        await conn.connect(server_info, "s", use_tor=server_info.is_onion,
                           disable_cert_verify=True, short_term=True)
        try:
            hextx = await conn.RPC(method, addr)
            if hextx is not None:
                print(hextx)
                return hextx
            else:
                print("Failed to fetch transaction.")
        except ElectrumErrorResponse as ex:
            print(ex)
    finally:
        conn.close()


def checkup_label(label_id, loop):
    if label_id and loop:
        """
        [ ] get_or_create() OutputStat using unspent payload
        """
        elem = Label.objects.get(id=label_id)
        output = OutputStat.objects.filter(type_ref_hash=elem.type_ref_hash, network=elem.labelbase.network).last()
        if not output:
            output = OutputStat(type_ref_hash=elem.type_ref_hash, network=elem.labelbase.network, value=0)
        logger.debug("Output found {}".format(output.id))
        if elem.type == "output" and output.spent is not True:
            electrum_hostname = elem.labelbase.user.profile.electrum_hostname
            if not electrum_hostname:
                electrum_hostname = "bitcoin.lu.ke"
            electrum_ports = elem.labelbase.user.profile.electrum_ports
            if not electrum_ports:
                electrum_ports = "s50002"
            logger.debug("Processing Label {} using electrum server connection: {} {} {}".format(
                label_id, electrum_hostname, electrum_hostname, electrum_ports))
            server_info = ServerInfo(electrum_hostname, electrum_hostname, ports=((electrum_ports)))
            conn = StratumClient()
            logger.debug("type_ref_hash: {}".format(elem.type_ref_hash))
            assert elem.type_ref_hash
            utxo = elem.ref
            tx_hash, tx_pos = elem.ref.split(":")
            utxo_resp = loop.run_until_complete(interact(conn, server_info, "blockchain.transaction.get", utxo))
            blocktime = 0
            if utxo_resp:
                txid, index, address, value, blocktime = utxo_resp
                if blocktime:
                    HistoricalPrice.get_or_create_from_api(timestamp=blocktime)
                unspents = loop.run_until_complete(interact_addr(
                    conn, server_info, "blockchain.address.listunspent", address))
                unspent_utxo = False
                utxo_value = 0
                utxo_height = 0
                logger.debug("unspents {}".format(unspents))
                for unspent in unspents:
                    if unspent.get('tx_hash') == tx_hash and \
                        unspent.get('tx_pos') == int(tx_pos) and \
                        unspent.get('height') > 0 and \
                        unspent.get('value') > 0:
                        unspent_utxo = True
                        utxo_value = unspent.get('value')
                        utxo_height = unspent.get('height')
                        logger.debug("found {}".format(unspent))
                        break
                if output:
                    output.network = elem.labelbase.network
                    if utxo_height:
                        output.confirmed_at_block_height = utxo_height
                    if blocktime:
                        output.confirmed_at_block_time = blocktime
                    if utxo_value:
                        output.value = utxo_value
                    elif value: # take value from TX
                        output.value = value
                    if unspent_utxo:
                        output.spent = False
                    else:
                        output.spent = True
                    output.save()
                    logger.debug("saved output {}".format(output.id))
        else:
            logger.debug("Label is not an output. Spent is {}".format(output.spent))
    else:
        if not label_id:
            logger.error("Can't get label_id! {}".format(label_id))
        if not loop:
            logger.error("Can't get loop!")

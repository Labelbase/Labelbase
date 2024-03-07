from connectrum.client import StratumClient
from connectrum.svr_info import ServerInfo
from connectrum import ElectrumErrorResponse


from labelbase.models import Label
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

def is_valid_output_ref(ref):
    """
    """
    if not ref:
        return False
    if ":" in ref:
        return True
    return False

def checkup_label(label_id, loop):
    if label_id and loop:
        """
        [ ] get_or_create() OutputStat using unspent payload
        """
        elem = Label.objects.get(id=label_id)
        output = OutputStat.objects.filter(type_ref_hash=elem.type_ref_hash, network=elem.labelbase.network).last()
        if not output:
            print("Creating OutputStat")
            output = OutputStat(type_ref_hash=elem.type_ref_hash, network=elem.labelbase.network, value=0)
        print("Using OutputStat id {}".format(output))

        if elem.type == "output" and is_valid_output_ref(elem.ref) and output.spent is not True:
            electrum_hostname = elem.labelbase.user.profile.electrum_hostname
            if not electrum_hostname:
                electrum_hostname = "electrum.emzy.de"
            electrum_ports = elem.labelbase.user.profile.electrum_ports
            if not electrum_ports:
                electrum_ports = "s50002"
            server_info = ServerInfo(electrum_hostname, electrum_hostname, ports=((electrum_ports)))
            conn = StratumClient()
            assert elem.type_ref_hash
            utxo = elem.ref
            tx_hash, tx_pos = elem.ref.split(":")
            utxo_resp = loop.run_until_complete(interact(conn, server_info, "blockchain.transaction.get", utxo))
            blocktime = 0
            if utxo_resp:
                print("utxo_resp {}".format(utxo_resp))
                txid, index, address, value, blocktime = utxo_resp
                if blocktime:
                    print("Found blocktime {} for label id {}.".format(blocktime, label_id))
                    HistoricalPrice.get_or_create_from_api(timestamp=blocktime)
                try:
                    unspents = loop.run_until_complete(interact_addr(
                                conn, server_info, "blockchain.address.listunspent", address))
                except:
                    # TODO: Review this if needed.
                    # It seems some Electrum versions have issues using "blockchain.address.listunspent"
                    #   File "/usr/local/lib/python3.9/asyncio/selector_events.py", line 500, in sock_connect
                    #    return await fut
                    #  File "/usr/local/lib/python3.9/asyncio/selector_events.py", line 535, in _sock_connect_cb
                    #    raise OSError(err, f'Connect call failed {address}')
                    # ConnectionRefusedError: [Errno 111] Connect call failed ('198.244.201.86', 50002)
                    unspents = loop.run_until_complete(interact_addr(
                                conn, server_info, "blockchain.scripthash.listunspent", address))

                unspent_utxo = False
                utxo_value = 0
                utxo_height = 0
                print("unspents: {}".format(unspents))
                for unspent in unspents:
                    if unspent.get('tx_hash') == tx_hash and \
                        unspent.get('tx_pos') == int(tx_pos) and \
                        unspent.get('height') > 0 and \
                        unspent.get('value') > 0:
                        unspent_utxo = True
                        utxo_value = unspent.get('value')
                        utxo_height = unspent.get('height')
                        print("found unspent: {}".format(unspent))
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
                    print("output id {} saved".format(output.id))
    else:
        if not label_id:
            logger.error("Can't get label_id! {}".format(label_id))
        if not loop:
            logger.error("Can't get loop!")

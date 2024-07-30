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
                utxo = txn.get('vout')[int(index)]
                address = txn.get('vout')[int(index)].get('scriptPubKey', {}).get('address')
                value = txn.get('vout')[int(index)].get('value')*100000000
                return (txid, index, address, value, blocktime, utxo)
        except ElectrumErrorResponse as ex:
            logger.error("ERROR: {} {}".format(ex, conn.last_error))

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
    if not ref:
        return False
    if ":" in ref:
        return True
    return False

def checkup_label(label_id, loop):
    if label_id and loop:
        try:
            elem = Label.objects.get(id=label_id)
            output = OutputStat.objects.filter(user=elem.labelbase.user,
                                                type_ref_hash=elem.type_ref_hash,
                                                network=elem.labelbase.network).last()
            if not output:
                output = OutputStat(user=elem.labelbase.user,
                                    type_ref_hash=elem.type_ref_hash,
                                    network=elem.labelbase.network, value=0)

            if elem.type == "output" and is_valid_output_ref(elem.ref)  and \
                    (output.spent is not True or output.confirmed_at_block_time == 0):
                if elem.labelbase.is_mainnet:
                    electrum_hostname = elem.labelbase.user.profile.electrum_hostname or "electrum.emzy.de"
                    electrum_ports = elem.labelbase.user.profile.electrum_ports or "s50002"
                elif elem.labelbase.is_testnet:
                    electrum_hostname = elem.labelbase.user.profile.electrum_hostname_test or "testnet.qtornado.com"
                    electrum_ports = elem.labelbase.user.profile.electrum_ports_test or "s51002"
                server_info = ServerInfo(electrum_hostname, electrum_hostname, ports=(electrum_ports))

                conn = StratumClient()
                utxo = elem.ref
                utxo_data = {}
                utxo_resp = loop.run_until_complete(interact(conn, server_info, "blockchain.transaction.get", utxo))

                if utxo_resp:
                    txid, index, address, value, blocktime, utxo_data = utxo_resp
                    if utxo_data:
                        #output.next_input_attributes = utxo_data
                        output.set_next_input_attributes(utxo_data)
                    if blocktime:
                        HistoricalPrice.get_or_create_from_api(timestamp=blocktime)

                    try:
                        unspents = loop.run_until_complete(interact_addr(conn, server_info, "blockchain.address.listunspent", address))
                    except:
                        conn.last_error = None # reset error if needed
                        unspents = loop.run_until_complete(interact_addr(conn, server_info, "blockchain.scripthash.listunspent", address))

                    utxo_value = 0
                    utxo_height = 0

                    if unspents:
                        for unspent in unspents:
                            if unspent.get('tx_hash') == txid and \
                                   unspent.get('tx_pos') == int(index) and \
                                   unspent.get('height') > 0 and \
                                   unspent.get('value') > 0: # Output is confirmed, but not spent yet
                                output.spent = False
                                utxo_value = unspent.get('value')
                                utxo_height = unspent.get('height')

                                output.network = elem.labelbase.network
                                if utxo_height:
                                    output.confirmed_at_block_height = utxo_height
                                if blocktime:
                                    output.confirmed_at_block_time = blocktime
                                if utxo_value:
                                    output.value = utxo_value
                                elif value:
                                    output.value = value
                                break
                    #
                elif conn.last_error:
                    output.last_error = conn.last_error
                else:
                    output.last_error = {}
                output.save()
                try:
                    conn.close()
                except:
                    pass

        except Exception as e:
            logger.error("Error processing label {}: {}".format(label_id, e))
    else:
        if not label_id:
            logger.error("Can't get label_id! {}".format(label_id))
        if not loop:
            logger.error("Can't get loop!")


def checkup_label_buggy(label_id, loop):
    if label_id and loop:
        elem = Label.objects.get(id=label_id)
        output = OutputStat.objects.filter(user=elem.labelbase.user,
                                            type_ref_hash=elem.type_ref_hash,
                                            network=elem.labelbase.network).last()
        if not output:
            print("Creating OutputStat")
            output = OutputStat(user=elem.labelbase.user,
                                type_ref_hash=elem.type_ref_hash,
                                network=elem.labelbase.network, value=0)
        print("Using OutputStat id {}".format(output))
        print("elem.type {} {} {} {}".format(elem.type, is_valid_output_ref(elem.ref), elem.ref, output.spent))
        if elem.type == "output" and is_valid_output_ref(elem.ref) and \
                (output.spent is not True or output.confirmed_at_block_time == 0):
            electrum_hostname = elem.labelbase.user.profile.electrum_hostname
            if not electrum_hostname:
                electrum_hostname = "electrum.emzy.de"
            electrum_ports = elem.labelbase.user.profile.electrum_ports
            if not electrum_ports:
                electrum_ports = "s50002"
            print("going for server_info")
            server_info = ServerInfo(electrum_hostname, electrum_hostname, ports=((electrum_ports)))
            print("server_info: {}".format(server_info))
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
                    unspents = loop.run_until_complete(interact_addr(conn, server_info, "blockchain.address.listunspent", address))
                except:
                    conn.last_error = None # reset error if needed
                    unspents = loop.run_until_complete(interact_addr(conn, server_info, "blockchain.scripthash.listunspent", address))

                unspent_utxo = False
                utxo_value = 0
                utxo_height = 0
                print("unspents: {}".format(unspents))

                if unspents:
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
                    output.last_error = {}
            elif conn.last_error:
                # Damn...
                output.last_error = conn.last_error
            else:
                output.last_error = {}
            output.save()
            print("output id {} saved".format(output.id))
            try:
                conn.close()
            except:
                pass
    else:
        if not label_id:
            logger.error("Can't get label_id! {}".format(label_id))
        if not loop:
            logger.error("Can't get loop!")

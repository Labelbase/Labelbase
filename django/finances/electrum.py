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
                return hextx
        except ElectrumErrorResponse as ex:
            logger.error(ex)
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
            output = OutputStat.objects.filter(
                user=elem.labelbase.user,
                type_ref_hash=elem.type_ref_hash,
                network=elem.labelbase.network
            ).last()

            if not output:
                output = OutputStat(
                    user=elem.labelbase.user,
                    type_ref_hash=elem.type_ref_hash,
                    network=elem.labelbase.network,
                    value=0,
                    spent=None,
                    confirmed_at_block_height=0,
                    confirmed_at_block_time=0
                )
            logger.debug(f"Output before processing: {output.output_metrics_dict()}")

            if elem.type == "output" and is_valid_output_ref(elem.ref) and (
                output.spent is not True or output.confirmed_at_block_time == 0
            ):
                # Determine server info based on network
                if elem.labelbase.is_mainnet:
                    electrum_hostname = elem.labelbase.user.profile.electrum_hostname or "fulcrum.sethforprivacy.com"
                    electrum_ports = elem.labelbase.user.profile.electrum_ports or "s50002"
                elif elem.labelbase.is_testnet:
                    electrum_hostname = elem.labelbase.user.profile.electrum_hostname_test or "testnet.qtornado.com"
                    electrum_ports = elem.labelbase.user.profile.electrum_ports_test or "s51002"
                else:
                    raise ValueError("Unknown network type.")

                server_info = ServerInfo(electrum_hostname, electrum_hostname, ports=(electrum_ports))
                conn = StratumClient()
                utxo = elem.ref

                # Fetch transaction details
                utxo_resp = loop.run_until_complete(interact(conn, server_info, "blockchain.transaction.get", utxo))

                if utxo_resp:
                    txid, index, address, value, blocktime, utxo_data = utxo_resp
                    logger.debug(f"Transaction {txid} fetched with blocktime {blocktime}")
                    if blocktime:
                        output.confirmed_at_block_time = blocktime
                        output.confirmed_at_block_height = txn.get('height', 0)

                    # Fetch all unspents for the address
                    try:
                        unspents = loop.run_until_complete(interact_addr(conn, server_info, "blockchain.address.listunspent", address))
                    except:
                        conn.last_error = None
                        unspents = loop.run_until_complete(interact_addr(conn, server_info, "blockchain.scripthash.listunspent", address))

                    logger.debug(f"Unspents for address {address}: {unspents}")

                    utxo_found = False
                    for unspent in unspents:
                        if unspent.get('tx_hash') == txid and unspent.get('tx_pos') == int(index):
                            output.spent = False
                            output.value = unspent.get('value', 0)
                            output.confirmed_at_block_height = unspent.get('height', 0)
                            utxo_found = True
                            break

                    if not utxo_found:
                        output.spent = True
                        logger.warning(f"UTXO {txid}:{index} not found in unspent outputs.")
                    else:
                        logger.error(f"Failed to fetch transaction details for {utxo}")

                elif conn.last_error:
                    output.last_error = conn.last_error
                else:
                    logger.warning(f"Unknown error occurred for UTXO {utxo}")
                    output.last_error = {"error": "Unknown issue"}

                logger.debug(f"Output after processing (before save): {output.output_metrics_dict()}")
                output.save()
                output.refresh_from_db()
                logger.debug(f"Output after saving: {output.output_metrics_dict()}")
                conn.close()

        except Exception as e:
            logger.error(f"Error processing label {label_id}: {e}")
    else:
        logger.error(f"Invalid input: label_id={label_id}, loop={loop}")

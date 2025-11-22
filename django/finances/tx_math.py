# Constants
P2PKH_IN_SIZE = 148
P2PKH_OUT_SIZE = 34

P2SH_OUT_SIZE = 32
P2SH_P2WPKH_OUT_SIZE = 32
P2SH_P2WSH_OUT_SIZE = 32

P2WPKH_OUT_SIZE = 31
P2WSH_OUT_SIZE = P2TR_OUT_SIZE = 43

PUBKEY_SIZE = 33
SIGNATURE_SIZE = 72


def get_size_of_var_int(length):
    if length <= 252:
        return 1
    elif length <= 0xffff:
        return 3
    elif length <= 0xffffffff:
        return 5
    else:
        return 9


def get_size_of_script_length_element(length):
    if length < 75:
        return 1
    elif length <= 255:
        return 2
    elif length <= 65535:
        return 3
    elif length <= 4294967295:
        return 5
    else:
        raise ValueError("Script too large")


def get_input_size(input_attr):
    """Return (base_size, witness_size) for a single input."""
    script_type = input_attr['input_script']
    m = input_attr.get('input_m', 0)
    n = input_attr.get('input_n', 0)

    if script_type == "P2PKH":
        return P2PKH_IN_SIZE, 0
    elif script_type == "P2SH":
        # Redeem script: OP_m + n_pubkeys + OP_n + OP_CHECKMULTISIG
        redeem_script_size = 1 + n * (1 + PUBKEY_SIZE) + 1 + 1
        # scriptSig: OP_0 + m_sigs + push_opcode + redeem_script
        script_sig_size = 1 + m * (1 + SIGNATURE_SIZE) + get_size_of_script_length_element(redeem_script_size) + redeem_script_size
        input_base_size = 32 + 4 + get_size_of_var_int(script_sig_size) + script_sig_size + 4
        return input_base_size, 0
    elif script_type == "P2SH-P2WPKH":
        input_base_size = 32 + 4 + 1 + 23 + 4
        input_witness_size = 107
        return input_base_size, input_witness_size
    elif script_type == "P2WPKH":
        input_base_size = 32 + 4 + 1 + 4
        input_witness_size = 107
        return input_base_size, input_witness_size
    elif script_type == "P2WSH":
        input_base_size = 32 + 4 + 1 + 4
        witness_script_size = 1 + n * (1 + PUBKEY_SIZE) + 1 + 1
        num_stack_items = 1 + m + 1  # OP_0 + m sigs + witness script
        input_witness_size = (
            get_size_of_var_int(num_stack_items) +
            1 +                   # OP_0 length
            m * (1 + SIGNATURE_SIZE) +
            get_size_of_var_int(witness_script_size) +
            witness_script_size
        )
        return input_base_size, input_witness_size
    elif script_type == "P2TR":
        input_base_size = 32 + 4 + 1 + 4
        input_witness_size = 65
        return input_base_size, input_witness_size
    else:
        raise ValueError(f"Unsupported input script type: {script_type}")


def calculate_transaction_size(inputs, output_counts):
    """
    inputs: list of dicts with keys: input_script, input_m, input_n
    output_counts: dict with counts per output type
    """
    total_base = 0
    total_witness = 0


    # Total inputs / outputs
    input_count = len(inputs)
    output_count = sum(output_counts.values())

    # Transaction overhead: version(4) + varints + locktime(4)
    tx_base_size = 4 + get_size_of_var_int(input_count) + get_size_of_var_int(output_count) + 4


    # Segwit marker + flag if any input is segwit
    has_witness = any(inp['input_script'] in ["P2SH-P2WPKH", "P2WPKH", "P2WSH", "P2TR"] for inp in inputs)
    if has_witness:
        total_witness += 2  # marker + flag

    for inp in inputs:
        base, witness = get_input_size(inp)
        total_base += base
        total_witness += witness

    # Sum output sizes
    output_size = (P2PKH_OUT_SIZE * output_counts.get('p2pkh', 0) +
                   P2SH_OUT_SIZE * output_counts.get('p2sh', 0) +
                   P2SH_P2WPKH_OUT_SIZE * output_counts.get('p2sh_p2wpkh', 0) +
                   P2SH_P2WSH_OUT_SIZE * output_counts.get('p2sh_p2wsh', 0) +
                   P2WPKH_OUT_SIZE * output_counts.get('p2wpkh', 0) +
                   P2WSH_OUT_SIZE * output_counts.get('p2wsh', 0) +
                   P2TR_OUT_SIZE * output_counts.get('p2tr', 0))


    # Total base size
    tx_total_base_size = tx_base_size + total_base + output_size

    # Transaction weight and vbytes
    tx_weight = tx_total_base_size * 4 + total_witness
    tx_vbytes = tx_weight / 4

    # Raw bytes (base + witness discounted by 1/4)
    tx_bytes = tx_total_base_size + total_witness / 4

    return {
        'txBytes': round(tx_bytes),
        'txVBytes': round(tx_vbytes),
        'txWeight': tx_weight
    }



def calculate_fee(tx_vbytes, fee_rate_sats_per_vbyte):
    """
    tx_vbytes: virtual size from calculate_transaction_size()
    fee_rate_sats_per_vbyte: fee rate in sats per vbyte
    """
    return round(tx_vbytes * fee_rate_sats_per_vbyte)



def run_tests():
    fee_rate = 20  # sats per vbyte
    test_cases = [
        # 1. Single P2PKH input -> single P2PKH output
        {
            'inputs': [{'input_script': 'P2PKH'}],
            'outputs': {'p2pkh': 1},
            'description': 'Single P2PKH -> P2PKH'
        },
        # 2. Two P2WPKH inputs -> two P2WPKH outputs
        {
            'inputs': [{'input_script': 'P2WPKH'}, {'input_script': 'P2WPKH'}],
            'outputs': {'p2wpkh': 2},
            'description': 'Two P2WPKH -> Two P2WPKH'
        },
        # 3. Single P2SH 2-of-3 multisig input -> two P2PKH outputs
        {
            'inputs': [{'input_script': 'P2SH', 'input_m': 2, 'input_n': 3}],
            'outputs': {'p2pkh': 2},
            'description': 'P2SH 2-of-3 multisig -> 2x P2PKH'
        },
        # 4. Mixed inputs: P2PKH + P2WPKH + P2TR -> P2PKH + P2WPKH
        {
            'inputs': [
                {'input_script': 'P2PKH'},
                {'input_script': 'P2WPKH'},
                {'input_script': 'P2TR'}
            ],
            'outputs': {'p2pkh': 1, 'p2wpkh': 1},
            'description': 'Mixed inputs -> mixed outputs'
        },
        # 5. Two P2WSH multisig inputs -> P2WSH outputs
        {
            'inputs': [
                {'input_script': 'P2WSH', 'input_m': 2, 'input_n': 3},
                {'input_script': 'P2WSH', 'input_m': 1, 'input_n': 2}
            ],
            'outputs': {'p2wsh': 2},
            'description': 'Two P2WSH -> Two P2WSH'
        }
    ]

    for idx, test in enumerate(test_cases, 1):
        # Step 1: calculate size
        tx_size = calculate_transaction_size(test['inputs'], test['outputs'])

        # Step 2: calculate fee
        fee_sats = calculate_fee(tx_size['txVBytes'], fee_rate)

        print(f"Test {idx}: {test['description']}")
        print(f"  txBytes: {tx_size['txBytes']}, txVBytes: {tx_size['txVBytes']}, txWeight: {tx_size['txWeight']}")
        print(f"  Fee (@ {fee_rate} sats/vbyte): {fee_sats} sats\n")



# Example usage
if __name__ == "__main__":
    inputs = [
        {'input_script': 'P2PKH'},
        {'input_script': 'P2WPKH'},
        {'input_script': 'P2SH', 'input_m': 2, 'input_n': 3},
    ]
    output_counts = {
        'p2pkh': 1,
        'p2sh': 0,
        'p2sh_p2wpkh': 1,
        'p2sh_p2wsh': 0,
        'p2wpkh': 0,
        'p2wsh': 0,
        'p2tr': 0
    }

    tx_size = calculate_transaction_size(inputs, output_counts)
    print(tx_size)

    print("*"*80)
    run_tests()

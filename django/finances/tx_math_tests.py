def run_tests():
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
        result = calculate_transaction_size(test['inputs'], test['outputs'])
        print(f"Test {idx}: {test['description']}")
        print(f"  txBytes: {result['txBytes']}, txVBytes: {result['txVBytes']}, txWeight: {result['txWeight']}\n")

if __name__ == "__main__":
    run_tests()

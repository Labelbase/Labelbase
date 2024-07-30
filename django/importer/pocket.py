import csv
import json 


def validate_csv_format(csv_file_path):
    expected_sequence = ['withdraw', 'order', 'deposit']
    with open(csv_file_path, newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  # Skip the header
        for row in csv_reader:
            if len(row) != 11 or row[0] not in expected_sequence:
                return False
            expected_index = expected_sequence.index(row[0])
            if expected_index == 0 and expected_index != 0:
                return False
            expected_sequence.append(expected_sequence.pop(0))
    return True


def parse_csv_to_json(csv_file_path):
    json_list = []
    with open(csv_file_path, newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  # Skip the header
        group = []
        for row in csv_reader:
            if row[0] == 'withdraw':
                if group:
                    json_list.append(group)
                group = []
            data = {
                'transactionType': row[0],
                'date': row[1],
                'inBuyAmount': row[2],
                'inBuyAsset': row[3],
                'outSellAmount': row[4],
                'outSellAsset': row[5],
                'feeAmount': row[6] if row[6] else "",
                'feeAsset': row[7] if row[7] else "",
                'classification': row[8] if row[8] else "",
                'operationId': row[9] if row[9] else "",
                'comments': row[10] if row[10] else ""
            }
            group.append(data)
        if group:
            json_list.append(group)
    return json_list

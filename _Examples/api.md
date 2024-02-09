#
https://labelbase.space/api/labelbase/


import requests  # pip install requests
import json

# Replace 'your_key_here' with your actual API key
api_key = 'your_key_here'

# Replace with the ID of your Labelbase
labelbase_id  = 17

# URL of the Labelbase API endpoint
url = f'https://labelbase.space/api/v0/labelbase/{labelbase_id}/'

# Data to be sent in the POST request (if needed)
data = {
}

# Headers containing the API key
headers = {
    'Authorization': f'Token {api_key}'
}

# Make the POST request
response = requests.post(url, headers=headers, data=data)

# Print the response
print(response.status_code)
print(response.text)

>>> import json
>>> json.loads(response.text)
{'id': 30, 'name': '', 'fingerprint': '', 'about': ''}


# List all labelbases   
url = f'https://labelbase.space/api/v0/labelbase/'
response = requests.get(url, headers=headers, data=data)

# Create a new Labelbase and store its ID for further usage.

url = f'https://labelbase.space/api/v0/labelbase/'
data = {'name': 'Bitcoin Chronicles',
        'fingerprint': 'ticktock', 'about': 'Legendary transactions and important addresses.'}


response = requests.post(url, headers=headers, data=data)
labelbase_id = json.loads(response.text).get('id')

# Create a new label for a transaction
url = f'https://labelbase.space/api/v0/labelbase/{labelbase_id}/label/'


txid = "Cca7507897abc89628f450e8b1e0c6fca4ec3f7b34cccf55f3f531c659ff4d79"
f"/api/v0/labelbase/{labelbase_id}/label/"

# Sending no data / data={} creates an empty label
response = requests.post(url, headers=headers, data=data)

#
data = {
  "labelbase": labelbase_id,
  "type": "tx",
  "ref": txid,
  "label": "Two supreme pizzas from Papa John's"
}
response = requests.post(url, headers=headers, data=data)

# Create and update a label

data = {
  "labelbase": labelbase_id,
  "type": "tx",
  "ref": "F4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16",
  "label": "Satoshi sending sats"
}
response = requests.post(url, headers=headers, data=data)
label_data = json.loads(response.text)
label_id = label_data.get('id')

url = f'https://labelbase.space/api/v0/labelbase/{labelbase_id}/label/{label_id}/'
data["label"] = "First transaction from Satoshi to Hal Finney"

response = requests.put(url, headers=headers, data=data)

# List all labels of a labelbase
url = f'https://labelbase.space/api/v0/labelbase/{labelbase_id}/label/'
response = requests.get(url, headers=headers, data={})
response_data = json.loads(response.text)

for l in response_data:
    print(l)

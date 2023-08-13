# Integrating the Labelbase API: A Step-by-Step Python Guide


Welcome to the Labelbase API integration Python tutorial! In this guide, we'll walk you through the process of seamlessly integrating the Labelbase API into your project. The Labelbase API allows you to manage labelbases and labels, making it an invaluable tool for organizing and syncing your BIP-329 Bitcoin labels and coin information.




Below is a step-by-step guide that walks you through the process of using the Labelbase API to manage labelbases and labels. I've included explanations, code snippets, and comments to assist you in understanding each step.

Please note that you need to replace 'your_key_here' with your actual API key.



```
# Import required libraries
import requests  # pip install requests
import json

# Replace 'your_key_here' with your actual API key
api_key = 'your_key_here'

# Define the base URL for the Labelbase API
base_url = 'https://labelbase.space/api/v0/'

# Define headers containing the API key
headers = {
    'Authorization': f'Token {api_key}'
}
```


```
# Create a new Labelbase
url = f'{base_url}labelbase/'
data = {
    'name': 'Bitcoin Chronicles',
    'fingerprint': 'ticktock',
    'about': 'Legendary transactions and important addresses.'
}
response = requests.post(url, headers=headers, data=data)
labelbase_id = json.loads(response.text).get('id')

print(f'Created Labelbase with ID: {labelbase_id}')
```



**First Bitcoin Transaction:** On January 12, 2009, the first known Bitcoin transaction took place between Satoshi Nakamoto (the pseudonymous creator of Bitcoin) and Hal Finney. Nakamoto sent 10 BTC to Finney as a test.

```
# Create two labels within the created Labelbase
url = f'{base_url}labelbase/{labelbase_id}/label/'

data = {
    'type': 'tx',
    'ref': 'F4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16',
    'label': 'Satoshi sending sats'
}

response = requests.post(url, headers=headers, data=data)
print(json.loads(response.text))
label_id = json.loads(response.text).get('id')
print(f'Created Label with ID: {label_id}')
```


**Pizza Purchase:** On May 22, 2010, a programmer named Laszlo Hanyecz famously paid 10,000 BTC (worth millions of dollars today) for two pizzas, making it one of the earliest examples of a real-world transaction using Bitcoin.

```
data = {
    'type': 'tx',
    'ref': 'Cca7507897abc89628f450e8b1e0c6fca4ec3f7b34cccf55f3f531c659ff4d79',
    'label': 'Two supreme pizzas from Papa John\'s'
}

response = requests.post(url, headers=headers, data=data)
print(json.loads(response.text))
label_id = json.loads(response.text).get('id')
print(f'Created Label with ID: {label_id}')
```


```
# List all labels within a Labelbase
url = f'{base_url}labelbase/{labelbase_id}/label/'
response = requests.get(url, headers=headers)
labels = json.loads(response.text)

print('Labels within the Labelbase with ID {labelbase_id}:')
for label in labels:
    print(label)

```



To perform label updates, you have two options.
You can either provide the label ID along with the updated data, or you can retrieve the existing label data using a known ID, modify the relevant JSON fields, and then send the modified data. Keep in mind that in the latter approach, you should replace 'your_satoshi_label_id' with the specific label ID you are working with.

```
# Update a label within a Labelbase

# V1
data = {
    'type': 'tx',
    'ref': 'F4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16',
    'label': 'First transaction from Satoshi to Hal Finney'
}

label_id = 'your_satoshi_label_id'
url = f'{base_url}labelbase/{labelbase_id}/label/{label_id}/'
response = requests.put(url, headers=headers, data=data)
print(json.loads(response.text))
label_id = json.loads(response.text).get('id')
print(f'V1) Updated Label with ID: {label_id}')
```


```
# V2
for label in labels:
    if label.get('id') == 'your_satoshi_label_id':
        data = label

assert data
data['label'] = 'First transaction from Satoshi to Hal Finney'
label_id = data.get('id')

url = f'{base_url}labelbase/{labelbase_id}/label/{label_id}/'
response = requests.put(url, headers=headers, data=data)
print(json.loads(response.text))
label_id = json.loads(response.text).get('id')
print(f'V2) Updated Label with ID: {label_id}')
```


```
# Delete a label within a Labelbase
url = f'{base_url}labelbase/{labelbase_id}/label/{label_id}/'
response = requests.delete(url, headers=headers, data={})
print(f'Deleted Label with ID: {label_id}')
```

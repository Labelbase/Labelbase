import logging
from background_task import background
from labelbase.models import Label

logger = logging.getLogger('labelbase')


"""
 def get_transaction_outspend(self, txid, vout):
        txid = txid.replace(' ', '')
        vout = vout.replace(' ', '')
        api_url = f'{self.api_base_url}tx/{txid}/outspend/{vout}'
        return self.__request(api_url)

# @ login, check all unspent outputs
#
# last checked @ block_height <- if spent, set block_height from status
# "block_time": (for price info lookup)
# labelbase_id
# output/txid:vout (encrypted)
# JSON FIELD = {
"spent":true,
"txid":" ","vin":3,
"status":
    "confirmed":true,
    "block_height":798098,
    "block_time":1688985257

"""

"""
if context["action"] == "labeling":

    if self.object.type == "tx":
        context["res_tx"] = mempool_api.get_transaction(self.object.ref)

return context


"""

import time

@background(schedule=0) # replace existing
def check_all_outputs(user_id):
    labels = Label.objects.filter(labelbase__user_id=user_id)
    for label in labels:
        if label.type == "output":
            #time.sleep(3)
            check_spent(label.id)

@background(schedule=0) # replace existing
def get_price_info(txid, vout):
    pass



@background(schedule=0) # replace existing
def check_spent(label_id):
    label =  Label.objects.get(id=label_id)
    mempool_api = label.labelbase.get_mempool_api()
    txid, vout = label.ref.split(":")
    res = mempool_api.get_transaction_outspend(txid, vout)
    logger.debug(res)


"""
for all my labelbasels:
  for all my labels fo type = "output":
      call check_spent(f'{txid} {vout}')
"""

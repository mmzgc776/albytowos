import requests
import json

class lnd_handler:

    def __init__(self, macaroon, host, verbose):
        self.host = host
        self.verbose = verbose   
        self.macaroon = macaroon
        

    def request(self, method, path, query, body):
        url = self.host + path
        if query:
            url += '?' + query

        if self.verbose:
            print(method, url)

        s = requests.Session()        
        s.headers['Content-Type']= 'application/json'
        s.headers['Grpc-Metadata-macaroon'] = self.macaroon
        if body:
            body_json = json.dumps(body)
            response = s.request(method, url, data=body_json, verify=False)
        else:
            response = s.request(method, url, verify=False)

        if response.status_code == 200:
            return response.json()
        if response.status_code == 201:
            return response.json()
        
        elif response.content:
            raise Exception(str(response.status_code) + ": " + response.reason + ": " + str(response.content))
        else:
            raise Exception(str(response.status_code) + ": " + response.reason)
    
    def get_balance(self):
        response = self.request('GET', '/balance', '', '')
        balance = response['balance']
        return balance
    
    def get_invoice(self, amount):
        data = {
            'memo': "Testing Script",            
            'value': amount                   
            }        
        response = self.request('POST', '/v1/invoices', '', data)        
        invoice = response['payment_request'] 
        return invoice
    
    def get_channel_outbound(self, channel_id):        
        response = self.request('GET', '/v1/channels', '', '')
        for channel in response["channels"]:
            if channel["chan_id"]==channel_id:
                local_balance = int(channel["local_balance"])
                remote_balance = int(channel["remote_balance"])
        return local_balance, remote_balance
    
    def get_channel_fee(self, channel_id):
        response = self.request('GET', '/v1/fees', '', '')
        for channel in response["channel_fees"]:
            if channel["chan_id"]==channel_id:
                  fee = channel["fee_per_mil"]        
        return fee
    
        #Request node to pay certain invoice
    def node_pay_invoice(self, invoice, outgoing_channel):
        success=0
        #print("Trying to pay invoice")   
        timeout = 60
        max_fee_sats = 1
        #print(max_fee_sats, end=" ")
        response = ""
        if outgoing_channel!="":
            params = {
                    "payment_request": invoice,
                    "timeout_seconds": timeout,
                    "fee_limit_sat": max_fee_sats,
                    "outgoing_chan_id": outgoing_channel,             
                    "max_parts": 4
                }
        else:
            params = {
                    "payment_request": invoice,
                    "timeout_seconds": timeout,
                    "fee_limit_sat": max_fee_sats,                
                    "max_parts": 4
                }            
        try:
            response = self.request('POST', "/v2/router/send", "", params)
        
        except:
            print("An exception occurred")

        
        #print("***************")    
        #str=str.replace('}{', '}\n{')
        #array = ndjson.loads(str)
        #print(array)
        #array = json.dump(str)
        if self.verbose:            
            '''
            if(response.status_code==200):
                print(",", end = '', flush=True)         
                for results in response: 
                    for result in results.values():
                        if result['status'] == "SUCCEEDED":
                            print("*")
                            success=1
            str=(response.content).decode('utf-8')
            print(str)
            '''
        return success
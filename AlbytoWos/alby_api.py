import requests
import json

class alby_handler:

    def __init__(self, token, verbose):
        self.host = "https://api.getalby.com"
        self.verbose = verbose   
        self.access_token = "Bearer "+token
        

    def request(self, method, path, query, body):
        url = self.host + path
        if query:
            url += '?' + query

        if self.verbose:
            print(method, url)

        s = requests.Session()
        s.headers['Authorization'] = self.access_token
        s.headers['Content-Type']= 'application/json'
        if body:
            body_json = json.dumps(body)
            response = s.request(method, url, data=body_json)
        else:
            response = s.request(method, url)

        if response.status_code == 200 or response.status_code == 201 :
            return response.json()
        
        elif response.status_code == 400 :
            print(Exception(str(response.status_code) + ": " + response.reason + ": " + str(response.content)))
            return 400
        
        elif response.content:
            raise Exception(str(response.status_code) + ": " + response.reason + ": " + str(response.content))
        else:

            raise Exception(str(response.status_code) + ": " + response.reason)
    
    def get_balance(self):
        response = self.request('GET', '/balance', '', '')
        balance = int(response['balance'])
        return balance
    
    def get_invoice(self, amount):
        if self.verbose:
            print ("Requesting an invoice for:", amount)
        data = {
            "description": "Testing Script", 
            "amount": amount
        }        
        response = self.request('POST', '/invoices', '', data) 
        if response == 400:
            return "reduce"                       
        invoice = response['payment_request'] 
        return invoice
    
    def pay_invoice(self, wos_invoice, amount):        
        if self.verbose:
            #print (wos_invoice, amount)
            print ("Requesting payment:", amount)
        data = {         
            "invoice": wos_invoice,
            "amount": amount
        }        
        response = self.request('POST', '/payments/bolt11', '', data)
        if response == 400:
            return "reduce"
        #print(response)        
        fee = int(response['fee'])
        return fee
        
        
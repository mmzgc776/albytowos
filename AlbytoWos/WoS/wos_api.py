import requests
import json

class wos_api_handler:

    def __init__(self, verbose):        
        self.verbose = verbose   
        #self.access_token = "Bearer "+token        

    def request(self, method, path, query, body):
        url = path
        if query:
            url += '?' + query

        if self.verbose:
            print(method, url)

        s = requests.Session()
        
        s.headers['Content-Type']= 'application/json'

        if body:
            body_json = json.dumps(body)
            response = s.request(method, url, data=body_json)
        else:
            response = s.request(method, url)

        if response.status_code == 200 or response.status_code == 201 :
            return response.json()
        elif response.status_code == 500 or response.status_code == 503 :
            print ("Server side error 500: Internal Server Error")
            return 500
        elif response.content:
            print(Exception(str(response.status_code) + ": " + response.reason + ": " + str(response.content)))
            return 500
        else:
            print( Exception(str(response.status_code) + ": " + response.reason) )
            return 500
   
    def get_callback(self, url):
        if self.verbose:
            print ("Requesting callback endpoint")            
        response = self.request('GET', url, '', '')        
        #print (response)
        #callback = response['callback']
        return response     
    
    def get_invoice_with_callback(self, callback, amount):
        #<callback><?|&>amount=<milliSatoshi>
        if self.verbose:
            print ("Requesting invoice to callback endpoint")        
        query  = "amount="+str(amount*1000)
        response = self.request('GET', callback, query, '')
        #print (response)
        #invoice = response['pr']         
        return response

        
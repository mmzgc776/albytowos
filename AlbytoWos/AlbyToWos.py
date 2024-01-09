import alby_api
import lnd_api
import urllib3
import random
import time
import pyperclip
from WoS.wos_handler import StepsDefinitions
urllib3.disable_warnings()

alby_access_token = "" #your api token
host = "xxx.xxx.xxx.xxx" #your local ip to open connections
alby_channel_id = "" #your alby channel id
wos_channel_id =  "" #your wos channel id
#wos_channel_id2 = "" #your second channel id
initial_time = time.time()
verbose = True

lnd_macaroon = "" #your lnd macaroon
lnd_host = 'https://xxx.xxx.xxx.xxx:8080' #your lnd host n port

alby_handler = alby_api.alby_handler(alby_access_token, verbose)
alby_sleep_time = 60*30
lnd_handler = lnd_api.lnd_handler(lnd_macaroon, lnd_host, verbose)

wos_handler = StepsDefinitions(verbose)
#wos_handler.list_ui_elements()

#Gets all necessary balances to calculate how much to route
def get_balances():
	wos_handler.open_app()
	start_time = time.time()
	local_alby_outbound, local_alby_inbound = lnd_handler.get_channel_outbound(alby_channel_id)
	local_wos_outbound, local_wos_inbound = lnd_handler.get_channel_outbound(wos_channel_id)
	alby_remote_balance = alby_handler.get_balance()        
	wos_remote_balance = wos_handler.get_balance()
	wos_handler.close_app()
	end_time= time.time() - start_time
	print("Getting balances in: ", end_time, "secs")
	return alby_remote_balance, local_alby_outbound, local_alby_inbound, wos_remote_balance, local_wos_outbound, local_wos_inbound

#Gets an invoice and pays to alby to start a cycle
def push_to_alby(amount_to_push):	
	#alby_invoice_amount = amount_to_push
	#Needs to be changed to dinamic sizes under the api limit
	#alby_invoice_amount = 714286 #day /8 mins	 
	alby_invoice_amount = 50000 #12 hours /16 	
	alby_invoice = alby_handler.get_invoice(alby_invoice_amount)
	if (alby_invoice=="reduce"):
		#Sleep for some time to gain quota
		time.sleep(alby_sleep_time)
		alby_invoice = alby_handler.get_invoice(alby_invoice_amount)
	response = lnd_handler.node_pay_invoice(alby_invoice, alby_channel_id)
	#print (alby_invoice)	
	return	alby_invoice

def get_invoice_amount():
	lower_bound = 2000
	upper_bound = 16000
	payment_amount=random.randint(lower_bound, upper_bound)
	return payment_amount

#Gets an invoice from WoS and pays it with Alby
def push_to_wos(amount_to_push, alby_remote_balance):
	start_time = time.time()
	#This size is arbitrary and would need to be optimized to match an optimal size for low cost rebalance
	payments= int(amount_to_push / 9000)
	payment_count = 0
	fees = 0
	amount_pushed = 0
	print ("First attempt to push to wos", payments, "payments")
	while payment_count < payments:
		#Minus an integer adjusment, to let it anough for fees 
		invoice_amount=get_invoice_amount()-100
		wos_invoice = wos_handler.get_invoice_lnurl(invoice_amount)
		#Add debugging prints
		fee = alby_handler.pay_invoice(wos_invoice, invoice_amount)
		if(fee == "reduce"):
				fee = 0
				break
		fees = fees + fee
		amount_pushed = amount_pushed + invoice_amount
		print("Pushed:", invoice_amount, "(of", amount_pushed , "total), sats to WoS, with", fees,"in fees")
		#Time wait expected to avoid wasting weekly quota
		pause = 60*38 
		print("waiting", pause/60 ,"minutes to save quota")
		time.sleep(pause) 
		payment_count+=1

	#make sure the balance has been pushed up to the desired amount	if not, repeat
	#maybe this is not required...
	alby_old_remote_balance = alby_remote_balance
	alby_remote_balance = alby_handler.get_balance()
	one_percent = int(alby_old_remote_balance*0.01)
	if (alby_remote_balance > one_percent):
		payments= int(alby_remote_balance / 4500)
		payment_count = 0
		print ("Second attempt to push to wos", payments)
		while payment_count < payments:
			invoice_amount=get_invoice_amount()
			wos_invoice = wos_handler.get_invoice_lnurl(invoice_amount)
			#Add debugging prints
			fee = alby_handler.pay_invoice(wos_invoice, invoice_amount)
			if(fee == "reduce"):
				fee = 0
				break
			fees = fees + fee
			amount_pushed = amount_pushed + invoice_amount
			print("Pushed:", invoice_amount, "(of", amount_pushed , "total), sats to WoS, with", fees,"in fees")
			time.sleep(5)
			payment_count+=1			
		alby_remote_balance = alby_handler.get_balance()

	#Show final output
	end_time = time.time() - start_time
	print("Pushing:", amount_to_push, "(", amount_pushed , "), sats to WoS, with", fees,"in fees, in", end_time/60, "minutes")
	return alby_remote_balance

def push_to_node(wos_remote_balance, local_wos_outbound, local_wos_inbound):
	print("Starting pushing from WoS to Node")
	start_time = time.time()
	wos_handler.open_app()
	#If remote wos balance is below channel inbound 		
	if(wos_remote_balance < local_wos_inbound):
		invoice = lnd_handler.get_invoice(int(wos_remote_balance*0.96))
	pyperclip.copy(invoice)
	#Let the emulator load	
	wos_handler.pay_invoice()
	wos_handler.close_app()	
	#pay invoice from wos
	#print (invoice)
	end_time= time.time() - start_time	
	print("Paying invoice from WoS app in: ", end_time, "secs")
	return 

''' All the logic of script here:
Intermediated rebalance to WoS

Push 99% to alby
	alby
		auth
		generate invoice
	lnd
		pay invoice

Pay to wos lnurl 
	generate an invoice amount (discover this value with the samples)
		split balance into n payments
			pay the invoice
			repeat until new balance < 1%
			save ppm
			wait a minute (determine a good wait time to avoid spam)

Pay from WoS to Jalisco
	lnd
		check local balance
		determine invoice size
		generate invoice
	Wos
		pay invoice
	
Get balances
	Alby balance is over 99%?
	WoS Outbound under 35%?
	Average ppm is lower than local wos fee
		Repeat

	Alby balance is under 2%?
	WoS Outbound is over 35%?
		Wait 1 hour
  
'''
while True:

	alby_remote_balance, local_alby_outbound, local_alby_inbound, wos_remote_balance, local_wos_outbound, local_wos_inbound = get_balances()

	print ("Alby Remote Balance:", alby_remote_balance)
	print ("Alby Local Outbound:", local_alby_outbound)
	print ("Alby Local Inbound:", local_alby_inbound)
	print ("WoS Remote Balance:", wos_remote_balance)
	print ("WoS Local Outbound:", local_wos_outbound)
	print ("WoS Local Inbound:", local_wos_inbound)

	#Evaluate if rebalance is worth 

	alby_channel_outbound_percent = local_alby_outbound/(local_alby_outbound+local_alby_inbound)

	alby_channel_ready = False
	alby_is_empty = False
	wos_is_empty = False

	if (alby_channel_outbound_percent > 0.5):    
		# Local Alby channel has enough outbound
		print ("Alby local channel has enough outbound", alby_channel_outbound_percent )
		alby_channel_ready = True
		# Start a rebalance cycle	
	else:     
		# Stop process, wait to fill Alby channel
		print ("Alby local channel has not enough outbound, wait a bit")

	if (alby_remote_balance < 50000):
		# Alby remote balance is empty
		# Ok to	start a cycle
		print ("Alby wallet ready to receive")
		alby_is_empty = True
	else:
		# Empty up alby balance
		print ("Alby wallet needs to be emptied")
		# Start over

	if (wos_remote_balance < 50000):    
		#WoS remote balance is empty
		print ("WoS wallet ready to receive")
		wos_is_empty = True
		# Ok to	start a cycle
	else:
		# Empty up WoS balance
		print ("WoS wallet needs to be emptied")
		# Start over

	#Start cycle

	#Start a cycle if all wallets are ready
	if (alby_channel_ready and alby_is_empty and wos_is_empty):
		#This step requires more cases to be covered
		#amount_to_push = local_wos_inbound - int((local_wos_outbound+local_wos_inbound)*0.02)
		amount_to_push = local_wos_inbound - int((local_wos_outbound+local_wos_inbound)*0.02)
		push_to_alby(amount_to_push)

	# Move alby balance to wos in random small chunks
	if (alby_channel_ready and (alby_is_empty==False)):
		amount_to_push = alby_remote_balance - alby_remote_balance*0.02
		alby_remote_balance = push_to_wos(amount_to_push, alby_remote_balance)		

	# Move WoS Balance to node
	if (alby_is_empty and (wos_is_empty==False)):
		push_to_node(wos_remote_balance, local_wos_outbound, local_wos_inbound)
	
	# There's no enough balance in alby channel, but need to push to WoS
	if (alby_channel_ready == False and alby_is_empty==False ):
		amount_to_push = alby_remote_balance - alby_remote_balance*0.02
		alby_remote_balance = push_to_wos(amount_to_push, alby_remote_balance)

	#Wait until we have enough outbound
	if (alby_channel_ready == False):
		print("Waiting 3 minutes")
		time.sleep (180)


	''' fees evaluation
	wos_current_fee = lnd_handler.get_channel_fee(wos_channel_id)
	print (wos_current_fee)
	'''
	#sats_per_hour will be the total speed in a whole cycle

secs_runtime = time.time()-initial_time
print ("Total run time:", secs_runtime, "secs")



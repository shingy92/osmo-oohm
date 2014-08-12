Features:

1) View BSC and SGSN Statistics
	* View Channel and Data Usage
	* See running versions
2) Administer Subscribers
	* Authorize IMSIs dynamically
	* Authorize IMSIs based on IMEI identification
	* Name IMSI and IMEI for easily identification
3) Send SMS
	* Send SMS to individual subscribers
	* Broadcast SMS to attached subscribers (useful for notifying about system upgrade)
4) Administer BTS Settings
	* View BTS IP address for easy debugging access
	* Change physical channgel configuration for allocating Voice and Data channels as needed
5) Management Scripts
	* In case of failure, the backend services can be restarted from the web interface.
		Supported init.d scripts are:
			* LCR
			* Asterisk
			* GSGN
			* OpenBSC
			* OsmoSGSN
6) Additional Scripts
	* SubscriberMonitor: Welcome message to new or returning roaming subscribers
	* RegisterIMEI: script for individually authorizing subscribers.
		Its easier to have OpenBSC scan the network for the current IMEI-IMSI relationship and authorize a SIM card in a device than finding out the IMSI manually.
		User only enters IMEI and the script does the rest
	* both scripts are managed by hlr_mgmt module and can also be run individually from the command line

Installation & Configuration:

1) Customize the init file to suit your settings. Lines of particular interest are shown below:

	hlr_mgmt/__init__.py
		# OpenBSC Settings
		settings['provider'] = '<<Provider Name>>'
		settings['db'] = '/etc/openbsc/hlr.sqlite3'
		settings['bsc_ip'] = "127.0.0.1"
		settings['sgsn_ip'] = "127.0.0.1"
		settings['bsc_port'] = 4242
		settings['sgsn_port'] = 4245
	
	OPTIONAL:
	If you can produce custom SIM cards with your own MCC/MNC for use in your local network,
	you can add your Provider Details at the end of hlr_mgmt/mcc_mnc.csv following the format:
		MCC,MNC,Network,Operator,Status

2) Install osmo-oohmi. This installation process resolves all the required dependencies and sets up its init scripts.

	sudo python setup.py install

3) Verify installation:

	python setup.py nosetests

	If the above command generates errors, try to fix these before running the software

4) Run the Server for the first time:
	/etc/init.d/osmocom-oohmi start
	
	OPTIONAL DEVELOPER INFO:
		the server can also be invoked manually as shown below
	
		cd /etc/openbsc/
		# pserve is a nice python daemonizing function, customize the execution of the hlr_mgmt module by changing runtime flags.
		pserve --help
		pserve production.ini start

5) Access the Web Interface

	http://localhost:8080/

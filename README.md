# Export 1password logins to csv

[1password] havn't tool to export data at Linux. 
But is has command line [client], which you can use to fetch all data.

Requirements:

-	1password command line [client]  (`op`)
-	Python 3
-	tar, gpg (for encryption) binaries

First login with `op` client. It exports session key to environment variables.
	
	$ eval $(op signin my)

Next run script

	$ python 1passord.py <file-name>

If you want encrypt exported data, pass `--password` argument

	$ python 1passord.py --password <password> <file-name> 	


[1password]: http://1password.com/
[client]: https://1password.com/downloads/command-line/
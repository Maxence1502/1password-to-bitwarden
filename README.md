# Export 1password logins to csv

[1password] hasn't tool to export data at Linux. 
But is has command line [client], which you can use to fetch all data.

Requirements:

-	1password command line [client]  (`op`)
-	Python 3
-	tar, gpg (for encryption) binaries

First login with `op` client. It exports session key to environment variables.
More details [signin](here).
	
	$ eval $(op signin my)

Next run script

	$ python3 1export.py <file-name>

If you want encrypt exported data, pass `--password` argument

	$ python3 1export.py --password <password> <file-name> 	

All together in one line:

	$ eval $(op signin my); python3 1export.py --password <password> "/home/av/Dropbox/1password-$(date '+%Y-%m-%d')"

[1password]: http://1password.com/
[client]: https://1password.com/downloads/command-line/
[signin]: https://support.1password.com/command-line-getting-started/#get-started-with-the-command-line-tool

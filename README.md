# Export 1password logins to csv

[1password] hasn't tool to export data at Linux. 
But is has command line [client], which you can use to fetch all data.

Requirements:

-	1password command line [client]  (`op`)
-	Python 3
-	tar, gpg (for encryption) binaries

First login with `op` client. It exports session key to environment variables.
More details [signin](https://developer.1password.com/docs/cli/sign-in-manually).
	
	$ eval $(op account add --signin --shorthand="value" --address my.1password.com)
	$ op account list
	$ eval $(op signin)

Next run script

	$ python3 1export.py <file-name>

[1password]: http://1password.com/
[client]: https://1password.com/downloads/command-line/
[signin]: https://support.1password.com/command-line-getting-started/#get-started-with-the-command-line-tool

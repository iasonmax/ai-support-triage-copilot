# Outlook Not Syncing Email

## Problem
Outlook not receiving new emails or syncing with server.

## Solution
1. Close Outlook completely
2. Open File Explorer > type %appdata%\Microsoft\Outlook in address bar
3. Look for ".ost" files (Outlook cache files)
4. Delete all .ost files
5. Reopen Outlook (it will rebuild cache automatically)
6. Wait 5 minutes for sync to complete

## If Still Not Working
1. Remove email account: File > Account Settings > Accounts
2. Click account, then "Remove"
3. Restart Outlook
4. Add account back: File > Add Account
5. Enter email and password

## Prevention
Keep Outlook updated to latest version.

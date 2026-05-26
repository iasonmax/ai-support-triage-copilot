# VPN Connection Failed

## Problem
Cannot connect to company VPN.

## Solution
1. Open VPN client (Cisco AnyConnect, GlobalProtect, etc.)
2. Clear VPN cache: File > Clear Cache
3. Close VPN client completely
4. Restart computer
5. Open VPN client again and login with credentials
6. If still fails, check if firewall is blocking VPN port

## If Firewall Is Issue
1. Open Windows Defender Firewall
2. Click "Allow app through firewall"
3. Find VPN client, check both "Private" and "Public" boxes

## Prevention
Keep VPN client software updated. Do not use public WiFi without VPN.

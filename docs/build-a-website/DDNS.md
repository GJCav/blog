---
tags:
    - Website
    - Network
    - Cloudflare
    - DNS
    - DDNS
---

# DDNS

## Basic

If you are hosting a website on your PC and suffering from dynamic IP, consider DDNS as the best way to ease the pain.

DDNS, dynamic-DNS, is a trivial upgrade of DNS. Normal DNS records are static and are cached in different DNS server. But when the server IP addresses change with time, DNS records should be updated, which is the reason to call it "dynamic DNS".

To enable DDNS, there are 2 methods.

1. Buy DDNS from DDNS provider.

2. Buy a domain, manage the domain with a DNS provider, such as Cloudflare, and use API to update the DNS records.

I recommend the second method and provide a simple python script to implement DDNS update.


## Cloudflare DDNS

Cloudflare does not officially offer DDNS, but its DNS records can be updated every minute, which is more than sufficient for DDNS. 

This python script, [cloudflare_ddns.py](https://gist.github.com/GJCav/9f5fca89ad6e5d7785ca9c7e1469a96c), detects the current IP address and invokes CF API to update the DNS record. Both IPv4 and IPv6 are supported.

**Configure the script**

Install `requests`:

``` bash
pip3 install requests
```

Change the following lines:

``` python 
ZONE_ID = "an ID associated with your domain"
TOKEN   = "a token to authenticate the request"
DNS_NAME = "name.ddns.domain.top"  # domain for your server
```

Select a proper function to get the IP according to your net environment.

In my practice, I recommend `get_inet_xxxx` series. For example, this is the source code for `get_inet_ip`

``` python 
def get_inet_ip():
    with S.socket(S.AF_INET, S.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

```

This function uses a trick to get the right IP address connected to the Internet, as a computer may have multiple NICs and a NIC may have multiple IPs. 

**Run the script**

``` bash 
python3 cloudflare_ddns.py
```

Here is an example output:

``` txt
2023-07-19 15:29:36
update records: A hpv4.ddns.gjm20.top 59.xx.29.xxx
```

**Run the script periodically**

Finally, setup a crontab or systemd service to run the script periodically. 

Here is my crontab example:

``` cron
*/5 * * * * /path/to/cloudflare_ddns.py >> /var/log/cfddns.log 2>&1
```

If everything works fine, your server now enjoys DDNS.


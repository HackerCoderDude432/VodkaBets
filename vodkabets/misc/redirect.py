from flask import redirect
from urllib.parse import urlparse, urljoin

def safe_redirect(host, target, fallback="/"):
    # Check to see if the url is a endpoint in this site,
    # and if it isn't redirect to the fallback
    if target:
        host_url = urlparse(host)
        target_url = urlparse(urljoin(host, target))
        if target_url.scheme is "http" or "https" and host_url.netloc == target_url.netloc:
            return redirect(target)    
    return redirect(fallback)

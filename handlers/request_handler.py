import aiohttp
from curl_cffi import requests
from time import sleep

# Helper function to handle HTTP requests for both aiohttp and tls_client
async def make_request(session, method, url, headers, payload=None, proxy=None):
    methods = {
        "POST": session.post,
        "GET": session.get,
        "PATCH": session.patch,
        "PUT": session.put,
        "DELETE": session.delete,
        "OPTIONS": session.options,
        "HEAD": session.head
    }

    if method not in methods:
        return f"[bold red]Unsupported HTTP method:[/bold red] {method}", 405

    try:
        async with methods[method](url, json=payload, headers=headers, proxy=proxy) as response:
            return await response.text(), response.status
    except Exception as e:
        return f"[bold red]Error fetching {url} with {session.__class__.__name__}:[/bold red] {e}", 500


# aiohttp request handler
async def request_aiohttp(url, method, headers, payload=None, proxy=None):
    async with aiohttp.ClientSession() as session:
        return await make_request(session, method, url, headers, payload, proxy)


# tls request handler
def request_tls(url, method, headers, payload=None, proxy=None):
    session = requests.Session()

    methods = {
        "POST": session.post,
        "GET": session.get,
        "PATCH": session.patch,
        "PUT": session.put,
        "DELETE": session.delete,
        "OPTIONS": session.options,
        "HEAD": session.head
    }

    if method not in methods:
        return f"[bold red]Unsupported HTTP method:[/bold red] {method}", 405

    try:
        res = methods[method](url, json=payload, headers=headers, proxy=proxy, impersonate="chrome")
        return res.text, res.status_code
    except Exception as e:
        return f"[bold red]Error fetching {url} with tls_client:[/bold red] {e}", 500


method_map = {
    "POST": request_aiohttp,
    "GET": request_aiohttp,
    "PATCH": request_aiohttp,
    "PUT": request_aiohttp,
    "DELETE": request_aiohttp,
    "OPTIONS": request_aiohttp,
    "HEAD": request_aiohttp,
}

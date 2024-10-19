import json
import argparse
import asyncio
import re
from time import sleep
from rich.console import Console
from rich.panel import Panel
from handlers.request_handler import request_tls, method_map
from handlers.file_handler import read_token, read_urls, save_results
from utils.anonymizer import anonymizer

console = Console()

def replace_placeholders(text, params):
    if isinstance(text, str):
        return re.sub(r"\{(\w+)\}", lambda m: params.get(m.group(1), m.group(0)), text)  # Replaces any {placeholder}
    elif isinstance(text, dict):
        return {key: replace_placeholders(value, params) for key, value in text.items()}
    return text

async def test_urls(showTls, showAiohttp, showFull, delay, outputFile, params, anonymize=False):
    token, include, exclude = read_token()
    if not token:
        console.print("[bold red]No token found, exiting...[/bold red]")
        return

    urls = read_urls()
    if not urls:
        console.print("[bold red]No URLs found, exiting...[/bold red]")
        return

    results = []  # To store results for output file

    if include:
        urls = [url for url in urls if any(incl in url['url'] for incl in include)]
    if exclude and exclude != "all":
        urls = [url for url in urls if not any(exc in url['url'] for exc in exclude)]

    for urlData in urls:  # Iterate through all URLs and make requests
        url = urlData['url']
        payload = urlData['payload'] if urlData['payload'] else None
        requiresToken = urlData['token'] == "true"
        method = urlData['method'].upper()

        headers = {}
        if requiresToken:
            headers['Authorization'] = f"{token}"
        proxy = None

        # Replace any placeholders in URL and payload dynamically using the params passed from CLI
        updatedUrl = replace_placeholders(url, params)
        updatedPayload = replace_placeholders(payload, params)

        aiohttpResp, aiohttpStatus = None, None
        tlsResp, tlsStatus = None, None

        # Only run aiohttp logic if the --aiohttp flag is provided
        if showAiohttp:
            aiohttpResp, aiohttpStatus = await method_map.get(method, lambda *args: (f"[bold red]Unsupported method:[/bold red]", 405))(updatedUrl, method, headers, updatedPayload, proxy)

            if aiohttpStatus == 429:
                try:
                    retryAfter = json.loads(aiohttpResp).get("retry_after", delay / 1000)
                    sleep(retryAfter)
                    aiohttpResp, aiohttpStatus = await method_map.get(method, lambda *args: (f"[bold red]Unsupported method:[/bold red]", 405))(updatedUrl, method, headers, updatedPayload, proxy)
                except json.JSONDecodeError:
                    pass

            # Anonymize aiohttp response if flag is set
            if anonymize and aiohttpResp and isinstance(aiohttpResp, str):
                try:
                    aiohttpJson = json.loads(aiohttpResp)
                    aiohttpJson = anonymizer(aiohttpJson)  # Anonymize the response
                    aiohttpResp = json.dumps(aiohttpJson)  # Convert back to string
                except json.JSONDecodeError:
                    console.print("[bold red]Failed to decode JSON for aiohttp response.[/bold red]")

            if aiohttpStatus in [200, 204] and not aiohttpResp:
                aiohttpRespDisplay = "[bold green]Success[/bold green]: No content returned [bold green](OK)[/bold green]"
            elif aiohttpResp:
                aiohttpRespDisplay = json.dumps(aiohttpResp, indent=4) if isinstance(aiohttpResp, dict) else (aiohttpResp[:100] + "..." if len(aiohttpResp) > 100 else aiohttpResp)
            else:
                aiohttpRespDisplay = "[dim]Skipped[/dim]"

        # Only run TLS logic if the --tls flag is provided
        if showTls:
            tlsResp, tlsStatus = request_tls(updatedUrl, method, headers, updatedPayload, proxy)

            if tlsStatus == 429:
                try:
                    retryAfter = json.loads(tlsResp).get("retry_after", delay / 1000)
                    sleep(retryAfter)
                    tlsResp, tlsStatus = request_tls(updatedUrl, method, headers, updatedPayload, proxy)
                except json.JSONDecodeError:
                    pass

            # Anonymize TLS response if flag is set
            if anonymize and tlsResp and isinstance(tlsResp, str):
                try:
                    tlsJson = json.loads(tlsResp)
                    tlsJson = anonymizer(tlsJson)  # Anonymize the response
                    tlsResp = json.dumps(tlsJson)  # Convert back to string
                except json.JSONDecodeError:
                    console.print("[bold red]Failed to decode JSON for TLS response.[/bold red]")

            if tlsStatus in [200, 204] and not tlsResp:
                tlsRespDisplay = "[bold green]Success[/bold green]: No content returned [bold green](OK)[/bold green]"
            elif tlsResp:
                tlsRespDisplay = json.dumps(tlsResp, indent=4) if isinstance(tlsResp, dict) else (tlsResp[:100] + "..." if len(tlsResp) > 100 else tlsResp)
            else:
                tlsRespDisplay = "[dim]Skipped[/dim]"

        if showFull:
            if showAiohttp and aiohttpResp:
                aiohttpRespDisplay = aiohttpResp
            if showTls and tlsResp:
                tlsRespDisplay = tlsResp
        else:
            if showAiohttp and aiohttpResp:
                aiohttpRespDisplay = json.dumps(aiohttpResp, indent=4) if isinstance(aiohttpResp, dict) else (aiohttpResp[:100] + "..." if len(aiohttpResp) > 100 else aiohttpResp)
            if showTls and tlsResp:
                tlsRespDisplay = json.dumps(tlsResp, indent=4) if isinstance(tlsResp, dict) else (tlsResp[:100] + "..." if len(tlsResp) > 100 else tlsResp)

        # Print URL and responses
        console.print(f"\n[bold cyan]Testing URL:[/bold cyan] [underline]{updatedUrl}[/underline]")

        if showAiohttp:
            console.print(Panel(f"[bold green]AIOHTTP Response ({aiohttpStatus}):[/bold green]\n{aiohttpRespDisplay}",
                                title=f"[bold magenta]Method: {method}[/bold magenta]", expand=False))

        if showTls:
            console.print(Panel(f"[bold yellow]TLS Client Response ({tlsStatus}):[/bold yellow]\n{tlsRespDisplay}",
                                title=f"[bold magenta]Method: {method}[/bold magenta]", expand=False))

        # Append to results
        results.append({
            "url": updatedUrl,
            "method": method,
            "aiohttp_response": aiohttpResp if showAiohttp else None,
            "tls_response": tlsResp if showTls else None
        })

        # Apply delay if needed
        if delay > 0:
            sleep(delay / 1000)  # Converts ms to seconds

    if outputFile:
        saveMessage = save_results(results, outputFile)
        console.print(f"[bold green]{saveMessage}[/bold green]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test URLs using aiohttp and tls_client")
    parser.add_argument('--tls', action='store_true', help="Test URLs with tls_client")
    parser.add_argument('--aiohttp', action='store_true', help="Test URLs with aiohttp")
    parser.add_argument('--full', action='store_true', help="Display full responses instead of truncated ones")
    parser.add_argument('--delay', type=int, default=0, help="Delay between requests in milliseconds")
    parser.add_argument('--output', type=str, help="Save the output to a file (supports .json or .txt)")
    parser.add_argument('--params', type=str, nargs='*', help="Dynamic parameters in the format key=value (e.g., --params channel_id=12345 content=dynamic_message)")
    parser.add_argument('--anonymize', action='store_true', help="Anonymize sensitive data in the output")

    args = parser.parse_args()

    # Parse the dynamic parameters into a dictionary
    params = {}
    if args.params:
        for param in args.params:
            key, value = param.split("=")
            params[key] = value

    if not args.tls and not args.aiohttp:
        console.print("[bold red]Please specify at least one testing method (--tls or --aiohttp)[/bold red]")
    else:
        # Run the tests
        asyncio.run(test_urls(args.tls, args.aiohttp, args.full, args.delay, args.output, params, args.anonymize))

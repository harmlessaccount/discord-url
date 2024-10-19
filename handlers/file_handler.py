# file_handler.py

import json
import yaml

def read_token():
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            return config.get('token'), config.get('include', []), config.get('exclude', [])
    except Exception as e:
        return None, [], []


def read_urls():
    try:
        with open('urls.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        return []


def save_results(results, output_file):
    try:
        if output_file.endswith(".json"):
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=4)
            return f"Results saved to {output_file}"
        elif output_file.endswith(".txt"):
            with open(output_file, 'w') as f:
                for result in results:
                    f.write(f"URL: {result['url']}\n")
                    f.write(f"Method: {result['method']}\n")
                    if result['aiohttp_response']:
                        f.write(f"AIOHTTP Response: {result['aiohttp_response']}\n")
                    if result['tls_response']:
                        f.write(f"TLS Client Response: {result['tls_response']}\n")
                    f.write("="*50 + "\n")
            return f"Results saved to {output_file}"
        else:
            return "Unsupported file format. Please use .json or .txt."
    except Exception as e:
        return f"Error saving results to file: {e}"
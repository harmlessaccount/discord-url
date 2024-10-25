# Discord URL

`discord-url` is a Command Line Interface (CLI) tool designed to test Discord-related URLs using two HTTP clients: `aiohttp` and `tls_client`. You can set different requests on `urls.json`. 

The CLI supports dynamic parameters, request retries, and offers options for anonymizing sensitive data within responses.

The project has the purpose of checking on updates of the Discord anti-bot  and anti-spam features. This may be useful for those who want to debug certain endpoints.

## Features

- **TLS and AIOHTTP Methods**: Test URLs using either `aiohttp` or `tls_client`.
- **Dynamic Parameters**: Replace placeholders within URLs and payloads dynamically using CLI parameters.
- **Request Delay**: Control the delay between multiple requests to avoid rate-limiting.
- **Anonymization**: Option to anonymize sensitive data in responses. This is not 100% precise, do your own diligence.
- **Results Export**: Save results to `.json` or `.txt` files.
- **Retry on 429 (Rate-Limit)**: Automatically retries when rate-limited by Discord, based on the `wait_for` response key.
- **Custom headers**: Allows you to use custom headers when making requests, which is set on `urls.json`.

## Installation

To get started, clone the repository and install the necessary dependencies:

```bash
git clone https://github.com/harmlessaccount/discord-url
cd discord-url
pip install -r requirements.txt
```
## Configuration

1. **Token Configuration**:  
   Update the `config.yaml` file with your token and any URLs you want to include or exclude from testing.

    ```yaml
    token: "YOUR_TOKEN"
    include: []
    exclude: "all"
    ```

2. **URLs**:  
   Add the URLs to be tested in the `urls.json` file. You can define the HTTP method, payload, and whether the URL requires a token.

    ```json
    [
      {
        "url": "https://discord.com/api/webhooks/{webhook_id}/{webhook_token}",
        "method": "POST",
        "token": "false",
        "payload": {
          "content": "{content}",
          "username": "Harmless"
        }
      }
    ]
    ```

## Usage

Run the tool by passing your options as arguments. Below are a few examples:

### Basic Example

```bash
python main.py --tls --params webhook_id="1234" webhook_token="token" content="Hey there!"
```

This will run all the URLs as normal, but setting those parameters will allow for you to send a request to the webhook credentials, removing the need of hard-coding or using configuration files.

```bash
python main.py --tls --aiohttp --full --delay 1000 --anonymize
```

This will run through all URLs as normal, but using both HTTP clients, outputting the full response to the console. If `--full` is not set, the output will be truncated at 100 characters. The delay is in miliseconds, on this example, it will wait one second between requests.

## CLI Options

- `--tls`: Test URLs using the `tls_client` HTTP client.
- `--aiohttp`: Test URLs using the `aiohttp` HTTP client.
- `--full`: Show complete responses instead of truncated ones.
- `--delay {milliseconds}`: Set a delay between requests in milliseconds (e.g., `--delay 200` for 200ms).
- `--output {file_path}`: Save results to a specified file (.json or .txt) (e.g., `--output results.json`).
- `--params`: Pass dynamic parameters in the format `key=value` (e.g., `channel_id=12345`).
- `--anonymize`: Anonymize sensitive data in the responses.

### Anonymization

When the `--anonymize` option is enabled, the following data fields will be modified to protect sensitive information:

- **ID**: Anonymized with random digits of the same length.
- **Discriminator**: Anonymized with random digits of the same length.
- **Username** and **Global Name**: Replaced with a random string of letters.
- **Email**: Anonymized to a format like `randomstring@harmless.com`.
- **Guild names**: Replaced with a fixed string, "Harmless Guild".
- **Icon blobs** and **Banner blobs**: Anonymized with a random 32-character hex string.

Use of this option is only recommend when opening an issue or sharing screenshots with others. The `--anonymize` option does not hide every potentially identifiable parameter, **so please use it with caution**.

## Contribute

You may contribute by adding more URLs to `urls.json`, the format is as follows:

```json
{
    "url": "https://discord.com/api/random_url",
    "method": "POST",
    "token": "false",
    "payload": {
        "content": "{content}",
        "username": "Harmless"
    },
    "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}
}
```

If your request requires an user token, set `token` to `true`. You can change the method to anything, make sure to type it correctly. If your request requires no payload, leave it as a empty string:

```json
{
    "url": "https://discord.com/api/random_url",
    "method": "GET",
    "token": "false",
    "payload": "",
}
```

Contributions are very easy to do and are always appreciated. If you can, contribute.

## Considerations

This project was made in a rush and will probably not fit for all use-cases. I'll eventually add more features to make the project usable for more people. If you feel like something is missing, feel free to make open an issue.

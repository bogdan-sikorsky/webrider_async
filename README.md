# WebRiderAsync

WebRiderAsync is an asynchronous web scraping utility designed to efficiently handle large volumes of web requests. It leverages Python's aiohttp for asynchronous HTTP requests, making it capable of achieving high performance by processing multiple requests in parallel.

## Features
- Asynchronous requests for high performance
- Customizable user agents and proxies
- Retry policy for handling failed requests
- Logging support with customizable log levels and file output
- Configurable concurrency and delay settings
- Statistics tracking and reporting

## Installation

To use WebRiderAsync, you need to have Python 3.8 or higher installed. Install the required packages using pip:

```shell
pip install webryder_async
```

## Usage

Here's a basic example of how to use the WebRiderAsync class:

### Initialization

```python
from webrider_async import WebRiderAsync

# Create an instance of WebRiderAsync
webrider = WebRiderAsync(
    log_level='debug',                  # Logging level: 'debug', 'info', 'warning', 'error'
    file_output=True,                   # Save logs to a file
    random_user_agents=True,            # Use random user agents
    concurrent_requests=20,             # Number of concurrent requests
    max_retries=3,                       # Maximum number of retries per request
    delay_before_retry=2                # Delay before retrying a request (in seconds)
)
```

### Making Requests

```python
urls = ['https://example.com/page1', 'https://example.com/page2']

# Perform requests
responses = webrider.request(urls)

# Process responses
for response in responses:
    print(response.url, response.status_code)
    print(response.html[:100])  # Print the first 100 characters of the HTML
```

### Updating Settings

```python
webrider.update_settings(
    log_level='info',
    file_output=False,
    random_user_agents=False,
    custom_user_agent='MyCustomUserAgent',
    concurrent_requests=10,
    max_retries=5
)
```

> Full working example of usage you can check in [examples folder](https://github.com/bogdan-sikorsky/webrider_async/examples).

### Tracking Statistics

```python
# Print current statistics
webrider.stats()

# Reset statistics
webrider.reset_stats()
```

## Parameters

## `__init__` Parameters

- log_level: Specifies the log level. Options: 'debug', 'info', 'warning', 'error'.
- file_output: If True, logs will be saved to a file.
- random_user_agents: If True, a random user agent will be used for each request.
- custom_user_agent: A custom user agent string.
- custom_headers: A dictionary of custom headers.
- custom_proxies: A list or single string of proxies to be used.
- concurrent_requests: Number of concurrent requests allowed.
- delay_per_chunk: Delay between chunks of requests (in seconds).
- max_retries: Maximum number of retries per request.
- delay_before_retry: Delay before retrying a failed request (in seconds).
- max_wait_for_resp: Maximum time to wait for a response (in seconds).

## Methods

- `request(urls, headers=None, user_agent=None, proxies=None)`: Perform asynchronous requests to the specified URLs.
- `update_settings(...)`: Update settings for the WebRiderAsync instance.
- `stats()`: Print current scraping statistics.
- `reset_stats()`: Reset statistics to zero.
- `chunkify(initial_list, chunk_size=10)`: Split a list into chunks of the specified size.

## Logging

Logging can be configured to print to the console or save to a file. The log file is saved in a logs directory under the current working directory, with a timestamp in the filename.

## Error Handling

If a request fails after the maximum number of retries, it is logged as a failure. Errors during request processing are logged with traceback information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

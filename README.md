# WebRiderAsync

WebRiderAsync is an asynchronous utility designed for very simple and highly tunable handling of large volumes of web requests. 

It leverages Python's `aiohttp` for asynchronous HTTP requests, making it capable of achieving high performance by processing multiple requests in parallel. This utility could be useful both for working with APIs and web scraping.

### Key Features:

- **Simple Setup**: Unlike complex frameworks like Scrapy, WebRiderAsync requires no in-depth knowledge of asynchronous programming or framework-specific structures. All settings are handled via class initialization, offering flexibility with minimal overhead.

- **Asynchronous by Design**: Designed to process multiple requests in parallel, WebRiderAsync leverages Python’s `asyncio` and `aiohttp` to maximize performance without requiring users to write asynchronous code themselves.

- **User-Friendly**: There’s no need to understand `asyncio` or `aiohttp`. Simply pass a list of URLs to the `request()` function, and WebRiderAsync will handle the rest.

### Why WebRiderAsync?

Compared to frameworks like Scrapy, WebRiderAsync is straightforward and ideal for users who want the power of asynchronous requests without the need for a deep dive into project structures or complex configurations. It’s perfect for both beginners and advanced users who need rapid, customizable scraping or API requests.

### Capabilities
- Asynchronous requests for high performance
- Customizable user agents and proxies
- Retry policy for handling failed requests
- Logging support with customizable log levels and file output
- Configurable concurrency and delay settings
- Statistics tracking and reporting

## Installation

To use WebRiderAsync, you need to have Python 3.8 or higher installed. Install the required packages using `pip`:

```shell
pip install webrider-async
```

Check out the [PyPI page](https://pypi.org/project/webrider-async/) for the latest version and updates.

## Usage

> Full working example of usage you can find here [examples folder](https://github.com/bogdan-sikorsky/webrider_async/tree/main/examples).

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
    max_retries=3,                      # Maximum number of retries per request
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

> Full working example of usage you can find here [examples folder](https://github.com/bogdan-sikorsky/webrider_async/tree/main/examples).

### Tracking Statistics

```python
# Print current statistics
webrider.stats()

# Reset statistics
webrider.reset_stats()
```

## Best practices

### General scraping advice

It is almost impossible nowadays to find websites that do not require a `user-agent` to respond. Don't forget to specify your own using `custom_user_agent` or just simply set `random_user_agents=True`.

You can specify `custom_headers` if the request requires that.

Use proxies if the website blocking you.

Remember that WebRiderAsync does not handle JavaScript.

### Speed and parallel requests

Nothing holds you from sending into the `request()` function list with 1000 URLs but unlikely that you will be satisfied with the result.

The problem with the example above is that all 1000 responses will be accumulating in the computer memory which will overload it at some point.

Use the `chunkify()` function to split your list of URLs into chunks of reasonable size and feed to `request()` those chunks.

**Efficient, safe and predictable usage looks like this:**

```python
my_urls = ['https://example.com/page1', 'https://example.com/page2', ...]
my_urls_chunks = webrider.chunkify(my_urls, 10)  # integer means number of urls in a single chunk
for urls_chunk in pagination_pages_chunks:
    responses = webrider.request(urls_chunk)  # Parsing chunks of 10 pages simultaneously
        for response in responses:
            parse_response(response.html)
```

You can set your own concurrent requests and delay per chunk policies but be aware that out-of-the-box settings might have weird behavior. To maximise efficiency each website requires tuning scraper according to its capabilities. 

### User-agents, headers and proxies

WebRider always keeps user-agents, headers and proxy policies in memory that you specified during initialization unless you used the `update_settings()` method.

Meanwhile, you might need to specify another header for specific chunks of requests and you can do it via the `request()` method. 

It will not overwrite settings passed to the class on initialization but the `request()` method will prioritise settings passed in the method over passed in class. 

## Parameters

### `__init__` Parameters

- `log_level`: Specifies the log level. Options: 'debug', 'info', 'warning', 'error'.
- `file_output`: If True, logs will be saved to a file.
- `random_user_agents`: If True, a random user agent will be used for each request.
- `custom_user_agent`: A custom user agent string.
- `custom_headers`: A dictionary of custom headers.
- `custom_proxies`: A list or single string of proxies to be used.
- `concurrent_requests`: Number of concurrent requests allowed.
- `delay_per_chunk`: Delay between chunks of requests (in seconds).
- `max_retries`: Maximum number of retries per request.
- `delay_before_retry`: Delay before retrying a failed request (in seconds).
- `max_wait_for_resp`: Maximum time to wait for a response (in seconds).

### Methods

- `request(urls, headers=None, user_agent=None, proxies=None)`: Perform asynchronous requests to the specified URLs.
- `update_settings()`: Update settings for the WebRiderAsync instance.
- `stats()`: Print current scraping statistics.
- `reset_stats()`: Reset statistics to zero.
- `chunkify(initial_list, chunk_size=10)`: Split a list into chunks of the specified size.

## Logging

Logging can be configured to print to the console or save to a file. The log file is saved in a logs directory under the current working directory, with a timestamp in the filename.

## Error Handling

If a request fails after the maximum number of retries, it is logged as a failure. Errors during request processing are logged with traceback information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Thanks!**

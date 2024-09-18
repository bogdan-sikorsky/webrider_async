import ssl
import gzip
import random

import brotli
import asyncio
import aiohttp
import certifi
import datetime
import traceback

from io import BytesIO
from pathlib import Path
from select import select
from typing import Union, List

from webrider_async.logger import get_logger


class Response:
    def __init__(self, html: str = None, url: str = None, status_code: int = None):
        self.html = html
        self.url = url
        self.status_code = status_code


class WebRiderAsync:
    """
    Description
    -----------
    This class is for generating asynchronous request that works many times faster than regular requests.

    You can use start_async_requests() if you want to use this class from regular synchronous Python functions.

    Use make_requests_async() if you're making requests from asynchronous function of your scraper.

    You can specify usage of random user agents and proxies. Also, you can specify retry policy, number of concurrent
    requests and so on.

    Max speed noticed while testing this class was 20 received responses per second for 1000 requests.
    """

    def __init__(
            self,
            log_level: str = 'debug',
            file_output: bool = False,
            log_dir: str = None,

            random_user_agents: bool = False,
            custom_user_agent: str = None,
            custom_headers: dict = None,
            custom_proxies: Union[List[str], str] = None,

            concurrent_requests: int = 20,
            delay_per_chunk: int = 0,

            max_retries: int = 2,
            delay_before_retry: int = 1,

            max_wait_for_resp: int = 15
    ):
        """

        :param log_level:
            Switch between log levels. Accepted values: 'debug', 'info', 'warning', 'error'.

        :param file_output:
            Saves all log to file

        :param log_dir:
            Custom path to log output file

        :param random_user_agents:
            Enabling using random user agents for each request. Uses single ua if False.

        :param custom_user_agent:
            Custom user agent

        :param custom_headers:
            Custom request headers

        :param custom_proxies:
            Enabling using proxies for each request.

        :param concurrent_requests:
            Number of requests that Manager sends in parallel.

        :param delay_per_chunk:
            Delay between sending one chunk of request and another one (sec).

        :param max_retries:
            Number of retries if status code is not 200 on the first try.

        :param delay_before_retry:
            Delay before retry of single request if status code wasn't 200 on previous attempt (sec).

        :param max_wait_for_resp:
            Maximum time to wait for response (sec). Sometimes one single response can provide a couple of minutes lag
            for whole chunk. If max_wait_for_resp time expired than class will make retry attempt according to
            max_retries policy.
        """

        # ---LOGGER---
        self.logger = get_logger(log_level, file_output, log_dir)
        self.logger.info(f'WEBRIDER_ASYNC: Launching Async Requests Manager')

        # ---BASIC SETTINGS---
        self.random_user_agents = random_user_agents
        self.custom_user_agent = custom_user_agent
        self.custom_headers = custom_headers
        self.custom_proxies = custom_proxies

        # ---NUMERIC BASE SETTINGS---
        self.concurrent_requests = concurrent_requests
        self.delay_per_chunk = delay_per_chunk
        self.max_retries = max_retries
        self.delay_before_retry = delay_before_retry
        self.max_wait_for_resp = max_wait_for_resp

        # ---EXTRACTING USER AGENTS POOL---
        path = Path(__file__).parents[0].joinpath()
        file_name = f'user_agents_pool.txt'
        file = Path(path).joinpath(file_name)
        with open(file) as data_file:
            user_agents_pool = data_file.readlines()
        user_agents_pool = [item.strip() for item in user_agents_pool]
        self.user_agents_pool = user_agents_pool

        # ---SSL PROBLEM SOLVER---
        self.sslcontext = ssl.create_default_context(cafile=certifi.where())  # Prevents random SSL errors

        # ---STATS---
        self.requests_amount = 0
        self.requests_good = 0
        self.requests_bad_status = 0  # Status code different from 200
        self.requests_unsuccessful = 0  # Possibly error while processing code
        self.requests_failed = 0  # Wasn't able to achieve result with all retries attempts
        self.time_start = datetime.datetime.now()

    def request(self,
                urls: Union[List[str], str],
                headers: dict = None,
                user_agent: str = None,
                proxies: Union[List[str], str] = None
    ):
        """
        This starts process of making asyncrequests

        :param urls: URLs to make request
        :param headers: custom headers
        :param user_agent: custom user agent
        :param proxies: custom proxies
        :return: responses
        """

        result = asyncio.run(self.create_tasks(urls, headers, user_agent, proxies))
        return result

    async def create_tasks(
            self,
            urls: Union[List[str], str],
            headers: dict,
            user_agent: str = None,
            proxies: Union[List[str], str] = None
    ):
        """
        This function creates async tasks

        :param urls: URLs to make request
        :param headers: custom headers
        :param user_agent: custom user agent
        :param proxies: custom proxies
        :return: responses
        """

        if isinstance(urls, str):
            urls = [urls]

        tasks = []

        # Create an aiohttp session with limited concurrency
        connector = aiohttp.TCPConnector(limit=self.concurrent_requests, verify_ssl=False)
        async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:

            for index, url in enumerate(urls):
                tasks.append(self.get_response(session, url, headers, user_agent, proxies))

                # Add a delay between chunks of requests
                if (index + 1) % self.concurrent_requests == 0:
                    await asyncio.sleep(self.delay_per_chunk)

            # Await all tasks and filter out None responses
            result = await asyncio.gather(*tasks)

        # Return responses
        return result


    async def get_response(self, session, url, headers: dict, user_agent: str = None, proxies: str = None):
        """
        This function makes requests and gets responses

        :param session: Aiohttp session object
        :param url: URL to make request
        :param headers: custom headers
        :param user_agent: custom user agent
        :param proxies: custom proxies
        :return: dict: {'response': response or None, 'url': request url, 'status_code': int}
        """

        timeout = aiohttp.ClientTimeout(total=self.max_wait_for_resp)

        request_attempt = 1
        result_exists = False
        response_404 = False
        while request_attempt <= self.max_retries and result_exists is False and response_404 is False:
            if request_attempt > 1:
                await asyncio.sleep(self.delay_before_retry)

            headers = self.cook_headers(headers, user_agent)
            proxy = self.cook_proxies(proxies)

            try:
                self.requests_amount += 1
                self.logger.debug(
                    f'WEBRIDER_ASYNC: Making request to the webpage: {url} - Attempt #{request_attempt}'
                )
                async with session.get(
                        url, ssl=False, proxy=proxy, headers=headers, timeout=timeout
                ) as response:
                    if response.status == 404:
                        self.logger.warning(
                            f"""WEBRIDER_ASYNC: Wrong status code [{response.status}] for: {url} - Attempt #{request_attempt}"""
                        )
                        self.requests_bad_status += 1
                        request_attempt += 1
                        response_404 = True
                        return Response(html=None, url=url, status_code=response.status)
                    elif response.status == 200 and response.content_type == 'application/x-gzip':
                        result = await response.read()
                        result = gzip.GzipFile(fileobj=BytesIO(result)).read().decode()
                        self.logger.info(
                            f"""WEBRIDER_ASYNC: Response status code [{response.status}] for: {url} - Attempt #{request_attempt}"""
                        )
                        self.requests_good += 1
                        return Response(html=result, url=url, status_code=response.status)
                    elif response.status == 200:
                        result = await response.content.read()
                        result = result.decode('utf-8', 'ignore')
                        self.logger.info(
                            f"""WEBRIDER_ASYNC: Response status code [{response.status}] for: {url} - Attempt #{request_attempt}"""
                        )
                        self.requests_good += 1
                        return Response(html=result, url=url, status_code=response.status)
                    else:
                        result_exists = False
                        self.logger.warning(
                            f"""WEBRIDER_ASYNC: Status code is [{response.status}]. Request unsuccessful for: {url} - Attempt #{request_attempt}"""
                        )
                        request_attempt += 1
                        self.requests_bad_status += 1
            except Exception as error:
                result_exists = False
                self.requests_unsuccessful += 1
                self.logger.error(
                    f"""WEBRIDER_ASYNC: Faced error while executing request. Request unsuccessful for: {url} - Attempt #{request_attempt}"""
                )
                self.logger.error(error, exc_info=True)
                request_attempt += 1

        self.requests_failed += 1
        self.logger.error(
            f"WEBRIDER_ASYNC: Failed to extract data from: {url}. Number of attempts used is {request_attempt}"
        )
        return Response(html=None, url=url)


    def cook_headers(self, headers_new: dict = None, user_agent_new: str = None):
        """
        Description
        -----------
        This function compiles headers before sending request.

        Headers and user agents passed to self.request() function
        have priority over passed to the class at initialization.

        :param headers_new: dict with headers.
        :param user_agent_new: string with user-agent
        :return: dict with headers
        """
        headers = {'User-Agent': None}

        if self.random_user_agents:
            headers = {'User-Agent': random.choice(self.user_agents_pool)}

        if self.custom_user_agent:
            headers = {'User-Agent': self.custom_user_agent}

        if self.custom_headers:
            headers = self.custom_headers

        if headers_new:
            headers = headers_new

        if user_agent_new:
            headers = {'User-Agent': user_agent_new}

        lowercase_headers = {k.lower(): v for k, v in headers.items()}
        check = lowercase_headers.get('user-agent')
        if not check:
            headers = {'User-Agent': None}

        return headers


    def cook_proxies(self, proxies: Union[List[str], str] = None):
        """
        Description
        -----------
        This function checks proxy settings
        before sending request to provide right settings.

        Proxies should be properly formated like:
            - "http://123.45.67.89:8080"
            - "http://username:password@123.45.67.89:8080"

        If there is more than 1 proxy function randomly rotate proxies.

        Proxies passed to self.request() function
        have priority over passed to the class at initialization.

        :param proxies: str or list of str with proxies

        :return: str with proxy like "http://123.45.67.89:8080"
        """
        proxy = None

        # First, check if custom proxies are provided and are a list
        if self.custom_proxies:
            if isinstance(self.custom_proxies, list):
                proxy = random.choice(self.custom_proxies)
            else:
                proxy = self.custom_proxies

        # Then check if the proxies argument is provided and override if necessary
        if proxies:
            if isinstance(proxies, list):
                proxy = random.choice(proxies)
            else:
                proxy = proxies

        return proxy


    def stats(self):
        """
        Description
        -----------
        This function prints scraping stats
        """

        execution_time = datetime.datetime.now() - self.time_start
        execution_time_seconds = execution_time.total_seconds()
        req_per_sec = self.requests_amount / execution_time_seconds

        result = {
            'total_requests_made': self.requests_amount,
            'total_good_responses': self.requests_good,
            'status_code_different_from_200': self.requests_bad_status,
            'other_errors': self.requests_unsuccessful,
            'completely_failed_to_achieve_response': self.requests_failed,
            'average_speed': f'{round(req_per_sec, 1)} requests/second'
        }

        self.logger.info(f'WEBRIDER_ASYNC: STATS')
        for key, value in result.items():
            d = {key: value}
            self.logger.info(f'WEBRIDER_ASYNC: {d}')


    def reset_stats(self):
        """
        Description
        -----------
        This function resets stats to 0 if you need to use already initialized class for another task
        """
        self.requests_amount = 0
        self.requests_bad_status = 0
        self.requests_failed = 0
        self.requests_good = 0
        self.requests_unsuccessful = 0
        self.time_start = datetime.datetime.now()

    def update_settings(
            self,
            log_level: str = 'debug',
            file_output: bool = False,
            log_dir: str = None,

            random_user_agents: bool = False,
            custom_user_agent: str = None,
            custom_headers: dict = None,
            custom_proxies: Union[List[str], str] = None,

            concurrent_requests: int = 20,
            delay_per_chunk: int = 0,

            max_retries: int = 2,
            delay_before_retry: int = 1,

            max_wait_for_resp: int = 15
    ):
        """
        Description
        -----------
        This function updates settings if you need to use already initialized class
        for another task with different settings
        """

        # ---LOGGER---
        self.logger = get_logger(log_level, file_output, log_dir)
        self.logger.info(f'WEBRIDER_ASYNC: Updating settings for Async WebRider')

        # ---BASIC SETTINGS---
        self.random_user_agents = random_user_agents
        self.custom_user_agent = custom_user_agent
        self.custom_headers = custom_headers
        self.custom_proxies = custom_proxies

        # ---NUMERIC BASE SETTINGS---
        self.concurrent_requests = concurrent_requests
        self.delay_per_chunk = delay_per_chunk
        self.max_retries = max_retries
        self.delay_before_retry = delay_before_retry
        self.max_wait_for_resp = max_wait_for_resp


    @staticmethod
    def chunkify(initial_list: list, chunk_size: int = 10):
        """
        Function that helps split big list of urls on chunks
        to feed into request() reasonable number a urls simultaneously
        :param initial_list: list of urls
        :param chunk_size: number of urls in a single chunk
        :return: chunkified list of lists
        """
        result = [initial_list[i:i + chunk_size] for i in range(0, len(initial_list), chunk_size)]
        return result

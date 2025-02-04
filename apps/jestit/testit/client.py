import requests
from objict import objict


class RestClient:
    """
    A simple REST client for making HTTP requests to a specified host.
    """

    def __init__(self, host, logger=None):
        """
        Initializes the SimpleRestClient with a host URL.

        Args:
            host (str): The base URL of the host for making requests.
        """
        self.host = host if host[-1] == "/" else f"{host}/"
        self.logger = logger

    def _make_request(self, method, path, **kwargs):
        """
        Makes an HTTP request using the specified method and path.

        Args:
            method (str): The HTTP method to use for the request (e.g., 'GET', 'POST').
            path (str): The endpoint path to append to the base host URL.
            **kwargs: Additional arguments to pass to the request (e.g., headers, params).

        Returns:
            dict: A dictionary containing the response data and status code. If an error occurs,
                  returns a dictionary with an error message instead.
        """
        url = f"{self.host}{path}"
        response = requests.request(method, url, **kwargs)
        if self.logger:
            self.logger.info("REQUEST", f"{method}:{url}")
            self.logger.info(kwargs.get("json", ""))
        try:
            data = objict.fromdict(response.json()) if response.content else None
            response_data = objict(response=data, status_code=response.status_code)
            if not response.ok:
                response_data['error_reason'] = response.reason
            if self.logger:
                self.logger.info("RESPONSE", f"{method}:{url}")
                self.logger.info(response_data)
            return response_data
        except Exception as e:
            if self.logger:
                self.logger.error("RESPONSE", f"{method}:{url}")
                self.logger.exception(str(e), response.text)
            return objict(error=str(e), text=response.text)

    def get(self, path, **kwargs):
        """
        Sends a GET request to the specified path.

        Args:
            path (str): The endpoint path to append to the base host URL.
            **kwargs: Additional arguments to pass to the request (e.g., headers, params).

        Returns:
            dict: A dictionary containing the response data and status code.
        """
        return self._make_request('GET', path, **kwargs)

    def post(self, path, json=None, **kwargs):
        """
        Sends a POST request to the specified path.

        Args:
            path (str): The endpoint path to append to the base host URL.
            json (dict, optional): The JSON data to include in the request body.
            **kwargs: Additional arguments to pass to the request (e.g., headers).

        Returns:
            dict: A dictionary containing the response data and status code.
        """
        return self._make_request('POST', path, json=json, **kwargs)

    def put(self, path, json=None, **kwargs):
        """
        Sends a PUT request to the specified path.

        Args:
            path (str): The endpoint path to append to the base host URL.
            json (dict, optional): The JSON data to include in the request body.
            **kwargs: Additional arguments to pass to the request (e.g., headers).

        Returns:
            dict: A dictionary containing the response data and status code.
        """
        return self._make_request('PUT', path, json=json, **kwargs)

    def delete(self, path, **kwargs):
        """
        Sends a DELETE request to the specified path.

        Args:
            path (str): The endpoint path to append to the base host URL.
            **kwargs: Additional arguments to pass to the request (e.g., headers).

        Returns:
            dict: A dictionary containing the response data and status code.
        """
        return self._make_request('DELETE', path, **kwargs)

import requests


class ApiRequest:
    """
    ApiRequest class
    """

    class RequestError(Exception):
        """
        RequestError class
        """

    class RequestNotFoundError(RequestError):
        """
        RequestNotFoundError class
        """

    @staticmethod
    def request_api(url: str, method="GET", kwargs={}) -> str:
        """
        Send request to url.

        Args:
            url (str): url to send request to
            method (str, optional): request method. Defaults to "GET"
            kwargs (dict, optional): request parameters. Defaults to {}

        Raises:
            RuntimeError: if request failed

        Returns:
            str: response body
        """

        try:
            res = requests.request(method, url, **kwargs)
        except Exception as e:
            raise ApiRequest.RequestError(e)

        if res.status_code == 404:
            raise ApiRequest.RequestNotFoundError(res.text)
        elif res.status_code != 200:
            raise ApiRequest.RequestError(res.text)

        return res.text

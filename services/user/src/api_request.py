import requests


def request_api(url: str, method="GET", kwargs={}) -> tuple[int, str]:
    """
    Send request to url.

    Args:
        url (str): url to send request to
        method (str, optional): request method. Defaults to "GET"
        kwargs (dict, optional): request parameters. Defaults to {}

    Raises:
        RuntimeError: if request failed

    Returns:
        tuple[int, str]: status code and response body
    """

    res = requests.request(method, url, **kwargs)

    return res.status_code, res.text

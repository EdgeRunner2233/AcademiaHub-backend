import json
import requests


def request_api(url: str, method="GET", kwargs={}) -> dict:
    """
    Send request to url.

    Args:
        url (str): url to send request to
        method (str, optional): request method. Defaults to "GET"
        kwargs (dict, optional): request parameters. Defaults to {}

    Raises:
        RuntimeError: if request failed

    Returns:
        dict: response from api
    """

    res = requests.request(method, url, **kwargs)

    if res.status_code != 200:
        raise RuntimeError("Request failed")

    return json.loads(res.text)

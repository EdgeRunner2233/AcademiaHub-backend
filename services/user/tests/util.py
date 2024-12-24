import json
from werkzeug.test import TestResponse


def check_success_field(response: TestResponse):
    assert response.status_code == 200

    payload: dict = json.loads(response.data)
    assert "success" in payload
    assert "code" in payload
    assert "message" in payload
    assert "data" in payload

    if payload["success"] == False:
        print("Error: ", payload["message"])
    assert payload["success"] == True

    return payload


def check_fail_field(response: TestResponse):
    assert response.status_code == 200

    payload: dict = json.loads(response.data)
    assert "success" in payload
    assert "code" in payload
    assert "message" in payload
    assert "data" in payload

    if payload["success"] == True:
        print("Error: ", payload["message"])
    assert payload["success"] == False

    return payload

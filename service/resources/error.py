"""Error Module"""

import traceback
import json
import jsend
import falcon

def generic_error_handler(err, resp):
    """
        handle generic errors
    """
    print("ERROR:")
    print("{0}".format(err))
    print(traceback.format_exc())
    resp.status = falcon.HTTP_500
    resp.text = json.dumps(jsend.error("{0}".format(err)))
    return resp

def http_error_handler(err, resp):
    """
        handle HTTPErrors
    """
    print("HTTPError:")
    print("{0} {1}".format(err.response.status_code, err.response.text))
    resp.status = falcon.code_to_http_status(err.response.status_code)
    resp.text = json.dumps(err.response.json())
    return resp

def value_error_handler(err, resp):
    """
        handle ValueError
    """
    print("VALUE ERROR:")
    print("{0}".format(err))
    resp.status = falcon.HTTP_400
    resp.text = json.dumps(jsend.error("{0}".format(err)))
    return resp

from typing import NamedTuple  # typed named tuple
from collections import namedtuple
import json
import random
from requests_futures.sessions import FuturesSession

def json_loads_to_named_tuple(jsonified_string: str, type_name: str):
    """Description: 
        convert `jsonified_string` into a list of named tuples
        or an named tuple having type of `type_name`
    """
    return json.loads(
        jsonified_string,
        object_hook=lambda d: namedtuple(type_name, d.keys())(*d.values()),
    )

class OTP_Params(NamedTuple):
    """
    Modifiable params: `phone`, `otp_code`
    
    Default params: `api_key`, `secret_key`, `brand_name`, `sms_type`
    """

    phone: str
    otp_code: str
    api_key: str = "FC3105030010CFA43486E8487C94BA"
    secret_key: str = "CCFE6EDD25DC8711DB78E4BFE704F0"
    brand_name: str = "BaoTriXeMay"
    # 1 means that message will be sent using a hotline number;
    # 2 means that message will be sent using brand name
    sms_type: int = 2

"""Notes
   - To convert a `named_tuple` to dictionary, do `named_tuple._asdict()`  
   - To get names of `named_tuple` fields, use `named_tuple._fields()`  
"""

def get_otp_code() -> str:
    """Get random 6-digit OTP code"""
    return "".join([random.choice("0123456789") for i in range(6)])


def send_otp_message(session: FuturesSession, phone_num: str):
    """Send an message with OTP code to user's phone number
    
    Parameters:
    - `session` (`requests_futures.sessions.FutureSession`): a `FutureSession` instance
    - `phone_num` (`str`): customer's phone number 
    
    Returns: 
    - status code (`int`),
    - otp code (`str`)
    - response body (untyped named tuple)
    """
    otp_code = get_otp_code()
    otp_params = OTP_Params(phone=phone_num, otp_code=otp_code)
    payload = {
        "Phone": otp_params.phone,
        "Content": f"Ma OTP cua ban la {otp_params.otp_code}",
        "ApiKey": otp_params.api_key,
        "SecretKey": otp_params.secret_key,
        "BrandName": otp_params.brand_name,
        "SmsType": otp_params.sms_type,
    }

    # future: concurrent.futures._base.Future
    future = session.get(
        "http://rest.esms.vn/MainService.svc/json/SendMultipleMessage_V4_get",
        params=payload,
    )
    # resp: requests.models.Response
    resp = future.result()

    # get result as an untyped named tuple
    resp_body = json_loads_to_named_tuple(resp.text, "OtpResponse")

    return resp.status_code, otp_code, resp_body

if __name__ == "__main__":
    """
    This section is for debugging purpose
    """

    session = FuturesSession()
    code, otp, data_body = send_otp_message(session, phone_num="0976162652")

    print(f"Status code: {code}, of type {type(code)}")
    print(f"OTP code is {otp}")
    print(f"Data received: of type {type(data_body)}")
    print(f"...content: {data_body}")



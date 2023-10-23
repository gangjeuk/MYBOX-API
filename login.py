import time
import requests
from bs4 import BeautifulSoup
import rsa
import uuid
from lzstring import LZString
import json

from log import set_logger
from logging import CRITICAL
from credential import Credential


_FIELD_SEPARATOR = ':'

'''
from
https://github.com/mpetazzoni/sseclient

For Server-Sent Events control.

SSE is needed for OTP service

'''
class SSEClient(object):
    """Implementation of a SSE client.
    See http://www.w3.org/TR/2009/WD-eventsource-20091029/ for the
    specification.
    """

    def __init__(self, event_source, char_enc='utf-8'):
        """Initialize the SSE client over an existing, ready to consume
        event source.
        The event source is expected to be a binary stream and have a close()
        method. That would usually be something that implements
        io.BinaryIOBase, like an httplib or urllib3 HTTPResponse object.
        """
        #self._logger = logging.getLogger(self.__class__.__module__)
        self._logger = set_logger(None)
        self._logger.debug('Initialized SSE client from event source {}'.format(event_source))
        self._event_source = event_source
        self._char_enc = char_enc

    def _read(self):
        """Read the incoming event source stream and yield event chunks.
        Unfortunately it is possible for some servers to decide to break an
        event into multiple HTTP chunks in the response. It is thus necessary
        to correctly stitch together consecutive response chunks and find the
        SSE delimiter (empty new line) to yield full, correct event chunks."""
        data = b''
        for chunk in self._event_source:
            for line in chunk.splitlines(True):
                data += line
                if data.endswith((b'\r\r', b'\n\n', b'\r\n\r\n')):
                    yield data
                    data = b''
        if data:
            yield data

    def events(self):
        for chunk in self._read():
            event = Event()
            # Split before decoding so splitlines() only uses \r and \n
            for line in chunk.splitlines():
                # Decode the line.
                line = line.decode(self._char_enc)

                # Lines starting with a separator are comments and are to be
                # ignored.
                if not line.strip() or line.startswith(_FIELD_SEPARATOR):
                    continue

                data = line.split(_FIELD_SEPARATOR, 1)
                field = data[0]

                # Ignore unknown fields.
                if field not in event.__dict__:
                    self._logger.warning('Saw invalid field %s while parsing '
                                       'Server Side Event', field)
                    continue

                if len(data) > 1:
                    # From the spec:
                    # "If value starts with a single U+0020 SPACE character,
                    # remove it from value."
                    if data[1].startswith(' '):
                        value = data[1][1:]
                    else:
                        value = data[1]
                else:
                    # If no value is present after the separator,
                    # assume an empty value.
                    value = ''

                # The data field may come over multiple lines and their values
                # are concatenated with each other.
                if field == 'data':
                    event.__dict__[field] += value + '\n'
                else:
                    event.__dict__[field] = value

            # Events with no data are not dispatched.
            if not event.data:
                continue

            # If the data field ends with a newline, remove it.
            if event.data.endswith('\n'):
                event.data = event.data[0:-1]

            # Empty event names default to 'message'
            event.event = event.event or 'message'

            # Dispatch the event
            self._logger.debug('Dispatching ...%s', event)
            yield event

    def close(self):
        """Manually close the event source stream."""
        self._event_source.close()


class Event(object):
    """Representation of an event from the event stream."""

    def __init__(self, id=None, event='message', data='', retry=None):
        self.id = id
        self.event = event
        self.data = data
        self.retry = retry

    def __str__(self):
        s = '{0} event'.format(self.event)
        if self.id is not None:
            s += ' #{0}'.format(self.id)
        if self.data != '':
            s += ', {0} byte{1}'.format(len(self.data),
                                        's' if len(self.data) else '')
        else:
            s += ', no data'
        if self.retry is not None:
            s += ', retry in {0}ms'.format(self.retry)
        return s




class NaverLogin(requests.Session):
    # Code in NaverLogin class is very NAVER specific code.
    # Which means, every url or parameters are only for NAVER login functions
    # If you find any error or malfunction, when you use this code.
    # Please check the params or url by using the Chrome Debugger and make an issue on github 

    # NOTICE codes of NaverLogin is not my original code
    
    # There are several login methods on NAVER
    # But only normal login(just type your ID/PW and push login button) and OTP method are supported 
    # QR code login or OTN(One Time Number) login methods are NOT supported

    def __init__(self, NAVER_ID, NAVER_PASS):
        super().__init__()
        self.NAVER_ID = NAVER_ID
        self.NAVER_PASS = NAVER_PASS
        self.session_key = None
        self.key_name = None
        self.dynamic_key = None
        self.public_key = None
        self.encpw = None
        self. header = {
        "User-Agent" : "Mozilla/5.0 (iPod; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 \
        (KHTML, like Gecko) CriOS/87.0.4280.163 Mobile/15E148 Safari/604.1"
        }

        self.login_url = "https://nid.naver.com/nidlogin.login"

        self._logger = set_logger(None)

    def _get_keys(self):
        url = self.login_url + "?mode=form" + "&svctype=262144"
        r = self.get(url, headers=self.header)
        bs = BeautifulSoup(r.text, "lxml")
        keys = bs.find("input", {"id": "session_keys"}).attrs.get("value")
        self.session_key, self.key_name, e, N = keys.split(",")
        self.dynamic_key = bs.find("input", {"id": "dynamicKey"}).attrs.get("value")
        self.public_key = rsa.PublicKey(int(e, 16), int(N, 16))

    def _get_encpw(self):
        t = [self.session_key, self.NAVER_ID, self.NAVER_PASS]
        result = ""
        for k in t:
            result += "".join([chr(len(k)) + k])
        encode_result = result.encode()
        self.encpw = rsa.encrypt(encode_result, self.public_key).hex()

    def _otp(self, token, key):
        otp_url = "https://nid.naver.com/push/otp?session=" + token
        r = self.get(otp_url, stream=True, headers=self.header)
        self._logger.debug(r.status_code)
        self._logger.debug(r.headers)
        self._logger.debug(r.content)

        client = SSEClient(r)
        for event in client.events():
            self._logger.debug(json.loads(event.data))

        params = {
            "mode": "otp",
            "auto": "",
            "token_push": token,
            "locale": "ko_KR",
            "key": key,
            "otp": ""
        }

        self._logger.debug("token_push: {}".format(token))
        self._logger.debug("key: {}".format(key))

        r = self.post(self.login_url, data=params, headers=self.header)
        self._logger.debug(r.status_code)
        self._logger.debug(r.headers)
        self._logger.debug(r.content)

        if r is not None:
            self._logger.critical("Login Failed: ", r)
            return False

        # if runtime
        if self._logger.level == CRITICAL:
            Credential.set_credentials(NID_AUT=r.cookies.get("NID_AUT"),
                                       NID_SES=r.cookies.get("NID_SES"),
                                       NID_JKL=r.cookies.get("NID_JKL"))
        # else if you debugging the module
        else:
            with open('auth.json', 'r') as f:
                AUTH = json.load(f)
                AUTH["NID_AUT"] = r.cookies.get("NID_AUT")
                AUTH["NID_SES"] = r.cookies.get("NID_SES")
                AUTH["NID_JKL"] = r.cookies.get("NID_JKL")
                
            with open('auth.json', 'w') as f:
                f.write(json.dumps(AUTH))

        return True

    def login(self):
        self._get_keys()
        self._get_encpw()
        
        bvsd_uuid = str(uuid.uuid4())
        encData = str({
            "a": f"{bvsd_uuid}-4",
            "b": "1.3.4",
            "d": [{
                    "i": "id",
                    "b": {
                        "a": ["0", self.NAVER_ID]
                    },
                    "d": self.NAVER_ID,
                    "e": "false",
                    "f": "false"
                },
                {
                    "i": self.NAVER_PASS,
                    "e": "true",
                    "f": "false"
                }],
            "h": "1f",
            "i":{"a": "Mozilla/5.0"}
        })

        bvsd = str({
            "uuid": bvsd_uuid,
            "encData": LZString.compressToEncodedURIComponent(encData.replace("'", '"'))
        })

        params = {
            "dynamicKey" : self.dynamic_key,
            "encpw" : self.encpw,
            "enctp" : "1",
            "svctype" : "1",
            "smart_LEVEL" : "-1",
            "bvsd" : bvsd.replace("'", '"'),
            "encnm" : self.key_name,
            "locale" : "ko_KR",
            "url" : "https://www.naver.com",
        }
        self._logger.debug("Sending passwd and ID to server")
        self._logger.debug(params)

        r = self.post(self.login_url + "?mode=form", data=params, headers=self.header)

        # Found the secret key in HTML 
        if r.text.find("location") >= 0:
            # if runtime
            if self._logger.level == CRITICAL:
                Credential.set_credentials(NID_AUT=r.cookies.get("NID_AUT"),
                                        NID_SES=r.cookies.get("NID_SES"),
                                        NID_JKL=r.cookies.get("NID_JKL"))
            # else when debugging the module
            else:
                with open('auth.json', 'r') as f:
                    AUTH = json.load(f)
                    AUTH["NID_AUT"] = r.cookies.get("NID_AUT")
                    AUTH["NID_SES"] = r.cookies.get("NID_SES")
                    AUTH["NID_JKL"] = r.cookies.get("NID_JKL")
                    
                with open('auth.json', 'w') as f:
                    f.write(json.dumps(AUTH))
            return True
        
        # Found the otp keyword --> you have to operate OTP procedure
        elif r.text.find('id="otp"') >= 0:
            bs = BeautifulSoup(r.text, "lxml")
            token = bs.find("input", {"id": "token_push"}).attrs.get("value")
            key = bs.find("input", {"id": "key"}).attrs.get("value")
            return self._otp(token, key)
        
        # Any other Login method is not supported
        # ex) QR code, OTN(One Time Number)
        else:
            self._logger.warning("Capcha is not implemented Yet!")
            return False

if __name__ == "__main__":

    # Code for testing login
    # if you run this module, then the test code will be operated

    with open('./login.json', 'r') as f:
        LOGIN = json.load(f)

    naver = NaverLogin(LOGIN["NAVER_ID"], LOGIN["NAVER_PASS"])
    if naver.login():
        naver._logger.debug("로그인 성공")
    else:
        naver._logger.debug("로그인 실패")

    
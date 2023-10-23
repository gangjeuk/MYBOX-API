from log import set_logger

# Credential class
# Singletone pattern

class Credential(object):
    __shared_state = {'NID_JKL': '', 'NID_AUT': '', 'NID_SES': ''}
    __logger = set_logger(None)
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass
    
    @staticmethod
    def set_credentials(NID_JKL, NID_AUT, NID_SES):
        Credential.__logger.info("Credential Set")
        Credential.__logger.info("Before Set", Credential.__shared_state)
        Credential.__logger.info("After Set", Credential.__shared_state)
        
        Credential.__shared_state['NID_JKL'] = NID_JKL
        Credential.__shared_state['NID_AUT'] = NID_AUT
        Credential.__shared_state['NID_SES'] = NID_SES

    @staticmethod
    def get_credentials():
        if Credential.__shared_state.items == ['', '', '']:
            Credential.__logger.error("No Items in Credential")

        return Credential.__shared_state

        
import os
import requests
import json
from typing import Union, Literal, Tuple
from urllib import parse

import time
from datetime import datetime

import deco 
from log import set_logger
from logging import CRITICAL
from credential import Credential


'''
This module is basic MYBOX api implementation.

You can find many functions in this module, but most of them are for API control

For example, the function 'do_zip', 'do_unzip' is literally zipping the file in MYBOX.

So the functions that something useful are not in this file;; 

If you want to know the usage of these functions, PLEASE CHECK the test.py file
'''

 
'''
The comments on functions are describing 
- the URL of API
- API method (POST, GET, etc...)
- Simple explanation 
- Structure of return value  
'''


class mybox():

    cookies = {
        #'NNB': 'MRM4YDPHX4LWI',
        #'ASID': 'a3987f4800000186fe157a2400000060',
        #'nx_ssl': '2',
        #'nid_inf': '-1146551022',
        #'NID_AUT': auth['NID_AUT'] ,
        #'NID_JKL': '',
        #'page_uid': 'ib8SllprvToss4tLX8wssssstmh-156294',
        #'NID_SES': auth['NID_SES'] ,
    }

    headers = {
        'authority': 'api.mybox.naver.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ko,en;q=0.9,en-US;q=0.8',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://mybox.naver.com',
        'referer': 'https://mybox.naver.com/',
        'sec-ch-ua': '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50',
    }

    def __init__(self, save_path: str = os.path.curdir):

        self._logger = set_logger(None)
        self._save_path = save_path
        # if it is runtime use Credential class
        if self._logger.level == CRITICAL:
            self.set_cookies(Credential.get_credentials())
        # else use auth.json which have cookies
        else:
            with open('./auth.json') as f:
                auth = json.load(f)
                self.set_cookies(auth)

    def set_save_path(self, path: str):
        if os.path.exists(path):
            self._logger.debug("path chaged to: " + path)
            self._save_path = path
        else:
            self._logger.error("Invalid path")
            

    def set_cookies(self, cookies: dict):
        self.cookies['NID_AUT'] = cookies['NID_AUT']
        self.cookies['NID_SES'] = cookies['NID_SES']


    def get(self, *args, **kargs):
        return requests.get(timeout=5000, cookies= self.cookies, headers= self.headers, *args, **kargs)

    def post(self, *args, **kargs):
        return requests.post(timeout=5000, cookies= self.cookies, headers= self.headers, *args, **kargs)
    

    def get_recent_list(self, startNum=0, pagingRow=200, sort: Literal['create', 'access'] = 'access', order: Literal['desc', 'asc'] = 'desc', recentType: Literal['update', 'access'] = 'access'):
        """
        # https://api.mybox.naver.com/service/file/search/recent
        # POST
        # get list
        # you can get
        # list{
        #    0:{
        #       resourceKey: str 
        #       access, update, createDate: int
        #       resourcePath: str
        #       resourceNo: int
        #       updateUser: str
        #       updateUserNick: str
        #       resourceType: str       -> hint for searching directory. "version" | 
        #       resourceSize: int
        #       childFolderCount: int
        #       folderType: str
        #       imageType: str
        #       passwordLockStatus: str 
        #       memberShare: ?
        #       ...
        # ...
        """

        """
        # fileOption:
        #    all: every data in users MYBOX
        """

        
    
        query = {'NDriveSvcType': 'NHN/ND-WEB Ver',
                 'startNum': startNum,
                 'pagingRow': pagingRow,
                 'sort': sort,
                 'order': order,
                 'recentType': recentType,
                 'startDate': parse.quote(time.strftime('%Y-%m-%dT%X.053Z', time.localtime(time.time()-1209600 + 1000))), # 1209600 = 2 weeks
                 'endDate': parse.quote(time.strftime('%Y-%m-%dT%X.053Z', time.localtime(time.time() + 1000))), 
                 'fileOption': 'all',
                 'resourceOption': 'file'}
        
        return requests.post('https://api.mybox.naver.com/service/file/search/recent',data=query, cookies=self.cookies, headers=self.headers)



    def get_list(self, resourceKey: str = 'root', fileOption: Literal['all', 'folder', None] = None, resourceOption: Literal['photo', None] = None, startNum=0, pagingRow=200, optFields=None, sort: Literal['create', 'name'] = 'create', order: Literal['desc', 'asc'] = 'desc'):
        """
        # https://api.mybox.naver.com/service/file/list
        # POST
        # get list
        # you can get
        # list{
        #    0:{
        #       resourceKey: str 
        #       access, update, createDate: int
        #       resourcePath: str
        #       resourceNo: int
        #       updateUser: str
        #       updateUserNick: str
        #       resourceType: str       -> hint for searching directory. "version" | 
        #       resourceSize: int
        #       childFolderCount: int
        #       folderType: str
        #       imageType: str
        #       passwordLockStatus: str 
        #       memberShare: ?
        #       ...
        # ...
        """

        """
        # fileOption:
        #    all: every data in users MYBOX
        """
    
        if (fileOption is None and resourceOption is None) or (fileOption is not None and resourceOption is not None):
            self._logger.warning("Only one field is available!!!. fileOption or resourceOption")

        query = {'NDriveSvcType': 'NHN/ND-WEB Ver',
                 'resourceKey': resourceKey,
                 'startNum': startNum,
                 'pagingRow': pagingRow,
                 'optFields': list(['parentKey', 'nickname'] if optFields is None else optFields),
                 'sort': sort,
                 'order': order}
        
        query['fileOption'] = fileOption if fileOption is not None else None
        query['resourceOption'] = resourceOption if resourceOption is not None else None 

        return requests.post('https://api.mybox.naver.com/service/file/list',data=query, cookies=self.cookies, headers=self.headers)
    
    def rm_by_key(self, resourceKey: str):
        query = {'resourceKey': resourceKey,
                 'deleteType': 'normal'}
        
        return self.post('https://files.mybox.naver.com/file/delete.api', data=query)


    def mkdir(self, parentKey: str = 'root', dir_name: str =''):
        query = {'resourceKey':           parentKey,
                 'resourceName':          '새 폴더' if dir_name == '' else dir_name}
                 #'useAutoCorrectFilename':['true' if dir_name == '' else 'false']}
        
        self._logger.info("mkdir: {}".format(query['resourceName']))

        ret = self.post('https://files.mybox.naver.com/file/mkdir.api?{}'.format(parse.urlencode(query)))

        # Code 1008 means
        #{'code': 1008, 'message': 'Duplicated Folder Exist'
        if ret.json()['code'] == 1008:
            self._logger.info("Directory {} is already exists".format(query['resourceName']))
        return ret 

    def mv(self, filename: str, resourceKey: str, toParentKey: str = ""):
        query = {'resourceKey':         [resourceKey],
                 'toParentKey':         ['root' if toParentKey == "" else toParentKey],
                  'resourceName':       [filename]}

        return requests.get('https://files.mybox.naver.com/file/move.api?{}'.format(parse.urlencode(query)), cookies=self.cookies, headers=self.headers)


    def get_metadata(self, resourceKey: str = 'root'):
        """
        # https://api.mybox.naver.com/service/file/get
        # GET
        # get 'file' or 'directory' metadata whether you are owner of the 'file' or 'directory' or NOT
        # if resourceKey == 'root' then site will return metadata of root directory
        # you can get
        # accessDate: int
        # copyRight: 'N' | 'Y'
        # createDate: int
        # updateDate: int
        # ...
        # ownership: str
        # resourceKey: str
        # parentKey: str
        # resourcePath: str
        # ...
        """
        query = {'resourceKey':         [resourceKey]}

        return requests.get('https://api.mybox.naver.com/service/file/get?{}'.format(parse.urlencode(query)), cookies=self.cookies, headers=self.headers)


    def get_count(self, resourceKey: str):
        # probably count number to element of 'file or directory'
        # in case of directory(=resourceKey is directory) they count the number to directories
        query = {'resourceKey':         [resourceKey]}

        return requests.get('https://api.mybox.naver.com/service/file/count?{}'.format(parse.urlencode(query)), cookies=self.cookies, headers=self.headers)

    def get_thumb(self, fileName: str, resourceNo: str):
        url = 'https://thumb1.photo.mybox.naver.com/' + resourceNo + '?type=m740_390_2'

        savePath = os.path.join(self._save_path, '.thumbnails/')
        if os.path.exists(savePath) == False:
            os.mkdir(savePath)

        savePath += fileName + '_' + resourceNo + '.jpg' 

        ret = 0
        r = self.get(url)
        r.raw.decode_content = True
        with self.get(url, stream=True) as r:
            r.raise_for_status()
            self._logger.debug("Save thumb at: {}".format(savePath))
            with open(savePath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    ret += f.write(chunk)
        if ret == 0:
            os.remove(savePath)

        return ret
    def get_thumb2(self, fileName: str, resourceKey: str, resourceNo: str, resourceType='thumbnail', thumbType='thumbnail.jpg'):
        """
        get document format(e.g. pdf, txt ...) file thumbnail
        #       resourceType: str       -> hint for searching directory. "version" | "thumbnail"

        """
        query = {'resourceKey': [resourceKey],
                 'resourceType': [resourceType],
                 'thumbType': [thumbType]}
        url = 'https://files.mybox.naver.com/file/download.api?resourceKey=' + resourceKey + '&resourceType=thumbnail&thumbType=thumbnail.png'
        savePath = os.path.join(self._save_path, '.thumbnails/')
        if os.path.isdir(savePath) == False:
            os.mkdir(savePath)

        savePath += fileName + '_' + resourceNo + '.jpg' 

        ret = 0
        r = self.get(url)
        r.raw.decode_content = True
        with self.get(url, stream=True) as r:
            r.raise_for_status()
            self._logger.debug("Save thumb at: {}".format(savePath))
            with open(savePath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    ret += f.write(chunk)
        if ret == 0:
            os.remove(savePath)
        return ret
    
    def get_thumb3(self, fileName: str, resourceNo: str):
        """

        #       resourceType: str       -> hint for searching directory. "version" | "thumbnail"

        """
        url = 'https://thumb2.photo.mybox.naver.com/' + resourceNo + '?type=m740_390_2&recycle='+ fileName + '_' + resourceNo + '&origin=false'
        savePath = os.path.join(self._save_path, '.thumbnails/')

        if os.path.isdir(savePath) == False:
            os.mkdir(savePath)

        savePath += fileName + '_' + resourceNo + '.jpg' 

        ret = 0
        r = self.get(url)
        r.raw.decode_content = True
        with self.get(url, stream=True) as r:
            r.raise_for_status()
            self._logger.debug("Save thumb at: {}".format(savePath))
            with open(savePath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    ret += f.write(chunk)
        if ret == 0:
            os.remove(savePath)

        return ret

    def access_file(self, resourceKey: str):
        # do or undo star
        # protected == true: do star
        # protected == false: undo star
        query = {'resourceKey': resourceKey,
                'accessDate': time.strftime('%Y-%m-%dT%X+09:00', time.localtime(time.time()))}
        
        return requests.get('https://api.mybox.naver.com/service/file/update?{}'.format(parse.urlencode(query)), cookies=self.cookies, headers=self.headers)




    def do_star(self, resourceKey: str, protected: bool):
        # do or undo star
        # protected == true: do star
        # protected == false: undo star
        query = {'resourceKey': [resourceKey],
                'accessDate': [time.strftime('%Y-%m-%dT%X+09:00', time.localtime(time.time()))],
                 'protected': [protected]}
        
        return requests.get('https://api.mybox.naver.com/service/file/update?{}'.format(parse.urlencode(query)), cookies=self.cookies, headers=self.headers)


    def do_zip(self, fileName: str, resourceKeys: list):
        """
        # https://zip.mybox.naver.com/compression/zip
        # POST
        # do zip
        # you can get
        # uploadedParentKey: str
        # uploadedFolderType: str
        """
        query = {"resourceKeys": resourceKeys, 
                 "fileName": fileName}
        header_for_zip = self.headers
        header_for_zip['content-type'] = 'application/json;charset=UTF-8'

        # replace ['] to ["]
        return requests.post('https://zip.mybox.naver.com/compression/zip', data=query.__repr__().replace("'", '"'), cookies=self.cookies, headers=header_for_zip)


    
    def do_upload(self, toParentKey: str, resourceName: str, isRetResourceKey: bool = True, fileLocation: str = ''):
        """
        # https://files.mybox.naver.com/file/upload.api
        # POST
        # do upload
        # you can upload file
        # !!!!ONLY Picture uploading has been tested
        # toParentKey: str --> resourceKey of parent directory
        # resourceName: str
        # fileLocation: str --> location of the file you want to upload
        # 
        # you can get
        # {
        #    "code":0,
        #    "message":"Success",
        #    "result":{
        #        "versionNo":"",
        #        "virus":"N"
        #        "resourceKey: str ---> if you check True on isRetResourceKey
        #        }
        #    }

        """


        if os.path.exists(fileLocation) == False:
            self._logger.error("Can't find file location")
            return None
        
        with open(fileLocation, 'rb') as f:
            data = f.read()


        query = {'toParentKey': toParentKey,
                 'resourceKey': '',
                 'resourceName': resourceName,
                 'resourceSize': len(data),
                 'writeMode': 'None',
                 'lastModified': parse.quote(time.strftime('%Y-%m-%dT%X+09:00', time.localtime(time.time())))}
        
        # Call checkupload.api and check status
        status = requests.post('https://files.mybox.naver.com/file/checkupload.api', cookies=self.cookies, headers=self.headers).status_code
        self._logger.debug('uploadCheck API: {}'.format(status))

        if status != 200:
            self._logger.error('Upload Failed')
            return None

        query = {'toParentKey': toParentKey,
                 'resourceName': parse.quote(resourceName),
                'lastModified':  parse.quote(time.strftime('%Y-%m-%dT%X+09:00', time.localtime(time.time()))),
                'isRetResourceKey': 'true' if isRetResourceKey is True else 'false' ,
                'linkAction': 'false',
                'writeMode': 'none',
                'filesize': len(data)}
        
        self._logger.debug('len data: {}'.format(len(data)))
        
    
        header_for_upload = self.headers.copy()
        if status == 200:
            del header_for_upload['content-type']
            uploaded = requests.post('https://files.mybox.naver.com/file/upload.api', files={'Filedata': data}, data=query,cookies=self.cookies, headers=header_for_upload)
            self._logger.info('File uploaded Name: {}'.format(resourceName))
            return uploaded
        else:
            self._logger.error('Upload Failed')
            return None



    def do_unzip(self, resourceKey: str):
        """
        # https://zip.mybox.naver.com/compression/unzip
        # POST
        # do unzip
        # you can get
        # uploadedParentKey: str
        # uploadedFolderType: str
        """
        query = {"resourceKey": resourceKey}
        header_for_zip = self.headers
        header_for_zip['content-type'] = 'application/json;charset=UTF-8'

        # replace ['] to ["] 
        return requests.post('https://zip.mybox.naver.com/compression/unzip', data=query.__repr__().replace("'", '"'), cookies=self.cookies, headers=header_for_zip)


    def get_image_info(self, fileId: int, catalogType='folder'):
        #folder_info = self.get_folder_info().json()
        #useridx = folder_info['resultvalue']['addition']['resources']['resources'][0]['file']['ownerIdx']
        userIdx = self.get_userIdx()
        query = {'fileId': str(fileId) + ':' + str(userIdx),
                 'catalogType': catalogType}

        self._logger.debug(parse.urlencode(query))

        return requests.post('https://photo.mybox.naver.com/api/imageProperty/getImageInfo', data=parse.urlencode(query), cookies=self.cookies, headers=self.headers)


    def get_folder_info(self, folderPath='/', include='resourceKey'):
        resources = {"sort": "U",
                     "order": "D",
                     "startIndex": 59,
                     "displayCount": 50,
                     "cloudResourceType":"property",
                     "include": ["resourceKey"]}
        query = {"folderPath": folderPath,
                 "include": include,
                 "addition": json.dumps({"resources": resources})} # use json.dumps because of the format

        self._logger.debug('https://photo.mybox.naver.com/v3/api/folder?{}'.format(parse.urlencode(query, quote_via=parse.quote)))
        
        return requests.get('https://photo.mybox.naver.com/v3/api/folder?{}'.format(parse.urlencode(query, quote_via=parse.quote)), cookies=self.cookies, headers=self.headers)
                                

    def get_user_info(self):
        """
        # https://api.mybox.naver.com/service/quota/get
        # GET
        # get user info 
        # you can get
        # userId: str
        # userIdx: int
        # ...
        """
        return requests.get('https://api.mybox.naver.com/service/user/get', cookies=self.cookies, headers=self.headers)
    

    def get_shared_users_info(self, resourceKey: str, sharedStatus='accepted'):
        """
        # https://api.mybox.naver.com/service/shared/users/profile
        # POST
        # get user list of sharing file. 
        # you can choose the file by resourceKey
        # you can get
        # list[
        #   0: 
        #       id: str
        #       name: str
        #       ownership: 'M' | 'W'    -> 'M' means onwer (maybe?)
        #       ...
        """
        query = {'NDriveSvcType': 'NHN/ND-WEB',
                 'resourceKey': resourceKey,
                 'sharedStatus': sharedStatus}

        return self.post('https://api.mybox.naver.com/service/shared/users/profile', data=parse.urlencode(query))


    def get_file_legacy_info(self, resourceKey: str):
        """
        # https://api.mybox.naver.com/service/addon/file/getLegacyInfo
        # GET
        # get legacy info of old file
        # you can get userIdx by resourceKey not only your info but for other user info
        # you can get
        # folderType: str
        # ownderId: str
        # ownderIdc: int
        # ownderIdx: int
        # shareNo: int
        # subPath: str
        """
        query = {'resourceKey': resourceKey}

        return self.get('https://api.mybox.naver.com/service/addon/file/getLegacyInfo?{}'.format(parse.urlencode(query)))

    def get_userIdx(self):
        # you can use get_user_info or get_folder_info
        # but get_user_info is less expensive
        user_info = self.get_user_info().json()

        self._logger.debug(user_info)

        return user_info['result']['userIdx']
    
    def get_share_list(self, startNum=0, pagingRow=200, sort='share', order='desc'):
        query = {'startNum': 0,
                 'pagingRow': 200,
                 'sort': sort,
                 'order': order}

        return self.get('https://api.mybox.naver.com/service/share/list?{}'.format(parse.urlencode(query)))
    def get_shared_list(self, startNum=0, pagingRow=200, sort='invite', order='asc'):
        query = {'startNum': 0,
                 'pagingRow': 200,
                 'sort': sort,
                 'order': order}

        #return requests.get('https://api.mybox.naver.com/service/shared/list?{}'.format(parse.urlencode(query)), cookies=self.cookies, headers=self.headers)
        return self.get('https://api.mybox.naver.com/service/shared/list?{}'.format(parse.urlencode(query)))

    def get_waste_list(self, startNum=0, pagingRow=200, sort='delete', order='desc'):
        """
        # https://api.mybox.naver.com/service/waste/list
        # GET
        # get waste list
        # you can get
        # totalCount: int
        #   list[
        #       0:
        #           resourceType: str
        #           resourceName: str
        #           resourceSize: int
        #           update, deleteDate: int
        #           originalPath: str
        #           resourceNo: int
        #           resourceKey: str
        #           isThumbnail: True | False
        # ...
        """
        query = {'startNum': startNum,
                 'pagingRow': pagingRow,
                 'sort': sort,
                 'order': order}
        return self.get('https://api.mybox.naver.com/service/waste/list?{}'.format(parse.urlencode(query)))



    def do_search_with_option(self, NDriveSvcType='NHN/ND-WEB Ver',minSize = 0, maxSize = 0, startDate = '', endDate = '', startNum=0, pagingRow=200, sort='create', order='desc', fileOption: Literal['all', 'image', 'doc', 'video', 'audio', 'zip'] = 'all', keyword='', resourceKey='root', searchArea='all', highlightTag='<em style="color:#157efd">$SEARCH</em>'):
        """
        # https://api.mybox.naver.com/service/file/search
        # POST
        # return search result --> can't search shared file 
        # fileOption: set file type
        # minSize-maxSize: set file size
        # startDate-endDate: set 'uploaded' date. format should be %Y-%m-%d
        # resourceKey: set searching deriectory by 'directory key'
        # you can get
        # list[
        #       0:  
        #           resourceKey: str
        #           access, create, update Date: int
        #           authToken: str
        #           share{
        #               isRoot: True | False
        #               isSharedRootFolder: True | False
        #               ownderId: str
        #               shareNo: int
        # ...
        """
        query = {'NDriveSvcType': NDriveSvcType,
                 'startNum': startNum,
                 'pagingRow': pagingRow,
                 'sort': sort,
                 'order': order,
                 'keyword': keyword,
                 'fileOption': fileOption,
                 'resourceKey': resourceKey,
                 'searchArea': searchArea,
                 'highlightTag': highlightTag}

        if minSize != 0: query['minSize'] = minSize
        if maxSize != 0: query['maxSize'] = maxSize

        def validateDateFormat(date_text):
            try:
                datetime.fromisoformat(date_text)
                return True
            except ValueError:
                raise ValueError("Incorrect data format, should be YYYY-MM-DD")
                return False

        if validateDateFormat(startDate): query['startDate'] = startDate + 'T00:00:00+09:00'
        if validateDateFormat(endDate): query['endDate'] = endDate + 'T23:59:59+09:00'
        self._logger.debug(parse.urlencode(query, quote_via=parse.quote)) 
        return self.post('https://api.mybox.naver.com/service/file/search', data=parse.urlencode(query, quote_via=parse.quote))


    def do_search(self, NDriveSvcType='NHN/ND-WEB Ver', startNum=0, pagingRow=200, sort='create', order='desc', keyword='', highlightTag='<em style="color:#157efd">$SEARCH</em>'):
        """
        # https://api.mybox.naver.com/service/file/search
        # POST
        # return search result
        # you can get
        # list[
        #       0:  
        #           resourceKey: str
        #           access, create, update Date: int
        #           authToken: str
        #           share{
        #               isRoot: True | False
        #               isSharedRootFolder: True | False
        #               ownderId: str
        #               shareNo: int
        # ...
        """
        query = {'NDriveSvcType': NDriveSvcType,
                 'startNum': startNum,
                 'pagingRow': pagingRow,
                 'sort': sort,
                 'order': order,
                 'keyword': keyword,
                 'highlightTag': highlightTag}

 
        self._logger.debug(parse.urlencode(query, quote_via=parse.quote))
        
        return self.post('https://api.mybox.naver.com/service/file/search', data=parse.urlencode(query, quote_via=parse.quote))


    def get_search_count(self):
        """
        # https://api.mybox.naver.com/service/file/searchCount
        # POST
        # return total count of search result
        # you can get
        # totalCount: int
        """
    
    def get_login_status(self):
        """
        # https://static.nid.naver.com/getLoginStatus
        # GET 
        # get login status and user info of service
        # you can get 
        # membership: False | True
        # nickname: 
        # loginId: 
        # ...
        """
        return self.get('https://static.nid.naver.com/getLoginStatus?callback=showGNB&charset=utf-8&svc=ndrive&template=gnb_utf8&one_naver=1')

        

    def get_user_payment_info(self):
        """
        # https://mybox.naver.com/api/pay/userInfo
        # GET
        # get user info for payment
        # you can get
        # payment: False | True 
        # atpmnt: False | True -> not sure what is it
        # membership: False | True 
        # 
        # itemName, quota, nextQuota, expiredate, expireInfo, maxQuota, storeType
        """
        return self.get('https://mybox.naver.com/api/pay/userInfo')


    def send_list(self):
        """
        # https://mybox.naver.com/api/pay/gift/sendList
        # POST
        # Gussing!: send gift list something related to payment
        # 
        """
        query = {'pagingRow': 10,
                 'startNum': 0}
        
        return self.post('https://mybox.naver.com/api/pay/gift/sendList', data = parse.urlencode(query))


    def get_quota(self):
        """
        # https://api.mybox.naver.com/service/quota/get
        # GET
        # drive volume user can use. default value is 30GB(32212254720). If you pay for MYBOX it could be bigger than this. 
        # you can get
        # fileMaxSize: int
        # totalQuota: int
        # unusedQuota: int
        # usedQuota: int
        # 
        # waste{
        #   cycle: int
        #   size: int
        #}
        """

        return self.get('https://api.mybox.naver.com/service/quota/get')
    

    def get_root_resourceKey(self):
        ret = self.get_root_info().json()
        return ret['result']['resourceKey']

    def get_info_by_resourceKey(self, resourceKey: str = ''):
        """
        # https://api.mybox.naver.com/service/file/get?resourceKey=root
        # GET
        # get resourceKey of Root directory
        #{
        #"code" : "0",
        #"message" : "success",
        #"result" : {
        #    "resourceKey" : "Z2FuZ2p...",
        #    "resourcePath" : "/",
        #    "resourceNo" : 200224974,
        #    "resourceType" : "folder",
        #    "fileType" : "folder",
        #    "imageType" : null,
        #    "resourceSize" : 31723827918,
        #    "createDate" : 1355878795000,
        #    "updateDate" : 1688463863000,
        #    "accessDate" : 1355878795000,
        #    "updateUser" : "gangjeuk",
        #               .
        #               .
        #               .
        """
        return self.post('https://api.mybox.naver.com/service/file/get?resourceKey=' + resourceKey)


    def get_root_info(self):
        """
        # https://api.mybox.naver.com/service/file/get?resourceKey=root
        # GET
        # get resourceKey of Root directory
        #{
        #"code" : "0",
        #"message" : "success",
        #"result" : {
        #    "resourceKey" : "Z2FuZ2pld...",
        #    "resourcePath" : "/",
        #    "resourceNo" : 200224974,
        #    "resourceType" : "folder",
        #    "fileType" : "folder",
        #    "imageType" : null,
        #    "resourceSize" : 31723827918,
        #    "createDate" : 1355878795000,
        #    "updateDate" : 1688463863000,
        #    "accessDate" : 1355878795000,
        #    "updateUser" : "gangjeuk",
        #               .
        #               .
        #               .
        """
        return self.post('https://api.mybox.naver.com/service/file/get?resourceKey=root')


    def get_resourceKey_by_path(self,resourcePath: str, shareNo: int, ownderId: str):
        """
        # https://api.mybox.naver.com/service/file/getResourceKeyByPath
        # POST
        # get resourceKey  
        # you can get 
        # resourceKey: str
        """
        query = {'NDriveSvcType': 'NHN/ND-WEB Ver',
                 'resourcePath': resourcePath,
                 'shareNo': shareNo,
                 'ownderId': ownderId}

        return self.post('https://api.mybox.naver.com/service/file/getResourceKeyByPath', data=parse.urlencode(query))


    def get_share_history(self, resourceKey: str, startNum=0, pagingRow=200):
        """
        # https://api.mybox.naver.com/service/share/history
        # GET
        # ?
        """
        query = {'resourceKey': resourceKey,
                 'startNum': startNum,
                 'pagingRow': pagingRow}

        return self.get('https://api.mybox.naver.com/service/share/history?{}'.format(parse.urlencode(query)))


    def get_select_memo(self, userId: str, userIdx: int, ownerId: str, ownerIdx: int, shareNo: int, targetNo: int, currentMsgNo=0, currentReplyCount=0, order='desc'):
        """
        # https://mybox.naver.com/api/memo/selectMemo
        # POST
        # ?
        # you can get
        # memolist: ?
        """

        query = {'userid': userId,
                 'useridx': userIdx,
                 'ownerid': ownerId,
                 'owneridx': ownerIdx,
                 'shareno': shareNo,
                 'targetNo': targetNo,
                 'currentMsgNo': currentMsgNo,
                 'currentReplyCount': currentReplyCount,
                 'order': order}

        return self.post('https://mybox.naver.com/api/memo/selectMemo', data=parse.urlencode(query))


    ####################################################################################################
    # routine for link sharing
    # when you press the sharing-link button
    # backend check
    # 1. check Sub Folder: https://api.mybox.naver.com/service/link/create
    # 2. create link: https://api.mybox.naver.com/service/link/create
    # 3. get file metadata: https://api.mybox.naver.com/service/file/get
    # 4. get property: ttps://api.mybox.naver.com/service/v2/share/link/[resourceKey]/property
    # 5. get file metadata again: https://api.mybox.naver.com/service/file/get
    #


    def check_sub_folder(self, resourceKey: str):
        """
        # https://api.mybox.naver.com/service/share/checkSubFolder
        # POST
        # check sub folder
        # you can get
        # folderExist: True | False
        # folderName: ?
        """
        query = {'NDriveSvcType': 'NHN/ND-WEB Ver',
                 'resourceKey': resourceKey}

        return self.post('https://api.mybox.naver.com/service/share/checkSubFolder', data=parse.urlencode(query))


    def create_share_link(self, resourceKey: str):
        """
        # https://api.mybox.naver.com/service/link/create
        # GET
        # create sharing link
        # if sharing link already exist then return code: 4204 
        # you can get
        # blockDownload: True | False
        # createDate: int
        # expireDate: ?
        # expireDaysConfig: -1 
        # remainAccessCount: -1 
        # remainAccessCountConfig: -1 
        # resourceName: str
        # resourceNo: int
        # resourcePath: str
        # resourceType: str
        # shortUrl: str         -> sharing link
        """

        query = {'resourceKey': resourceKey}

        return self.get('https://api.mybox.naver.com/service/link/create?{}'.format(parse.urlencode(query)))


    def get_share_link_property(self, resourceKey: str):
        """
        # https://api.mybox.naver.com/service/v2/share/link/[resourceKey]/property
        # GET
        # get sharing link property
        # if there is no property or no permission it return code: 3111 
        # you can get
        # shortUrl: str
        # fullUrl: str
        # hasPassword: True | False
        # expireDate: int | None
        # path: str
        # size: int
        # accessibleCount: -1 
        # ownerShip: str
        # ownerId: int
        # ownderName: str
        # ownerIdx: int
        # createDate: int
        # resourceKey: str
        # resourceName: str
        # blockDownload: True | False
        # resourceType: str
        # accessibleCountConfig: -1 
        # expireDaysConfig: -1
        """
        return self.get('https://api.mybox.naver.com/service/v2/share/link/' + resourceKey + '/property')


    def delete_share_link(self, resourceKey: str):
        """
        # https://api.mybox.naver.com/service/link/delete
        # GET
        # delete sharing link
        # it always success whether the sharing link is actually exist or not
        """
        query = {'resourceKey': resourceKey}
        return self.get('https://api.mybox.naver.com/service/link/delete?{}'.format(parse.urlencode(query)))

    # end of routine for link sharing
    ####################################################################################################    

    def download_file(self, resourceKey: str, fileName: Tuple[str, None] = None, resourceType: Literal[None, 'version'] = None):
        """
        # resourceType 
        # if resourceType is version, means download past file 
        """

        savePath = os.path.join(self._save_path, 'download/')
        if fileName is None:
            # resourcePath. ex) /test/124.jpg
            self._logger.debug("File name is None. Trying to search fileName...")
            try:
                fileName = self.get_metadata(resourceKey).json()['result']['resourcePath'].split('/')[-1]
                self._logger.debug("File found file name: {}".format(fileName))
            except Exception:
                self._logger.error('get file name failed: ', Exception)
                fileName = resourceKey

        query = {'NDriveSvcType': 'NHN/ND-WEB Ver',
                'resourceKey': resourceKey}
        
        url = 'https://files.mybox.naver.com/file/download.api?{}'.format(parse.urlencode(query))

        ret = 0
        with self.get(url, stream=True) as r:
            r.raise_for_status()
            if os.path.exists(savePath) == False:
                os.mkdir(savePath)

            with open(savePath+fileName, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    ret += f.write(chunk)
                self._logger.info("File Downloaded Size: {} Filename: {} Path: {}".format(ret, fileName, savePath + fileName))
        return True


    def get_file_version_list(self, resourceKey: str, startNum=0, pagingRow=200):
        """
        # https://api.mybox.naver.com/service/file/version/list
        # GET
        # get version list
        # only support image file(as far as I know)
        # 
        # Item of the version list has dictionary value [name:resourceKey]
        # So backend register multiple files which have same name and difference resourceKey 
        # Each file name of list is registed in this form "/.version/[version_key]_[name].jpg"
        # 
        # you can get
        # totalCount: int
        #   list[
        #       0:
        #         createUser: str
        #         fileSize: int
        #         getlastmodified: int
        #         resourcePath: str
        #         updateUserName: str
        #         versionResourceKey: str
        #         versioninfo: str          -> It means replacement method. e.g) "overwrite"
        #         versionkey: int
        # ...
        """
        query = {'resourceKey': resourceKey,
                 'startNum': startNum,
                 'pagingRow': pagingRow}

        return self.get('https://api.mybox.naver.com/service/file/version/list?{}'.format(parse.urlencode(query)))


    def get_doc_collection(self, sort='create', order='desc', startNum=0, pagingRow=200):
        """
        # https://api.mybox.naver.com/service/file/getDocCollection
        # GET
        # get document data list
        # 
        # you can get
        # totalCount: int
        #   list[
        #       0:
        #         update, createDate: int
        #         resourceSize: int
        #         resourceNum: int
        #         resourceKey: str
        #         parentKey: str
        #         resourcePath: str
        #         isProtected: true | false
        #         isUploaded: treu | false
        #         isUrlLink: true | false
        # ...
        """
        query = {'sort': sort,
                'order': order,
                'startNum': startNum,
                'pagingRow': pagingRow}

        return self.get('https://api.mybox.naver.com/service/file/getDocCollection?{}'.format(parse.urlencode(query)))


    def get_movie_collection(self, sort='create', order='desc', startNum=0, pagingRow=200):
        """
        # https://api.mybox.naver.com/service/file/getMovieCollection
        # GET
        # get movie data list
        # 
        # you can get
        # totalCount: int
        #   list[
        #       0:
        #         update, createDate: int
        #         resourceSize: int
        #         resourceNum: int
        #         resourceKey: str
        #         parentKey: str
        #         resourcePath: str
        #         isProtected: true | false
        #         isUploaded: treu | false
        #         isUrlLink: true | false
        # ...
        """
        query = {'sort': sort,
                'order': order,
                'startNum': startNum,
                'pagingRow': pagingRow}

        return self.get('https://api.mybox.naver.com/service/file/getMovieCollection?{}'.format(parse.urlencode(query)))




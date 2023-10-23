#!/usr/bin/env python3

import os
import sys
import json
import argparse
import urllib.parse
import time
from urllib import parse
from logging import DEBUG

from mybox import mybox
from credential import Credential
from login import NaverLogin
from log import *

__author__ = 'Jeuk Kang'
__email__ = 'gangjeuk@gmail.com'
__version__ = '0.0.0'



def encode_message(msg: str) -> str:
    return urllib.parse.quote(msg)

def print_progress(status: str, **kwargs) -> None:
    assert status in ['start', 'loading', 'warning', 'error', 'end'], 'Invalid status ({})'.format(status)

    log_params = {
        'status': status,
        **kwargs
    }
    log_params = ['{0}={1}'.format(k, encode_message(str(v))) for k, v in log_params.items()]
    log = '&'.join(log_params)

    print(log, file=sys.stdout)



class CloudCollectMybox:

    _headers = {}
    IMAGE_FORMAT = ['BMP','CR2','CUR','DDS','DNG','ERF','EXR','FTS','GIF','HDR','HEIC','HEIF','ICO','JFIF','JP2','JPE','JPEG','JPG','JPS','MNG','NEF','NRW','ORF','PAM','PBM','PCD','CD','PCX','PEF','PES','PFM','PGM','PICON','PICT','PNG','PNM','PPM','PSD','RAF','RAS','RW2','SFW','SGI','SVG','TGA','TIFF','WBMP','WEBP','WPG','X3F','XBM','XCF','XPM','XWD']
    MOVIE_FORMAT = ['3GP','ASF','AVI','F4V','FLV','HEVC','M2TS','M2V','M4V','MJPEG','MKV','MOV','MP4','MPEG','MPG','MTS','MXF','OGV','RM','TS','VOB','WEBM','WMV','WTV']
    AUDIO_FORMAT = ['8SVX','AAC','AC3','AIFF','AMB','AU','AVR','CAF','CDDA','CVS','CVSD','CVU','DTS','DVMS','FAP','FLAC','FSSD','GSRT','HCOM','HTK','IMA','IRCAM','M4A','M4R','MAUD','MP2','MP3','NIST','OGA','OGG','OPUS','PAF','PRC','PVF','RA','SD2','SLN','SMP','SND','SNDR','SNDT','SOU','SPH','SPX','TTA','TXW','VMS','VOC','VOX','W64','WAV','WMA','WV','WVE']
    DOCUMENT_FORMAT = ['CSV','DJVU','DOC','DOCX','ODP','ODS','ODT','OTT','PDF','PPT','RTF','TXT','XLS','XLSX']

    def __init__(self, savepath):
        self.mb = mybox(save_path=savepath)
        self._logger = set_logger(None)
        self._savepath = savepath
        self._cookies = {}

    
    def set_credentials(self, **kwargs):
        Credential.set_credentials(NID_JKL=kwargs['NID_JKL'],
                                   NID_AUT=kwargs['NID_AUT'],
                                   NID_SES=kwargs['NID_SES'])

    def get_credentials(self):
        return Credential.get_credentials()
    
    def login(self, id, pw) -> bool:
        if self._logger.level == DEBUG:
            return True
        
        ret = True 
        
        naver = NaverLogin(id, pw)
        ret = naver.login()
        self.mb.set_cookies(Credential.get_credentials())
        return ret
    
    def fetch_file_list(self):
        mb_get_list = self.mb.get_list('root').json()

        root = [self._generate_common_data(self.mb.get_root_info().json()['result'])]

        # Set root directory name to ROOT
        root[0]['common']['name'] = '[ROOT]'
        root[0]['files'] = []
        self._visit_recursively(mb_get_list['result']['list'], root[0]['files'], root[0]['common']['shared'])

        if self._logger.level == DEBUG:
            with open('file_list.json', 'w') as f:
                f.write(json.dumps(root))

        return root
    
    def fetch_recent_file_list(self):
        root = []
         
        self._visit_recursively(self.mb.get_recent_list().json()['result']['list'], root, False)
        self._visit_recursively(self.mb.get_recent_list(sort='create', order='asc', recentType='update').json()['result']['list'], root, False)

        return root
    
    def fetch_shared_file_list(self):
        root = []

        self._visit_recursively(self.mb.get_shared_list().json()['result']['list'], root, True)
        self._visit_recursively(self.mb.get_share_list().json()['result']['list'], root, True)

        return root

    
    def fetch_trash_file_list(self):
        ret = []

        # You can't visit folder in trash.
        # Only linear format data will be accepted 
        for i in self.mb.get_waste_list().json()['result']['list']:
            common_data = self._generate_common_data(i)
            ret.append(common_data)
            if common_data['common']['thumbnail'] != '':
                self._download_thumbnail(common_data)
        return ret
    
    def download(self, file):
        resourceKey = file['resourceKey']
        return self.mb.download_file(resourceKey=resourceKey)
    
    def search(self, query):
        return self.mb.do_search(keyword=query).json()
    
    def _generate_common_data(self, data_node):

        # handle ownderId Field
        ownerId = 0
        if 'ownderId' in data_node:
            ownerId = data_node['ownderId']
        elif 'updateUser' in data_node:
            ownerId = data_node['updateUser']
        else:
            ownerId = 0

        # handle name field
        if 'resourcePath' in data_node:
            if data_node['resourceType'] == 'folder':
                name = data_node['resourcePath'].split('/')[-2]
            else:
                name = data_node['resourcePath'].split('/')[-1]
        elif 'resourceName' in data_node:
            name = data_node['resourceName']
        else:
            name = ''
        # handle file extension field
        ext = ''
        fileType=''
        if name.find('.') != -1:
            tail = name.split('.')[-1]
            if tail.upper() in CloudCollectMybox.DOCUMENT_FORMAT:
                ext = tail
                fileType = 'document'
            elif tail.upper() in CloudCollectMybox.IMAGE_FORMAT:
                ext = tail
                fileType = 'picture'
        else:
            ext = ''
            if data_node['resourceType'] == 'folder':
                fileType = 'folder'
            else:
                fileType = 'file'

        # handle download URL field
        query = {'NDriveSvcType': 'NHN/ND-WEB Ver',
                'resourceKey': data_node['resourceKey']}
    
        download_url = 'https://files.mybox.naver.com/file/download.api?{}'.format(parse.urlencode(query))

        # handle shared field
        shared = False

        if 'isSharing' in data_node and data_node['isSharing'] == True:
            # when called by https://api.mybox.naver.com/service/file/get?resourceKey=, then you can find isSharing field 
            shared = True 
        elif 'memberShare' in data_node and data_node['memberShare'] is not None:
            # when you get shared by friend or someone else
            shared = True 
        elif 'linkShare' in data_node and data_node['linkShare'] is not None:
            # when you share file
            shared = True 
        elif 'isUrlLink' in data_node:
            # if you share file then isUrlLink should be true
            if data_node['isUrlLink'] == True and 'linkShare' in data_node:
                shared = True

        # fileid
        fileId = str(data_node.get('resourceNo', 0))

        # Final format
        format = {'common':{
            'file_id': fileId,
            'download_url': download_url if fileType != 'folder' and 'deleteDate' not in data_node else '',
            'type': fileType,
            'name': name, 
            'size': data_node.get('resourceSize', 0),
            'ext': ext,
            'ctime': time.strftime('%Y-%m-%d %X', time.localtime(data_node.get('createDate', 1)/1000)),
            'mtime': time.strftime('%Y-%m-%d %X', time.localtime(data_node.get('updateDate',1)/1000)),
            'owner': ownerId,
            'history_count': 0,
            'shared': shared,
            'thumbnail': os.path.join(self._savepath, '.thumbnail/', (name + '_' + fileId + '.jpg'))  if 'isThumbnail' in data_node.keys() and data_node['isThumbnail'] == True else '',
            },
            'accessDate': time.strftime('%Y-%m-%d %X', time.localtime(data_node.get('accessDate', 1)/1000)),
            'isProtected': data_node.get('isProtected', False),
            'isPasswordLocked': data_node.get('isPasswordLocked', False),
            'resourcePath': data_node.get('resourcePath', False),
            'resourceKey': data_node.get('resourceKey', False)
        }

        # for shared files.
        # shared files include 'inviteDate', 'membeShare' field

        if 'inviteDate' in data_node:
            format['inviteDate'] = time.strftime('%Y-%m-%d %X', time.localtime(data_node['inviteDate']/1000))
        if 'membeShare' in data_node:
            format['membeShare'] = data_node['membeShare']
        if 'linkShare' in data_node:
            format['linkShare'] = data_node['linkShare']

        # for deleted file
        # deleted files include 'deleteDate', 'originalPath' field
        if 'deleteDate' in data_node:
            format['deleteDate'] = time.strftime('%Y-%m-%d %X', time.localtime(data_node['deleteDate']/1000))
        if 'originalPath' in data_node:
            format['originalPath'] = data_node['originalPath']

        return format
    
    def _check_file_type(self, file):
        return file['resourceType']
    
    def _download_thumbnail(self, file: dict):
        if self._logger.level == DEBUG:
            return
    
        fileName = file['common']['name']
        file_id = str(file['common']['file_id'])
        if file['common']['type'] == 'document':
            self.mb.get_thumb2(fileName, file['resourceKey'], str(file_id))
        else:
            if self.mb.get_thumb3(fileName, file_id) == 0:
                self.mb.get_thumb(fileName, file_id)
            

    def _visit_recursively(self, folder_list, parent, parent_dir_is_shared):

        for i in folder_list:
            common_data = self._generate_common_data(i)
            if parent_dir_is_shared == True:
                common_data['common']['shared'] = True
            if i['resourceType'] == 'folder':
                common_data['files'] = []
                
                self._visit_recursively(self.mb.get_list(resourceKey=i['resourceKey']).json()['result']['list'], common_data['files'], common_data['common']['shared'])
            else:
                if common_data['common']['thumbnail'] != '':
                    self._download_thumbnail(common_data)
            parent.append(common_data)
        return parent

def main():
    parser = argparse.ArgumentParser(
        description='네이버 MYBOX 서버로부터 파일 목록을 수집하는 모듈'
    )

    parser.add_argument('user_id', 
                        help='네이버 MYBOX ID', 
                        type=str)
    parser.add_argument('user_pw', 
                        help='네이버 MYBOX 패스워드', 
                        type=str)
    parser.add_argument('savepath', 
                        help='섬네일 등을 저장할 작업경로', 
                        type=str)
    
    parser.add_argument("-c", "--use_creds",
                        action="store_true",
                        help="Use existing credentials [NID_JKL] [NID_AUT] [NID_SES]")

    parser.add_argument('--nid_jkl', 
                        help='네이버 인증 쿠키값', 
                        type=str)
    parser.add_argument('--nid_aut', 
                        help='네이버 인증 쿠키값', 
                        type=str)
    parser.add_argument('--nid_ses', 
                        help='네이버 인증 쿠키값', 
                        type=str)

    parser.add_argument('-d', '--download',
                        help='File id to download the file from server',
                        type=str)
    parser.add_argument('--download_name',
                        help='Stored file name of the file downloaded from server',
                        type=str,
                        default='')

    parser.add_argument("-q", "--query",
                        type=str,
                        help="Query to search in Mybox")

    args = parser.parse_args()


    if not os.path.exists(args.savepath):
        os.makedirs(args.savepath)
        
    m = CloudCollectMybox(args.savepath)
    if args.use_creds:
        m.set_credentials(NID_JKL=args.nid_jkl, NID_AUT=args.nid_aut, NID_SES=args.nid_ses)
    else:
        if not m.login(args.user_id, args.user_pw):
            raise Exception('Failed to login')
        print_progress('loading', progress=10, message='Success to login')

    res = {
        'service': 'mybox',
        'credential': m.get_credentials(),
        'drive_files': [],
        'shared_files': [],
        'trash_files': [],
        'recent_files': []
    }

    if args.download:
        res = m.download(args.download, args.download_name)
    
    elif args.query:
        # TODO
        res['drive_files'] = m.search(args.query)

    else:
        res['drive_files'] = m.fetch_file_list()
        print_progress('loading', progress=30, message='Success to fetch drive files')

        res['shared_files'] = m.fetch_shared_file_list()
        print_progress('loading', progress=50, message='Success to fetch shared files')

        res['trash_files'] = m.fetch_trash_file_list()
        print_progress('loading', progress=70, message='Success to fetch trash files')

        res['recent_files'] = m.fetch_recent_file_list()
        print_progress('loading', progress=90, message='Success to fetch recent files')

        print_progress('loading', progress=100, message='Success to fetch all files')

        if m._logger.level == DEBUG:
            with open('parsing_result.json', 'w') as f:
                f.write(json.dumps(res))
        res = json.dumps(res)
    return json.dumps(res) if type(res) in [dict, list] else str(res)



if __name__ == '__main__':
    data = ''
    try:
        print_progress('start')
        data = main()
    except Exception as e:
        import traceback
        print_progress('error', message=str(e)+'\n'+traceback.format_exc())
    finally:
        print_progress('end', data=data)
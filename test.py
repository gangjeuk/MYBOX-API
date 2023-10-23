import unittest
import mybox
import os
from log import set_logger
from logging import DEBUG
import time


class testInitializer:
    def __init__(self):
        
        self.mb = mybox.mybox()
        self._logger = set_logger(None)
        self._root_resourceKey = self.mb.get_root_resourceKey()
        # Make directory for testing
        mkdir = self.mb.mkdir('root', 'mybox').json()
        # 0 means success

        # code 1008 means {'code': 1008, 'message': 'Duplicated Folder Exist', 'result': {
        if mkdir['code'] == 1008:
            duplicateKey = mkdir['result']['resourceKey']
            rmdir = self.mb.rm_by_key(duplicateKey)
            self._logger.debug("Deleting testing directory {}".format(rmdir.content))
            mkdir = self.mb.mkdir('root', 'mybox').json()
        elif mkdir['code'] != 0:
            self._logger.debug("Mkdir Failed default test directory will be set to ROOT")
            self._parentKey = self._root_resourceKey

        self._parentKey = mkdir['result']['resourceKey']

        self._FLOWER_FILE_NAME = 'asalskjdfljasgoiqhwlej.jpg'
        self._MOUNTAIN_FILE_NAME = 'gsdfsbsdgjoqiwjehowqigt.jpg'
        self._BIRD_FILE_NAME = 'bzxclvkjqoijhqowjmmdf.jpg'
        self._PDF_FILE_NAME = 'slgksjdlfoiqjmowe.pdf'
        self._DOCX_FILE_NAME = 'galjsdkkclmzxlkf.docx'

        self._uploaded = {}
        # upload files 
        upload = self.mb.do_upload(self._parentKey, 'asalskjdfljasgoiqhwlej.jpg', fileLocation='./data/flower.jpg').json()
        self._logger.debug(upload)
        self._uploaded[self._FLOWER_FILE_NAME] = upload['result']['resourceKey']
        time.sleep(0.5)
        upload = self.mb.do_upload(self._parentKey, 'gsdfsbsdgjoqiwjehowqigt.jpg', fileLocation='./data/mountain.jpg').json()
        self._logger.debug(upload)
        self._uploaded[self._MOUNTAIN_FILE_NAME] = upload['result']['resourceKey']
        time.sleep(0.5)
        upload = self.mb.do_upload(self._parentKey, 'bzxclvkjqoijhqowjmmdf.jpg', fileLocation='./data/bird.jpg').json()
        self._logger.debug(upload)
        self._uploaded[self._BIRD_FILE_NAME] = upload['result']['resourceKey']
        time.sleep(0.5)
        upload = self.mb.do_upload(self._parentKey, 'slgksjdlfoiqjmowe.pdf', fileLocation='./data/sample.pdf').json()
        self._logger.debug(upload)
        self._uploaded[self._PDF_FILE_NAME] = upload['result']['resourceKey']
        time.sleep(0.5)
        upload = self.mb.do_upload(self._parentKey, 'galjsdkkclmzxlkf.docx', fileLocation='./data/sample.docx').json()
        self._logger.debug(upload)
        self._uploaded[self._DOCX_FILE_NAME] = upload['result']['resourceKey']


    def get_parentKey(self):
        return self._parentKey

class myboxTest(unittest.TestCase):
    
        
    mb = mybox.mybox()
    __initalize = testInitializer()
    _root_resourceKey = mb.get_root_resourceKey()
    _logger = set_logger(None)
    _parentKey = __initalize.get_parentKey()
    _parentName = 'mybox'


    # keywords
    _RESOURCEKEY = 'resourceKey'
    _RESULT = 'result'
    _LIST = 'list'
    _CODE = 'code'


    def tearDown(self) -> None:
        '''
        tearDown() will be executed after every test within that TestCase class.
        Give little sleep between the test.
        '''
        time.sleep(0.5)
 

    def test_get_root(self):
        return
        folder_info = self.mb.get_folder_info('/').json()
        self.assertEqual(folder_info['resultcode'], '000')

        ownerId = folder_info['resultvalue']['addition']['resources']['resources'][0]['file']['ownerIdx']

        resourceKey_by_path = self.mb.get_resourceKey_by_path('/', 0, ownerId).json()
        root_get_by_path = resourceKey_by_path[self._RESULT][self.RESOURCEKEY]
        root_get_by_folder = folder_info['resultvalue']['response'][self.RESOURCEKEY]
        root_get_by_rootsourceKey = self.mb.get_root_resourceKey()

        self.assertEqual(self._root_resourceKey, root_get_by_path)
        self.assertEqual(self._root_resourceKey, root_get_by_folder)
        self.assertEqual(self._root_resourceKey, root_get_by_rootsourceKey)


    def test_get_file_list(self):
        return
        mb_get_list = self.mb.get_list('root').json()
        self.assertEqual(mb_get_list['code'], '0')
        self.assertEqual(mb_get_list['message'], 'success')

        folder_list = mb_get_list[self._RESULT][self._LIST]

        
        for i in folder_list:
            if i['resourceType'] == 'folder':
                folder_head = i
                break

        mb_get_list = self.mb.get_list(resourceKey=folder_head['resourceKey']).json()
        self.assertEqual(mb_get_list['code'], '0')
        self.assertEqual(mb_get_list['message'], 'success')
        folder_list = mb_get_list[self._RESULT][self._LIST]
        self._logger.debug(folder_list)


    def test_get_folder_recursive(self):
        return
        mb_get_list = self.mb.get_list('root').json()
        self.assertEqual(mb_get_list['code'], '0')
        self.assertEqual(mb_get_list['message'], 'success')


        root = {'path': '/', 'depth': 0, 'child': []}

        def recur(folder_list, parent, depth):
            for i in folder_list:
                if i['resourceType'] == 'folder':
                    child = recur(self.mb.get_list(resourceKey=i['resourceKey']).json()[self._RESULT][self._LIST], [], depth+1)
                    parent.append({'path': i['resourcePath'], 'depth': depth, 'child': child})
            return parent

        root['child']= recur(mb_get_list[self._RESULT][self._LIST], [], 0)
        
        def draw_tree(root, depth=0):
            ret = "\t"*depth+repr(root['path'])+"\n"
            self._logger.debug(ret)
            for child in root['child']:
                draw_tree(child, depth+1)
        
        draw_tree(root, 0)

    def test_mkdir_rmdir(self):
        return 
        ret = self.mb.mkdir('root', 'testing').json()
        
        self.assertEqual(ret[self._CODE], 0)

        ret = self.mb.rm_by_key(ret[self._RESULT][self._RESOURCEKEY]).json()
    
        self.assertEqual(ret[self._CODE], 0)

    def test_upload_download(self):
        return
        upload = self.mb.do_upload(self._parentKey, 'sample.gif', fileLocation='./data/sample.gif').json()
        self._logger.debug(upload)

        # code 1009 means Duplicated file
        #{'code': 1009, 'message': 'Duplicated File Exist', 'result': {}}
        if upload['code'] == 1009:
            duplicate_file_key = self.mb.get_resourceKey_by_path( '/' + self._parentName + '/sample.gif')
            self.mb.rm_by_key(duplicate_file_key)

        upload_resourceKey = upload[self._RESULT][self._RESOURCEKEY]
        self._logger.debug(upload_resourceKey)
        self.mb.download_file(upload_resourceKey)
        
        fd1 = open('./data/sample.gif', 'rb')
        fd2 = open('./download/sample.gif', 'rb')

        data1 = fd1.read()
        data2 = fd2.read()

        self.assertEqual(data1, data2)

        fd1.close()
        fd2.close()

        os.remove('./download/sample.gif')

    def test_do_search(self):
        return

        search = self.mb.do_search(keyword=self.__initalize._BIRD_FILE_NAME).json()

        self._logger.debug('Searching... Result: {}'.format(search))

        self.assertEqual(search[self._RESULT]['list'][0]['resourcePath'].split('/')[-1], self.__initalize._BIRD_FILE_NAME)

    def test_get_recent(self):
        return 
        # open file
        access = self.mb.access_file(self.__initalize._uploaded[self.__initalize._BIRD_FILE_NAME]).json()

        time.sleep(5)
        # recently opened
        search = self.mb.get_recent_list().json()
        self._logger.debug(search)
        self.assertEqual(search[self._RESULT][self._LIST][0]['resourcePath'].split('/')[-1], self.__initalize._BIRD_FILE_NAME)
        time.sleep(1)

        # recently uploaded
        # docx file is the last one
        search = self.mb.get_recent_list(sort='create', recentType='update').json()
        self._logger.debug(search)
        self.assertEqual(search[self._RESULT][self._LIST][0]['resourcePath'].split('/')[-1], self.__initalize._DOCX_FILE_NAME)


    def test_get_share_list(self):
        return

        search = self.mb.get_shared_list().json()
        self._logger.debug(search)
        time.sleep(3)

        link = self.mb.create_share_link(self.__initalize._uploaded[self.__initalize._BIRD_FILE_NAME]).json()
        self._logger.debug(link)
        time.sleep(5)
        search = self.mb.get_share_list().json()
        self._logger.debug(search)
        self.assertEqual(search[self._RESULT][self._LIST][0]['resourcePath'].split('/')[-1], self.__initalize._BIRD_FILE_NAME)

        link = self.mb.delete_share_link(self.__initalize._uploaded[self.__initalize._BIRD_FILE_NAME]).json()
        self._logger.debug(link)


    def test_trash_lish(self):
        return
        search = self.mb.get_waste_list().json()
        self._logger.debug(search)

    def test_get_thumb(self):
        return 
        info = self.mb.get_info_by_resourceKey(self.__initalize._uploaded[self.__initalize._BIRD_FILE_NAME]).json()
        self._logger.debug(info)
        file_id = str(info[self._RESULT]['resourceNo'])
        self.mb.get_thumb3('bird.jpg', file_id)

        thumbPath = os.path.join(self.mb._save_path, '.thumbnails/')
        thumbPath += 'bird.jpg' + '_' + file_id + '.jpg' 

        downPath = os.path.join(self.mb._save_path, 'data/')
        downPath += 'bird_thumb.jpg'

        fd1 = open(thumbPath, 'rb')
        fd2 = open(downPath, 'rb')

        self.assertEqual(fd1.read(), fd2.read())

        fd1.close()
        fd2.close()


        

if __name__ == '__main__':
    logger = set_logger(None)

    if logger.level != DEBUG:
        print('To test the code please set logging level to DEBUG. you can find the code in log.py')
        exit()

    unittest.main()
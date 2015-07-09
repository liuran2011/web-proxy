import hashlib

class MD5(object):
    @staticmethod
    def get(data):
        md5=hashlib.md5()
        md5.update(data)
        return md5.hexdigest()



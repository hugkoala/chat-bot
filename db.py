import pymongo



def mongoClientConnet(dbNm):
    mongoClient = pymongo.MongoClient("mongodb://test:123456@localhost/" + dbNm)
    useDb = mongoClient[dbNm]
    return useDb


class FbUser:

    def __init__(self):
        self.useDb = mongoClientConnet('test')
        self.fbUser = self.useDb['fb_user']

    def select(self, obj):
        if len(obj.keys()) == 0:
            return self.fbUser.find()
        else:
            return self.fbUser.find({}, obj)

    def insert(self, obj):
        if isinstance(obj, dict):
            self.fbUser.insert_one(obj)
        elif isinstance(obj, list):
            self.fbUser.insert_many(obj)

    def delete(self, obj, delete_setting):
        if delete_setting == 'one':
            self.fbUser.delete_one(obj)
        elif delete_setting == 'many':
            self.fbUser.delete_many(obj)




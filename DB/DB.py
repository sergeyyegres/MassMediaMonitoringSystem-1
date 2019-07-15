import urllib
from functools import reduce

import pymongo


class DB:
    def __init__(self):
        """ initialization """
        self.myclient = pymongo.MongoClient(
            'mongodb://%s:%s@188.120.231.51' % (urllib.parse.quote_plus('app'),
                                                urllib.parse.quote_plus('FJWE*uTej58E&')))
        self.mydb = self.myclient["MMM"]
        self.posts_collection = self.mydb["Vk_posts"]
        self.news_collection = self.mydb["News"]
        self.comments_collection = self.mydb["Comments"]
        self.cache_collection = self.mydb["Cache"]
        self.twits_collection = self.mydb['Twits']
        self.vk_users_collection = self.mydb['Vk_users']

    def add_posts(self, mylist):
        return self.posts_collection.insert_many(mylist).inserted_ids

    def get_posts(self, query=None):
        return list(self.posts_collection.find({} if query is None else {"query": query}))

    def get_all_posts(self):
        listt = list(self.posts_collection.find())
        print('Posts collected successfully')
        return listt

    def aggregate_posts(self, start, end):
        pipeline = [
            {
                '$match': {
                    '$and': [
                        {'date': {'$gte': start}},
                        {'date': {'$lte': end}}
                    ]
                }
            },
            {
                '$group': {
                    '_id': '$query',
                    'count': {'$sum': 1},
                    'average': {'$avg': '$polarity'}
                }
            }
        ]

        return list(self
                    .posts_collection
                    .aggregate(pipeline))

    def aggregate_posts_sa(self, start, end):
        pipeline = [
            {
                '$match': {
                    '$and': [
                        {
                            'date': {
                                '$gte': start
                            }
                        }, {
                            'date': {
                                '$lte': end
                            }
                        }, {
                            'owner_id': {
                                '$gt': 0
                            }
                        }
                    ]
                }
            }, {
                '$lookup': {
                    'from': 'Vk_users',
                    'localField': 'owner_id',
                    'foreignField': 'user_id',
                    'as': 'users'
                }
            }, {
                '$replaceRoot': {
                    'newRoot': {
                        '$mergeObjects': [
                            {
                                '$arrayElemAt': [
                                    '$users', 0
                                ]
                            }, '$$ROOT'
                        ]
                    }
                }
            }, {
                '$match': {
                    '$and': [
                        {
                            'sex': {
                                '$exists': True
                            }
                        }, {
                            'age': {
                                '$exists': True
                            }
                        }
                    ]
                }
            }, {
                '$group': {
                    '_id': {
                        'query': '$query',
                        'sex': '$sex',
                        'age': '$age'
                    },
                    'count': {
                        '$sum': 1
                    },
                    'polarity': {
                        '$avg': '$polarity'
                    }
                }
            },
            {
                '$replaceRoot': {
                    'newRoot': {
                        '$mergeObjects': [
                            '$_id', '$$ROOT'
                        ]
                    }
                }
            }, {
                '$group': {
                    '_id': '$query',
                    'list': {
                        '$push': {
                            'age': '$age',
                            'sex': '$sex',
                            'count': '$count',
                            'polarity': '$polarity'
                        }
                    }
                }
            },
        ]

        pre = self.posts_collection.aggregate(pipeline)
        res = []
        for i in pre:
            base = reduce(lambda x, y: [x[0] + y['count'], x[1] + y['polarity']], i['list'], [0, 0])
            base[1] /= len(i['list'])
            slist, alist = [{'id': 'Женщины',
                             'polarity': 0,
                             'value': 0},
                            {'id': 'Мужчины',
                             'polarity': 0,
                             'value': 0}], \
                           [{'id': "0-14 лет", 'polarity': 0, 'value': 0},
                            {'id': "15-21 лет", 'polarity': 0, 'value': 0},
                            {'id': "22-35 лет", 'polarity': 0, 'value': 0},
                            {'id': "36-50 лет", 'polarity': 0, 'value': 0},
                            {'id': "50-inf лет", 'polarity': 0, 'value': 0}]

            scnt = [0, 0]
            acnt = [0, 0, 0, 0, 0]
            for j in i['list']:
                if j['sex'] != -1 and j['age'] != -1:
                    slist[j['sex']]['value'] += j['count']
                    slist[j['sex']]['polarity'] += j['polarity']
                    alist[j['age']]['value'] += j['count']
                    alist[j['age']]['polarity'] += j['polarity']
                    scnt[j['sex']] += 1
                    acnt[j['age']] += 1

            for j in range(len(scnt)):
                slist[j]['polarity'] /= max(1, scnt[j])

            for j in range(len(acnt)):
                alist[j]['polarity'] /= max(1, acnt[j])

            res.append({'name': i['_id'],
                        'count': base[0],
                        'polarity': base[1],
                        'sex': slist,
                        'age': alist})

        return res

    def add_news(self, mylist):
        return self.news_collection.insert_many(mylist).inserted_ids

    def get_news(self):
        return list(self.news_collection.find())

    def add_comments(self, mylist):
        return self.comments_collection.insert_many(mylist).inserted_ids

    def get_comments(self):
        return list(self.comments_collection.find())

    def add_cache(self, query, data):
        res = {"query": query, "result": data}
        return self.cache_collection.insert_one(res)

    def get_ya_news_by_cache(self, query):
        return list(self.news_collection.find({"query": query}))

    def get_vk_posts_by_cache(self, query):
        return list(self.posts_collection.find({"query": query}))

    def get_cache(self, query):
        return self.cache_collection.find_one({"query": query})

    def add_twits(self, mylist):
        return self.twits_collection.insert_many(mylist).inserted_ids

    def add_vk_users(self, mylist):
        return self.vk_users_collection.insert_many(mylist).inserted_ids

    def add_vk_user(self, element):
        return self.vk_users_collection.insert_one(element)


# print(DB().aggregate_posts_sa(1562830000, 1662840000))

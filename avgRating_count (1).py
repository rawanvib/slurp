from pymongo import MongoClient, UpdateOne
from random import randint
from pandas import DataFrame
from datetime import datetime

if __name__ == '__main__':

    # mongo server
    # my_client = MongoClient("mongodb://localhost:27017/")
    my_client = MongoClient('10.134.2.79', 27017, username='htlabs-slurrp-stg', password='SlurrP031xU3',
                              authSource='slurrp', authMechanism='SCRAM-SHA-256')
    
    # database name
    my_db = my_client['slurrp']

    # collection name
    my_col = my_db['Recipe']
    
    db_data = my_col.find({}, {'_id': 1})
    df = DataFrame(db_data)
    
    # update fields: avgRating, totalRatingCount
    upsert_df = df.apply(lambda x: UpdateOne(filter={'_id': x['_id']},
                                             update={'$set':
                                                     {'avgRating': randint(3, 5), 'totalRatingCount': randint(200, 400)}}, upsert=False), axis=1)

    print("Started dumping process")
    start_time = datetime.now()
    
    # bulk update data into database
    result = my_col.bulk_write(upsert_df.tolist())
    print(result.bulk_api_result)
    
    end_time = datetime.now()
    print("Total time to dump records:-{}".format(end_time - start_time))

import pymongo
from settings import username, password

uri = "mongodb+srv://" + username + ":" + password + "@cluster0.qads0yo.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(uri)['todo_db']

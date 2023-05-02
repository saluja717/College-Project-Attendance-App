from pymongo.mongo_client import MongoClient


def store_db(name, owner, data):
    try:
        conn = MongoClient("mongodb+srv://manpreet:manpreet@cluster0.7r4za.mongodb.net/")
        print("Connected successfully!!!")

        # database
        db = conn.attendance_portal

        collection = db.attendance
        rec_id1 = collection.insert_one({"AttendanceRecord": name, "owner": owner, "data": data})
        print("Data inserted with record ids", rec_id1)

    except:
        print("Could not connect to MongoDB")

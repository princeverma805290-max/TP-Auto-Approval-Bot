from pymongo import MongoClient
from configs import cfg

client = MongoClient(cfg.MONGO_URI)
db = client['main']
users = db['users']
groups = db['groups']
admins = db['admins']

def add_user(user_id):
    if not users.find_one({'user_id': str(user_id)}):
        users.insert_one({'user_id': str(user_id)})

def remove_user(user_id):
    users.delete_one({'user_id': str(user_id)})

def add_group(chat_id):
    if not groups.find_one({'chat_id': str(chat_id)}):
        groups.insert_one({'chat_id': str(chat_id)})

def all_users():
    return users.count_documents({})

def all_groups():
    return groups.count_documents({})

# Admin Logic
def is_admin(user_id):
    return True if admins.find_one({'user_id': str(user_id)}) else False

def add_admin(user_id):
    if not is_admin(user_id):
        admins.insert_one({'user_id': str(user_id)})

def remove_admin(user_id):
    admins.delete_one({'user_id': str(user_id)})

def get_admins():
    admin_list = []
    for admin in admins.find():
        admin_list.append(admin['user_id'])
    return admin_list
    

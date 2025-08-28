from datetime import datetime
import json
import os

class UserManagement:
    def __init__(self, user_data_file='user_data.json'):
        self.user_data_file = user_data_file
        self.users = self.load_users()

    def load_users(self):
        if os.path.exists(self.user_data_file):
            with open(self.user_data_file, 'r') as file:
                return json.load(file)
        return {}

    def save_users(self):
        with open(self.user_data_file, 'w') as file:
            json.dump(self.users, file)

    def register_user(self, name, face_encodings=None):
        if name not in self.users:
            self.users[name] = {'timestamp': str(datetime.now())}
            if face_encodings is not None:
                # Convert numpy arrays to lists for JSON serialization
                self.users[name]['face_encodings'] = [enc.tolist() for enc in face_encodings]
            self.save_users()
            return True, f"{name} is registered successfully!"
        return False, f"Failed!!! {name} is registered already!"

    def reset_users(self):
        self.users.clear()
        self.save_users()

    def get_users(self):
        return list(self.users)

    def is_registered(self, name):
        return name in self.users

    def get_user_info(self, name):
        return self.users.get(name, None)
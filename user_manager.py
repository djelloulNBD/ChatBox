import hashlib
import json
import os
from typing import Dict, Optional

class UserManager:
    def __init__(self, env_var_name: str = "APP_USERS"):
        self.env_var_name = env_var_name
        self.users = self._load_existing_users()

    def _load_existing_users(self) -> Dict[str, str]:
        """Load existing users from .env file"""
        try:
            if not os.path.exists('.env'):
                print("Warning: .env file not found")
                return {}
                
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read().strip()
                print(f"Debug: Raw .env content: {content}")  # Debug line
                
                if not content:
                    print("Warning: .env file is empty")
                    return {}
                    
                try:
                    key, value = content.split('=', 1)
                    if key != self.env_var_name:
                        print(f"Warning: Expected {self.env_var_name} but found {key}")
                        return {}
                        
                    users = json.loads(value)
                    print(f"Debug: Loaded users: {users}")  # Debug line
                    return users
                except ValueError as e:
                    print(f"Error parsing .env content: {str(e)}")
                    return {}
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {str(e)}")
                    return {}
        except Exception as e:
            print(f"Error reading .env file: {str(e)}")
            return {}
        return {}

    def add_user(self, username: str, password: str) -> bool:
        """Add a new user"""
        if username in self.users:
            print(f"Error: User '{username}' already exists")
            return False
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.users[username] = password_hash
        print(f"User '{username}' added successfully!")
        self._show_current_json()
        return True

    def remove_user(self, username: str) -> bool:
        """Remove an existing user"""
        if username not in self.users:
            print(f"Error: User '{username}' does not exist")
            return False
        
        del self.users[username]
        print(f"User '{username}' removed successfully!")
        self._show_current_json()
        return True

    def list_users(self):
        """List all users"""
        if not self.users:
            print("No users found")
            return
        
        print("\nCurrent Users:")
        print("-" * 20)
        for username in self.users:
            print(f"Username: {username}")
        print("-" * 20)
        self._show_current_json()

    def change_password(self, username: str, new_password: str) -> bool:
        """Change a user's password"""
        if username not in self.users:
            print(f"Error: User '{username}' does not exist")
            return False
        
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        self.users[username] = password_hash
        print(f"Password changed successfully for user: {username}")
        self._show_current_json()
        return True

    def _show_current_json(self):
        """Show the current JSON configuration"""
        if not self.users:
            print("\nNo users configured")
            return

        users_json = json.dumps(self.users, ensure_ascii=False)
        print("\nCurrent configuration:")
        print(f"{self.env_var_name}={users_json}")
        print("\nCopy this line to your .env file")

def main():
    manager = UserManager()
    
    # Show initial users if any exist
    if manager.users:
        print("\nLoaded existing users:")
        manager.list_users()
    else:
        print("\nNo existing users found in .env file")
    
    while True:
        print("\nUser Management System")
        print("1. Add User")
        print("2. Remove User")
        print("3. List Users")
        print("4. Change Password")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            username = input("Enter username: ")
            password = input("Enter password: ")
            manager.add_user(username, password)
        
        elif choice == "2":
            username = input("Enter username to remove: ")
            manager.remove_user(username)
        
        elif choice == "3":
            manager.list_users()
        
        elif choice == "4":
            username = input("Enter username: ")
            new_password = input("Enter new password: ")
            manager.change_password(username, new_password)
        
        elif choice == "5":
            if manager.users:
                print("\nFinal configuration:")
                manager._show_current_json()
            print("\nExiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 
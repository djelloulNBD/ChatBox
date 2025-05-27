import os

def check_env_file():
    print("Checking .env file...")
    print("-" * 30)
    
    # Check if file exists
    if not os.path.exists('.env'):
        print("Error: .env file not found!")
        print("Please create a .env file with your users.")
        return
    
    # Read file contents
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read().strip()
            print("\n.env file contents:")
            print("-" * 30)
            print(content)
            print("-" * 30)
            
            if not content:
                print("\nError: .env file is empty!")
            elif not content.startswith('APP_USERS='):
                print("\nError: .env file should start with 'APP_USERS='")
            else:
                print("\n.env file exists and has content.")
                print("Make sure it has the format:")
                print('APP_USERS={"username":"hashed_password"}')
    except Exception as e:
        print(f"\nError reading .env file: {str(e)}")

if __name__ == "__main__":
    check_env_file()
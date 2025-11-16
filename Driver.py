import matplotlib.pyplot as plt


from Connection.Auth import NorenAuth
from Connection.Config import *

if __name__ == "__main__":
    # Initialize authentication
    auth = NorenAuth()
    
    # Get session token
    susertoken, login_response = auth.login(UID, PWD, FACTOR2, APKVERSION, VC, APPKEY, IMEI)
    
    if susertoken:
        print(f"Session Token: {susertoken}")
        
        # Save session to CurrentSession.py
        with open('CurrentSession.py', 'w') as f:
            f.write(f"SESSION_TOKEN = '{susertoken}'\n")
        print("Session saved to CurrentSession.py")
    else:
        print(f"Login failed: {login_response}")

    
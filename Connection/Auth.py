import requests
import json
import hashlib

class NorenAuth:
    def __init__(self):
        self.base_url = "https://go.mynt.in/NorenWClientTP"
        self.login_url = f"{self.base_url}/QuickAuth"
        self.logout_url = f"{self.base_url}/Logout"
    
    def _sha256(self, data):
        return hashlib.sha256(data.encode()).hexdigest()
    
    def login(self, uid, pwd, factor2, apkversion, vc, appkey, imei="", source="API"):
        data = {
            "uid": uid,
            "pwd": self._sha256(pwd),
            "factor2": factor2,
            "apkversion": apkversion,
            "vc": vc,
            "appkey": self._sha256(f"{uid}|{appkey}"),
            "imei": imei,
            "source": source
        }
        
        payload = f"jData={json.dumps(data)}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(self.login_url, headers=headers, data=payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get("stat") == "Ok":
                return result.get("susertoken"), result
            else:
                return None, result
        except requests.RequestException as e:
            return None, {"error": str(e)}
    
    def logout(self, uid, susertoken):
        data = {"uid": uid}
        payload = f"jData={json.dumps(data)}&jKey={susertoken}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(self.logout_url, headers=headers, data=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
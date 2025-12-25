import websocket
import json
import threading
import requests
from collections import deque
from typing import Callable ,Any
from websocket import WebSocket
import logging


class CDP():
    def __init__(self, web_socket_debugger_url:str,on_message:Callable[[WebSocket,Any],None]| None):
        
        self.web_socket_debugger_url = web_socket_debugger_url
        self.ws:websocket.WebSocketApp|None = None
        self.commands_to_run_at_start=[]
        self.runed_commands = []
        self.recived_result= []
        self._command_index=1
        self.is_connected = False
        
        self._on_massages:Callable[[WebSocket,Any],None]| None =on_message
        

    
    def connect(self):
        if not self.is_connected:
            self.ws = websocket.WebSocketApp(
                url= self.web_socket_debugger_url,
                on_open=self._on_open_ws,
                on_message=self._on_message_ws,
                on_error=self._on_error,
                on_close=self._on_close_ws,
                header=[
                    "Origin: http://127.0.0.1"
                ],
            )
            # اجرای WebSocket در thread جدا
            threading.Thread(target=self.ws.run_forever, daemon=True,kwargs={"ping_interval": 0}).start()
            
    def send_command(self,cmd:dict):
        if not self.is_connected or self.ws == None:
            raise RuntimeError("WebSocket not connected")
        
        payload = dict(cmd)
        payload["id"] = self._command_index
        
        self.ws.send(
            json.dumps(payload),
            websocket.ABNF.OPCODE_TEXT
        )
        self._command_index+=1
        self.runed_commands.append(payload)
        return payload["id"]
            
            
    def _on_open_ws(self,ws:WebSocket)->None:
        logging.debug(f"CDP Connected {self.web_socket_debugger_url}")
        self.is_connected =True
        for cmd in self.commands_to_run_at_start:
            self.send_command(cmd)
            
        
    def _on_message_ws(self,ws:WebSocket,msg) -> None:
        self.recived_result.append(json.loads(msg))
        if self._on_massages :
            self._on_massages(ws,msg)
            
    def _on_error(self,ws:WebSocket,error) -> None:
        #logging.error(error,exc_info=True)
        pass
    def _on_close_ws(self,ws:WebSocket,close_status_code, close_msg) ->None:
        self.is_connected =False
        logging.debug(f"CDP Disconnected {self.web_socket_debugger_url}")
   
        
    def get_command_response(self,command_id:int)->Any|None:
        for r in self.runed_commands:
            if r.get("id") == command_id:
                return r
    def disconnect(self):
        #self.ws.close()
        pass
    
    
class ChromePage(CDP):
    def __init__(self, id:str, web_socket_debugger_url:str, url:str, devtools_frontend_url:str,*args, **kwargs):
        super().__init__(web_socket_debugger_url,self.on_message_rcv, *args, **kwargs)
        self.id = id
        self.url = url
        self.devtools_frontend_url = devtools_frontend_url
        self.string_looking_for="https://www.recaptcha.net/recaptcha/enterprise/payload"
        
       
  
    def on_message_rcv(self, ws: WebSocket, msg) -> None:
        data = json.loads(msg)

   
        method = data.get("method")
        if method != "Network.requestWillBeSent":
            return

        params = data.get("params", {})
        request = params.get("request", {})
        url = request.get("url", "")

        if self.string_looking_for in url:
            global urlfound
            #TODO i need way to get this url
            logging.debug(f"MATCHED URL:{url}")
            urlfound=url
            
            
            
class ChromeBrowserCDP(CDP):
    def __init__(self,user_agent:str="",
                 web_socket_debugger_url:str="",
                 *args, **kwargs
                 ):
        super().__init__(web_socket_debugger_url,self.self_message_handler, *args, **kwargs)
        self.user_agent = user_agent
        self.temp=""
        
        self .run_on_discovered_target = []
        self.frames=[]
        
    def set_discover_targets(self):
        
        self.temp = self.send_command({"method":"Target.setDiscoverTargets","params":{"discover":True}})
        
    def self_message_handler(self, ws: WebSocket, msg) -> None:
        data = json.loads(msg)

        method = data.get("method")

        # ===== target created =====
        if method == "Target.targetCreated":
            target_id = data.get("params", {}) \
                            .get("targetInfo", {}) \
                            .get("targetId")

            if not target_id:
                return

            response = requests.get("http://127.0.0.1:9222/json")
            for page in response.json():
                if page["id"] == target_id:
                    target = ChromePage(
                        page["id"],
                        page["webSocketDebuggerUrl"],
                        page["url"],
                        page["devtoolsFrontendUrl"]
                    )
                    target.commands_to_run_at_start.extend(self.run_on_discovered_target)
                    target.connect()
                    self.frames.append(target)
                    self.send_command({
                        "method": "Target.targetDestroyed",
                        "params": {
                            "targetId": f"{target_id}"
                        }
                        }
                    )
                    break

        # ===== target destroyed =====
        elif method == "Target.targetDestroyed":
            target_id = data.get("params", {}).get("targetId")

            if not target_id:
                return

            # حذف از لیست frames
            self.frames = [
                f for f in self.frames if f.id != target_id
            ]


    @staticmethod
    def find_browser_and_create_CDP_object() -> "ChromeBrowserCDP": 
        response = requests.get("http://127.0.0.1:9222/json/version")
        data = response.json()
        return ChromeBrowserCDP(
            user_agent=data.get("userAgent",""),
            web_socket_debugger_url=data.get("webSocketDebuggerUrl","")
        )

urlfound=""
if __name__ == "__main__":
    import time
    main_browser = ChromeBrowserCDP.find_browser_and_create_CDP_object()
    main_browser.run_on_discovered_target.append({"method": "Network.enable", "params": {"maxPostDataSize": 10485760}})
    main_browser.connect()
    time.sleep(1)
    main_browser.set_discover_targets()

    while True:
        time.sleep(1)
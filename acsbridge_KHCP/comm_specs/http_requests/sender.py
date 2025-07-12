import requests

# from config import Config

# class Sender:
# 	def __init__(self) -> None:
# 		self.config = Config()

# 	def send(self, message: dict) -> None:
# 		if 'command' not in message or message['command'] == '':
# 			return
# 		try:
# 			requests.post(f'http://{self.config.acs_bridge_host}:{self.config.acs_bridge_port}/api/mes', json=message)
# 			#requests.post(f'http://192.168.0.193:8000/api/test2', json=message)
# 			#print("POST to Simulation:",message)
# 		except:
# 			print("POST ERROR",message)
class ConnectionInfo(object):
   def __init__(self, ip: str, port: int, id: int) -> None:
     self.ip = ip
     self.port = port
     self.id = id
   
   def get_info(self) -> list:
      return self.ip, self.port, self.id
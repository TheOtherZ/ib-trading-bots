import json
import os
from pathlib import Path
import threading
import time
import random

class CapitolManager():
   _save_file = "Save/capitol.json"
   _instance = None
   _lock = threading.Lock()

   @classmethod
   def initialize(cls, starting_cap):
      with cls._lock:
         if not os.path.exists("Save/"):
            os.makedirs("Save/")
         path = Path(cls._save_file)
         if not path.is_file():
            with open(cls._save_file, 'w') as sv:
               sv.write('{"capitol": ' + str(starting_cap) + '}')

   @classmethod
   def add_capitol(cls, cap):
      with cls._lock:
         save = open(cls._save_file, "r")
         data = json.load(save)
         save.close()
         capitol = cap
         capitol += float(data["capitol"])
         data["capitol"] = round(capitol, 2)

         save = open(cls._save_file, "w")
         json.dump(data, save)
         save.close()

   @classmethod
   def take_capitol(cls, cap):
      available_cap = 0
      with cls._lock:
         save = open(cls._save_file, "r")
         data = json.load(save)
         save.close()
         capitol = float(data["capitol"])
         if capitol > cap:
            capitol -= cap
            available_cap = cap
         elif capitol > 0:
            available_cap = capitol
            capitol = 0.0
         data["capitol"] = round(capitol, 2)

         save = open(cls._save_file, "w")
         json.dump(data, save)
         save.close()
      
      return available_cap
      

   def __new__(cls):
      if cls._instance is None: 
         with cls._lock:
         # Another thread could have created the instance
         # before we acquired the lock. So check that the
         # instance is still nonexistent.
            if not cls._instance:
               cls._instance = super().__new__(cls)
      return cls._instance
   
def capital_user():
   for _ in range(30):
      rand_wait = random.random()
      rand_capitol = 5000 * random.random()
      rand_capitol = CapitolManager.take_capitol(rand_capitol)
      time.sleep(rand_wait)
      CapitolManager.add_capitol(rand_capitol)

   
if __name__ == "__main__":
   #Test the capitol singlton
   CapitolManager.initialize(60000)
   thread_list = []
   for _ in range(60):
      thread_list.append(threading.Thread(target=capital_user))

   for thread in thread_list:
      thread.start()

   for thread in thread_list:
      thread.join()
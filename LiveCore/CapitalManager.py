import json
import os
from pathlib import Path
import threading
import time
import random

class CapitalManager():
   _save_file_path = Path()
   _instance = None
   _lock = threading.Lock()

   @classmethod
   def initialize(cls, starting_cap, save_file_name="capital.json"):
      with cls._lock:
         if not os.path.exists("Save/"):
            os.makedirs("Save/")
         cls._save_file_path = Path("Save/" + save_file_name)
         if not cls._save_file_path.is_file():
            with open(cls._save_file_path, 'w') as sv:
               sv.write('{"capital": ' + str(starting_cap) + '}')

   @classmethod
   def add_capital(cls, cap):
      with cls._lock:
         with open(cls._save_file_path, "r+") as save:
            data = json.load(save)
            capital = cap
            capital += float(data["capital"])
            data["capital"] = round(capital, 2)

            json_data = json.dumps(data, indent=3)
            save.seek(0)
            save.write(json_data)
            save.truncate()

   @classmethod
   def take_capital(cls, cap):
      available_cap = 0
      with cls._lock:
         with open(cls._save_file_path, "r+") as save:
            data = json.load(save)
            capital = float(data["capital"])
            if capital > cap:
               capital -= cap
               available_cap = cap
            elif capital > 0:
               available_cap = capital
               capital = 0.0
            data["capital"] = round(capital, 2)

            json_data = json.dumps(data, indent=3)
            save.seek(0)
            save.write(json_data)
            save.truncate()
      
      return available_cap
   
   @classmethod
   def get_available_capital(cls):
      with cls._lock:
         with open(cls._save_file_path, "r") as save:
            data = json.load(save)
            return data["capital"]      

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
      rand_capital = 5000 * random.random()
      if CapitalManager.get_available_capital() > rand_capital:
         rand_capital = CapitalManager.take_capital(rand_capital)
         time.sleep(rand_wait)
         CapitalManager.add_capital(rand_capital)
      else:
         time.sleep(rand_wait)

def threadTest():
   #Test the capital singlton
   CapitalManager.initialize(60000)
   thread_list = []
   for _ in range(60):
      thread_list.append(threading.Thread(target=capital_user))

   for thread in thread_list:
      thread.start()

   for thread in thread_list:
      thread.join()

def simpleTest():
   CapitalManager.initialize(60000)

   cap = CapitalManager.get_available_capital()
   print(cap)
   CapitalManager.take_capital(cap)

   print(CapitalManager.get_available_capital())

   CapitalManager.add_capital(cap)

   print(CapitalManager.get_available_capital())

   
if __name__ == "__main__":
   #simpleTest()
   threadTest()
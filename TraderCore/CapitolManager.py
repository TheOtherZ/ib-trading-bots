import threading
import time
import random

class CapitolManager():
   _instance = None
   _lock = threading.Lock()
   _capitol = 0.0

   @classmethod
   def add_capitol(cls, cap):
      with cls._lock:
         cls._capitol += cap

   @classmethod
   def take_capitol(cls, cap):
      available_cap = 0
      with cls._lock:
         if cls._capitol > cap:
            cls._capitol -= cap
            available_cap = cap
         elif cls._capitol > 0:
            available_cap = cls._capitol
            cls._capitol = 0
      
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
   CapitolManager.add_capitol(60000.0)
   thread_list = []
   for _ in range(60):
      thread_list.append(threading.Thread(target=capital_user))

   for thread in thread_list:
      thread.start()

   for thread in thread_list:
      thread.join()

   print(CapitolManager._capitol)
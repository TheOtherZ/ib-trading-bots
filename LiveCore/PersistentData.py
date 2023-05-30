import pickle

import os
import json

from pathlib import Path

class PersistentData(object):
   save_file = None
   data = None

   def __init__(self, save_dir: Path, save_file_name: str) -> None:
      self.save_file = save_dir / save_file_name
      if not save_dir.exists():
         print(f"Save directory not exist, creating: {save_dir}")
         os.makedirs(save_dir)

   def commit_store(self, file_name: str) -> None:
      """ Will overrite!"""
      save_file = self.save_directory / file_name
      with open(save_file, 'w') as f:
         json.dump(self.data, f)

   def read_store(self, file_name: str) -> dict:
      save_file = self.save_directory / file_name
      data = None
      with open(save_file, 'r') as f:
         data = json.load(f)
      
      return data
   
   def touch_store(self, file_name) -> None:
      save_file = self.save_directory / file_name
      if not save_file.is_file():
         print(f"Save file does not exist, creating: {save_file}")
         with open(save_file, 'w') as sv:
            sv.write("{}")

class TestClass(object):
   profit = 0
   drawdown = 0
   num_trades = 5
   short_trades = 0
   long_trades = 24
   stop_trades = 0
   win_trades = 0
   win_percent = 25.6
   def __init__(self) -> None:
      self.data_list = []
      for x in range(50):
         self.data_list.append(x)



if __name__ == "__main__":
   #  save_dir = Path("Save/")
   #  data_store = PersistentData(save_dir)

   #  file_save = "test.json"
   #  test_data = {"key1": {"subkey1": [0, 1, 2, 3],
   #                        "subkey2": [None, "foo", "bar"]},
   #               "key2": "lorumipsum"}
    
   #  data_store.commit_store(file_save, test_data)

   #  vals = data_store.read_store(file_save)
   #  print(vals)

   data_obj = TestClass()

   with open("Save/test.pkl", 'wb') as f:
      pickle.dump(data_obj, f)

   new_data_obj = None
   with open("Save/test.pkl", 'rb') as f:
      new_data_obj = pickle.load(f)

   print(new_data_obj.data_list)
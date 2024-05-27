from idaapi import *
from ida_search import *
from ida_funcs import *

cnt = 0
my_pattern = b'\x55\x8B\xEC'

def is_function(start_addr):
   content = get_bytes(start_addr, 3, False)
   if content == my_pattern:
      return True
   return False

addr = find_unknown(0, 1)
while addr != BADADDR:
   is_valid = is_function(addr)
   if is_valid:
      add_func(addr)
      print(hex(addr))
      cnt += 1
   addr = find_unknown(addr, 1)


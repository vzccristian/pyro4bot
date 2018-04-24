from getkey import getkey, keys
key = getkey()
if key == keys.UP:
    print("up")
elif key == keys.DOWN:
    print("d")
elif key == 'a':
    print("a")
elif key == 'Y':
   print("Y")
else:
  # Handle other text characters
  buffer = buffer+ str(key)
  print(buffer)

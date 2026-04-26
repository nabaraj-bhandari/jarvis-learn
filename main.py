file = open("test.txt", "w")

try:
    file.write("Writing updated")
except Exception as e:
    print(f"Error writing file: {e}")
finally:
    file.close()

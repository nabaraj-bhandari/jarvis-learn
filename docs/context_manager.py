file = open("test.txt", "w")

try:
    file.write("Writing updated")
except Exception as e:
    print(f"Error writing file: {e}")
finally:
    file.close()


with open("newfile.txt", "w") as file:
    file.write("This is new file created using context manager")

from pathlib import Path

print("Current working directory:")
print(Path.cwd())

print("Iterate all files in current working directory:")
for p in Path().iterdir():
    print(p)

print("Folders and Files:")
my_dir = Path("docs")
my_file = Path("test.txt")

print(my_dir)  # whole name
print(my_file)

print(my_dir.suffix)  # extensions
print(my_file.suffix)

print(my_dir.stem)  # name only
print(my_file.stem)

new_file = my_dir / "newtext.txt"  # 2 methods of joining path and files
new_file1 = my_dir.joinpath("newtext.txt")

print(new_file)
print(new_file1)

print(my_file.exists())  # check if exists or not
print(new_file.exists())
print(my_dir.exists())

print("Check Parent Dir:")
print(new_file.parent.absolute())
print(new_file.parent.parent.absolute())

print("Working with paths:")
print(Path().absolute())
print(Path(__file__))
print(Path("..").resolve())
print(Path("~").resolve())  # doesnot work as expected
print(Path("~").expanduser())  # works as expected
print(Path(__file__).resolve())
print(Path(__file__).resolve().parent)

print("Searching a pattern in a folder:")
home_dir = Path("~").expanduser()  # use case
config_dir = home_dir / ".config"

print("NOTE: rglob -> sub-directories & case_sensitive param(default=True)")
for p in config_dir.glob("*.json", case_sensitive=False):
    print(p)

import os, shutil

def main():
    os.makedirs("/output", exist_ok=True)
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    shutil.copyfile(src, "/output/entry.png")

if __name__ == "__main__":
    main()

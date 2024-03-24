import json 
import os


def main():
    with open("./server/server/database.json", 'w') as  file:
        json.dump({"users": []}, file)

if __name__ == '__main__':
    main()
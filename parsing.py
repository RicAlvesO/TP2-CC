import argparse
from ast import main

def parseFile(file):
    f = open(file, 'r')
    lines = f.readlines()
    for line in lines:
        if line=='\n' or line=='\r' or line[0]=='#':
            continue
        else:
            list = line.split(' ')
            print(list)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="the file to parse")
    args = parser.parse_args()
    parseFile(args.file)

if __name__ == "__main__":
    main()
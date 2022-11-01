import argparse
from ast import main

def parseFile(file):
    f = open(file, 'r')
    lines = f.readlines()
    for line in lines:
        if line=='\n' or line=='\r' or line[0]=='#' or line.startswith('#'):
            continue
        else:
            list = line.split(' ')
            list[2] = list[2].replace('\n', '')
            if list[1]=='DB':
                #setSP(list[0], list[2])
                print('DB',list[0],list[2])
            elif list[1]=='SP':
                print('DW',list[0],list[2])
            elif list[1]=='SS':
                print('DW',list[0],list[2])
            elif list[1]=='DD':
                print('DD',list[0],list[2])
            elif list[1]=='ST':
                if list[0]=='root':
                    #stList(list[2])
                    print('ST',list[0],list[2])
            elif list[1]=='LG':
                if list[0]=='all':
                    #registerActivity(list[2])
                    print('LG',list[0],list[2])
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="the file to parse")
    args = parser.parse_args()
    parseFile(args.file)

if __name__ == "__main__":
    main()
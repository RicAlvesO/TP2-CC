import argparse
from ast import main


def parse_config(file):
    dic = {}
    f = open(file, 'r')
    lines = f.readlines()
    for line in lines:
        if line=='\n' or line=='\r' or line[0]=='#' or line.startswith('#'):
            continue
        else:
            list = line.split(' ')
            list[2] = list[2].replace('\n', '')
            if list[1]=='DB':
                if 'ADDRESS' not in dic:
                    dic['ADDRESS'] = list[0].split(':')[0]
                    if len (list[0].split(':')) > 1:
                        dic['PORT'] = (int)(list[0].split(':')[1])
                    else:
                        dic['PORT'] = 53

                if list[1] in dic:
                    dic['DB'].append(list[2])
                else:
                    dic['DB'] = [list[2]]
            elif list[1]=='SP':
                ip = list[2].split(':')
                if len(ip) == 1:
                    ip.append(53)
                if list[1] in dic:
                    dic['SP'].append((ip[0],int(ip[1])))
                else:
                    dic['SP'] = [(ip[0],int(ip[1]))]
            elif list[1]=='SS':
                ip = list[2].split(':')
                if len(ip) == 1:
                    ip.append(53)
                if list[1] in dic:
                    dic['SS'].append((ip[0],int(ip[1])))
                else:
                    dic['SS'] = [(ip[0],int(ip[1]))]
            elif list[1]=='DD':
                ip = list[2].split(':')
                if len(ip) == 1:
                    ip.append(53)
                if list[1] in dic:
                    dic['DD'].append((ip[0],int(ip[1])))
                else:
                    dic['DD'] = [(ip[0],int(ip[1]))]
            elif list[1]=='ST':
                if list[1] in dic:
                    dic['ST'].append((list[0],list[2]))
                else:
                    dic['ST'] = [(list[0],list[2])]
            elif list[1]=='LG':
                if list[1] in dic:
                    dic['LG'].append((list[0],list[2]))
                else:
                    dic['LG'] = [(list[0],list[2])]
    if 'SP' not in dic:
        dic['TYPE'] = 'SP'
    elif 'SS' not in dic:
        dic['TYPE'] = 'SS'
    else:
        dic['TYPE'] = 'SR'
    return dic
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="the file to parse")
    args = parser.parse_args()
    dictionary = parse_config(args.file)
    print (dictionary)
    

if __name__ == "__main__":
    main()
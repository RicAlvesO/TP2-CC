import argparse

# Método usado para fazer o parser de um ficheiro de configuração
# file: Ficheiro de configuração 
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
                if 'ADDRESS' not in dic:
                    dic['ADDRESS'] = list[0].split(':')[0]
                    if len (list[0].split(':')) > 1:
                        dic['PORT'] = (int)(list[0].split(':')[1])
                    else:
                        dic['PORT'] = 53
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

# Método usado para fazer o parser de um ficheiro de dados
# file: Ficheiro de dados
def parse_dataFile(file):
    dic = {}
    arro = ''
    ttl = ''
    f = open(file, 'r')
    lines = f.readlines()
    for line in lines:
        if line=='\n' or line=='\r' or line[0]=='#' or line.startswith('#'):
            continue
        else:
            list = line.split(' ')
            if list[1]=='DEFAULT':
                list[2] = list[2].replace('\n', '')
                if list[0]== '@':
                    arro = list[2]
                if list[0]=='TTL':
                    ttl = list[2]
            elif list[1]=='NS':
                if len(list)<4:
                    list.append('-1')
                list.append('-1')
                list[3] = list[3].replace('\n', '')
                if list[0] == '@':
                    list[0] = arro
                if list[3] == 'TTL':
                    list[3] = ttl
                if list[1] in dic:
                    dic['NS'].append((list[0],list[2]+' '+list[3]+' '+list[4]))
                else:
                    dic['NS'] = [(list[0],list[2]+' '+list[3]+' '+list[4])]
            else:
                list[3] = list[3].replace('\n', '')
                if len(list)<5:
                    list.append('-1')
                else:
                    list[4] = list[4].replace('\n', '')
                if list[0] == '@':
                    list[0] = arro
                if list[3] == 'TTL':
                    list[3] = ttl
                if list[1]=='SOASP':
                    if list[1] in dic:
                        dic['SOASP'].append((list[0],list[2]+' '+list[3]+' '+list[4]))
                    else:
                        dic['SOASP'] = [(list[0],list[2]+' '+list[3]+' '+list[4])]
                elif list[1]=='SOAADMIN':
                    if list[1] in dic:
                        dic['SOAADMIN'].append((list[0],list[2]+' '+list[3]+' '+list[4]))
                    else:
                        dic['SOAADMIN'] = [(list[0],list[2]+' '+list[3]+' '+list[4])]
                elif list[1]=='SOASERIAL':
                    if list[1] in dic:
                        dic['SOASERIAL'].append((list[0],list[2]+' '+list[3]+' '+list[4]))
                    else:
                        dic['SOASERIAL'] = [(list[0],list[2]+' '+list[3]+' '+list[4])]
                elif list[1]=='SOAREFRESH':
                    if list[1] in dic:
                        dic['SOAREFRESH'].append((list[0],list[2]+' '+list[3]+' '+list[4]))
                    else:
                        dic['SOAREFRESH'] = [(list[0],list[2]+' '+list[3]+' '+list[4])]
                elif list[1]=='SOARETRY':
                    if list[1] in dic:
                        dic['SOARETRY'].append((list[0],list[2]+' '+list[3]+' '+list[4]))
                    else:
                        dic['SOARETRY'] = [(list[0],list[2]+' '+list[3]+' '+list[4])]
                elif list[1]=='SOAEXPIRE':
                    if list[1] in dic:
                        dic['SOAEXPIRE'].append((list[0],list[2]+' '+list[3]+' '+list[4]))
                    else:
                        dic['SOAEXPIRE'] = [(list[0],list[2]+' '+list[3]+' '+list[4])]
                elif list[1]=='A':
                    if list[1] in dic:
                        dic['A'].append((list[0],list[2]+' '+list[3]+' '+list[4]))
                    else:
                        dic['A'] = [(list[0],list[2]+' '+list[3]+' '+list[4])]
                elif list[1]=='CNAME':
                    if list[1] in dic:
                        dic['CNAME'].append((list[0],list[2]+' '+list[3]+' '+list[4]))
                    else:
                        dic['CNAME'] = [(list[0],list[2]+' '+list[3]+' '+list[4])]
                elif list[1]=='MX':
                    if list[1] in dic:
                        dic['MX'].append((list[0],list[2]+' '+list[3]+' '+list[4]))
                    else:
                        dic['MX'] = [(list[0],list[2]+' '+list[3]+' '+list[4])]
                elif list[1]=='PTR':
                    if list[1] in dic:
                        dic['PTR'].append((list[0],list[2]+' '+list[3]+' '+list[4]))
                    else:
                        dic['PTR'] = [(list[0],list[2]+' '+list[3]+' '+list[4])]

    return dic

# Método principal para a execução do programa 
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="the file to parse")
    args = parser.parse_args()
    dictionary = parse_dataFile(args.file)
    print (dictionary)

if __name__ == "__main__":
    main()
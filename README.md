# TP2 CC

## Description

Ce projet est un TP de la matière Conception et Construction de Logiciels (CC) de l'Université de Lorraine.

## Utilização

### Client

Para iniciar o cliente, os argumentos são:

* -IP: ip para o qual o cliente se conectará
* -Dominio: domínio da querie
* -Tipo: tipo da querie

Exemplo:

```bash
python3 dnscl.py 10.3.3.1 Barcelos.cam MX
```

### Servidor Primário e Secundário

Para iniciar o servidor, os argumentos necessários são:

* name.config : arquivo de configuração do servidor
* porta : porta para a qual o servidor se conectará
* timeout : tempo de espera para a resposta do servidor
* debug/shy : modo de execução do servidor

Exemplo:

```bash
python3 dnssp.py ./test_configs/Bastuco.config 53 8640 debug
```

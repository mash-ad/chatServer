#!/usr/bin/python3

import select
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 7777))
s.listen(10)

l = [s]
nick = {}
clients = []
cmd = ['NICK', 'QUIT', 'KILL', 'MSG', 'WHO']

def brodcast(msg, connection):
    for i in clients:
        if i != connection:
            i.sendall(msg.encode())
            i.sendall('\n'.encode())

def Disconnect(client):
    l.remove(i)
    clients.remove(i)
    print("client disconnected " + "\"%s\""%(str(nick[i.getpeername()[1]])))
    client.close()

def Error_Command(msg):
    if msg.split(' ')[0] == 'NICK':
        if len(msg.split(' ')) != 2:
            connection.sendall("invalid command\n".encode())
            return (-1)
        else:
            return (1)
    if msg.split(' ')[0] in ['QUIT', 'MSG', 'KILL']:
        if len(msg.split(' ')) < 2:
            connection.sendall("invalid command\n".encode())
            return (-1)
        else:
            return (1)

def MSG(msg, connection):
    mm = "[%s] %s"%(str(nick[connection.getpeername()[1]]), str(' '.join(msg.split(' ')[1:])))
    brodcast(mm, connection)

def KILL(msg, connection):
    mm = "[%s] %s\n"%(str(nick[connection.getpeername()[1]]), str(' '.join(msg.split(' ')[2:])))
    k_list = list(nick.keys())
    v_list = list(nick.values())
    port = int(k_list[v_list.index(msg.split(' ')[1])])
    for p in clients:
        if p.getpeername()[1] == port:
            client = p
    client.sendall(mm.encode())
    l.remove(client)
    print("client disconnected " + "\"%s\""%(str(nick[client.getpeername()[1]])))
    nick.pop(client.getpeername()[1])
    clients.remove(client)
    client.close()

def QUIT(msg, connection):
    sms = "[%s] %s"%(str(nick[connection.getpeername()[1]]), str(' '.join(msg.split(' ')[1:])))
    brodcast(sms, connection)
    print("client disconnected " + "\"%s\""%(str(nick[connection.getpeername()[1]])))
    clients.remove(connection)
    l.remove(connection)
    nick.pop(connection.getpeername()[1])
    connection.close()

def WHO(msg, connection):
    connection.sendall("[server] ".encode())
    for i in clients:
        connection.sendall(nick[i.getpeername()[1]].encode())
        connection.sendall(' '.encode())
    connection.sendall('\n'.encode())

def NICK(msg, connection):  
    name = "client " + str(nick.get(connection.getpeername()[1])) + " => " + "\"%s\""%(str(msg.split(' ')[1].strip('\n')))
    print(name)
    brodcast(name, connection)
    nick[connection.getpeername()[1]] = msg.split(' ')[1].strip('\n')

def handel(msg, connection):
    if msg.split(' ')[0] not in cmd:
        connection.sendall("invalid command\n".encode())
    elif msg.split(' ')[0] == 'WHO':
       WHO(msg, connection)
    elif msg.split(' ')[0] == 'NICK':
        print(msg)
        if Error_Command(msg) == 1:
            NICK(msg, connection)
    elif msg.split(' ')[0] == 'QUIT':
        if Error_Command(msg) == 1:
            QUIT(msg, connection)
    elif msg.split(' ')[0] == 'MSG':
        if Error_Command(msg) == 1:
            MSG(msg, connection)
    elif msg.split(' ')[0] == 'KILL':
        if Error_Command(msg) == 1:
           KILL(msg, connection)

        
while True:
    intr, nint, nit = select.select(l, [], [])
    for i in intr:
        if i == s:
            sc, a = s.accept()
            print("client connected \"%s:%i\""%(str(a[0]), int(a[1])))
            nick[sc.getpeername()[1]] = "%s:%i"%(str(a[0]), int(a[1]))
            l.append(sc)
            clients.append(sc)
        else:
            try:
                msg = i.recv(1500)
                sms = msg.decode().strip('\n')
                if len(msg) == 0:
                    Disconnect(i)
                    break
                handel(sms, i)
            except:
                continue


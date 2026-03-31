# ChitChat
A simple group chat Application using Socket Programming. Implementations are provided in both **Java** and **Python**. A simple GUI demonstration on localhost is shown below... This can be implemented over LAN connected machines by using their IP Address. #socket #socketProgramming #chat #groupchat

To watch how it is implemented click the link below:

https://www.linkedin.com/posts/deysarkarswarup_socket-socketprogramming-chat-activity-6581552689602236416-vMxm

## Java

Run the server first, then one or more clients.

```bash
javac SocketServer.java SocketClient.java
java SocketServer   # starts the server (and opens a local client)
java SocketClient   # open additional clients
```

## Python

Requires Python 3 and the standard library only (no extra packages needed).

```bash
python socket_server.py          # start the server in one terminal
python socket_client.py          # start a client in another terminal
```

The Python client (`socket_client.py`) presents a tkinter GUI and prompts you for the server IP and a nickname, mirroring the Java Swing client.

Starting with the code as is, make additions to it to increase its functionality.

## Additions

[Easy]

- Add documentation about how to use this app.
- Add logging to the server to log all connections and messages to some loggin sink (a file or a DB).

[Moderate]
- Add a current user list, and the UI required to show it (either a chat command or a UI widget)

[Advanced]
- Add a chat bot of some kind which can supply stock market news or details, sports headlines, or weather info.
- Add a way to message images

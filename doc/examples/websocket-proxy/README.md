Example of proxying websockets with nginx and wildcards.

This comprises a few parts:
1. a Python web server that handle websockets
2. An nginx configuration for proxying to that server
3. A node tool for sending data to a websocket

First, install the dependencies:

```
npm install
pip install -r requirements.txt
```

Then start the servers:

```
python server.py > /dev/null &
nginx -c `pwd`/nginx.conf
```

Now you can run `wscat` to talk to the echoing websocket:

```
wscat --connect ws://localhost:8020/socket/kata/animal
```

You can replace 'kata' and 'animal' with anything...that's the whole point of
the exercise.

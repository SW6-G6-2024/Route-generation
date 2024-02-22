# ⛷️🏂 Ski Map Project 🏂 ⛷️


## How to run

It is recommended that unless you run in Docker, you should run this in a virtual environment.

Windows:

```
py -m venv .venv
```

Unix/Mac:
```
python3 -m venv .venv
```

You should now have a .venv folder.
Once you have that, run below command in terminal:

Windows:
```
.venv\Scripts\activate
```

Unix/Mac:
```
source .venv/bin/activate
```

Run following command in terminal, to download dependencies:
```
pip install -r requirements.txt
```

To run the server, use following command:
```
flask --app main --debug run 
```

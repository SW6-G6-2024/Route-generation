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

Windows:
```
py src/main.py
```

Unix/Mac:
```
python3 src/main.py
```


## Function Documentation in Python:

We use Google style documentation for functions:

```py
def multiply_numbers(a, b):
    """
    Multiplies two numbers and returns the result.
 
    Args:
        a (int): The first number.
        b (int): The second number.
 
    Returns:
        int: The product of a and b.
    """
    return a * b
print(multiply_numbers(3,5))
```
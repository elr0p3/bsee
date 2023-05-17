# bsee
BabelFy system efficiency evaluation

## How to run?

Create an account at [Babelnet](https://babelnet.org/login), and retreive your API key.

Create a `.env` file, in the same path as `main.py`, that contains your API key just like this:
```
API_KEY=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

Finally run the following commands:

```
$ pip install -r requirements.txt

$ python main.py --csv <CSV_INFILE> -o <CSV_OUTFILE>
```

# Textualize

This is my collection of small, self-contained applications that use Textualize to demonstrate features.

You must create a virtual environment in order to run the examples:

```shell
python3 -m venv ~/virtualenv/Textualize && . ~/virtualenv/Textualize/bin/activate
pip install --upgrade pip
pip install --upgrade wheel
pip install -r requirements.txt
```

Code may work with Python 3.7, but I used Python 3.10 while writing the code.

## [Table with detail screen](table_with_detail_screen.py)

Shows a table, with sortable columns. When you click in a row, you get more details.

To run:
```shell
# Terminal 1
. ~/virtualenv/Textualize/bin/activate
textual console
```

```shell
# Terminal 2
. ~/virtualenv/Textualize/bin/activate
textual run --dev table_with_detail_screen.py
```

## Log details from an external Linux command


# Textualize

This is my collection of small, self-contained applications that use Textualize to demonstrate features.

You must create a virtual environment in order to run the examples:

```shell
python3 -m venv ~/virtualenv/Textualize
. ~/virtualenv/Textualize/bin/activate
pip install --upgrade pip
pip install --upgrade wheel
pip install --upgrade build
pip install --editable .
```

Code may work with Python 3.8, but I used Python 3.10 while writing the code.

## [Table with detail screen](kodegeek_textualize/table_with_detail_screen.py)

Shows a table, with sortable columns. When you click in a row, you get more details.

To run:
```shell
# Terminal 1
. ~/virtualenv/Textualize/bin/activate
textual console
```

Then from another terminal:

```shell
# Terminal 2
. ~/virtualenv/Textualize/bin/activate
textual run --dev --command kodegeek_textualize/table_with_detail_screen.py
```

## [Log details from an external Linux command](kodegeek_textualize/log_scroller.py)

This example runs an external command and uses async and workers to display
the output on near realtime back to the GUI

```shell
. ~/virtualenv/Textualize/bin/activate
textual run --dev --command kodegeek_textualize/log_scroller.py
```

## Building

If you want to build and install from the wheel project just do this:

```shell
. ~/virtualenv/Textualize/bin/activate
python -m build
pip install dist/KodegeekTextualize-*-py3-none-any.whl
```

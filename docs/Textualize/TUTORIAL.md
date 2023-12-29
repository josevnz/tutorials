# Crash course to Textual

Python on Linux has nice GUI (Graphic User Interface) development libraries like [TkInter](https://docs.python.org/3/library/tkinter.html), but what if you cannot run graphical applications?

Text terminals, are available on not just Linux but BSD and other great Unix like operating systems. And if you write code in Python you should be using [Textual](https://textual.textualize.io/)

So what is Textual?

> Textual is a Rapid Application Development framework for Python, built by Textualize.io.
> Build sophisticated user interfaces with a simple Python API. Run your apps in the terminal or a web browser!

In this quick introduction, I will show you 2 examples of what you can do with Textual and where you can go after that

## Installation

First create a virtual environment

```shell
python3 -m venv ~/virtualenv/Textualize
```

Then you can either clone the Git repository and make an editable distribution:

```shell
. ~/virtualenv/Textualize/bin/activate
pip install --upgrade pip
pip install --upgrade wheel
pip install --upgrade build
pip install --editable .
```

Or just Install from Pypi.org:

```shell
. ~/virtualenv/Textualize/bin/activate
pip install --upgrade KodegeekTextualize
```

## Our first application: A log scroller

![Log scroller, select commands to run](output_of_multiple_well_known_unix_commands_2023-12-28T19_13_32_605621.svg)


### Display results on a separate screen

![The results of the command, pretty print](output_of_multiple_well_known_unix_commands_2023-12-28T19_13_40_503695.svg)

*TODO*

## Second example: A table with race results

![Racing summary table](summary_2023-12-28T19_05_20_213933.svg)

This example shows you how to display race results on a table (Using a DataTable widget). The application allows you to:

* Sort by column 
* Click on a row to show race details on a full window
* Search the table and show racer details or run application commands

### Using screens to show more complex views

![Runner details, using a markdown renderer](summary_2023-12-28T19_05_44_404837.svg)

### You can search too, using the command palette

![](summary_2023-12-28T19_05_55_822030.svg)

## Debugging a Textual application

*TODO*

## What is next

* You should definitely take a look at the [official tutorial](https://textual.textualize.io/tutorial/). Lots of examples and pointers to the reference [API](https://textual.textualize.io/api/).
* Textual can use widgets from the project that started all, [Rich](https://github.com/Textualize/rich). I think some, if not any of these components will get merged into Textual at some point. Textual framework is more capable for complex applications using a high level API, but Rich has lots of nice features.
* [Textual-web](https://github.com/Textualize/textual-web) is a promising project, that will allow you to run Textual applications on a browser. It is less mature than Textual but is evolving really fast.
* Finally, [check the projects](https://www.textualize.io/projects/). There are a lot of useful Open Source applications on the portfolio.
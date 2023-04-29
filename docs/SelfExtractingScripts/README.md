# Packaging software and data with self compressed scripts

Sometimes, you need a quick and reliable way to distribute data or software to users that doesn't involve using a package manager (for example, the end user may not have root access to install an application).

It's true that this issue could be tackled by using containers and Podman or Docker, but what if they're not available on the destination system? What if one of the requirements is for the application to work on a bare-metal environment?

You could use Python with `pip` (and you probably know that you can package non-Python artifacts, too) but then you may be faced with some installation limitations (a virtual environment, or the `--user` option), not to mention that you need boilerplate code to [package your code](https://opensource.com/article/21/11/packaging-python-setuptools).

So is everything lost? Fear not! In this article, I demonstrate a very small but effective technique that you can use to write a self-extracting script that doesn't require elevated privileges.

## Setup

Damiaan Zwietering has a cool [git repository](https://gitlab.com/dzwietering/corona/) about Corona Virus with data and visualizations (Jupyter books, Excel spreadsheets), but no installer. Suppose you want to give this to your users, but they don't have access to Git. You do, and you can create a self-extracting installer for your users.

First, so you have some sample data to work with, clone the repository to your home directory:

```shell=
$ git clone \
https://gitlab.com/dzwietering/corona.git
```

Of course, in real life you'd already have data that you want to distribute. 
In this case, there's now a lot of data and a not-so-shallow directory structure, but you can create a [tar](https://opensource.com/article/17/7/how-unzip-targz-file) file using the `git archive` command:

```shell=
$ cd $HOME/corona
$ git archive --verbose --output $tempdir/corona.tar.gz HEAD
```

For the sake of this example, this is the file you want to share with your users.

## Structure of our self extracting script

The self-extracting script is split into the following sections:

1. Code that helps users extract the data (the "payload")
2. An anchor separating data (to be extracted) from the script
3. Finding the position for the anchor, and extracting the data that comes *after* it.

Bash, as it turns out, is pretty good at defining a script this way.

## Creating the payload

Here is an idea: Say you need to distribute a directory with a bunch of scripts and also data. You want to ensure you keep your permissions and structure intact, and you want the user to just "unpack" this into their home directory.

This sounds like a job for the `tar` command. But, for the sake of argument, say your users don't know how to use `tar`, or they want special options when installing the `tar` file (like extracting only a specific file).

Another issue is that your tar archive is a binary file. If you want to send it by email, you have to encode it properly with uuencode or base64 so it can be transmitted safely.

What to do? Don't throw away the tar file yet. Instead, prepare it so you can *append it* to a bash script (which you'll write shortly):

```shell=
$ base64 $tempdir/corona.tar.gz > $tempdir/corona_payload
$ file $tempdir/corona_payload
/tmp/tmp.8QNdzdKEkG/corona_payload: ASCII text
```

## Extracting data from a tar file

You can either dump all of the contents into a new directory:

```shell=
$ newbase=$HOME/coronadata
$ test ! -d $newbase && /bin/mkdir --parents --verbose $newbase
$ tar --directory $newbase \
--file corona.tar.gz --extract --gzip --verbose
```

Or you can extract just part of it, such as the measures test and experiment directories:

```shell=
$ newbase=$HOME/coronadata
$ test ! -d $newbase && /bin/mkdir --parents --verbose $newbase
$ tar --directory $newbase --file corona.tar.gz \
--extract --gzip --verbose measures experiment test
```

For this exercise, extract the whole thing to a base directory (like $HOME) so the end result is:

```shell=
$HOME/$COVIDUSERDIR
```

## Anatomy of the self-extracting script

Below is the code of the [self extracting script](https://github.com/josevnz/tutorials/raw/main/SelfExtractingScripts/covid_extract.sh) itself. This, you can save on Git and reuse for other deployments. Things to notice:

* SCRIPT_END: The position where the payload starts inside the script.
* Sanitize user input!
* Once you figure out the position of the metadata, you extract it from the script ($0), decode it back to binary, and then unpack it.

```shell=
#!/usr/bin/env bash
# Author: Jose Vicente Nunez
SCRIPT_END=$(/bin/grep --max-count 2 --line-number ___END_OF_SHELL_SCRIPT___ "$0"| /bin/cut --field 1 --delimiter :| /bin/tail -1)|| exit 100
((SCRIPT_END+=1))
basedir=
while test -z "$basedir"; do
    read -r -p "Where do you want to extract the COVID-19 data, relative to $HOME? (example: mydata -> $HOME/mydata. Press CTRL-C to abort):" basedir
done
:<<DOC
Sanitize the user input. This is quite restrictive, so it depends of the real application requirements.
DOC
CLEAN=${basedir//_/}
CLEAN=${CLEAN// /_}
CLEAN=${CLEAN//[^a-zA-Z0-9_]/}
if [ ! -d "$HOME/$CLEAN" ]; then
    echo "[INFO]: Will try to create the directory $HOME/$CLEAN"
    if ! /bin/mkdir --parent --verbose "$HOME/$CLEAN"; then
        echo "[ERROR]: Failed to create $HOME/$CLEAN"
        exit 100
    fi
fi

/bin/tail --lines +"$SCRIPT_END" "$0"| /bin/base64 -d| /bin/tar --file - --extract --gzip --directory "$HOME/$CLEAN"

exit 0
# Here's the end of the script followed by the embedded file
___END_OF_SHELL_SCRIPT___
```

So how do we add the payload to our script? Just put together the two pieces with a little bit of `cat` glue:

```shell=
$ cat covid_extract.sh \
$tempdir/corona_payload > covid_final_installer.sh
```

Make it executable:

```shell=
$ chmod u+x covid_final_installer.sh
```

You can see how the [installer combined with the payload](https://github.com/josevnz/tutorials/raw/main/SelfExtractingScripts/covid_final_installer.sh). It's big because it contains the payload.

## Running the installer

Does it work? Test it out for yourself:

```shell=
$ ./covid_final_installer.sh 
Where do you want to extract the COVID-19 data, relative to /home/josevnz? (example: mydata -> /home/josevnz/mydata. Press CTRL-C to abort):COVIDDATA
[INFO]: Will try to create the directory /home/josevnz/COVIDDATA
/bin/mkdir: created directory '/home/josevnz/COVIDDATA'

$ tree /home/josevnz/COVIDDATA
/home/josevnz/COVIDDATA
├── acaps_covid19_government_measures_dataset_0.xlsx
├── acaps_covid19_government_measures_dataset.xlsx
├── COVID-19-geographic-disbtribution-worldwide.xlsx
├── EUCDC.ipynb
├── experiment
...
```

## Self-extracting installers are useful

If find self-extracting installers useful for many reasons.

First, you can make them as complicated or simple as you want them to be. The most complicated part is dictating where the payload should be extracted.

And it's useful to know this technique, because this can be used by malware installers. Now you're more prepared to spot code like this in a script. Just as importantly, you now know how to prevent shell injection misuse by *validating user input* in your own self-extracting scripts.

There are [good tools out there to automate this](https://makeself.io/). Give them a try (but check their code first).


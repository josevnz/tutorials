# 20 single line commands you would not be able to live without on Linux

> Every Linux user has their favorite one line command. In this article we will share 20 of them with you

(By Ricardo Gerardi, Roberto Nozaki, Anthony Critelli and Jose Nunez)

By the end of this article, you will have:

* A list of 20 commands that will make your tasks easier when working on Linux
* Will show you the posibilities of combinining simple commands to create more powerful commands
* Definitely have fun running those :laughing: 


## Without an specific order of importance here they are:

### 1 Applying a command on files with different names:

The shell '{}' operator is great for this

```shell
mkdir -p -v \
/home/josevnz/tmp/{dir1,anotherdir,similardir}
```

### 2 Edit a file in place.

You want to replace a string on one or more file, without using an editor? Sure, sed to the rescue:

```shell=
/bin/sed -i 's#ORIGINAL_VALLUE#NEW_VALUE#g' myfile1 myfile2
```

But wait, Perl lovers will tell you they can do the same:

```shell=
/bin/perl -p -i -e 's#ORIGINAL#NEW_VALUE#' myfile1 myfile2
```

### 3 You need to share a file quickly, so you use a webserver

Raise your hand if you haven't use this at least *once*:

```shell=
cd $mydir && python3 -m http.server 8888
```

### 4 Downloading and running a shell script in one shot

If you are in a hurry is a time saver but also you should ever, ever run an untested script like this:
```shell=
curl --silent --fail --location \
--output - \
http://localhost:8000/myscript.sh \
|/bin/bash -s
```

So if the script keeps changing and you are low in disk space, this is perfect. Also means you can execute more dynamic generated Bash commands (just by pointing the URL to the right location)

### 5 Making a backup on a remote machine, with encryption

SSH + Tar to make secure backups. It is like peanut butter and jelly:

```shell=
/bin/tar --create --directory /home/josevnz/tmp/ \
--file - *| \
ssh raspberrypi "tar --directory /home/josevnz \
--verbose --list --file -"
```

You can spicy it with compression, encryption… Just like a sandwich.

### 6 Instantaneous files

Big fan when I you  need to write multiline documents
```shell=
/bin/cat<<DOC>/my/new/file
Line1
Line2
A $VARIABLE
DOC
```

### 7 Lets search for it, include some extensions and exclude others files

The grep way (pretty fast and easy to remember)

```shell=
grep -R 'import' --include='*.java' \
--color MySourceCodeDir
```

Or the 'find' way (xargs to handle a large number of matches properly)

```shell=
find MySourceCodeDir/ -name '*.java' \
-type f -print| \
xargs /bin/grep --color 'import
```

Why find you may ask? You can tell find to execute actions with '-exec' on your files first, then pass it to the filter. Processing possibilites are endless here...


### 8.  If you think top or htop are overkill and you just want to monitor memory utilization (just checking every 5 seconds)

This is almost cheating. Repeate a command every 5 seconds and highlit the differences

```shell=
/bin/watch -n 5 -d '/bin/free -m'
```

(Or if you don't want to check the free column of 'vmstat 1').

### 9. Size of each one of my disks partitions

lsbk (ls block) + jq (to manipulate JSON on the CLI). Never been easier:

```
josevnz@dmaf5 ~]$ /bin/lsblk --json| \
/bin/jq -c  '.blockdevices[]|[.name,.size]'

["loop0","55.5M"]
["loop1","156M"]
["loop2","32.3M"]
["zram0","4G"]
["nvme0n1","476.9G"]

```

### 10. "What is": A function that tells me quickly what type a file is...

_Note_: functions are superior and can do the same as an alias:

```shell
function wi { test -n "$1" && stat \
--printf "%F\n" $1; }
```

### 11. Size of a installed [RPM](https://en.wikipedia.org/wiki/RPM_Package_Manager):

If you have an RPM based system sooner or later you will format your queries:

```shell
rpm --queryformat='%12{SIZE} %{NAME}\n' \
-q java-11-openjdk-headless
```

### 12. Total size of a group of files

Find acts as a filter, then you get the size in bytes of each file and finally you accumulate the total size...

```shell
t=0; for n in \
$(find ~/Documents -type f -name '*.py' -print| \
xargs stat --printf "%s "); do ((t+=n)); done; echo $t
```
Or if you want a function (better)

```shell
function size { t=0; test -d "$1" && for n in $(find $1 \
-type f -name '*.py' -print| \
xargs stat --printf "%s "); do ((t+=n)); done; echo $t; }

size $mydir

```

### 13 Update all the [git](https://git-scm.com/) repositories on a directory

```shell=
$ for i in */.git; do cd $(dirname $i); \
git pull; cd ..; done
```

### 14 Expose a web directory but using [containers](https://podman.io/)

```shell=
$ podman run --rm \
-v .:/usr/share/nginx/html:ro,Z \
-p 30080:80 -d nginx
```

### 15 Check the weather

Check the weather (using a function):

```shell=
$ weather() {curl -s --connect-timeout 3 \
-m 5 http://wttr.in/$1}
```

### 16 Get top 10 IPs hitting a webserver from the access log

A frequent one I use with NGINX (I think it works with Apache also) to grab the top 10 IPs hitting a webserver from the access log:

```shell
cat /var/log/nginx/access.log | \
cut -f 1 -d ' ' | \
sort | \
uniq -c | \
sort -hr | \
head -n 10
```

### 17 Rounding floats in Bash, with Python help

But you can do pretty cool stuff with Python, nut just limited to rounding numbers:

```shell=
echo "22.67892" \
| python3 -c "print(f'{round(float(input()))}')"
23
```

### 18 A mini calculator with [bc](https://man7.org/linux/man-pages/man1/bc.1p.html)

function to define a quick calculator on the command line with variable precision (default 2):

```shell
function qqbc() { echo "scale=${2:-2}; $1" | bc -l
```

Now I can perform a quick calculation like this:

```shell
$ qqbc "2/3"
.66
```

In case you need additional precision just define a second parameter:

```shell
$ qqbc "2/3" 4
.6666
```

This is called qqbc because it’s an improvement on my the old function qbc :wink:

### 19 Convert a CSV to JSON

A modification of [this popular recipe](https://wiki.python.org/moin/Powerful%20Python%20One-Liners).

```shell
python3 -c \
"import csv,json,sys;print(json.dumps(list(csv.reader(open(sys.argv[1])))))" \
covid19-vaccinations-town-age-grp.csv
```


### 20 Installing and running tools with Docker

Another favorite. If you have Docker installed and you want to run a command without installing a bunch of dependencies on your system (while doing a quick run) then this may be all you need:

```shell
docker run --rm --interactive --verbose --location --fail \
--silent --output - \
https://raw.githubusercontent.com/josevnz/tutorials/main/20%20-single-line-commands-you-would-not-be-able-to-live-without-on-Linux.md
```

This will let you run the latest version of curl from a container, to later remove it. The possibilities are endless here.

## Summary

* You saw so far how you can build powerful commands using simple commands. That is the one of the reasons Unix and Linux are so popular...
* It is not difficult to learn. Focus on remembering what a simple command do and then think about how you can mix many simple commands to make a powerful recipe!
* Always check the 'man page' or 'info command' to figure out what else the tool can do. You will be surprised than one tool can do everything without combining it with another tool.
* There are many sites on the Internet with plenty of one line examples, we hope this will lead you to write better one liners of your own.

# 6 replacements for common tools on Linux

You finally mastered a tool on Linux; That hard to earned knowledge comes at the cost of repeated usage, reading the manual pages or using a search engine (trying to avoid the bad examples that exist out there).

So what incentive you have to learn or try new tools?; I can give you a few reasons:

1. You want to be more productive, as do more in less time
2. A new tool mimics the way you work: It is nice when you use a tool, and it just works the way you expect it
3. A new tool challenge the way you do things: This is important, as we improve and so the tools and technology around us. When a tool forces you to think outside the box this is always good.

By the end of this article you should have tried few new tools that are very interesting, and you should consider using; As usual you consider the community around the tools, easy to use and functionality you need.

One last thing: The topic of "replacement tools" is always controversial, be open-minded and give them a try. There is nothing tool with the original tools that will be mention on the article.

Also for obvious reasons this article doesn't cover every available tool out there, consider it a start point.

## What do you need before trying any of these tools

* You should be familiar with the CLI on Linux. Fear not, [read this article](https://www.redhat.com/sysadmin/bash-navigation) to get started.
* Some of these tools may not be on the system and will require to elevated privileges to install (with tools like [RPM](https://www.redhat.com/sysadmin/package-linux-applications-rpm), [apt-get](https://wiki.debian.org/apt-get), etc.)
* And some actually may be better installed under your user instead of system-wide, with tools like [pip](https://www.redhat.com/sysadmin/packaging-applications-python).

OK, let's, move on and try some tools.

## Better than top: htop, glances

[top](https://www.redhat.com/sysadmin/customize-top-command) is without a doubt, one of the best swiss knifes of the resource monitoring tools on Linux. It has nice features like the ability to save stats into a file, sort columns by criteria.

### Htop

On the same spirit, the [htop](https://github.com/hishamhm/htop) command shows you more content (like how hard each CPU core is working). Below is a simple session showing how you can filter, s[ort and search processes](https://www.redhat.com/sysadmin/process-management-htop) using htop:

[![asciicast](https://asciinema.org/a/507515.svg)](https://asciinema.org/a/507515)

So what makes this tool stand apart? The user interface gives you access to powerful operations, with ease.

To install on Ubuntu:

```shell=
sudo apt-get install htop
```

Or RPM based distribution:

```shell=
sudo dnf install -y htop
```

### Glances

Glances is another tool that will give you lots of information about your system, similar to htop:

[![asciicast](https://asciinema.org/a/507522.svg)](https://asciinema.org/a/507522)

Why another tool like htop? Well, [glances](https://github.com/nicolargo/glances) has _key_ features that may make it interesting to you:

1. I can run in server mode, allowing you to connect to it using a web browser or with a REST client
2. It can export results in several formats, including Prometheus
3. You can write plugins to extend it, in Python

To install it, you can use a virtual environment or do a user installation:

```shell
pip install --user glances
```

### When you only care about memory: smem

top, htop and glances give you a full array of details about your server, but what if you only care about memory utilization?

[smem](https://github.com/kwkroeger/smem) is probably a great tool for that:

[![asciicast](https://asciinema.org/a/507535.svg)](https://asciinema.org/a/507535)

It is possible to filter by user, show totals, group usage by users and even create plots with Mathlib.

To install it on Ubuntu:

```shell
sudo apt-get install smem
```

Or Fedora Linux:

```shell
sudo dnf install -y smem
```

## ripgrep instead of grep

Grep is probably one of the most well known filtering tools out there; if you ever needed to find files by a filter then chances are you already used grep, even without knowing about it.

A nice contender is [ripgrep](https://github.com/BurntSushi/ripgrep). It is fast and has modern features than grep doesn't have:

1. You can export the output to JSON format. This is a great feature for data capture, interaction with other scripts
2. Automatic recursive directory search, skipping hidden files and common 'ignorable' backup files.

So let's start by comparing a regular recursive grep that only looks inside files with extension '*.pyb', search is case-insensitive:

```shell
[josevnz@dmaf5 ~]$ time grep --dereference-recursive --ignore-case --count --exclude '.ipynb_*' --include '*.ipynb'  death COVIDDATA/
COVIDDATA/.ipynb_checkpoints/Curve-checkpoint.ipynb:0
COVIDDATA/.ipynb_checkpoints/EUCDC-checkpoint.ipynb:37
COVIDDATA/.ipynb_checkpoints/Gammamulti-checkpoint.ipynb:11
COVIDDATA/.ipynb_checkpoints/Gammapivot-checkpoint.ipynb:11
# ... Omitted output
COVIDDATA/tweakers/zzcorwav.ipynb:10

real	0m0.613s
user	0m0.505s
sys	0m0.105s
```

Still, it is showing the Jupyter '.ipynb_checkpoints/*' checkpoint files. Let's see ripgrep (rg) in action:
```shell
[josevnz@dmaf5 ~]$ time rg --ignore-case --count --type 'jupyter' death COVIDDATA/
COVIDDATA/tweakers/zzcorwav.ipynb:10
COVIDDATA/tweakers/zzbenford.ipynb:2
COVIDDATA/tweakers/EUCDC.ipynb:19
COVIDDATA/Modelpivot.ipynb:9
COVIDDATA/experiment/zzbenford.ipynb:2
COVIDDATA/experiment/zzcorwavgd.ipynb:10
# ... Omitted output
COVIDDATA/experiment/zzcasemap.ipynb:13

real	0m0.068s
user	0m0.087s
sys	0m0.071s
```

The command line is shorter and also rg is skipping the Jupyter checkpoint files, without any extra help.

Check below to see rg in action, with a few flags:

[![asciicast](https://asciinema.org/a/507560.svg)](https://asciinema.org/a/507560)

If you are interested, you can install on Fedora Linux:

```shell
sudo dnf install ripgrep
```

Or if you have Ubuntu:
```shell
sudo apt install -y ripgrep
```

## drill (ldns) instead of dig, nslookup

Once again, if you were trying to find the IP address of a given DNS record you probably ended using dig or nslookup to do the task; These commands have been around for a long time
and have even entered/ left [the deprecation state](https://www.redhat.com/sysadmin/deprecated-linux-command-replacements).

One tool that offers same functionality and is more modern is drill (from the [lndns project](https://nlnetlabs.nl/projects/ldns/about/));

So say we want to see the MX (Mail Exchangers) for the nasa.org domain:

```shell
[josevnz@dmaf5 tutorials]$ dig @8.8.8.8 nasa.org MX +noall +answer +nocmd
nasa.org.		3600	IN	MX	5 mail.h-email.net.
```

Drill gives you the same information, plus some more:

```shell
[josevnz@dmaf5 tutorials]$ drill @8.8.8.8 mx nasa.org
;; ->>HEADER<<- opcode: QUERY, rcode: NOERROR, id: 50948
;; flags: qr rd ra ; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0 
;; QUESTION SECTION:
;; nasa.org.	IN	MX

;; ANSWER SECTION:
nasa.org.	3600	IN	MX	5 mail.h-email.net.

;; AUTHORITY SECTION:

;; ADDITIONAL SECTION:

;; Query time: 126 msec
;; SERVER: 8.8.8.8
;; WHEN: Sun Jul 10 14:31:48 2022
;; MSG SIZE  rcvd: 58
```

What does this means for the end-user, like you?

* Drill can be used as a drop-in replacement of dig.
* It is good to have a separate implementation of DNS tools, to troubleshoot and diagnose bugs.

Distribution maintainers and application developers have probably more compelling arguments to use ldns:
* Some distributions like ArchLinux called for [dns-tools removal](https://archlinux.org/todo/dnsutils-to-ldns-migration/), and use instead ldns [because of dependency management and bugs](https://lists.archlinux.org/pipermail/arch-dev-public/2013-March/024588.html).
* ldns has nice bindings for Python3

Let's see in action [a small program](https://github.com/josevnz/tutorials/blob/main/ReplacementCommands/mx_list.py) that can query the list of the MX records for a given list of domains:

[![asciicast](https://asciinema.org/a/507605.svg)](https://asciinema.org/a/507605)

Installation on Fedora Linux can be done like this:
```shell
sudo dnf install -y python3-ldns ldns-utils ldns
```

Ubuntu steps:
```shell
sudo apt-get -y install ldnsutils python3-ldns
```

## One CLI to render all formats: rich-cli

Let's face it: It is quite annoying to use different tools to render different data types nicely on the command line.

For example, a JSON file (no special filtering):

```shell
[josevnz@dmaf5 ~]$ /bin/jq '.' ./.thunderbird/pximovka.default-default/sessionCheckpoints.json
{
  "profile-after-change": true,
  "final-ui-startup": true,
  "quit-application-granted": true,
  "quit-application": true,
  "profile-change-net-teardown": true,
  "profile-change-teardown": true,
  "profile-before-change": true
}
```

An XML file:

```shell
[josevnz@dmaf5 ~]$ /bin/xmllint ./opencsv-source/checkstyle-suppressions.xml
<?xml version="1.0"?>
<!DOCTYPE suppressions PUBLIC "-//Puppy Crawl//DTD Suppressions 1.0//EN" "http://www.puppycrawl.com/dtds/suppressions_1_0.dtd">
<suppressions>
    <suppress files="." checks="LineLength"/>
    <suppress files="." checks="whitespace"/>
    <suppress files="." checks="HiddenField"/>
    <suppress files="." checks="FinalParameters"/>
    <suppress files="." checks="DesignForExtension"/>
    <suppress files="." checks="JavadocVariable"/>
    <suppress files="." checks="AvoidInlineConditionals"/>
    <suppress files="." checks="AvoidStarImport"/>
    <suppress files="." checks="NewlineAtEndOfFile"/>
    <suppress files="." checks="RegexpSingleline"/>
    <suppress files="." checks="VisibilityModifierCheck"/>
    <suppress files="." checks="MultipleVariableDeclarations"/>
</suppressions>
```

A markup file? a CSV file? A Python script? You see where this is going, a different application for each type. 
Also, some of them offer syntax colorization others do not. If you want pagination then most likely you need to pipe the output to 'less' but then kiss goodbye the colorization.

Enter [Rich-cli](https://github.com/Textualize/rich-cli) (an application part of the [Textualize](https://github.com/Textualize) project) to the rescue; Let's revisit the two files we opened before; JSON file:

```shell
[josevnz@dmaf5 ~]$ rich ./.thunderbird/pximovka.default-default/sessionCheckpoints.json
{
  "profile-after-change": true,
  "final-ui-startup": true,
  "quit-application-granted": true,
  "quit-application": true,
  "profile-change-net-teardown": true,
  "profile-change-teardown": true,
  "profile-before-change": true
}
```

The same XML file we did earlier:
```shell
[josevnz@dmaf5 ~]$ rich ./opencsv-source/checkstyle-suppressions.xml
<?xml version="1.0"?>

<!DOCTYPE suppressions PUBLIC "-//Puppy Crawl//DTD Suppressions 1.0//EN"
        "http://www.puppycrawl.com/dtds/suppressions_1_0.dtd">
<suppressions>
    <suppress files="." checks="LineLength"/>
    <suppress files="." checks="whitespace"/>
    <suppress files="." checks="HiddenField"/>
    <suppress files="." checks="FinalParameters"/>
    <suppress files="." checks="DesignForExtension"/>
    <suppress files="." checks="JavadocVariable"/>
    <suppress files="." checks="AvoidInlineConditionals"/>
    <suppress files="." checks="AvoidStarImport"/>
    <suppress files="." checks="NewlineAtEndOfFile"/>
    <suppress files="." checks="RegexpSingleline"/>
    <suppress files="." checks="VisibilityModifierCheck"/>
    <suppress files="." checks="MultipleVariableDeclarations"/>
</suppressions>
```

Please check the demo below to see how the rendering is done on multiple file types, all with a single command:

[![asciicast](https://asciinema.org/a/507593.svg)](https://asciinema.org/a/507593)

Installation is trivial with pip:

```shell
pip install --user rich-cli
```

## Conclusion

* You don't need to settle with the default tools that come with the operating system; many of them out there offer new functionality that will make your more productive and if more people like you use them, they become the default tools.
* Also, when evaluating this tools look ad their community and how often the tools are updated for bugs, new features. An active community is as important as the tool itself.


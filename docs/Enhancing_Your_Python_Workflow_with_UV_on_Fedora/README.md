# Enhancing Your Python Workflow with UV on Fedora

## Installation

If you have a Linux installation you can install uv like this:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

What about an RPM? [Fedora lists](https://src.fedoraproject.org/rpms/uv) several packages since version 40. So there you can do something like this:

```shell
sudo dnf install uv
```

Or get yourself an RPM using the statically compiled binaries from Astral and a little help from Podman and [fpm](https://www.freecodecamp.org/news/getting-started-with-fpm/):

```shell
josevnz@dmaf5 docs]$ podman run --mount type=bind,src=$HOME/tmp,target=/mnt/result --rm --privileged --interactive --tty fedora:37 bash
[root@a9e9dc561788 /]# gem install --user-install fpm
...
[root@a9e9dc561788 /]# curl --location --fail --remote-name https://github.com/astral-sh/uv/releases/download/0.6.9/uv-x86_64-unknown-linux-gnu.tar.gz
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
100 15.8M  100 15.8M    0     0  8871k      0  0:00:01  0:00:01 --:--:-- 11.1M
[root@a9e9dc561788 /]# fpm -t rpm -s tar --name uv --rpm-autoreq --rpm-os linux --rpm-summary 'An extremely fast Python package and project manager, written in Rust.' --license 'Apache 2.0' --version v0.6.9 --depends bash --maintainer 'Jose Vicente Nunez <kodegeek.com@protonmail.com>' --url https://github.com/astral-sh/uv  uv-x86_64-unknown-linux-gnu.tar.gz
Created package {:path=>"uv-v0.6.9-1.x86_64.rpm"}
mv uv-v0.6.9-1.x86_64.rpm /mnt/result/
# exit the container
exit
```

You can then install on /usr/local, using `--prefix`:
```shell
sudo -i
[root@a9e9dc561788 /]# rpm --force --prefix /usr/local -ihv /mnt/result/uv-v0.6.9-1.x86_64.rpm 
Verifying...                          ################################# [100%]
Preparing...                          ################################# [100%]
Updating / installing...
   1:uv-v0.6.9-1                      ################################# [100%]
[root@a9e9dc561788 /]# rpm -qil uv-v0.6.9-1
Name        : uv
Version     : v0.6.9
Release     : 1
Architecture: x86_64
Install Date: Sat Mar 22 23:32:49 2025
Group       : default
Size        : 40524181
License     : Apache 2.0
Signature   : (none)
Source RPM  : uv-v0.6.9-1.src.rpm
Build Date  : Sat Mar 22 23:28:48 2025
Build Host  : a9e9dc561788
Relocations : / 
Packager    : Jose Vicente Nunez <kodegeek.com@protonmail.com>
Vendor      : none
URL         : https://github.com/astral-sh/uv
Summary     : An extremely fast Python package and project manager, written in Rust.
Description :
no description given
/usr/local/usr/lib/.build-id
/usr/local/usr/lib/.build-id/a1
/usr/local/usr/lib/.build-id/a1/8ee308344b9bd07a1e3bb79a26cbb47ca1b8e0
/usr/local/usr/lib/.build-id/e9
/usr/local/usr/lib/.build-id/e9/4f273a318a0946893ee81326603b746f4ffee1
/usr/local/uv-x86_64-unknown-linux-gnu/uv
/usr/local/uv-x86_64-unknown-linux-gnu/uvx
```


## Using UV to run everyday tools like Ansible, Glances, Flake8, Autopep8

One of the best things about uv is that you can download and install tools on your account with less typing.

One of my favorite tools, glances, can be installed with pip on the user account:

```shell
pip install --user glances
glances
```

But that will pollute my python installation with glances dependencies. So the best next thing is to isolate it on a virtual environment:

```shell
python -m venv ~/venv/glances
. ~/venv/glances/bin/activate
pip install glances
glances
```

You can see now where this is going. Instead, I could do the following with uv:

```shell
uv tool run glances
```

OK, a single line, This creates a temporary environment which is discarded once we're done with the tool.

Let me show you the equivalent command, it is called `uvx`:

```shell
uvx --from glances glances
```

If the command and the distribution matches then we can skip explicitly where it comes '--from':

```shell
uvx glances
```

Less typing, uv created a virtual environment for me and downloaded glaces there. Say that I want to use a different Python 3.12 to run it:

```shell
uvx --from glances --python 3.12 glances
```

If you call this command again, uvx will re-use the virtual environment it created, using the Python interpreter of your choice.

### It is a good idea to install custom Python interpreters?

Letting developers and DevOps [install custom Python interpreters](https://docs.astral.sh/uv/concepts/python-versions/#installing-a-python-version) can be a time saver, specially if you can contain your installation using a virtual environment.

Say than you are ready to use Python:

```shell
[josevnz@dmaf5 ~]$ which uv
~/.local/bin/uv
Installed Python 3.13.1 in 3.21s
 + cpython-3.13.1-linux-x86_64-gnu
```

So where it was installed? Let search for it and run it:
```shell
# Is not the system python3
[josevnz@dmaf5 ~]$ which python3
/usr/bin/python3
# And is not in the default PATH
[josevnz@dmaf5 ~]$ which python3.13
/usr/bin/which: no python3.13 in (/home/josevnz/.cargo/bin:/home/josevnz/.local/bin:/home/josevnz/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/home/josevnz/.local/share/JetBrains/Toolbox/scripts)
# Let's find it (Pun intended)
[josevnz@dmaf5 ~]$ find ~/.local -name python3.13
/home/josevnz/.local/share/uv/python/cpython-3.13.1-linux-x86_64-gnu/bin/python3.13
/home/josevnz/.local/share/uv/python/cpython-3.13.1-linux-x86_64-gnu/include/python3.13
/home/josevnz/.local/share/uv/python/cpython-3.13.1-linux-x86_64-gnu/lib/python3.13
# Let's run it
[josevnz@dmaf5 ~]$ /home/josevnz/.local/share/uv/python/cpython-3.13.1-linux-x86_64-gnu/bin/python3.13
Python 3.13.1 (main, Jan 14 2025, 22:47:38) [Clang 19.1.6 ] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 
```

Interesting. Now say that I want to install autopep8 using this Python3.13
```shell
[josevnz@dmaf5 ~]$ uv tool install autopep8 --python 3.13.1
Resolved 2 packages in 158ms
Prepared 2 packages in 72ms
Installed 2 packages in 8ms
 + autopep8==2.3.2
 + pycodestyle==2.12.1
Installed 1 executable: autopep8
```

Did the new autopep8 re-used the Python3.13 we installed before? 

```shell
[josevnz@dmaf5 ~]$ which autopep8
~/.local/bin/autopep8
[josevnz@dmaf5 ~]$ head -n 1 ~/.local/bin/autopep8
#!/home/josevnz/.local/share/uv/tools/autopep8/bin/python
[josevnz@dmaf5 ~]$ ls -l /home/josevnz/.local/share/uv/tools/autopep8/bin/python
lrwxrwxrwx. 1 josevnz josevnz 83 Mar 22 16:50 /home/josevnz/.local/share/uv/tools/autopep8/bin/python -> /home/josevnz/.local/share/uv/python/cpython-3.13.1-linux-x86_64-gnu/bin/python3.13
```

Very good, we are not wasting space with duplicate python interpreter installations. 

But what if we want to re-use the existing system python3? If we force the installation, we will have a duplicate?

my system has Python 3.11, let's force the autopep8 and see what happens:

```shell
josevnz@dmaf5 ~]$ uv tool install autopep8 --force --python 3.11 
Resolved 2 packages in 3ms
Uninstalled 1 package in 1ms
Installed 1 package in 3ms
 ~ autopep8==2.3.2
Installed 1 executable: autopep8
[josevnz@dmaf5 ~]$ which autopep8
~/.local/bin/autopep8
[josevnz@dmaf5 ~]$ head -n 1 ~/.local/bin/autopep8
#!/home/josevnz/.local/share/uv/tools/autopep8/bin/python3
[josevnz@dmaf5 ~]$ ls -l /home/josevnz/.local/share/uv/tools/autopep8/bin/python3
lrwxrwxrwx. 1 josevnz josevnz 6 Mar 22 16:56 /home/josevnz/.local/share/uv/tools/autopep8/bin/python3 -> python
[josevnz@dmaf5 ~]$ ls -l /home/josevnz/.local/share/uv/tools/autopep8/bin/python
lrwxrwxrwx. 1 josevnz josevnz 19 Mar 22 16:56 /home/josevnz/.local/share/uv/tools/autopep8/bin/python -> /usr/bin/python3.11
```

It is smart enough to use the system Python.

Say that you want to make this Python3 version the default for your user? There is a way to do that using the experimental flag `--preview` and `--default` (makes it python3):

```shell
[josevnz@dmaf5 ~]$ uv python install 3.13 --default --preview
Installed Python 3.13.1 in 23ms
 + cpython-3.13.1-linux-x86_64-gnu (python, python3, python3.13)
# Which one is now python3
[josevnz@dmaf5 ~]$ which python3
~/.local/bin/python3
# Is python3.13 our default python3?
[josevnz@dmaf5 ~]$ which python3.13
~/.local/bin/python3.13
```

What if you have company policies that discourages downloading a Python runtime, or you want to enforce a more strict control?

If you create a `$XDG_CONFIG_DIRS/uv/uv.toml` or `~/.config/uv/uv.toml` file, you can put the following [settings](https://docs.astral.sh/uv/reference/settings/) there:

```toml
# ~/.config/uv/uv.toml or /etc/uv/uv.toml
# https://docs.astral.sh/uv/reference/settings/#python-preference: only-managed, *managed*, system, only-system
python-preference = "only-system"
# https://docs.astral.sh/uv/reference/settings/#python-downloads: *automatic*, manual or never
python-downloads = "manual"
```

Fedora managers had an interesting conversation about [how manage this policy](https://src.fedoraproject.org/rpms/uv/pull-request/18), worth reading. Or you can go and check the [used system uv.toml](https://src.fedoraproject.org/rpms/uv/blob/rawhide/f/uv.toml) file yourself.

To wrap this section, you can remove an installed python as well using uv:

```shell
[josevnz@dmaf5 docs]$ uv python uninstall 3.9
Searching for Python versions matching: Python 3.9
Uninstalled Python 3.9.21 in 212ms
 - cpython-3.9.21-linux-x86_64-gnu
```

#### But this still is a lot of typing

Nothing like ye old Bourne Shell (or favorite shell) cannot fix.  Put this on your ~/.profile or [environment initialization configuration file](https://fedoramagazine.org/customizing-bash/):

```shell
#  Use a function instead of an alias (deprecated but still supported)
function glances
   uvx --from glances --python 3.12 glances $*
}
```

There is a better way to install tools in our environment, once we are sure we want to keep  a tool around.

### If your tool is useful, consider installing it instead of using a transient installation.

You probably use Ansible to manage your infrastructure. And you don't want to use uv or uvx to call your favorite tools:

```shell
uv tool install --force ansible
Resolved 10 packages in 17ms
Installed 10 packages in 724ms
 + ansible==11.3.0
 + ansible-core==2.18.3
 + jinja2==3.1.6
...
```

Then we can call it without using uv nor uvx as long as you put ~/.local/bin in your PATH environment variable. You can confirm if that is the case by calling which:

```shell
which ansible-playbook
~/.local/bin/ansible-playbook
```

Another advantage of using 'tools install' is that if they are big (like Ansible), or you have a slow network connection, you only install once and next time you call it, is there. 

Last time, if you installed several python tools like this, you can upgrade them all in one shot as well with the `--upgrade` flag:

```shell
[josevnz@dmaf5 ~]$ uv tool upgrade --all
Updated glances v4.3.0.8 -> v4.3.1
 - glances==4.3.0.8
 + glances==4.3.1
Installed 1 executable: glances

```

Pretty convenient!

## Learning more

We cover a lot but there is still lots more to learn. As everything, you will need to try  to see what fits better to your style and available resources.

Below is a list of links I found useful and may also help you:

* The official [uv](https://docs.astral.sh/uv/) documentation is very complete, and you will most likely spend your time going back and forth reading it.
* Users of older Fedora distributions may take a look at the [UV Source RPM](https://src.fedoraproject.org/rpms/uv/blob/rawhide/f/uv.spec). Lots of good stuff, including Bash auto-completion for UV.
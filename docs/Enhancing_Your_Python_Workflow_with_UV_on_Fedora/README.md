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

Or you can package your own

TODO


## Using UV to run everyday tools like Ansible, Glances, Flake8, Autopep8

One of the best things about uv is that you can dowload and install tools on your account with less typing.

One of my favorite tools, glances, can be installed with pip on the user account:

```shell
pip install --user glances
glances
```

But that will polute my python installation with glances dependencies. So the best next thing is to isolate it on a virtual environment:

```shell
python -m venv ~/venv/glances
. ~/venv/glances/bin/activate
pip install glances
glances
```

You can see now where this is going. Instead I could do the following with uv:

```shell
uv tool run glances
```

OK, a single line, This creates an temporary environment which is discarded once we're done with the tool.

Let me show you the equivalent command, it is called `uvx`:

```shell
uvx --from glances glances
```

If the command and the distribution matches then we can skip explicitely where it comes '--from':

```shell
uvx glances
```

Less typing, uv created a virtual environment for me and downloaded glaces there. Say that I want to use a different Python 3.12 to run it:

```shell
uvx --from glances --python 3.12 glances
```

If you call this command again, uvx will re-use the virtual environment it created.

#### But this still is a lot of typing

Nothing like ye old Bourne Shell (or favorite shell) cannot fiX.  Put this on your ~/.profile or [environment initialization configuration file](https://fedoramagazine.org/customizing-bash/):

```
#  Use a function instead of an alias (deprecated but still supported)
function glances
   uvx --from glances --python 3.12 glances $*
}
```

There is a better way to install tools in our environment, once we are sure we want to keep them around.

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

Then we can call it without using uv nor uvx as long as you put ~/.local/bin in your PATH environment variable:

```shell
which ansible-playbook
~/.local/bin/ansible-playbook
```

If you installed several python tools like this, you can upgrade them all in one shot as well:

```shell
uv tool upgrade --all
```

Pretty convenient.

## Learning more

We cover a lot but there is still lots more to learn. As everything, you will need to try  to see what fits better to your style and available resources.

Below is a list of links I found useful and may also help you:

* The official [uv](https://docs.astral.sh/uv/) documentation is very complete and you will most likely spend your time going back and forth reading it.

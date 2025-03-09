# Enhancing Your Python Workflow with UV on Fedora

## Installation

If you have a Linux installation you can install uv like this:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

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

### If your tool is useful, consider installing it instead if

You probably use Ansible to manage your infrastructure. Say than you want a persistent installation of the tool, instead of a transitory one:

```shell
uv tool install --force ansible
Resolved 10 packages in 17ms
Installed 10 packages in 724ms
 + ansible==11.3.0
 + ansible-core==2.18.3
 + cffi==1.17.1
 + cryptography==44.0.2
 + jinja2==3.1.6
 + markupsafe==3.0.2
 + packaging==24.2
 + pycparser==2.22
 + pyyaml==6.0.2
 + resolvelib==1.0.1
...
```

Then we can call it without using uv nor uvx as long as you put ~/.local/bin in your PATH environment variable:

```shell
which ansible-playbook
~/.local/bin/ansible-playbook
```


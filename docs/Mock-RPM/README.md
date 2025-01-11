* [Why Mock](#heading-why-mock)
    
* [Packaging scenarios with Mock and Podman](#heading-packaging-scenarios-with-mock-and-podman)
    
* [Conclusion](#heading-conclusion)
    

## Why Mock

We already have Python virtual environments, so why bother to have an RPM of the same library? Well, if you want to ensure consistent deployment across different systems, RPM packaging can be beneficial. It allows for easier management and distribution of software, especially in environments where system-wide installations are preferred over virtual environments.

Let see next a few scenarios on where you can use mock.

## Packaging scenarios with Mock and Podman

### Packaging a newer version of the module, on an older Linux distribution

On this case, say we want to re-use the existing textual 0.6.2 package from Fedora 41 into Fedora 40. With Mock is possible, but to make it more secure we should run it inside a PODMAN container, which will give us more isolation from the real operating system.

```shell
mkdir --parent ---verbose $HOME/.config/containers/
/bin/cat<<EOF>$HOME/.config/containers/storage.conf
[storage]
driver = "overlay"
runroot = "/mnt/data/podman/"
graphroot = "/mnt/data/podman/"
EOF
```

We want to save the results to /mnt/result and because we use a chain of RPM, we must pass '--localrepo' instead of '--resultdir'

```shell
mkdir --parent --verbose $HOME/tmp
mkdir --parent --verbose /mnt/data/podman
TMPDIR=/mnt/data/podman podman run --mount type=bind,src=$HOME/tmp,target=/mnt/result --rm --privileged --interactive --tty fedora:40 bash
dnf install -y mock
useradd mockbuilder
usermod -a -G mock mockbuilder
chown mockbuilder /mnt/result/
su - mockbuilder
mock --localrepo /mnt/result/ --chain https://download.fedoraproject.org/pub/fedora/linux/releases/41/Everything/source/tree/Packages/p/python-rich-13.7.1-5.fc41.src.rpm https://download.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/source/tree/Packages/p/python-textual-0.62.0-2.fc41.src.rpm
```

For example, on my Raspberry PI4 with Fedora 40, the final outout looks like this:

```shell
...
INFO: Success building python-textual-0.62.0-2.fc41.src.rpm
INFO: Results out to: /mnt/result/results/default
INFO: Packages built: 2
INFO: Packages successfully built in this order:
INFO: /tmp/tmpc6651dxo/python-rich-13.7.1-5.fc41.src.rpm
INFO: /tmp/tmpc6651dxo/python-textual-0.62.0-2.fc41.src.rpm
```

Outside the container, we test the installation:

```shell
josevnz@raspberypi1:~$ sudo dnf install -y /home/josevnz/tmp/results/default/python-rich-13.7.1-5.fc41/python3-rich-13.7.1-5.fc40.noarch.rpm /home/josevnz/tmp/results/default/python-textual-0.62.0-2.fc41/python3-textual-doc-0.62.0-2.fc40.noarch.rpm /home/josevnz/tmp/results/default/python-textual-0.62.0-2.fc41/python3-textual-0.62.0-2.fc40.noarch.rpm
...
nstalled:
  python3-linkify-it-py-2.0.3-1.fc40.noarch            python3-markdown-it-py-3.0.0-4.fc40.noarch    python3-markdown-it-py+linkify-3.0.0-4.fc40.noarch  
  python3-markdown-it-py+plugins-3.0.0-4.fc40.noarch   python3-mdit-py-plugins-0.4.0-4.fc40.noarch   python3-mdurl-0.1.2-6.fc40.noarch                   
  python3-pygments-2.17.2-3.fc40.noarch                python3-rich-13.7.1-5.fc40.noarch             python3-textual-0.62.0-2.fc40.noarch                
  python3-textual-doc-0.62.0-2.fc40.noarch             python3-uc-micro-py-1.0.3-1.fc40.noarch      

Complete!
```

Note than the contents of the container will be removed from the original window once you exit, except the mounted volume. This is great, as we don’t have to worry about uninstalling building packages ourselves.

But is it perfect?

Can you use Mock to package newer code on much older distributions?

Mock works really well as long your dependencies aren't too far away from the version you are running. For example, say you want to build the RPMS for Fedora 37 instead of Fedora 40:

```shell
sudo rm -rf $HOME/tmp/results/*
TMPDIR=/mnt/data/podman podman run --mount type=bind,src=$HOME/tmp,target=/mnt/result --rm --privileged --interactive --tty fedora:37 bash
dnf install -y mock
useradd mockbuilder && usermod -a -G mock mockbuilder && chown mockbuilder /mnt/result/ && su - mockbuilder
mock --nocheck --localrepo /mnt/result/ --chain https://download.fedoraproject.org/pub/fedora/linux/releases/41/Everything/source/tree/Packages/p/python-rich-13.7.1-5.fc41.src.rpm https://download.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/source/tree/Packages/p/python-textual-0.62.0-2.fc41.src.rpm
...
Package python3-poetry-core-1.0.8-3.fc37.noarch is already installed.
Package python3-pytest-7.1.3-2.fc37.noarch is already installed.
Package python3-setuptools-62.6.0-3.fc37.noarch is already installed.
Error: 
 Problem: nothing provides requested (python3dist(pygments) < 3~~ with python3dist(pygments) >= 2.13)
```

Oh oh, Fedora 37 doesn’t provide some of the dependencies. Can we build them in chain? I Tried to add the SRPM for pygments, before building rich as it is a dependency:

```shell
mock --nocheck --localrepo /mnt/result/ --chain https://download.fedoraproject.org/pub/fedora/linux/releases/39/Everything/source/tree/Packages/p/python-pygments-2.15.1-4.fc39.src.rpm https://download.fedoraproject.org/pub/fedora/linux/releases/41/Everything/source/tree/Packages/p/python-rich-13.7.1-5.fc41.src.rpm https://download.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/source/tree/Packages/p/python-textual-0.62.0-2.fc41.src.rpm
```

Yet *two more dependencies where broken*, this time for textual on Fedora 37:

```shell
...
no matching package to install: 'python3-syrupy'
No matching package to install: 'python3-time-machine'
Not all dependencies satisfied
```

Looks like a game of trial an error. How bad it can be?

Several tries later found that *Syrupy* added a dependency on *Poetry*, which complicated things a little bit as Fedora 37 expects an older version of *Poetry*: poetry-1.1.14-1.fc37

What could you do next? Well you could try to get a version of Syrupy that works with this older version of Poetry, but that could potentially introduce vulnerabilities on your system or force you to use a version of Syrupy that doesn't work at all with Textual, because of API changes.

It is easier to work your dependencies upwards than downwards.

### Building a newer non packaged version of the software

Can mock help us with that? Textual made huge improvements and added new features on the first official release, 1.0.0. Let's see if we can take a few shortcuts to build an RPM that we can use with the system Python.

We will recycle the RPM Spec file from Textual we used before, but with a few modifications. First, let's prepare our sources again:

```shell
josevnz@raspberypi1:~$ TMPDIR=/mnt/data/podman podman run --mount type=bind,src=$HOME/tmp,target=/mnt/result --rm --privileged --interactive --tty fedora:40 bash
[root@ccae845daa84 /]# dnf install -y rpmdevtool
[root@ccae845daa84 /]# dnf install -y mock && useradd mockbuilder && usermod -a -G mock mockbuilder && chown mockbuilder /mnt/result/ && su - mockbuilder
[root@ccae845daa84 /]# for dep in https://download.fedoraproject.org/pub/fedora/linux/releases/41/Everything/source/tree/Packages/p/python-rich-13.7.1-5.fc41.src.rpm https://download.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/source/tree/Packages/p/python-textual-0.62.0-2.fc41.src.rpm; do rpm -ihv $dep; done
```

Then we update the RPM spec file for Textual, bumping the version from 0.62.0 to 1.0.0:

```shell
[root@ccae845daa84 /]# sed -i 's#0.62.0#1.0.0#' ~/rpmbuild/SPECS/python-textual.spec
[root@ccae845daa84 /]# sed -i 's#%{url}/archive/v%{version}/textual-%{version}.tar.gz#%{url}/archive/refs/tags/v%{version}.tar.gz#' ~/rpmbuild/SPECS/python-textual.spec
[root@ccae845daa84 /]# spectool --get-files ~/rpmbuild/SPECS/python-textual.spec --sourcedir
Downloading: https://github.com/Textualize/textual/archive/refs/tags/v1.0.0.tar.gz
|  28.3 MiB Elapsed Time: 0:00:02                                                                                                                       
Downloaded: v1.0.0.tar.gz
[root@ccae845daa84 /]# rpmbuild -bs ~/rpmbuild/SPECS/python-textual.spec
setting SOURCE_DATE_EPOCH=1717891200
Wrote: /root/rpmbuild/SRPMS/python-textual-1.0.0-2.fc40.src.rpm
```

We rebuild the SRPM and and, we make make sure mock can find it too when running from the exposed volume:

```shell
[root@ccae845daa84 /]# cp -pv /root/rpmbuild/SRPMS/python-textual-1.0.0-2.fc40.src.rpm /tmp/
'/root/rpmbuild/SRPMS/python-textual-1.0.0-2.fc40.src.rpm' -> '/tmp/python-textual-1.0.0-2.fc40.src.rpm'
[root@ccae845daa84 /]# su - mockbuilder
[mockbuilder@ccae845daa84 ~]$ ls -l /tmp/python-textual-1.0.0-2.fc40.src.rpm
-rw-r--r--. 1 root root 29612335 Jan 11 00:12 /tmp/python-textual-1.0.0-2.fc40.src.rpm
```

Moment of truth, let’s build it:

```shell
[mockbuilder@ccae845daa84 ~]$ mock --nocheck --localrepo /mnt/result/ --chain https://download.fedoraproject.org/pub/fedora/linux/releases/41/Everything/source/tree/Packages/p/python-rich-13.7.1-5.fc41.src.rpm /tmp/python-textual-1.0.0-2.fc40.src.rpm
Wrote: /builddir/build/SRPMS/python-textual-1.0.0-2.fc40.src.rpm
Wrote: /builddir/build/RPMS/python3-textual-1.0.0-2.fc40.noarch.rpm
Wrote: /builddir/build/RPMS/python3-textual-doc-1.0.0-2.fc40.noarch.rpm
INFO: Done(/tmp/python-textual-1.0.0-2.fc40.src.rpm) Config(default) 2 minutes 38 seconds
```

Finally, test the installation by installing the RPMS outside the container:

```shell
josevnz@raspberypi1:~$ sudo dnf install /home/josevnz/tmp/results/default/python-rich-13.7.1-5.fc41/python3-rich-13.7.1-5.fc40.noarch.rpm /home/josevnz/tmp/results/default/python-textual-1.0.0-2.fc40/python3-textual-doc-1.0.0-2.fc40.noarch.rpm /home/josevnz/tmp/results/default/python-textual-1.0.0-2.fc40/python3-textual-1.0.0-2.fc40.noarch.rpm
Last metadata expiration check: 3:42:37 ago on Fri 10 Jan 2025 03:50:49 PM EST.
Package python3-rich-13.7.1-5.fc40.noarch is already installed.
Dependencies resolved.
=========================================================================================================================================================
 Package                                    Architecture                 Version                                Repository                          Size
=========================================================================================================================================================
Upgrading:
 python3-textual                            noarch                       1.0.0-2.fc40                           @commandline                       1.3 M
 python3-textual-doc                        noarch                       1.0.0-2.fc40                           @commandline                        24 M
Installing dependencies:
 python3-platformdirs                       noarch                       3.11.0-3.fc40                          fedora                              46 k

Transaction Summary
=========================================================================================================================================================
Install  1 Package
Upgrade  2 Packages

Total size: 25 M
Total download size: 46 k
Is this ok [y/N]: y
Downloading Packages:
python3-platformdirs-3.11.0-3.fc40.noarch.rpm                                                                             53 kB/s |  46 kB     00:00    
---------------------------------------------------------------------------------------------------------------------------------------------------------
Total                                                                                                                     41 kB/s |  46 kB     00:01     
Running transaction check
Transaction check succeeded.
Running transaction test
Transaction test succeeded.
Running transaction
  Preparing        :                                                                                                                                 1/1 
  Installing       : python3-platformdirs-3.11.0-3.fc40.noarch                                                                                       1/5 
  Upgrading        : python3-textual-1.0.0-2.fc40.noarch                                                                                             2/5 
  Upgrading        : python3-textual-doc-1.0.0-2.fc40.noarch                                                                                         3/5 
  Cleanup          : python3-textual-0.62.0-2.fc40.noarch                                                                                            4/5 
  Cleanup          : python3-textual-doc-0.62.0-2.fc40.noarch                                                                                        5/5 
  Running scriptlet: python3-textual-doc-0.62.0-2.fc40.noarch                                                                                        5/5 

Upgraded:
  python3-textual-1.0.0-2.fc40.noarch                                       python3-textual-doc-1.0.0-2.fc40.noarch                                      
Installed:
  python3-platformdirs-3.11.0-3.fc40.noarch                                                                                                              

Complete!
```

Not bad, we can now build sophisticated TUI using Textual and the system Python, without the need to create a virtual environment.

## Conclusion

As you can see, mock is a very valuable tool that can help you automate packaging Python libraries that are not yet available in your platform. It allows you to automate getting dependencies for the RPM and alert you when some are missing in your platform.

As an added bonus, the fact than you can run it inside PODMAN gives you even more isolation from RPMs that could be dangerous when executed as root.

### Extra documentation (RTFM, Read The Fine Manual)

* [RPM-Macros](https://gitlab.com/redhat/centos-stream/rpms/pyproject-rpm-macros/)
    
* [Mock](https://rpm-software-management.github.io/mock/)
    
* [RPM macro documentation](https://docs.fedoraproject.org/en-US/packaging-guidelines/Python_201x/#_macros)
    
* [Packaging Python3 RPMS](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10-beta/html/packaging_and_distributing_software/packaging-python-3-rpms)
    
* [PyPA specifications](https://packaging.python.org/en/latest/specifications/)
    
* [Fedora Textual RPM](https://koji.fedoraproject.org/koji/buildinfo?buildID=2466451)

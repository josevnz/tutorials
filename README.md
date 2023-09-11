# Tutorials by KodeGeek

![](raspberry_pi4.png)

This repository has links to all the [tutorials](docs/README.md) I have written for [Enable Sysadmin](https://www.redhat.com/sysadmin/users/jose-vicente-nunez), [MyFreeCodeCamp](https://www.freecodecamp.org/news/author/jose-vicente-nunez/), 
[Medium](https://medium.com/@kodegeek-com) and others.

The layout follows a format that is compatible with both GitPages and my own Blog at kodegeek.com.

## License

All code is Open Source, same as the tutorials. If you find any issues, please report it and I will fix them as soon as I can.

Or even better, submit a patch.

## Checking out this repository

```shell
https://github.com/josevnz/tutorials.git && \
cd tutorials && \
bin/git submodule sync --recursive
git -c protocol.version=2 submodule update --init --force --depth=1 --recursive
```


If you want to refresh it with the latest changes

```shell
bin/git submodule sync --recursive && \
git -c protocol.version=2 submodule update --init --force --depth=1 --recursive
```

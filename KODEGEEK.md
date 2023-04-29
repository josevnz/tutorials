# Kodegeek.com publishing

I use [mkdocs](https://www.mkdocs.org/) to publish to my personal site, [http://kodegeek.com/]

And this is just in case I have to copy and paste nonsense on my terminal one day :-)

## Hwo does it work

```shell
python3 -m venv ~/virtualenv/mkdocs
. ~/virtualenv/mkdocs/bin/activate
cd tutorials
mkdocs build
```
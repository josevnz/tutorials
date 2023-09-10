# How to generate the diagrams for this tutorial

```shell
python3 -m venv ~virtualenv/spyonnfs
. ~virtualenv/spyonnfs/bin/activate
pip install -r requirements
sudo dnf install graphviz
./NfsLayout.py $PWD/NfsLayout
```
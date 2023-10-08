# Empire State Building Run-Up (2023 edition)

> The Empire State Building Run-Up (ESBRU)—the world’s first and most famous tower race—challenges runners from near and far to race up its famed 86 flights—1,576 stairs. 
> While visitors can reach the building’s Observatory via elevator in under one minute, the fastest runners have covered the 86 floors by foot in about 10 minutes. 
> Leaders in the sport of professional tower-running converge at the Empire State Building in what some consider the ultimate test of endurance.

## Normalizing the data

Data is not ready to be used (like CSV) so I saved it into a TXT one page at the time, and then did some massaging:

```shell
es_normalizer --rawfile /home/josevnz/tutorials/docs/EmpireStateRunUp/test/raw_data.txt /home/josevnz/tutorials/docs/EmpireStateRunUp/empirestaterunup/results.csv
```

## Running the code in developer mode

```shell
python3 -m venv ~/virtualenv/EmpireStateRunUp
. ~/virtualenv/EmpireStateRunUp/bin/activate
pip install --upgrade pip
pip install --upgrade build
pip install --upgrade wheel
pip install --editable 
```

## Packaging 

```shell
python3 -m venv ~/virtualenv/EmpireStateRunUp
. ~/virtualenv/EmpireStateRunUp/bin/activate
pip install --upgrade pip
pip install --upgrade build
pip install --upgrade wheel
python -m build .
```

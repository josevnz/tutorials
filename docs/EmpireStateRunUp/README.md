# Empire State Building Run-Up (2023 edition)
```
#########################%%%%####################################
####################%#%###%##%#+#%%%%###%%#%%%%%%#%###############
###############%%%%%%%%%%%%%%%#=*%%%%%%%%%#%%%%%%%%%%%%###########
###############%#%%%%%%%%%%%%%#=#%%%%%%%%%%%%%%%%%%%%%%%%%%#%%%###
#################%%%%%%%%%%%%%*=#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%##
################%%%%%%%%%%%%%%*+*%#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%##
#################%###%%%%%%%%#**+=#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
#######################%%%%#*==-=-+%%%%%%%%%%%%%%%%%%%%%%%%%%%%%##
#########################%%-:.--+=*%%%%%%%%%%%%%%%%%%%%%%%%%%%%%##
#**#**#####################:+=+=-:+#%%%%%%%%%%%%%%%%%%%%%%%##%####
******###################*==*=+==:+#%%%%%%%%%%%%%%%%%%%###########
*********################*++#++=+-+###%%%%%%%%%%%##%#%############
**********###############***#++==-=%%#%%%%%######%################
***************##########**+#*+=#==%%%%%%#%#######################
***************#########+:+*#*+=#-=%%%%%%##%######################
***************####*####+-+*#*++#-=%%%%%%#########################
*+*******************###+-+*##++*-=%%%%%%#########################
++++++++****************+-+*##=**-=%%%%%%########################*
++++++++++++++++********=-++#*=**-=%%%%%%########*****#########***
==+++++++++++++++***+***+-++#*=*+:=%%%%%####**********#######*****
====+++++++++++++++++++*=-++#*=*+-+%%%%%%##**********#######******
=====+++++++++++++++++++=-++#*=*+:+%%%%%#***********#######*******
=========++=+=====++++++=-++#*=*+-*%%%%%#*************************
---=================++++=-++#*=*+-*##%%%#*************************
-------===============++=-++#+-++-*##%%%#****************+++*****+
----------===============-++#+-+*-#####%#***************+++*****++
---------------==========-++#=-+*=####%%#*********************++=+
-------------------=====--++#+=+*=####%%#*********************++==
-------------------=====--=+#+=+#+##%%%%%*+*******************+===
-------------------======-=+#==+#+##%%%%%*++***********+****++++==
--------------------------++#==+#**#%%%%%*++++**+++++++++++++++===
---------------=*---------++#==+#**%%%%%%*+++++++++++++++++++=====
-------:------==#---------+++-+*##**+#%%%#++++++++++++++++++======
---:-----==---=+#+-++=====+*+=*###***#%%%%*+++*#*++++++++++++=====
======*###%#*++*#+=#%==+==**+=****+*##%##*#%##*##++***+++*******++
#*==--*%%#%%%#%*+**++#*+=+#*+=*+*#+#%%%%#*%%%%%%***%###*#****#***+
**====#%%#%%%#%*+*+==#=+==#*+=*+*#=#*+*###%%#%**##+*%##%%%%%%%%%%*
**+==-*%%#%%%###*%%%%#++**###=#++%=*+:*##%%%%#**####%%%%%%%%%%%%%#
###*#*##*+++=======-==++%%%%%##*+#-*+-#*#%%%%#%%%==#%%%**###%%*+++
########*+++++++++*#***#%%%%%%+:##-++=#*#%%%%%%%%%*+==+=#*++#%%%#*
*+*#####***#*##*#+***+*+*%%%%%#*##**++##%%%%%%%%%%*+-:-:#*:-+%%#*+
++*#####+*+#++*+%****+#**%%%%##+*+**+*##%%%%%%%%%%*==--:#*-++#%%##
**#######%+*+***%*##*=#+*%%%#:=###---*#%%%%%%%%%%%+==-=:*#****+*##
*##***+++##-:+*#*+#****+#%#**=-###:::#*=+**#%%%%%*+#%%%%***+***###
..:-=+=-=#+.-#*###**+*****####*#%*#+:++==++====+=+++++++=:::**::+:
=--=---=+=+==#*%%%%%%%#%###%#######:::::::--====+***++*+*-::**++++
```

> The Empire State Building Run-Up (ESBRU)—the world’s first and most famous tower race—challenges runners from near and far to race up its famed 86 flights—1,576 stairs. 
> While visitors can reach the building’s Observatory via elevator in under one minute, the fastest runners have covered the 86 floors by foot in about 10 minutes. 
> Leaders in the sport of professional tower-running converge at the Empire State Building in what some consider the ultimate test of endurance.

## Analyzing the data

### Browsing through the data

The 'esru_browser' is a simple browser that lets you navigate through the race raw data.

```shell
esru_browser
```

### Running summary reports

This application will provide details about the following:

* count, std, mean, min, max 45%, 50% and 75% for age, time, and pace
* Group and count distribution for Age,  Wave and Gender

```shell
esru_numbers
```

### Finding outliers

This application uses the Z-score to find the outliers for several metrics for this race

```shell
esru_outlier
```

### A few plot graphics for you

The `simple_plot` application offers a few plot graphics to help you visualize the data.

#### Age plots

The program can generate two flavors

![](age_plot.png)

![](age_histogram.png)

#### Participants per country plot

![](participants_per_country.png)

#### Gender distribution

![](gender_distribution.png)

## For developers

### Normalizing the data

Data is not ready to be used (like CSV) so I saved it into a TXT one page at the time, and then did some massaging:

```shell
es_normalizer --rawfile /home/josevnz/tutorials/docs/EmpireStateRunUp/raw_data.txt /home/josevnz/tutorials/docs/EmpireStateRunUp/empirestaterunup/results.csv
```

### Running the code in developer mode

```shell
python3 -m venv ~/virtualenv/EmpireStateRunUp
. ~/virtualenv/EmpireStateRunUp/bin/activate
pip install --upgrade pip
pip install --upgrade build
pip install --upgrade wheel
pip install --editable .
```

#### Modifying the layout without restarting the apps

For example, playing with the 'esru_outlier' application:

```shell
pip install textual-dev
textual run --dev empirestaterunup.apps:run_outlier 
```

### Packaging 

```shell
python3 -m venv ~/virtualenv/EmpireStateRunUp
. ~/virtualenv/EmpireStateRunUp/bin/activate
pip install --upgrade pip
pip install --upgrade build
pip install --upgrade wheel
python -m build .
```

#### Country codes

I used the files generated by the [ISO-3166-Countries-with-Regional-Codes
](https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/tree/master) for the flag lookup, using [Regional indicator symbol](https://en.wikipedia.org/wiki/Regional_indicator_symbol).


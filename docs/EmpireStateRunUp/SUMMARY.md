# Empire State Building Run-Up meets Open Source tools

The Empire State is one of the most iconic buildings in the world. Standing tall in Manhattan is a symbol of the city what type of vibrant city is New York City.

A less-known fact is that you can run through the stars to the observatory on the top, in a competition:

> The Empire State Building Run-Up (ESBRU)—the world’s first and most famous tower race—challenges runners from near and far to race up its famed 86 flights—1,576 stairs. 
> While visitors can reach the building’s Observatory via elevator in under one minute, the fastest runners have covered the 86 floors by foot in about 10 minutes. 
> Leaders in the sport of professional tower-running converge at the Empire State Building in what some consider the ultimate test of endurance.

Racing to get to the top of a building is also known as [a tower running race](https://en.wikipedia.org/wiki/Tower_running) and it happens around the world.

As one of the things that fuel your imagination, I always wondered how well I would fare running a race on the Empire State. I started my research around 4 years ago and found out about a lottery and also running through a charity. In the end, I tried the lottery, getting rejected over and over.

And then, out of the blue, I got an email a little bit more than two months before the race saying that I was accepted and more instructions would come as the race date got closer.

Sufficient to say I was nervous as this was not a Marathon (I Ran the New York City Marathon), nor a Mile Race (also ran the Fifth Avenue Mile) but a different animal; As a geek, I started looking for statistics about the race, finishing times, gender information, anything that would clarify of the upcoming challenge, but all the details were scattered or in a format that I didn't like.

## Preparing for the race, preparing to code

I'm not the first one to tackle a tower race and there are plenty of tips and resources online, I took advantage of that. Also stayed consistent with my regular training, so I ended up making some adaptations to be ready for the challenges of this type of race.

One problem was not solved and it was the lack of a nice tool to analyze the race results. Race organizers collected the race results and showed them on their sites with minimal analysis, and none of them offered a way to download the data for more complex processing.

That's where Open Source comes into play. I'm a DevOps and I love to automate things, so my plan to solve this issue was like this:

1. Wait until the race results get published (better, survive the race on the first place)
2. Web-scrape the website and retrieve the data, with minimal processing to speed up the data capture. Write some unit tests but don't expect the code to be very re-usable (web scrapping will force you to make some decisions to stick the parsing depending on how the raw data looks like)
3. Clean up and normalize the data, so it can be analyzed. Write a unit test for each step. Rinse and repeat
4. Write a nice user interface to show the results. In my case, I wanted to avoid the burden of writing a web application, and a TUI (Text User Interface) seemed a logical choice.
5. Have some fun with charts! Who doesn't like those? Make sure they are easy to generate, KISS principle
6. Share the code! What if others want to suggest features, and even submit a patch? The code gets a life of its own.

I decided to run my stack on Linux (I used Fedora) and the programming language of choice was Python (was more concerned with writing quality code fast than having fast running code). Python was also an easy choice given the number of mature libraries you can use to solve this problem, from web scrapping to doing data science on the parsed data.

## Necessity is the mother of invention

Some compromises were made but the whole exercise forced me to come up with some interesting solutions.

### Getting the data, the hard way
This is very true. I was looking first for some software to take the data from the website where the results were published, without luck. I contacted the site support but did not get an answer if was even possible to download the data.

And every decent website these days forces clients to render the contents in JavaScript. Just try deactivating Javascript and go to one of your favorite websites and you will find out very quickly how fun they are (hint: they're not).

So my best next choice was to manage my web browser (I use Firefox) programmatically, going through every link on the race results website, and saving the contents of the rendered table; [Selenium WebDriver](https://www.selenium.dev/documentation/webdriver/) with a Python extention made it very easy for me and after a few tries I [produced simple code](https://github.com/josevnz/tutorials/blob/main/docs/EmpireStateRunUp/empirestaterunup/scrapper.py) that got all the data for this race.

Why all the data? I wanted to know more about other racers (like country of origin, age, etc.), and now with a local copy in a friendly format I could try to answer my questions

### Data is never clean, scrubbing is not hard

Before you can start asking questions you need to massage up the data:

* Remove outliers
* Normalize values
* Convert some strings to data types like numbers, and dates to be able to get meaningful information

Python [Pandas DataFrames](https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html) are highly descriptive and provide lots of features to query and manipulate the data:

```shell
>>> # Using custom load_data function that returns a Panda DataFrame
>>> from empirestaterunup.data import load_data
>>> load_data('empirestaterunup/results-full-level-2023.csv')
                    name  overall position            time gender  gender position  age  ...  65th floor division position 65th floor pace 65th floor time       wave        level     finishtimestamp
bib                                                                                      ...                                                                                                          
19         Wai Ching Soh                 1 0 days 00:10:36      M                1   29  ...                             1 0 days 00:54:03 0 days 00:07:34  ELITE MEN  Full Course 2023-09-04 20:10:36
22        Ryoji Watanabe                 2 0 days 00:10:52      M                2   40  ...                             1 0 days 00:54:31 0 days 00:07:38  ELITE MEN  Full Course 2023-09-04 20:10:52
16            Fabio Ruga                 3 0 days 00:11:14      M                3   42  ...                             2 0 days 00:57:09 0 days 00:08:00  ELITE MEN  Full Course 2023-09-04 20:11:14
11        Emanuele Manzi                 4 0 days 00:11:28      M                4   45  ...                             3 0 days 00:59:17 0 days 00:08:18  ELITE MEN  Full Course 2023-09-04 20:11:28
249             Alex Cyr                 5 0 days 00:11:52      M                5   28  ...                             2 0 days 01:01:19 0 days 00:08:35   SPONSORS  Full Course 2023-09-04 20:11:52
..                   ...               ...             ...    ...              ...  ...  ...                           ...             ...             ...        ...          ...                 ...
555     Caroline Edwards               372 0 days 00:55:17      F              143   47  ...                            39 0 days 04:57:23 0 days 00:41:38  GENERAL 2  Full Course 2023-09-04 20:55:17
557        Sarah Preston               373 0 days 00:55:22      F              144   34  ...                            41 0 days 04:58:20 0 days 00:41:46  GENERAL 2  Full Course 2023-09-04 20:55:22
544  Christopher Winkler               374 0 days 01:00:10      M              228   40  ...                            18 0 days 01:49:53 0 days 00:15:23  GENERAL 2  Full Course 2023-09-04 21:00:10
545          Jay Winkler               375 0 days 01:05:19      U               93   33  ...                            18 0 days 05:28:56 0 days 00:46:03  GENERAL 2  Full Course 2023-09-04 21:05:19
646           Dana Zajko               376 0 days 01:06:48      F              145   38  ...                            42 0 days 05:15:14 0 days 00:44:08  GENERAL 3  Full Course 2023-09-04 21:06:48

[375 rows x 24 columns]
```

### You have the data, displaying facts the next step

A Text User Interface (TUI) is probably the easiest way to show your users quickly and nicely interesting facts about your data.

![A table that shows the Race results, in Python Textual](https://github.com/josevnz/tutorials/blob/main/docs/EmpireStateRunUp/images/esru_browser.png?raw=true)

As you can imagine, this is an iterative process where you refine your application to answer the most important questions first and to improve your answers. I ended up writing the TUI with Textual, which made the process much easier.

Now a TUI has some limitations, especially with graphics I needed to summarize some important facts; [Mathplotlib](https://matplotlib.org/) let me tackle each one of these visualizations, showing information in ways not possible with the terminal:

![Gender distribution for the racers](https://github.com/josevnz/tutorials/blob/main/docs/EmpireStateRunUp/images/gender_distribution.png?raw=true)


## King Kong had a terrible experience in the Empire State, you will have fun instead

Most of the challenges in this race are mental. Yes, it is tough to climb so many stairs quickly but the trick is to use both rails and to pace yourself.

_Run your race and have fun_. And believe you can do it.

As for the coding part, it gave me an excuse to brush up my skills using [Python Pandas](https://pandas.pydata.org/), [Textual](https://textual.textualize.io/) and MathPlotLib as well to write a nice Python Wheelhouse you can get from Pypi.

I encourage you to visit the [tutorial site](https://github.com/josevnz/tutorials/blob/main/docs/EmpireStateRunUp/TUTORIAL.md), to get much more details on [how to code](https://github.com/josevnz/tutorials.git) a similar project yourself and also, if you are curious, apply to the lottery for the race and see if you can get it. You'll never know if you don't try.


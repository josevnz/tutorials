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

I'm not the first one to tackle a tower race and there are plenty of tips and resources online, I took advantage of that. Also stayed consistent with my regular training, so I ended up making some adaptations to adapt to the challenges of this type of race.

One problem was not solved and it was the lack of a nice tool to analyze the race results. Over the years different vendors collected the race results and showed them on their sites with minimal analysis, and none of them offered a way to download the data for more complex processing.

That's where Open Source comes into play. I'm a DevOps and I love to automate things, so my plan to solve this issue was like this:

1. Wait until the race results get published
2. Web-scrape the website and retrieve the data, with minimal processing to speed up the processing. Write some unit tests but don't expect the code to be very re-usable (web scrapping will force you to make some decisions to stick the parsing depending on how the raw data looks like)
3. Clean up and normalize the data, so it can be analyzed. Write a unit test for each step. Rinse and repeat
4. Write a nice user interface to show the results. In my case, I wanted to avoid the burden of writing a web application, and a TUI (Text User Interface) seemed a logical choice.
5. Have some fun with charts! Who doesn't like those? Make sure they are easy to generate, KISS principle
6. Share the code! What if others want to suggest features, and even submit a patch? The code gets a life of its own.

I decided to run my stack on Linux (I used Fedora) and the programming language of choice was Python (was more concerned with writing quality code fast than having fast running code). Python was also an easy choice given the number of mature libraries you can use to solve this problem, from web scrapping to doing data science on the parsed data.

## King Kong died in the Empire State, you will have fun instead

Most of the challenges in this race are mental. Yes, it is tough to climb so many stairs quickly but the trick is to use both rails and to pace yourself.

_Run your race and have fun_. And believe you can do it.

As for the coding part, it gave me an excuse to brush up my skills using [Python Pandas](https://pandas.pydata.org/), [Textual](https://textual.textualize.io/) and MathPlotLib as well to write a nice Python Wheelhouse you can get from Pypi.

I encourage you to visit the [tutorial site](https://github.com/josevnz/tutorials/blob/main/docs/EmpireStateRunUp/TUTORIAL.md), to get much more details on [how to code](https://github.com/josevnz/tutorials.git) a similar project yourself and also, if you are curious, apply to the lottery for the race and see if you can get it. You'll never know if you don't try.


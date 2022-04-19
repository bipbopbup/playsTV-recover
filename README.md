# PlaysTV-Recover
A python script to download your old "lost" plays.tv clips! 

What do you need to execute this?

- Your old plays.tv username
- Python 3.x
- pip install -r requirements.txt
- Download the geckodriver from here: https://github.com/mozilla/geckodriver/releases
-- Unzip it
-- Copy that .exe file and put your into python parent folder (e.g., C:\Python34)
- Some patiente since this script is a scrapper and needs to make some requests to the archives.org webpage :)

Issues!
- Sometimes it finds less videos than expected. I think this is due to requests execution time, which varies time to time. Before the script starts to download the videos, I recommend to interrupt the program if it reports less videos than expected, and execute again. Pull requests to solve this issue are welcomed!

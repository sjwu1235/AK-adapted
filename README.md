# information-retrieval <!-- omit in toc -->

A python program designed to scrape articles from JSTOR based on some user specified fields. This is a two stage process:
1. Stage_1_scraper.py scrapes the specified journal page on JSTOR for all issue links and then iterates through each issue page to get links to the first article of each issue eg: a pivot point.
2. Given a year range, Stage_2_scraper.py scrapes articles issue by issue using the pivots excel file from alt_scraper2.py and dumps metadata scraped from each article page into datadump.xlsx at the end of scraping an issue.

Users of this program will have to have access to an afflianted institution's username and password. 

Note: a potential inefficiency exists. It is possible to scrape all URLs or download the citations in bulk from the journal page. Then directly query these URLs rather than navigating the issue using 'next' and 'previous' buttons. However, it is uncertain if this method will raise reCAPTCHA issues. Still cannot confidently confirm if uBlock has defeated reCAPTCHA.

This is based off the original Aaron's Kit scraper program hosted at [https://github.com/FinHubSA/information-retrieval](FinHubSA)

## Table of Contents <!-- omit in toc -->

<!-- TOC -->
- [Quick Start](#quick-start)
- [Contributing](#contributing)
- [Run The Application](#run-the-application)
- [Speed test](#speed-test)
- [Additional Docs](#additional-docs)
<!-- /TOC -->
## Assumptions: 
* You have python installed on your machine. 
* You have Visual Studio Code or Spyder IDE installed on your machine 
* You have an excel reader installed on your machine
* You know the basics of installing python programs and running code in an IDE
* You have installed all the packages used in the alt_scraper.py and alt_scraper2.py file 
    * If not just type in ‘pip install packagename’ in the command terminal of your IDE
## Quick Start
1. Create a .json file in the cloned source directory called uctpw.json. Fill out 
your institution username and password in the following format; 
{"user":"Your user name ", "pass":" Your password "}
2. Check if you have all the programs used in the testing.py and testing2.py files (if not use 'pip install 'package name' ')
3. Copy datadump.xlsx into a folder where you want to store the pdfs, ensure that there is at least 20GB available on the disk
4. Take note of the folder path where datadump.xlsx is eg: "C:\Users\xxxx\Journal_Data"
5. Conduct a speed test on the download speed. See [speed test](#speed-test)
6. Now edit the inputs.json file in the cloned directory, it currently is set to scrape AER as an example
{"journal_URL":"URL of journal page on JSTOR",
 "journal_name":"Name of journal",
 "directory":"folder path to pdf data eg: C:\\Users\\xxxx\\Journal_Data", 
 "datadump":"path to datadump.xlsx eg: C:\\Users\\xxxx\\Journal_Data\\datadump.xlsx", 
 "pivots":"path to pivots file you can name it anything each session eg: C:\\Users\\xxxx\\Journal_Data\\pivots.xlsx",
 "start_year": year to start scraping eg: 2000, 
 "end_year": year to stop scraping (inclusive) eg: 2020, 
 "sleep_time": time taken to download pdf in speed test. Suggest 20 or longer}
7. Note: When editing inputs.json, replace all single "\" characters in file paths with "\\" eg: "C:\Users\xxxx\Journal_Data" to "C:\\Users\\xxxx\\Journal_Data"

## Speed test
Conduct a speed test manually to test hardware and download speed. Go to JSTOR and download a paper from the 2010 decade. Take note of how long it takes for the pdf popup to fully load and then how long it takes for a download of the pdf to complete.
Newer papers can get as large as 10mb so enough time needs to be given to the scraper to finish the download and return to the JSTOR page.

Alternatively, run a speed test. Google 'speed test' and run as below. Take note of the download speed and adjust the sleep_time field in inputs.json accordingly.

The suggested minimum is 20 seconds for the sleep_time field in inputs.json but if you believe in your internet speed, you can get away with less. At 20 seconds sleep time, this scraper will download 140 papers per hour.


**screenshot of google speed test**


## Run The Application
In command line
Run journal issue scraper
python alt_scraper2.py
Run article scraper
python alt_scraper.py
In the event of a stall, the scraper will require you to resolve the URL or stall and allow it to continue. Hence, I don't reccomend setting the window to headless in the code.
**detailed stall troubleshooting**



## Contributing

Before contributing **please read through everything in [Contributing](docs/contributing.md)**.

**[⬆ back to top](#table-of-contents)**



**[⬆ back to top](#table-of-contents)**

## Additional Docs

- [Contributing](docs/contributing.md)
- [Prerequisites](docs/prerequisites.md)
- [Node Version](docs/node-version.md)
**[⬆ back to top](#table-of-contents)**

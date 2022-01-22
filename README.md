# information-retrieval <!-- omit in toc -->

A python program designed to scrape articles from JSTOR based on some user specified fields. This is a two stage process:
1. Stage_1_scraper.py scrapes the specified journal page on JSTOR for all issue links and then iterates through each issue page to get links to the first article of each issue eg: a pivot point.
2. Given a year range, Stage_2_scraper.py scrapes articles issue by issue using the pivots excel file from stage 1 and dumps metadata scraped from each article page into datadump.xlsx at the end of scraping an issue.

Users of this program will have to have access to an afflianted institution's username and password. 

Note: a potential inefficiency exists. It is possible to scrape all URLs or download the citations in bulk from the journal page. Then directly query these URLs rather than navigating the issue using 'next' and 'previous' buttons. However, it is uncertain if this method will raise reCAPTCHA issues. Still cannot confidently confirm if uBlock has defeated reCAPTCHA.

This is based off the original Aaron's Kit scraper program hosted at [https://github.com/FinHubSA/information-retrieval](FinHubSA)

## Table of Contents <!-- omit in toc -->

<!-- TOC -->
- [Assumptions](#assumptions)
- [Quick start](#quick-start)
- [Speed test](#speed-test)
- [Run The Applications](#run-the-applications)
- [Additional Docs](#additional-docs)
<!-- /TOC -->
## Assumptions: 
* You have python installed on your machine. 
* You have Visual Studio Code or Spyder IDE installed on your machine 
* You have an excel reader installed on your machine
* You know the basics of installing python programs and running code in an IDE
* You have installed all the packages used in the alt_scraper.py and alt_scraper2.py file 
    * If not just type in ‘pip install packagename’ in the command terminal of your IDE

## Quick start
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
8. Run the scrapers. First Stage_1_scraper.py then Stage_2_scraper.py. See [Run The Applications](#run-the-applications) for details

## Speed test
### Option 1
Conduct a speed test manually to test hardware and download speed. Go to JSTOR and download a paper from the 2010 decade. Take note of how long it takes for the pdf popup to fully load and then how long it takes for a download of the pdf to complete.
Newer papers can get as large as 5mb, so the scraper needs enough time to finish the download and return to the JSTOR page.

### Option 2
Alternatively, run a speed test (google 'speed test'). The internet speed test below shows a connection that was able to handle downloading 140 papers per hour using a 20s sleep time without crashing over a 12 hour period. Take note of your download speed and latency compared to that in the reference and adjust the sleep_time field in inputs.json accordingly. It should deliver similar performance provided your internet speed is as good or better than the speed test screenshot above (20mbps download, 10mbps upload, 40ms latency). If not, please set a higher sleep time.


![image](https://user-images.githubusercontent.com/80747408/150649316-f92d129e-5aee-490d-8c84-4ca3eca4ab3a.png)


## Run The Applications
Run the journal issue scraper
```
python Stage_1_scraper.py
```
After navigating to the journal page, manually verify that the scraper expands all the decade fields. This will take about 2 minutes. This is to ensure that all issue URLs are scraped in this stage. Thereafter, you can leave it undisturbed to run. This scraper will iterate through each issue of the journal and scrape the issue's first article URL which will be used in the stage_2_scraper. The output from this scraper will be saved to whatever excel file path is in the 'pivots' field of inputs.json.

Run article scraper
```
python Stage_2_scraper.py
```
In the event of a stall, eg: page taking too long to load or a reCAPTCHA, the script will instruct you to resolve the URL and allow it to continue. Hence, I don't reccomend setting the window to headless as you may be required to help the scraper sometimes.



**detailed stall troubleshooting **
Still to come


## Contributing

Before contributing **please read through everything in [Contributing](docs/contributing.md)**.

**[⬆ back to top](#table-of-contents)**



**[⬆ back to top](#table-of-contents)**

## Additional Docs

- [Contributing](docs/contributing.md)
- [Prerequisites](docs/prerequisites.md)
- [Node Version](docs/node-version.md)
**[⬆ back to top](#table-of-contents)**

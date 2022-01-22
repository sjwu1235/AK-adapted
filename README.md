# information-retrieval <!-- omit in toc -->

A python program designed to scrape articles from JSTOR based on some user specified fields. This is a two stage process:
1. alt_scraper2.py scrapes the specified journal page on JSTOR for all issue links and then iterates through each issue page to get links to the first article of each issue eg: a pivot point.
2. alt_scraper.py scrapes all articles issue by issue and dumps metadata scraped from the  
Users of this program will have to have access to an 
afflianted institution's username and password. 

This is based off the original Aaron's Kit hosted at FinHubSA

## Table of Contents <!-- omit in toc -->

<!-- TOC -->
- [Quick Start](#quick-start)
- [Contributing](#contributing)
- [Run The Application](#run-the-application)
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
4. Take note of the folder path where datadump.xlsx is eg:
5. 
6. Now edit the .json file in the cloned directory called inputs.json
{"journal_URL":"URL of journal page on JSTOR",
 "journal_name":"Name of journal",
 "directory":"folder path to pdf data eg: C:\\Users\\sjwu1\\Journal_Data", 
 "datadump":"path to datadump.xlsx eg: C:\\Users\\sjwu1\\Journal_Data\\datadump.xlsx", 
 "pivots":"path to pivots file you can name it anything each session C:\\Users\\sjwu1\\Journal_Data\\pivots.xlsx",
 "start_year": year to start scraping eg: 2000, 
 "end_year": year to stop scraping (inclusive) eg: 2020, 
 "sleep_time": time taken to download pdf. suggest 20 or longer}
 
![image](https://user-images.githubusercontent.com/80747408/150616145-7d542700-ca1d-4320-93ca-86cc6cf41faa.png)
![image](https://user-images.githubusercontent.com/80747408/150616412-7734b3db-d48a-4cc2-9343-96bb3db537aa.png)



If you run into issues, see the additional docs below **[bottom of page](#Additional-Docs)**
## Contributing

Before contributing **please read through everything in [Contributing](docs/contributing.md)**.

**[⬆ back to top](#table-of-contents)**

## Run The Application


**[⬆ back to top](#table-of-contents)**

## Additional Docs

- [Contributing](docs/contributing.md)
- [Prerequisites](docs/prerequisites.md)
- [Node Version](docs/node-version.md)
**[⬆ back to top](#table-of-contents)**

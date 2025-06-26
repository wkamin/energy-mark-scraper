## Energy Market Scraper

This project contains two approaches to scrapig data from a energy market database of companies

1.) Selenium
     - Login to the energy market website
     
     - Run the script selenium_scraper.py - a new chromium browser will start scraping using the same login session
     
     - The script will automatically scroll and dump he results into a CSV
     
2.) API Based - this was discovered after option 1, and returns a lot more data much quicker. 
     - The API URL was exposed in the DOM of the browser, along with a bearer token.
     - The token likely needs to be updated based on log-in session.
     
     - Look for authorization: Bearer <token> in the Network Monitor of your Browser - you should see a POST command to a domain starting with "api."
     
     - Replace the bearer token in a .env file within the project working directory
     
     - Run api_company_detailed_scraper.py
     
     - All companies will be queried for, followed by a detailed extraction of each company. This could take multiple hours considering the amount of companies in the Database - a progress bar was implemeneted to see progress in the terminal.
     
     - A flattened CSV will be generated for all companies and their details

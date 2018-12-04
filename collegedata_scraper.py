import pandas as pd
import re
from os.path import isfile
from requests import get
from IPython.core.display import clear_output
from bs4 import BeautifulSoup


#############################################################################
# Use this tool to scrape CollegeData.com into a CSV.
#############################################################################
# The URLs of interest on collegedata.com are broken down like this:
BASE_URL_1 = "https://www.collegedata.com/cs/data/college/college_pg0"
# followed by a `school_id` number. Following that, there is:
BASE_URL_2 = "_tmpl.jhtml?schoolId="
# Finally, there is a `page_id` number, ranging from 1 to 6, inclusive.
# Not all possible `school_id` numbers corresponds to a school, but most do.
# A page requested corresponding to a `school_id` with no school data will
# load a page that has a <h1> tag heading with this string:
EMPTY_H1_HEADING = "Retrieve a Saved Search"
# At larger `school_id` values, especially over 1000, no-school pages are
# returned more often. I'm fairly confident there are none over 5000.
SCHOOL_ID_START = 1
SCHOOL_ID_END = 10
# CollegeData.com has no problem with requests without headers, but we can
# send a fake header anyway:
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) "
           "AppleWebKit/605.1.15 (KHTML, like Gecko) "
           "Version/12.0 Safari/605.1.15"}
# Finally, we'll export our scraped data to a CSV. The scraper will check
# if the CSV already exists, and if so, will adjust the `SCHOOL_ID_START` to
# begin with the `school_id` after the highest already scraped in the CSV:
PATH = "test_scraped.csv"


#############################################################################
# Exceptions
#############################################################################
# These errors could arise while requesting and scraping the pages.
class PageRequestError(Exception):
    # The response code was something other than 200.
    pass

class NoHeadingError(Exception):
    # The HTML has no <h1> tag.
    pass

class NoSchoolError(Exception):
    # There is no school data for the given `school_id`. Not really an error.
    pass

class IncompletePageError(Exception):
    # The comment code at the bottom of a fully loaded page was not found.
    pass

class EmptyPageError(Exception):
    # No data was scraped from a fully loaded normal page.
    pass


#############################################################################
# Functions
#############################################################################
def scrape_collegedata(start = SCHOOL_ID_START, stop = SCHOOL_ID_END):
    """Extract data from CollegeData.com.

    Keyword arguments:
    start -- `schoolId` in URL to begin scraping, inclusive.
    stop  -- `schoolId` in URL to end scraping, inclusive.

    If data for a `schoolId` exists, scrape_collegedata will request
    all six pages (Overview, Admissions, Money Matters, Academics, Campus
    Life, and Students) associated with that school. Relevant rows and tables
    will be scraped from the six pages and saved together as a single pandas 
    Series, with the `schoolId` as the Series' name. 

    scrape_collegedata will return a list of Series, one for each
    scraped school.
     """

    # Hold scraped schools as a list of pandas series.
    scraped_list = []

    # Scrape and save each page of each school.
    for school_id in range(start, stop + 1):
        try:
            # Request and parse HTML for all six pages associated w/ a school_id.
            soups = [get_soup(school_id, page_id) for page_id in range(1, 7)]
            
            # Relabel some problematic <th> labels before scraping.
            soups = relabel(soups)
            
            # School dictionary to hold all scraped values.
            school_dict = extract(soups)

        except PageRequestError:
            print('PageRequestError: Status Code != 200')
        except NoHeadingError:
            print('NoHeadingError: Page HTML has no <h1> tag.')
        except NoSchoolError:
            print('NoSchoolError: Page intentionally has no school data.')
        except IncompletePageError:
            print('IncompletePageError: Page did not completely load.')
        except EmptyPageError:
            print('EmptyPageError: No data scraped from page.')
        else:
            # Convert dict to pandas Series and append to scaped_list.
            scraped_series = pd.Series(school_dict, name = school_id)
            scraped_list.append(scraped_series)
        finally:
            # Clear status message.
            clear_output()

    return scraped_list


def get_soup(school_id, page_id):
    # Build the CollegeData.com URL corresponding to school_id and page_id.
    url = BASE_URL_1 + str(page_id) + BASE_URL_2 + str(school_id)

    # Request page and check if page returned.
    result = get(url, headers = HEADERS)
    if result.status_code != 200:
        raise PageRequestError
        
    # Parse page text into BeautifulSoup object.
    soup = BeautifulSoup(result.text, "lxml")
    
    # Raise an error if no <h1> tag exists.
    if not soup.h1:
        raise NoHeadingError

    # Raise an error if the <h1> text suggests no school exists.
    if soup.h1.string == EMPTY_H1_HEADING:
        raise NoSchoolError

    # Raise an error if the HTML comment at the end of the page content
    # didn't load, which can sometimes happen when requesting too fast.
    if not soup.find(string = 'Content END'):
        raise IncompletePageError
        
    # Print a status update.
    print('Scraped school {}, page {}'.format(school_id, page_id))

    return soup


def relabel(soups):
    # Prepend headings and clean repeated gender labels.
    strings = ['\xa0\xa0 Women', '\xa0\xa0 Men']
    tr_list = [[tr for soup in soups for tr in soup('tr') \
                if re.search(string, tr.get_text())] for string in strings]
    headings = [tr.find_previous_sibling('tr').th.get_text() for tr in tr_list[0]]*2
    th_list = [tr.th for trs in tr_list for tr in trs] # flatten list
    labels = [th.get_text(strip = True) for th in th_list]
    _ = [th.string.replace_with(headings[i] + ', ' + labels[i]) \
                for i, th in enumerate(th_list)]
    
    # Prepend heading to repeated phone and email labels.
    heading = 'Financial Aid Office'
    table = soups[2].find('caption', string = re.compile(heading)).parent
    _ = [th.string.replace_with(heading + ', ' + th.string) \
         for th in table.tbody('th')[0:2]]
    
    # Append captions to duplicate financial aid labels.
    tables = soups[2].find('div', id = 'section11')('table')[0:2]
    captions = [table.caption.get_text(strip = True) for table in tables]
    tr_list = [table.tbody('tr') for table in tables]
    th_list = [[tr.th for tr in trs] for trs in tr_list]
    _ = [[th.insert(1, ', ' + captions[i]) \
                for th in ths if not th.has_attr('class')] \
                    for i, ths in enumerate(th_list)]
    
    # Prepend a heading to the GPA labels.
    regex = re.compile("Grade Point Average")
    table = soups[1].find('caption', string = regex).parent
    _ = table.tbody.th.string.replace_with('GPA, Average')
    _ = [th.insert(0, 'GPA, ') for th in table.tbody('th')[1:]]
    
    return soups


def extract(soups):   
    extracted_dict = {}
    
    # Extract the school name.
    #h1 = soups[0].h1.extract()
    #d['Name'] = h1.get_text()
    extracted_dict.update(extract_name())
    
    # Extract the fafsa code and filing cost.
    regex = re.compile('Forms Required')
    table = soups[2].find('th', string = regex).find_parent('table').extract()
    extracted_dict['FAFSA'] = table.tbody.th.get_text()
    extracted_dict['Financial Aid Filing Cost'] = table.tbody.td.get_text()
    #d.update(extract_applying_finaid())

    # Extract the city population.
    regex = re.compile('Population')
    tr = soups[0].find('th', string = regex).find_parent('tr').extract()
    _ = soups[4].find('th', string = regex).find_parent('tr').decompose()
    extracted_dict['City Population'] = tr.td.get_text()
    #d.update(extract_city_pop())
    
    # Extract <th class='sub'> rows with appropriate header labels prepended to keys.
    tr_list = [[th.parent for th in soup('th', class_ = 'sub')] for soup in soups]
    tr_list = [tr for sublist in tr_list for tr in sublist]  # flatten list
    sub_keys = [tr.th.get_text(strip = True) for tr in tr_list]
    headers = [tr.find_previous('th', class_ = None).get_text() for tr in tr_list]
    keys = [headers[i] + ', ' + sub_key for i, sub_key in enumerate(sub_keys)]
    vals = [tr.extract().td.get_text(strip = True) for tr in tr_list]
    extracted_dict.update(dict(zip(keys, vals)))
    #d.update(extract_sub_rows())

    # Extract from 'Selection of Students' table.
    table = soups[1].find('div', id = 'section7').table.extract()
    col_labels = [td.get_text() for td in table.thead.tr('td')]
    rows = [tr for tr in table.tbody('tr') if 'X' in [td.get_text() for td in tr('td')]]
    index = [[td.get_text() for td in tr('td')].index('X') for tr in rows]
    keys = ['Selection Factor, ' + tr.th.get_text() for tr in rows]
    vals = [col_labels[i] for i in index]
    extracted_dict.update(dict(zip(keys, vals)))
    #d.update(extract_table_selection_students())

    # Extract from majors / programs of study tables.
    keys = ['Undergraduate Majors',
            "Master's Programs of Study",
            'Doctoral Programs of Study']
    regexs = [re.compile(key) for key in keys]
    tags = soups[3]('caption', string = regexs)
    tables = [tag.find_parent('table').extract() for tag in tags]
    vals = [[li.get_text(strip = True) for li in table('li')] for table in tables]
    extracted_dict.update(dict(zip(keys, vals)))
    #d.update(extract_table_majors())

    # Extract from master's / doctoral degrees tables.
    keys = ["Master's Degrees Offered",
            "Doctoral Degrees Offered"]
    regexs = [re.compile(key) for key in keys]
    tags = soups[3]('caption', string = regexs)
    tables = [tag.find_parent('table').extract() for tag in tags]
    vals = [table.th.get_text(strip = True).split(", ") for table in tables]
    extracted_dict.update(dict(zip(keys, vals)))
    #d.update(extract_table_degrees())

    # TO DO: Extract remaining tables (HS units, sports).

    # Finally, extract all <th> as key, <td> as value data from key/val rows.
    rows = [row.extract() for soup in soups for row in soup('tr') \
                if len(row('th')) == 1 and len(row('td')) == 1]
    keys = [tr.th.get_text(strip = True) for tr in rows]
    vals = [tr.td.get_text(strip = True) for tr in rows]
    extracted_dict.update(dict(zip(keys, vals)))
    #d.update(extract_rows())

    # Return scraped data as a dictionary.
    return extracted_dict


def extract_name():
    d = {}
        
    h1 = soups[0].h1.extract()
    d['Name'] = h1.get_text()
    
    return d
    

#############################################################################
# Running the scraper.
#############################################################################

if isfile(PATH):
    df = pd.read_csv(PATH, index_col = 'school_id')
    SCHOOL_ID_START = df.index.max() + 1
else:
    df = pd.DataFrame()

if SCHOOL_ID_START < SCHOOL_ID_END:
    scraped_list = scrape_collegedata(SCHOOL_ID_START, SCHOOL_ID_END)
    print("Scraped {} schools.".format(len(scraped_list)))

    scraped_df = pd.DataFrame(scraped_list)
    scraped_df.index.name = 'school_id'
    df = df.append(scraped_df, sort = True)
    df.to_csv(PATH)
else:
    print("Scraped no schools.")
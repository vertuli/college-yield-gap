# CollegeData scraper.
import numpy as np
import pandas as pd
from requests import get
from bs4 import BeautifulSoup, SoupStrainer

#############################################################################
# Use this tool to scrape CollegeData.com into a CSV.
#############################################################################
# The URLs of interest on collegedata.com are broken down like this:
URL_PT_1 = "https://www.collegedata.com/cs/data/college/college_pg0"
# followed by a `school_id` number. Following that, there is:
URL_PT_2 = "_tmpl.jhtml?schoolId="
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

def get_soup(url, SoupStrainer = None):
    # Request page and check if page returned.
    result = get(url, headers = HEADERS)
    if result.status_code != 200:
        raise PageRequestError
    # Parse page text into BeautifulSoup object.
    soup = BeautifulSoup(result.text, "lxml", parse_only = SoupStrainer)
    return soup

def get_collegedata_page(school_id, page_id):
    url = URL_PT_1 + str(page_id) + URL_PT_2 + str(school_id)
    strainer = SoupStrainer(
        lambda tag, d: tag == 'h1' or d.get('id') == 'tabcontwrap')
    soup = get_soup(url, strainer)
    return soup

school_id = 59
# Get each of the six pages for a school.
pages = [get_collegedata_page(school_id, i) for i in range(1, 7)]

# Hold all scraped values in a single pandas Series.
school_s = pd.Series(name = school_id)

# Get the school Name and Description from the first page.
# These values are the only we'll be extracted that are not
# found inside an HTML table.
school_s['Name'] = pages[0].h1.text
school_s['Description'] = pages[0].p.text

# Convert all HTML tables as a list of DataFrame objects.
na_vals = ['Not reported', 'Not Reported']
df_list = []
for page in pages:
    dfs = pd.read_html(page.decode(), na_values = na_vals, index_col = 0)
    for i in range(len(dfs)):
        dfs[i] = dfs[i][dfs[i].index.notnull()]  # del rows w/ null indices
    df_list += dfs

# List scalar objects squeezed from the scraped DataFrames with zero columns.
val_list = [df.reset_index().squeeze() for df in df_list if df.shape[1] == 0]

# List pandas Series objects squeezed from DataFrames w/only one column.
s_list = [df.squeeze() for df in df_list if df.shape[1] == 1]

# List only the scraped DataFrame objects with more than one column.
df_list = [df for df in df_list if df.shape[1] > 1]

# For both the 'High School Units Required or Recommended' table and the 
# 'Examinations' table - both on the 'Admissions' page - there are two columns
# and each row in those tables could have data for each columns.
results = [df for df in df_list if df.index.name in ['Subject', 'Exam']]
for df in results:
    s_list = [df[col] for col in df.columns]
    for s in s_list:
        s.index = s.index + ', ' + s.name
    school_s = school_s.append(pd.concat(s_list))

# The 'Selection of Students' table has 'Factor' as an index name.
results = [df for df in df_list if df.index.name == 'Factor']

# There are two of these tables, the first a short one on the 'Overview' page
# and the second a full version on the 'Admissions' page. Take the second.
df = results[1]

d = {}
for row_name, row in df.iterrows():
    # Each row in this table can only have one 'X' mark value.
    # Get the marked column names by dropping the other null row values.
    col_names = row.dropna().index.tolist()
    
    # There should only be one marked columns.
    # Pair the column name with the row label.
    d[row_name] = col_names[0]

# Create series of extrated pairs and add to the other extracted values.
s = pd.Series(d)
school_s = school_s.append(s)

# The sports table has a two level column headers, which pd.read_html converts
# to a multiindex with a names attribute that we can use to find the table.
results = [df for df in df_list if df.columns.names == ['Sport', 'Offered']]

# There should only be one result.
df = results[0]

# We'll just manually simplify the columns with new string names.
df.columns = ['Sports, Women, Scholarships Given',
              'Sports, Women, Offered',
              'Sports, Men, Scholarships Given',
              'Sports, Men, Offered']

# Otherwise, this procedure is similar to the previous table.
# In this table, multiple columns can be marked.
# It makes more sense to store each column as the key, and a
# list of all marked rows as the value in our dictionary.
d = {}
for col_name in df.columns:
    row_names = df[col_name].dropna().index.tolist()
    d[col_name] = row_names
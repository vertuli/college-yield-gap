import pandas as pd
import re
from os.path import isfile
from requests import get
from IPython.core.display import clear_output
from bs4 import BeautifulSoup, SoupStrainer

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
SCHOOL_ID_END = 5000
# CollegeData.com has no problem with requests without headers, but we can
# send a fake header anyway:
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) "
           "AppleWebKit/605.1.15 (KHTML, like Gecko) "
           "Version/12.0 Safari/605.1.15"}
# Finally, we'll export our scraped data to a CSV. The scraper will check
# if the CSV already exists, and if so, will adjust the `SCHOOL_ID_START` to
# begin with the `school_id` after the highest already scraped in the CSV:
PATH = "test_scraped.csv"


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

		# Print status message.
		print("Scraping school {}".format(school_id))

		try:
			# School dictionary to hold all scraped values.
			school_dict = {}

			# Scrape all six pages for each school and update school_dict.
			for page_id in range(1, 7):
				# Print status message.
				print("Scraping page {}".format(page_id))

				# Build URL.
				url = BASE_URL_1 + str(page_id) + BASE_URL_2 + str(school_id)

				soup = get_soup(url)

				cleaned_soup = clean_soup(soup)

				page_dict = scrape_page(cleaned_soup)

				school_dict.update(page_dict)

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
			# Convert dict to series and append to scaped_list.
			scraped_series = pd.Series(school_dict, name = school_id)
			scraped_list.append(scraped_series)
		finally:
			# Clear status message.
			clear_output()

	return scraped_list


def get_soup(url):
	# Request page and check if page returned.
	result = get(url, headers = HEADERS)
	if result.status_code != 200:
		raise PageRequestError
		
	# Parse result into soup object and check if valid page returned.
	soup = BeautifulSoup(result.text, "lxml")

	if not soup.h1:
		raise NoHeadingError

	if soup.h1.string == EMPTY_H1_HEADING:
		raise NoSchoolError

	if not soup.find(string = 'Content END'):
		raise IncompletePageError

	return soup


def clean_soup(soup):
	# Simplify all string text inside each header and data cells.
	for tag in soup(['th','td']):
		tag.string = " ".join(tag.stripped_strings)
	
	# Relabel the varying '{city_name} Population' tag with a constant label.
	tag = soup.find('th', string = re.compile('Population'))
	if tag:
		tag.string = 'City Population'

	# Add prefix to table labels to remove ambiguity with other fields.
	tag = soup.find('div', id = 'section7')
	if tag:
		th_tags = tag.table.tbody.find_all('th')
		for th_tag in th_tags:
			label = " ".join(th_tag.stripped_strings)
			th_tag.string = 'Factor - ' + label

	# Add gender suffixes to duplicate field names.
	tag = soup.find('div', id = 'section8')
	if tag:
		adm_rate_w = tag.find_next('th', string = re.compile('Women'))
		adm_rate_m = tag.find_next('th', string = re.compile('Men'))
		enrolled_w = adm_rate_w.find_next('th', string = re.compile('Women'))
		enrolled_m = adm_rate_m.find_next('th', string = re.compile('Men'))

		adm_rate_w.string = 'Overall Admission Rate (women)'
		adm_rate_m.string = 'Overall Admission Rate (men)'
		enrolled_w.string = 'Students Enrolled (women)'
		enrolled_m.string = 'Students Enrolled (men)'

	# Add appropriate markup to ambiguous need-based award labels.
	div_tag = soup.find('div', id = 'section11')
	if div_tag:
		captions = ['Freshmen', 'All Undergraduates']
		for caption in captions:
			cap_tag = div_tag.find('caption', string = re.compile(caption))
			table_tag = cap_tag.parent
			tags = table_tag.tbody.find_all('th')
			for tag in tags:
				tag.string = tag.string + ' (' + caption + ')'
				if tag.attrs == {'class': ['sub']}:
					tag.string = 'Average Award - ' + tag.string

	# Add appropriate markup to ambiguous non-need based award labels.
	div_tag = soup.find('div', id = 'section12')
	if div_tag:
		caption = re.compile('Non-Need Awards')
		cap_tag = div_tag.find('caption', string = caption)
		table_tag = cap_tag.parent
		tags = table_tag.tbody.find_all('th')
		for tag in tags:
			if tag.attrs != {'class': ['sub']}:
				tag.string = " ".join(tag.stripped_strings)
				subtags = tag.find_all_next('th')[:2]
				for subtag in subtags:
					subtag.string = " ".join(subtag.stripped_strings)
					subtag.string = tag.string[:-12] + " - " + subtag.string  

	# Restructure the data involved with the varying FAFSA code labels:
	tag = soup.find('th', string = re.compile('FAFSA'))
	if tag:
		fafsa_code = re.search('(\d+)', tag.string)[0]  #extract fafsa code
		finaid_filing_fee = tag.next_sibling.string  #extract filing fee

		tag.string = 'FAFSA_code'  # add new header tag
		tag.next_sibling.string = fafsa_code # add data

		new_heading = soup.new_tag('th') # create new header tag
		new_heading.string = 'finaid_filing_fee' # add header
		new_data = soup.new_tag('td') # create new data tag
		new_data.string = finaid_filing_fee # add data

		new_row = soup.new_tag('tr') # create new row tag
		new_row.insert(0, new_heading) # insert the header tag into new row
		new_row.insert(1, new_data) # insert the data tag into new row
		tag.parent.insert_after(new_row) # insert the new row

	# Delete certain div sections by their id tags.
	div_ids = ['section19']
	tags = soup.find_all(id = div_ids)
	if tags:
		for tag in tags:
			tag.decompose()

	# Delete certain duplicate values.
	tag = soup.find('div', id = 'section26')
	if tag:
		strings = ['All Undergraduates','Women','Men']
		for string in strings:
			regex = re.compile(string)
			tag.find_next('th', string = regex).parent.decompose()

	# Delete certain redundant tables by their caption strings.
	captions = [
		'Selection of Students',
		'Grade Point Average of Enrolled Freshmen',
		'SAT Scores of Enrolled Freshmen',
		'ACT Scores of Enrolled Freshmen',
		'Financial Aid Office',
		'Undergraduate Majors',
		'Intercollegiate Sports Offered'
		]
	regexs = [re.compile(caption) for caption in captions]
	tags = soup.find_all('caption', string = regexs)
	if tags:
		for tag in tags:
			tag.parent.decompose()

	# Relabel some labels on first page to remove ambiguity with duplicates.
	tag = soup.find('th', string = 'Undergraduate Students')
	if tag:
		women = tag.find_next('th', string = re.compile('Women'))
		men = tag.find_next('th', string = re.compile('Men'))
		grads = tag.find_next('th', string = re.compile('Graduate Students'))

		tag.string = 'All Undergraduates'
		women.string = 'Undergrads (women)'
		men.string = 'Undergrads (men)'
		grads.string = 'All Graduate Students'

	return soup


def scrape_page(soup):
	# Store and return scraped values as a dictionary.
	page_dict = {}

	# Restrict the search area in the soup to the primary 'tabcontwrap' div.
	content = soup.find('div', id = 'tabcontwrap')

	# First, only consider rows with a header cell and exactly one data cell.
	# Rows with more than one data cell will be handled afterwards as tables.
	for tr in content('tr'):
		if tr.th and tr.th.string and len(tr.find_all('td')) == 1:
			# Use the table header string as the dictionary key.
			key = tr.th.string
			# Append '*' to duplicate keys until key is unique.
			while key in page_dict.keys():
				key += '*'
			page_dict[key] = tr.td.string

			# Delete all scraped rows from the soup.
			tr.decompose()

	# Next, consider remaining rows that are in "table" format.
	# They are structured inside actual tables, each with thead tags.
	for thead in content('thead'):

		# Get the table column labels.
		td_tags = thead('td')
		col_labels = []
		for i, td_tag in enumerate(td_tags):
			label = " ".join(td_tag.stripped_strings)
			col_labels.append(label)

		# For each table row, get the row labels and row data cell values.
		tr_tags = thead.parent.tbody('tr')
		for tr_tag in tr_tags:
			
			# Get the row label.
			row_label = tr_tag.th.string

			# Get the row values.
			row_values = []
			td_tags = tr_tag('td')
			for td_tag in td_tags:
				row_values.append(td_tag.string)

			# There are two table formats in use across the site.
			# The first type has data cells either marked with "X" or null.
			# If the table is this first type, then each row can be
			# represented as a single key:value pair using the row label
			# as the key and column label marked by "X" as the value.
			unique_vals = set(row_values)
			if (len(unique_vals) == 2) and ('X' in unique_vals):
				index_val = row_values.index('X')
				key = row_label
				page_dict[key] = col_labels[index_val]

			# If there is data different from only 'X' in the table cells,
			# then each cell must be saved as its own key:value pair.
			# The value is simply the cell value. The key will be the row
			# label combined with the column label corresponding to the cell.
			else:
				for j, row_value in enumerate(row_values):
					key = row_label
					if key:
						if col_labels[j]:
							key = key + " - " + col_labels[j]
						page_dict[key] = row_value

	if not page_dict:
		raise EmptyPageError

	return page_dict


# Run scraper.
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
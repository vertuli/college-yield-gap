import numpy as np

col_rename_dict = {
	'ACT Composite - 1':'ACT Mean',
	'ACT Composite - 2':'ACT 25th',
	'ACT Composite - 3':'ACT 75th',
	'ACT Composite - 4':'*delete*',
	'Application Fee - 1':'Application Fee',
	'Average Award - Merit-Based Gift (All Undergraduates) - 1':'FinAid Merit-Based Gift (all)',
	'Average Award - Merit-Based Gift (All Undergraduates) - 2':'FinAid Merit-Based Gift pct of FinAid Received (all)',
	'Average Award - Merit-Based Gift (Freshmen) - 1':'FinAid Merit-Based Gift (freshmen)',
	'Average Award - Merit-Based Gift (Freshmen) - 2':'FinAid Merit-Based Gift pct of FinAid Received (freshmen)',
	'Average Award - Need-Based Gift (All Undergraduates) - 1':'FinAid Need-Based Gift (all)',
	'Average Award - Need-Based Gift (All Undergraduates) - 2':'FinAid Need-Based Gift pct of FinAid Received (all)',
	'Average Award - Need-Based Gift (All Undergraduates) - 3':'FinAid Need-Based Gift avg Amount (all)',
	'Average Award - Need-Based Gift (Freshmen) - 1':'FinAid Need-Based Gift (freshmen)',
	'Average Award - Need-Based Gift (Freshmen) - 2':'FinAid Need-Based Gift pct of FinAid Received (freshmen)',
	'Average Award - Need-Based Gift (Freshmen) - 3':'FinAid Need-Based Gift avg Amount (freshmen)',
	'Average Award - Need-Based Self-Help (All Undergraduates) - 1':'FinAid Need-Based Self-Help (all)',
	'Average Award - Need-Based Self-Help (All Undergraduates) - 2':'FinAid Need-Based Self-Help pct of FinAid Received (all)',
	'Average Award - Need-Based Self-Help (All Undergraduates) - 3':'FinAid Need-Based Self-Help avg Amount (all)',
	'Average Award - Need-Based Self-Help (Freshmen) - 1':'FinAid Need-Based Self-Help (freshmen)',
	'Average Award - Need-Based Self-Help (Freshmen) - 2':'FinAid Need-Based Self-Help pct of FinAid Received (freshmen)',
	'Average Award - Need-Based Self-Help (Freshmen) - 3':'FinAid Need-Based Self-Help avg Amount (freshmen)',
	'Average Starting Salary - 1':'Average Starting Salary',
	'Campus Size - 1':'Campus Size (acres)',
	'Cost of Attendance - 1':'Cost of Attendance',
	'Early Action Admission Rate - 1':'Offer Rate (EA)',
	'Early Action Admission Rate - 2':'Applications (EA)',
	'Early Decision Admission Rate - 1':'Offer Rate (ED)',
	'Early Decision Admission Rate - 2':'Applications (ED)',
	'Ethnicity of Students from U.S. - 1':'Demographics pct American Indian/Alaskan Native',
	'Ethnicity of Students from U.S. - 2':'Demographics pct Asian',
	'Ethnicity of Students from U.S. - 3':'Demographics pct Black/African-American',
	'Ethnicity of Students from U.S. - 4':'Demographics pct Hispanic/Latino',
	'Ethnicity of Students from U.S. - 5':'Demographics pct Multi-race (not Hispanic/Latino)',
	'Ethnicity of Students from U.S. - 6':'Demographics pct Native Hawaiian/Pacific Islander',
	'Ethnicity of Students from U.S. - 7':'Demographcis pct White',
	'Ethnicity of Students from U.S. - 8':'Demographics pct Unknown',
	'Financial Aid Applicants (All Undergraduates) - 1':'FinAid Apps (all)',
	'Financial Aid Applicants (All Undergraduates) - 2':'FinAid Apps (pct of all)',
	'Financial Aid Applicants (Freshmen) - 1':'FinAid Apps (freshmen)',
	'Financial Aid Applicants (Freshmen) - 2':'FinAid Apps (pct of freshmen)',
	'Found to Have Financial Need (All Undergraduates) - 1':'FinAid Need Found (all)',
	'Found to Have Financial Need (All Undergraduates) - 2':'FinAid Need Found pct of FinAid Apps (all)',
	'Found to Have Financial Need (Freshmen) - 1':'FinAid Need Found (freshmen)',
	'Found to Have Financial Need (Freshmen) - 2':'FinAid Need Found pct of FinAid Apps (freshmen)',
	'Fraternities - 1':'Fraternities pct of Men',
	'High School Class Rank - 1':'Freshmen pct in HS Top 10th',
	'High School Class Rank - 2':'Freshmen pct in HS Top 25th',
	'High School Class Rank - 3':'Freshmen pct in HS Top 50th',
	'International Students - 1':'International pct of students',
	'International Students - 2':'International countries represented',
	'Merit-Based Gift (All Undergraduates) - 1':'No FinAid Merit-Based Gift (all)',
	'Merit-Based Gift (All Undergraduates) - 2':'No FinAid Merit-Based Gift pct of students (all)',
	'Merit-Based Gift (All Undergraduates) - 3':'No FinAid Merit-Based Gift avg Amount (all)',
	'Merit-Based Gift (Freshmen) - 1':'No FinAid Merit-Based Gift (freshmen)',
	'Merit-Based Gift (Freshmen) - 2':'No FinAid Merit-Based Gift pct of students (freshmen)',
	'Merit-Based Gift (Freshmen) - 3':'No FinAid Merit-Based Gift avg Amount (freshmen)',
	'Need Fully Met (All Undergraduates) - 1':'FinAid Need Fully Met (all)',
	'Need Fully Met (All Undergraduates) - 2':'FinAid Need Fully Met pct of FinAid Received (all)',
	'Need Fully Met (Freshmen) - 1':'FinAid Need Fully Met (freshmen)',
	'Need Fully Met (Freshmen) - 2':'FinAid Need Fully Met pct of FinAid Received (freshmen)',
	'Overall Admission Rate (men) - 1':'Offer Rate (men)',
	'Overall Admission Rate (men) - 2':'Applications (men)',
	'Overall Admission Rate (women) - 1':'Offer Rate (women)',
	'Overall Admission Rate (women) - 2':'Applications (women)',
	'Overall Admission Rate - 1':'Offer Rate (all)',
	'Overall Admission Rate - 2':'Applications (all)',
	'Rain - 1':'Rainy Days (annual mean)',
	'Received Financial Aid (All Undergraduates) - 1':'FinAid Received (all)',
	'Received Financial Aid (All Undergraduates) - 2':'FinAid Received pct of FinAid Need Found (all)',
	'Received Financial Aid (Freshmen) - 1':'FinAid Received (freshmen)',
	'Received Financial Aid (Freshmen) - 2':'FinAid Received pct of FinAid Need Found (freshmen)',
	'SAT Critical Reading - 1':'SAT Reading Mean',
	'SAT Critical Reading - 2':'SAT Reading 25th',
	'SAT Critical Reading - 3':'SAT Reading 75th',
	'SAT Critical Reading - 4':'*delete*',
	'SAT Math - 1':'SAT Math Mean',
	'SAT Math - 2':'SAT Math 25th',
	'SAT Math - 3':'SAT Math 75th',
	'SAT Math - 4':'*delete*',
	'Sororities - 1':'Sororities pct of Women',
	'Students Enrolled (men) - 1':'Freshmen Enrolled (men)',
	'Students Enrolled (men) - 2':'Yield Rate (men)',
	'Students Enrolled (men) - 3':'Offers (men)',
	'Students Enrolled (women) - 1':'Freshmen Enrolled (women)',
	'Students Enrolled (women) - 2':'Yield Rate (women)',
	'Students Enrolled (women) - 3':'Offers (women)',
	'Students Enrolled - 1':'Freshmen Enrolled (all)',
	'Students Enrolled - 2':'Yield Rate (all)',
	'Students Enrolled - 3':'Offers (all)',
	'Students in College Housing - 1':'College Housing pct of Students',
	'Temperature - 1':'Temperature (January mean low)',
	'Temperature - 2':'Temperature (September mean high)',
	'Tuition and Fees - 1':'Tuition and Fees',
	'Undergrads (men) - 1':'Undergraduates (men)',
	'Undergrads (men) - 2':'Undergraduates (men pct of all)',
	'Undergrads (women) - 1':'Undergraduates (women)',
	'Undergrads (women) - 2':'Undergraduates (women pct of all)'
}

dirty_cols_extract_dict = {
    'ACT Composite':{
        'ACT 25th':'(\d+)-',
        'ACT 75th':'-(\d+)',
        'ACT Mean':'(\d)+ average'
    },
    'Average Award - Merit-Based Gift (All Undergraduates)':{
        'FinAid Merit-Based Gift (all)':'(\d+)'
    },
    'Average Award - Merit-Based Gift (Freshmen)':{
        'FinAid Merit-Based Gift (freshmen)':'(\d+)'
    },
    'Average Award - Need-Based Gift (All Undergraduates)':{
        'FinAid Need-Based Gift (all)':'Received by (\d+)',
        'FinAid Need-Based Gift pct of FinAid Received (all)':'\(([\d\.]+)\)',
        'FinAid Need-Based Gift avg Amount (all)':'amount (\d+)'
    },
    'Average Award - Need-Based Gift (Freshmen)':{
        'FinAid Need-Based Gift (freshmen)':'Received by (\d+)',
        'FinAid Need-Based Gift pct of FinAid Received (freshmen)':'\(([\d\.]+)\)',
        'FinAid Need-Based Gift avg Amount (freshmen)':'amount (\d+)'
    },
    'Average Award - Need-Based Self-Help (All Undergraduates)':{
        'FinAid Need-Based Self-Help (all)':'Received by (\d+)',
        'FinAid Need-Based Self-Help pct of FinAid Received (all)':'\(([\d\.]+)\)',
        'FinAid Need-Based Self-Help avg Amount (all)':'amount (\d+)'
    },
    'Average Award - Need-Based Self-Help (Freshmen)':{
        'FinAid Need-Based Self-Help (freshmen)':'Received by (\d+)',
        'FinAid Need-Based Self-Help pct of FinAid Received (freshmen)':'\(([\d\.]+)\)',
        'FinAid Need-Based Self-Help avg Amount (freshmen)':'amount (\d+)'
    },
    'Average Starting Salary':{
    	'Average Starting Salary':'(\d+)'
    },
    'Campus Size':{
        'Campus Size (acres)':'(\d+)'
    },
    'Cost of Attendance':{
        'Cost of Attendance':'Out-of-state: (\d+)',
        'Cost of Attendance (in-state)':'In-state: (\d+)'
    },
    'Ethnicity of Students from U.S.':{
        'Demographics pct American Indian/Alaskan Native':'([\d\.]+) American',
        'Demographics pct Asian':'([\d\.]+) Asian',
        'Demographics pct Black/African-American':'([\d\.]+) Black',
        'Demographics pct Hispanic/Latino':'([\d\.]+) Hispanic',
        'Demographics pct Multi-race (not Hispanic/Latino)':'([\d\.]+) Multi',
        'Demographics pct Native Hawaiian/Pacific Islander':'([\d\.]+) Native',
        'Demographcis pct White':'([\d\.]+) White',
        'Demographics pct Unknown':'([\d\.]+) Unknown'
    },
    'Financial Aid Applicants (All Undergraduates)':{
        'FinAid Apps (all)':'(\d+)'
    },
    'Found to Have Financial Need (All Undergraduates)':{
        'FinAid Need Found (all)':'(\d+)'
    },
    'Found to Have Financial Need (Freshmen)':{
        'FinAid Need Found (freshmen)':'(\d+)'
    },
    'High School Class Rank':{
        'Freshmen pct in HS Top 10th':'Top tenth:\s*([\d\.]+)',
        'Freshmen pct in HS Top 25th':'Top quarter:\s*([\d\.]+)',
        'Freshmen pct in HS Top 50th':'Top half:\s*([\d\.]+)'
    },
    'International Students':{
        'International pct of students':'([\d\.]+)'
    },
    'Merit-Based Gift (All Undergraduates)':{
        'No FinAid Merit-Based Gift (all)':'^(\d+)',
        'No FinAid Merit-Based Gift pct of students (all)':'\(([\d\.]+)\)',
        'No FinAid Merit-Based Gift avg Amount (all)':'amount (\d+)'
    },
    'Merit-Based Gift (Freshmen)':{
        'No FinAid Merit-Based Gift (freshmen)':'^(\d+)',
        'No FinAid Merit-Based Gift pct of students (freshmen)':'\(([\d\.]+)\)',
        'No FinAid Merit-Based Gift avg Amount (freshmen)':'amount (\d+)'
    },
    'Need Fully Met (All Undergraduates)':{
    	'FinAid Need Fully Met (all)':'(\d+)'
    },
    'Need Fully Met (Freshmen)':{
    	'FinAid Need Fully Met (freshmen)':'(\d+)'
    },
    'Overall Admission Rate (men)':{
        'Offers (men)':'(\d+)'
    },
    'Overall Admission Rate (women)':{
        'Offers (women)':'(\d+)'
    },
    'Rain':{
        'Rainy Days (annual mean)':'(\d+)'
    },
    'Received Financial Aid (All Undergraduates)':{
        'FinAid Received (all)':'(\d+)'
    },
    'Received Financial Aid (Freshmen)':{
        'FinAid Received (freshmen)':'(\d+)'
    },
    'SAT Critical Reading':{
        'SAT Reading Mean':'(\d+)\s*average',
        'SAT Reading 25th':'(\d+)\s*-',
        'SAT Reading 75th':'-\s*(\d+)'
    },
    'SAT Math':{
        'SAT Math Mean':'(\d+)\s*average',
        'SAT Math 25th':'(\d+)\s*-',
        'SAT Math 75th':'-\s*(\d+)'
    },
    'Students Enrolled':{
        'Freshmen Enrolled (all)':'(\d+)'
    },
    'Students Enrolled (men)':{
        'Freshmen Enrolled (men)':'(\d+)'
    },
    'Students Enrolled (women)':{
        'Freshmen Enrolled (women)':'(\d+)'
    },
    'Temperature':{
        'Temperature (January mean low)':'([-\d\.]+) average low',
        'Temperature (September mean high)':'([-\d\.]+) average high'
    },
    'Tuition and Fees':{
        'Tuition and Fees':'Out-of-state: (\d+)',
        'Tuition and Fees (in-state)':'In-state: (\d+)'
    }
}


usnews_rename_names = {
	'Alabama Agricultural and Mechanical University':'Alabama A&M University',
	'Augusta University':'Georgia Regents University',
	'Brigham Young University--Hawaii':'Brigham Young University - Hawaii',
	'CUNY--New York City College of Technology':'New York City College of Technology',
	'CUNY--York College':'York College',
	'College of St. Benedict':'College of Saint Benedict',
	"College of St. Mary":"College of Saint Mary",
	'Concordia College':'Concordia College New York',
	'DeVry University':'DeVry University - Chicago',
	'Embry-Riddle Aeronautical University':'Embry-Riddle Aeronautical University - Daytona Beach',
	'Everglades University':'Everglades University - Boca Raton',
	'Fairleigh Dickinson University':'Fairleigh Dickinson University - Metropolitan Campus',
	'Florida A&M University':'Florida Agricultural and Mechanical University',
	'Lincoln College':'Lincoln Christian University',
	'Maryville University of St. Louis':'Maryville University of Saint Louis',
	'Notre Dame College of Ohio':'Notre Dame College',
	'Rutgers University--New Brunswick':'Rutgers The State University of New Jersey',
	'Rutgers University--Newark':'Rutgers The State University of New Jersey - Newark',
	'SUNY College of Technology--Alfred':'Alfred State College',
	'SUNY College--Old Westbury':'College at Old Westbury',
	'SUNY Polytechnic Institute--Albany/Utica':'State University of New York Institute of Technology',
	'South University':'South University - Savannah',
	'Southern University and A&M College':'Southern University and Agricultural and Mechanical College',
	"St. John's University":"Saint John's University",
	"St. Joseph's College":"St. Joseph's College of Maine",
	"St. Joseph's College New York":"St. Joseph's College - Brooklyn Campus",
	"St. Mary's College":"Saint Mary's College",
	"St. Mary's University of San Antonio":"St. Mary's University",
	"St. Francis University":"Saint Francis University",
	'University of Maryland--College Park':'University of Maryland',
	'University of Missouri':'University of Missouri - Columbia',
	'University of Providence':'University of Great Falls',
	'University of Saint Francis':'University of St. Francis',
 	'Virginia Wesleyan University':'Virginia Wesleyan College'
 }

usnews_rename_cities = {
  	'Laie Oahu':'Laie',
 	'St. Joseph':'Saint Joseph',
 	'St Louis':'St. Louis',
 	'Normal':'Huntsville',
 	'Downers Grove':'Chicago',
 	'Cleveland':'South Euclid',
 	'Norfolk':'Virginia Beach'
 }

num_col_ranges = {
	'ACT 25th':(1, 36),
	'ACT 75th':(1, 36),
	'ACT Mean':(1, 36),
	'Application Fee':(0,1000),
	'Applications (all)':(0,1000000),
	'Average Age':(18,100),
	'Average Award (All Undergraduates)':(0,100000),
	'Average Award (Freshmen)':(0,100000),
	'Average Earnings from On-Campus Employment':(0,100000),
	'Average Freshman Award':(0,100000),
	'Average GPA':(1,5),
	'Average Indebtedness of 2016 Graduates':(0,100000),
	'Books and Supplies':(0,100000),
	'Campus Size (acres)':(0,100000),
	'Computers Available on Campus':(0,100000),
	'Cost of Attendance':(0,100000),
	'FinAid Apps (all)':(0,100000),
	'FinAid Apps (freshmen)':(0,100000),
	'FinAid Merit-Based Gift (all)':(0,100000),
	'FinAid Merit-Based Gift (freshmen)':(0,100000),
	'FinAid Need Found (all)':(0,100000),
	'FinAid Need Found (freshmen)':(0,100000),
	'FinAid Need Fully Met (all)':(0,100000),
	'FinAid Need Fully Met (freshmen)':(0,100000),
	'FinAid Need-Based Gift (all)':(0,100000),
	'FinAid Need-Based Gift (freshmen)':(0,100000),
	'FinAid Need-Based Gift avg Amount (all)':(0,100000),
	'FinAid Need-Based Gift avg Amount (freshmen)':(0,100000),
	'FinAid Need-Based Self-Help (all)':(0,100000),
	'FinAid Need-Based Self-Help (freshmen)':(0,100000),
	'FinAid Need-Based Self-Help avg Amount (all)':(0,100000),
	'FinAid Need-Based Self-Help avg Amount (freshmen)':(0,100000),
	'FinAid Received (all)':(0,100000),
	'FinAid Received (freshmen)':(0,100000),
	'Full-Time Faculty':(0,100000),
	'Full-Time Faculty Teaching Undergraduates':(0,100000),
	'Holdings':(0,100000000),
	'International countries represented':(0,250),
	'Nearest Airport (miles)':(0,1000),
	'Nearest Bus Station (miles)':(0,1000),
	'Nearest Train Station (miles)':(0,1000),
	'No FinAid Merit-Based Gift (all)':(0,100000),
	'No FinAid Merit-Based Gift (freshmen)':(0,100000),
	'No FinAid Merit-Based Gift avg Amount (all)':(0,100000),
	'No FinAid Merit-Based Gift avg Amount (freshmen)':(0,100000),
	'Other Expenses':(0,100000),
	'Part-Time Faculty':(0,100000),
	'Rainy Days (annual mean)':(0,365),
	'Rank':(1,300),
	'Room and Board':(0,100000),
	'SAT Math 25th':(200,800),
	'SAT Math 75th':(200,800),
	'SAT Reading 25th':(200,800),
	'SAT Reading 75th':(200,800),
	'Temperature (January mean low)':(-50,150),
	'Temperature (September mean high)':(-50,150),
	'Tuition and Fees':(0,100000),
	'Students (all)':(0,100000)
}
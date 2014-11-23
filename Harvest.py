import requests, argparse, base64, workdays, datetime

parser = argparse.ArgumentParser(description='Perform Employee Harvest Calculations')
parser.add_argument('-u', '--user', required=True, help='Username')
parser.add_argument('-p', '--password', required=True, help='User password')
parser.add_argument('-ph', '--previousHours', required=False, help='Hours that are tracked outside or not inside of Harvest')
parser.add_argument('-v', '--vacationDays', required=False, help='Comma delimited list of YYYYMMDD expected vacation days. This should include holidays!')
parser.add_argument('-url', '--loginURL', required=True, help='The base URL you visit to log all Harvest time')
parser.add_argument('-s', '--salary', required=True, help='Yearly salary value used to calculate ultilization bonus')

args = parser.parse_args()

url = args.loginURL
salary = args.salary

credentialsEncoded = base64.b64encode(args.user + ':' + args.password)
authorizationData = "Basic " + credentialsEncoded
headers = {'Authorization': authorizationData, "Content-Type": "application/json", "Accept": "application/json"}

# Get the information about the current user that is needed.
resp = requests.get(url="https://" + str(url) + "/account/who_am_i", headers=headers)
data = resp.json()
userId = data['user']['id']

# Get all of the billable hours for the user.
resp = requests.get(url="https://" + str(url) + "/people/" + str(userId) + "/entries?from=20140101&to=20141231&billable=yes", headers=headers)
billableData = resp.json()

totalHours = 0
for entry in billableData:
    totalHours += float(entry['day_entry']['hours'])

# Print the YTD burn rate before adding previous hours because that will effect the calculation
ytdBurnRate = totalHours/len(billableData)

# Add the previous hours if specified.
if args.previousHours > 0:
    totalHours += float(args.previousHours)
    print args.previousHours + " hours were not calculated in YTD burn rate because their daily duration is unknown!"

print "Total Billable Hours: " + ('%.2f' % totalHours)
print "YTD Burn Rate: " + ('%.2f' % ytdBurnRate)

today = datetime.datetime.now()
lastDayOfYear = datetime.datetime(today.year, 12, 31)

print "Today is " + str(today) + " - Last Day of year is " + str(lastDayOfYear)

vacationDays = []
if args.vacationDays is not None:
    print "Considering Vacation Days -> " + args.vacationDays
    vacationDays = [datetime.datetime.strptime(n, '%Y%m%d') for n in str(args.vacationDays).split(",")]
    print str(len(vacationDays)) + " Vacation days will be taken into consideration"

# holidays.append(datetime.datetime.strptime('20141225', "%Y%m%d"))

numWorkDays = workdays.networkdays(today, lastDayOfYear, vacationDays)
print str(numWorkDays) + " work days remaining"

eighteenRemHours = 1880 - totalHours
fifteenRemHours = (1880 * 0.85) - totalHours
tenRemHours = (1880 * .80) - totalHours

print "\n"
print "18% hours remaining " + str(eighteenRemHours) + " burn rate required " + str(eighteenRemHours / numWorkDays) + " bonus after 30% tax: " + str((int(salary) * 0.18) * .70)
print "15% hours remaining " + str(fifteenRemHours) + " burn rate required " + str(fifteenRemHours / numWorkDays) + " bonus after 30% tax: " + str((int(salary) * 0.15) * .70)
print "10% hours remaining " + str(tenRemHours) + " burn rate required " + str(tenRemHours / numWorkDays) + " bonus after 30% tax: " + str((int(salary) * 0.10) * .70)
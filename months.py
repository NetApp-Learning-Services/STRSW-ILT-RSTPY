#! /usr/local/bin/python3.11
### Python script to display number of days in each month ###
month_days = {
    'January': '31',
    'February':'28',
    'March': '31',
    'April': '30',
    'May': '31',
    'June': '30',
    'July': '31',
    'August': '31',
    'September': '30',
    'October': '31',
    'November': '30',
    'December': '31'
}

for month, days in month_days.items():
    print(month.title(), days.title())

# Functions to help standardize data formatting

# ==============================================
# date_string_to_quoted
# ==============================================
#   args:
#       date_string   string of form 'M/D/Y'
#                     M and D may be 1-2 chars
#                     Y may be 2 or 4 chars
# 
#   returns:
#       string of form '"M/D/Y"'
#       where M, D, Y are each 2 chars long

def date_string_to_quoted(date_string):
  month, date, year = date_string.split('/')
  
  if len(month) == 1:
    month = '0' + month
  
  if len(date) == 1:
    date = '0' + date
  
  if len(year) == 4:
    year = year[-2:]
  
  return '"%s/%s/%s"' % (month, date, year)
	
from __future__ import print_function, division
from datetime import datetime
import csv,sys,os
import logging

_logger = logging.getLogger(__name__)

def do_login(usern):
    # create a login name based on username
    username = usern.split()
    login_name = ""
    if len(username) == 1:
        login_name = username[0]
    else:
        login_name = username[0] + '_' + username[1]
    return login_name

#  Create User or Salesperson
# Neither a Customer nor Supplier

# Main routine

# get partner to create from a csv file
DICTFILE = 'fidodict.csv'
OUTF = '/tmp/create_user.out'
ERRF = '/tmp/create_user.err'
outfile = open(OUTF,'w')
errfile = open(ERRF,'w')

with open(DICTFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        try:
            username = row['SalesPerson Name'].strip().upper()+'-SALES'
            partner = row['Customer Name'].strip().upper()
            user_obj = env['res.users'].search([('name','=',username)])

            assert len(user_obj) == 0, "user exists in DB"
            login_name = do_login(username)
            p = user_obj.sudo().create({'name': username,'login':login_name,\
                        'customer':False,'supplier':False,'notify_email':'none'})

            if p:
                print ('User Creation successful !!! ',username)
                print ('User creation successful !!! ', username,file=outfile)
            else:
                print ('*** User ',username,' Creation FAILED ***')
                print ('*** User ', username, ' Creation FAILED ***',file=errfile)

        except Exception, e:
           # print ("Error creating Partner: ",str(e),partner)
            print ('Creation Error. \n',str(e),username,file=errfile)
            # sys.exit(1)

self._cr.commit()

errfile.close()
outfile.close()

print ('====================ERRORS in ',ERRF)

print ('===============SUCCESSFUL OUTPUT IN ',OUTF)

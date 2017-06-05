from __future__ import print_function, division
from datetime import datetime
import csv,sys,os
import logging

_logger = logging.getLogger(__name__)

# update list of partners with given attributes

# Main routine

# get partner to update from a csv file
count = 0
DICTFILE = 'fpldb_customers.csv'
outfile = open('/tmp/update_partner.out','w')
errfile = open('/tmp/update_partner.err','w')
with open(DICTFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        try:
            count = count + 1

            username = row['SalesPerson Name']
            partner = row['Customer Name']
            partner_obj = env['res.partner'].search([('name','=',partner)])
            print('Processing...dict line', count,',',partner,',',username)
            assert partner_obj, "partner name does not exist in DB"

            partner_name = partner_obj.name
            user_obj = env['res.users'].search([('name', '=', username)])

            assert user_obj, "User name does not exist in DB"

            # change case for Partner
            pu = partner_obj.write({'name':partner.strip().upper()})
            if pu:
                print ('Partner CHange Case update successful !!! ',partner_name,',',partner.strip().upper())
                print('Partner CHange Case update successful !!! ', partner_name, ',', partner.strip().upper(),file=outfile)

            else:
                print ('*** Partner ',partner,' case update FAILED ***')
                print ('*** Partner ', partner, ' Case update FAILED ***',file=errfile)

            assert pu,'Partner CHange Case failed'

            #Change Case for User
            su = user_obj.write({'name':username.strip.upper()})
            assert su,'User upper-casing failed'

            user_id = user_obj.id
            assert partner_obj.user_id.id != user_id,"User_id Already in Partner"

            u = partner_obj.write({'user_id': user_id})

            if u:
                print ('Partner update successful with user !!! ',partner_name,',',username)
                print ('Partner update successful !!! ', partner_name.strip().upper(),',',username,file=outfile)
            else:
                print ('*** Partner ',partner,' update FAILED ***')
                print ('*** Partner ', partner, ' update FAILED ***',file=errfile)

        except Exception, e:
            # print ("Error updating Partner: ",str(e),'\n',partner,',',username)
            print ("Exception: Error updating Partner: ", str(e),',',partner,',',username,file=errfile)
            raise

self._cr.commit()
errfile.close()
outfile.close()
print('See out and err files /tmp/update_partner.err or .out\n Content of error file below:\n')
print ('====================See ERRORS a in /tmp/update_partner.err============\n')

print ('===========See SUCCESSFUL OUTPUT in /tmp/update_partner.out============\n')

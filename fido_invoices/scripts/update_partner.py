from __future__ import print_function, division
from datetime import datetime
import csv,sys
import logging

_logger = logging.getLogger(__name__)

# update list of partners with given attributes

class Update_Partner:
    # global vars
    partner_id =""

    # partner_obj is for a given partner and set by main routine
    partner_obj = ""
    partner_name = ""

    def update_userid(self, user_name):
        # updates partner with given username,
        # in Fido all user_names are UPPER
        try:
            username = user_name.strip().upper()
            user_obj = env['res.users'].search([('name','=',username)])
            user_id = user_obj.id
            if user_id:
                print ('Updating Partner ', partner_name, 'with user ', username)
                partner = partner_obj.write({'user_id':user_id})
                return partner
            else:
                print("User: ",user_obj.name, ' not in DB')
        except Exception, e:
            print ("Function: update_userid: Error updating with user name: ",username)
            _logger.info('Exception Error: ', str(e))
            sys.exit(1)

        return None


# Main routine

# get partner to update from a csv file
DICTFILE = 'fidodict.csv'
outfile = open('/tmp/update_partner.out','w')
errfile = open('/tmp/update_parner.err','w')
with open(DICTFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        try:
            username = row['SalesPerson Name'].strip().upper()+'-SALES'
            partner = row['Customer Name'].strip().upper()
            partner_obj = env['res.partner'].search([('name','=',partner)])
            partner_name = partner_obj.name

            u = Update_Partner().update_userid(username)

            if u is not None:
                print ('Partner update successful !!! ',u)
                print ('Partner update successful !!! ', partner_name,file=outfile)
            else:
                print ('*** Partner ',partner,' update FAILED ***')
                print ('*** Partner ', partner, ' update FAILED ***',file=errfile)

        except Exception, e:
            print ("Error updating Partner: ",partner)
            print ("Exception: Error updating Partner: ", partner,str(e),file=errfile)

            _logger.info('Exception Error: ', str(e))
            sys.exit(1)

print('See out and err files /tmp/update_partner.err or .out')
self._cr.commit()

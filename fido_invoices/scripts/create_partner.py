from __future__ import print_function, division
from datetime import datetime
import csv,sys,os
import logging

_logger = logging.getLogger(__name__)

#  Create Partner

# Main routine

# get partner to create from a csv file
DICTFILE = 'fidodict.csv'
outfile = open('/tmp/update_partner.out','w')
errfile = open('/tmp/update_partner.err','w')
with open(DICTFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        try:
            username = row['SalesPerson Name'].strip().upper()+'-SALES'
            partner = row['Customer Name'].strip().upper()
            partner_obj = env['res.partner'].search([('name','=',partner)])

            assert len(partner_obj) == 0, "partner exists in DB"
            p = partner_obj.sudo().create({'name': partner, 'customer': True, 'supplier': False})

            if p:
                print ('Partner Creation successful !!! ',partner)
                print ('Partner creation successful !!! ', partner,file=outfile)
            else:
                print ('*** Partner ',partner,' Creation FAILED ***')
                print ('*** Partner ', partner, ' Creation FAILED ***',file=errfile)

        except Exception, e:
           # print ("Error creating Partner: ",str(e),partner)
            print ('Creation Error. \n',str(e),partner,file=errfile)
            # sys.exit(1)

self._cr.commit()
errfile.close()
outfile.close()
print('See out and err files /tmp/update_partner.err or .out\n Content of error file below:\n')
print ('====================ERRORS in /tmp/update_partner.err============\n')

print ('====================================================================\n')

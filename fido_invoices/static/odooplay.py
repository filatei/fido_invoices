from __future__ import print_function, division
"""
from __future__ import print_function
sudo su -  odoo9 -s /bin/bash 
./odoo.py shell -d <dbname>
account_invoice_obj = env['account.invoice']

"""
"""
from openerp import api, fields, models
import datetime
import time
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)
"""

class ReportInvoice():
    
    """ out_invoice is customer invoice, not vendor bill"""
    def listInvoices(self,mydate,invtype):
        """ List all customer invoices greater than mydate
           invtype is 'out_invoice' for Customer invoice or 'in_invoice' for vendor bills
        """
        account_invoice_obj = env['account.invoice'].search([('date_invoice', '>', mydate), \
                                                     ('type','=',invtype)])
        prt = 'Date,Customer,product,qty,unitprice\n'
        prtl = ""
        for invoice in account_invoice_obj:
            lenlines = len(invoice.invoice_line_ids)
            if invoice.date_invoice  and lenlines > 0:
                prt = prt + str(invoice.date_invoice) + ',' + str(invoice.partner_id.name) +','+ \
			str(invoice.invoice_line_ids[0].name) + ',' + str(invoice.invoice_line_ids[0].quantity) \
                + ',' + str(invoice.invoice_line_ids[0].price_unit) + '\n'    
                lenlines = len(invoice.invoice_line_ids)
		
                prtl = ""
                for k in range(1,lenlines):
		   
                    prtl = ',,' + str(invoice.invoice_line_ids[k].name) + ',' + str(invoice.invoice_line_ids[k].quantity) \
                    + ',' + str(invoice.invoice_line_ids[k].price_unit) + '\n'
		    
                    prt = prt + prtl
        return prt 
                
file = '/tmp/outf2.csv'
OUTF = open(file,'w')
print ('****    SEE ',file)        
dateinv = '2016-07-05'
print('Customer Invoices since ', dateinv,file=OUTF)
OUT_INV = ReportInvoice().listInvoices(dateinv,'out_invoice')
print (OUT_INV,file=OUTF)
    
print ('Supplier Invoices or Vendor Bills since ',dateinv,file=OUTF)
IN_INV = ReportInvoice().listInvoices(dateinv,'in_invoice')
print(IN_INV,file=OUTF)
OUTF.close()
    

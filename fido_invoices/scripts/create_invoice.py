# Script to create invoices from csv file containing invoice details
#
from __future__ import print_function, division
from datetime import datetime
import csv
import logging

_logger = logging.getLogger(__name__)
SALESFILE = 'sales2.csv'
OUTF = '/tmp/create_invoice.out'
ERRF = '/tmp/create_invoice.err'
outfile = open(OUTF,'w')
errfile = open(ERRF,'w')

invoice_type = 'out_invoice'
total_inv = 0
with open(SALESFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        try:
            partner = row['CUSTOMER NAME'].strip().upper()
            username = row['SALESPERSON'].strip().upper() +'-SALES'

            partner_obj = env['res.partner'].search([('name','=',partner)])
            assert partner_obj,"Partner not in DB"
            partner_id = partner_obj.id
            user_obj = env['res.users'].search([('name','=',username)])
            assert user_obj,'Salesperson not in DB'
            user_id = user_obj.id

            invoice_name = 'INVOICE/' + str(partner_id) + '/' + datetime.now().strftime('%Y-%m-%d-%H-%M')
            account_invoice_obj = env['account.invoice']
            # Use Sales Journal
            journal_id = env['account.journal'].search([('type', '=', 'sale')])[0].id
            assert journal_id,'not valid journal_id'
            account_id = 7
            teamid = 1
            payment_term_id = 1
            teller_id = ''
            date_invoice = datetime.now().strftime('%Y-%m-%d')

            # Product info
            prodname = row['PRODUCT'].strip().upper()
            prod_obj = env['product.product'].search([('name', '=', prodname)])
            assert prod_obj,'not valid prod_obj'
            product_id = prod_obj.id

            prodacct_obj = prod_obj.property_account_income_id
            prod_account_id = prodacct_obj.id
            assert prod_account_id,'not valid prod_account_id'
            price_unit = prod_obj.list_price
            qty = row['QTY']
            assert price_unit,'not valid price_unit'

            lines = [
                (0, 0,
                 {
                     'product_id': product_id,
                     'quantity': qty,
                     'account_id': prod_account_id,
                     'name': prodname,
                     'price_unit': price_unit,
                     'uom_id': 1
                 }
                 )
            ]
            print('Creating Invoice for Partner ',partner, 'product ',prodname,' ....')
            account_invoice_customer0 = account_invoice_obj.sudo().create(dict(
            name=invoice_name,
            reference_type="none",
            payment_term_id=payment_term_id,
            journal_id=journal_id,
            partner_id=partner_id,
            date_invoice=date_invoice,
            account_id=account_id,
            user_id=user_id,
            team_id=teamid,
            type=invoice_type,
            invoice_line_ids=lines
            ))
            assert account_invoice_customer0,'Invoice Creation Failed'
            # I manually assign tax on invoice
            invoice_tax_line = {
                'name': 'Test Tax for Customer Invoice',
                'manual': 1,
                'amount': 0,
                'account_id': 1,
                'invoice_id': account_invoice_customer0.id,
            }
            tax = env['account.invoice.tax'].create(invoice_tax_line)
            assert tax, "Tax has not been assigned correctly"



            total_inv = total_inv + (float(qty)*float(price_unit))
            self._cr.commit()

            print('Invoice for ', partner, ' created successfully!!!', file=outfile)
            # Validate Invoice
            #account_invoice_customer0.action_invoice_open()
            # Check that invoice is open
            #assert account_invoice_customer0.state == 'open','Invoice not properly validated'
        except Exception, e:
            print('Invoice Creation Error.', partner,username,str(e))
            print ('Invoice Creation Error.',str(e),file=errfile)
            raise
print('Total Invoiced',total_inv)
print('Total Invoiced',total_inv, file=outfile)
errfile.close()
outfile.close()

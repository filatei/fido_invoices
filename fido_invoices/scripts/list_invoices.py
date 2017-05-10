from __future__ import print_function, division
from datetime import datetime
import csv
import logging
""" List all customer invoices 
"""
OUTF = '/tmp/list_invoices_o.out'
ERRF = '/tmp/list_invoices_o.err'
outfile = open(OUTF,'w')
errfile = open(ERRF,'w')
inv_type = 'out_invoice'
account_invoice_obj = env['account.invoice'].search([('type','=',inv_type)])
prt = 'Date,Customer,Salesperson,product,qty,unitprice\n'
prtl = ""
prod_totals = {}
for invoice in account_invoice_obj:
    try:
        lenlines = len(invoice.invoice_line_ids)
        lines = []
        line={}
        inv = {}
        for k in range(0, lenlines):
            product = invoice.invoice_line_ids[k].name

            assert product,'No product line'
            line = {'product': product, 'rate': invoice.invoice_line_ids[k].price_unit, \
                    'qty': invoice.invoice_line_ids[k].quantity, 'uom': invoice.invoice_line_ids[k].uom_id}
            if k == 0:

                inv = {'custname':invoice.partner_id.name,'term':invoice.payment_term_id.name,'invdate':invoice.date_invoice,\
                    'salesperson':invoice.user_id.name,'lines':[line]}

                # prod_totals[product] = prod_totals[product] + \
                #        invoice.invoice_line_ids[k].quantity*invoice.invoice_line_ids[k].price_unit
            else:

                inv['lines'].append(line)

                #prod_totals[product] = prod_totals[product] + \
                #                            invoice.invoice_line_ids[k].quantity * invoice.invoice_line_ids[k].price_unit

        print(inv)
        print(inv,file=outfile)
    except Exception, e:
        print(str(e))
        raise


print('Product Totals..........')

# for prod in prod_totals:
#    print(prod,',',prod_totals[prod])

errfile.close()
outfile.close()


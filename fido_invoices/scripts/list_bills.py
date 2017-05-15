from __future__ import print_function, division
from datetime import datetime
import csv
import logging
import numpy as np
""" List all customer invoices 
"""
OUTF = '/tmp/list_bills.out'
ERRF = '/tmp/list_bills.err'
outfile = open(OUTF,'w')
errfile = open(ERRF,'w')
inv_type = 'in_invoice'
account_invoice_obj = env['account.invoice'].search([('type','=',inv_type)])
prt = 'Date,Customer,Salesperson,product,qty,unitprice\n'
prtl = ""
prod_totals = {}
p = np.array([])
for invoice in account_invoice_obj:
    try:
        lenlines = len(invoice.invoice_line_ids)
        lines = []
        line={}
        inv = {}

        for k in range(0, lenlines):
            product = invoice.invoice_line_ids[k].name
            assert product, 'No product line'
            # Store product_line data for product totals computation
            prod_qty = invoice.invoice_line_ids[k].quantity
            rate = invoice.invoice_line_ids[k].price_unit
            amount = prod_qty * rate
            p=np.append(p,[product,prod_qty,rate,amount])

            line = {'product': product, 'rate': rate, \
                    'qty': prod_qty, 'uom': invoice.invoice_line_ids[k].uom_id}
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
print(p)
# for prod in prod_totals:
#    print(prod,',',prod_totals[prod])

errfile.close()
outfile.close()


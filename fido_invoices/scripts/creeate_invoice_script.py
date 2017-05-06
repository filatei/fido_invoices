# Script to create invoices from csv file containing invoice details
#
from datetime import datetime
import csv

class CreateInvoice():
    name = "CreateInvoice"
    description = "Create Fido Invoice in Odoo"

    """ global variables defined here
    """
    # customer

    # sales person




    def icreate(self,lines,partner_id,userid):
        """ Create invoice in odoo
               """
        account_invoice_obj = env['account.invoice']

        # Use Sales Journal
        journal_id = env['account.journal'].search([('type', '=', 'sale')])[0].id
        account_id = 1
        invoice_type = 'out_invoice'
        teamid = 1
        payment_term_id = 1
        date_invoice = datetime.now().strftime('%Y-%m-%d')
        teller_id = ''
        comment = ''

        account_invoice_customer0 = account_invoice_obj.sudo().create(dict(
            name="",
            reference_type="none",
            payment_term_id=payment_term_id,
            journal_id=journal_id,
            partner_id=partner_id,
            account_id=account_id,
            user_id=userid,
            team_id=teamid,
            comment=comment,
            type=invoice_type,
            invoice_line_ids=lines
        ))

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
        return account_invoice_customer0

    def ipartner(self,partner_name):
        # create a partner given name
        partner_obj = env['res.partner'].search([])
        return partner_obj.sudo().create({'name':partner_name})

    def iuser(self, user_name):
        # create a salesperson as user given name,
        # login derived from user_name
        username = user_name.split()
        if len(username) == 1:
            login_name = username[0]
        elif len(username) == 2:
            login_name = username[0] + '_' + username[1]
        user_obj = env['res.users'].search([])
        return user_obj.sudo().create({'name': user_name,'login':login_name})

DICTFILE = 'fidodict.csv'

"""
#Create Users (Salespersons) from FIDO DICTIONARY FILE
with open(DICTFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        username = row['SalesPerson Name'].strip().upper()

        try:
            if not env['res.users'].search([('name','=',username)]).name:
                print ("About to create user: ",username)
                u = CreateInvoice().iuser(username)
                print ('UserCreated: ', u)
            else:
                print ('User (May Exist) Not Created: ', username,' : ', env['res.users'].search([('name','=',username)]) )
        except:
            print ("Error Creating User",username)
self._cr.commit()
"""

"""
# create Partners

with open(DICTFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        partner = row['Customer Name'].strip().upper()
        username = row['SalesPerson Name'].strip().upper()

        try:
            if not env['res.partner'].search([('name','=',partner)]).name:
                print ("About to create Partner: ",partner)
                p = CreateInvoice().ipartner(partner)
                print ('Partner Created: ', p)
            else:
                print ('Partner (May Exist) Not Created: ', partner,' : ', env['res.partner'].search([('name','=',partner)]) )
        except:
            print ("Error Creating Partner")
self._cr.commit()
"""
# Add user_id to all Partners
"""
with open(DICTFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        username = row['SalesPerson Name'].strip().upper()
        partner = row['Customer Name'].strip().upper()
        user_id=env['res.users'].search([('name', '=', username)]).id
        partner_id = env['res.partner'].search([('name','=',partner)])
        try:
            if partner_id.id:
                partner_id.sudo().write({'user_id':user_id})
            else:
                print ('Partner not in Dictionary: ', partner_id.name)
        except:
            print ('Problem updating partner salesperson: ',partner_id.name, ' salesp: ',user_name)
self._cr.commit()
"""



# Create Invoices
SALESFILE='sales.csv'
product_purewater = env['product.template'].search([('name', '=', 'PUREWATER')])
with open(SALESFILE, 'rb') as csvfile:

    line = csv.DictReader(csvfile)
    for row in line:
        partner = row['CUSTOMER NAME'].strip().upper()

        try:


            partnerid = env['res.partner'].search([('name', '=', partner)]).id
            userid = env['res.partner'].search([('name', '=', partner)]).user_id.id
            print ('partner: ',partnerid)
            # self.user_id = self.partner_id.user_id
           # print('partner_id: ',partnerid.name,'product: ',self.product_purewater.id,\
           #       'account_id ',self.product_purewater.property_account_income_id,'prodname',\
            #      self.product_purewater.name)
            invoice_line_data = [
                (0, 0,
                 {
                     'product_id': 1,
                     'quantity': row['QTY'],
                     'account_id': 1,
                     'name': 'PUREWATER',
                     'price_unit': 70
                 }
                 )
            ]
            CreateInvoice().icreate(invoice_line_data,partnerid,userid)
        except:
            print ("opps. Error")
        self._cr.commit()
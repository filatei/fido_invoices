# Script to create invoices from csv file containing invoice details
#
from datetime import datetime
import csv
import logging

_logger = logging.getLogger(__name__)


class CreateInvoice():
    name = "CreateInvoice"
    description = "Create Fido Invoice in Odoo"

    """ global variables defined here
    """

    date_invoice = ''

    # customer
    partner_id = 0
    name = ""
    # sales person
    user_id = 0
    # Line Data
    product = ""
    prod_account_id = 1
    uom_id = 1
    qty = 0
    price_unit = 0

    journal_id = 1
    account_id = 7

    teller_id = 1
    teamid = 1
    payment_term_id = 1
    invoice_type = ''
    comment = ''




    def icreate(self,lines):
        """ Create invoice in odoo
               """
        account_invoice_obj = env['account.invoice']

        # Use Sales Journal
        journal_id = env['account.journal'].search([('type', '=', 'sale')])[0].id
        account_id = 7
        invoice_type = 'out_invoice'
        teamid = 1
        payment_term_id = 1

        teller_id = ''


        account_invoice_customer0 = account_invoice_obj.sudo().create(dict(
            name=self.name,
            reference_type="none",
            payment_term_id=payment_term_id,
            journal_id=journal_id,
            partner_id=self.partner_id,
            date_invoice=self.date_invoice,
            account_id=account_id,
            user_id=self.user_id,
            team_id=teamid,
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
        partner_obj = env['res.partner']

        return partner_obj.sudo().create({'name':partner_name})

    def iuser(self, user_name):
        # create a salesperson as user given name,
        # login derived from user_name
        username = user_name.split()
        login_name =""
        if len(username) == 1:
            login_name = username[0]
        elif len(username) == 2:
            login_name = username[0] + '_' + username[1]

        return env['res.users'].sudo().create({'name': user_name,'login':login_name,\
                        'customer':False,'supplier':False,'notify_email':'none'})

DICTFILE = 'fidodict.csv'


#Create Users (Salespersons) from FIDO DICTIONARY FILE
with open(DICTFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        username = row['SalesPerson Name'].strip().upper()+'-SALES'

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

# Add user_id to all Partners

with open(DICTFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        username = row['SalesPerson Name'].strip().upper()+'-SALES'
        partner = row['Customer Name'].strip().upper()
        user_id = env['res.users'].search([('name', '=', username)]).id
        partner_id = env['res.partner'].search([('name','=',partner)])

        try:
            plen = len(partner_id)
            if plen >1:
                print ("partner obj len: ",plen)
                for k in 1..plen:
                    partner_id[k].unlink()
                self._cr.commt()
                partner_id = env['res.partner'].search([('name', '=', partner)])

            if partner_id.id:
            # test if user_id exists
                if user_id:
                    partner_id.sudo().write({'user_id':user_id})
                else:
                    print ('User Attach to Partner: User not in DB: ', user_id)
            else:
                print ('Partner not in DB: ', partner_id.name)
        except:
            print ('Problem updating partner salesperson: ',partner_id.name, ' salesp: ',username)
self._cr.commit()



"""
# Create Invoices
SALESFILE='sales2.csv'
# Set Invoice values not related to customer

self.comment = "Fido Sales Invoice for " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
self.date_invoice = datetime.now().strftime('%Y-%m-%d')
with open(SALESFILE, 'rb') as csvfile:

    line = csv.DictReader(csvfile)
    for row in line:

        try:
            partner = row['CUSTOMER NAME'].strip().upper()
            prodname = row['PRODUCT'].strip().upper()

            self.product = env['product.product'].search([('name', '=', prodname)]).id

            prodacct_obj = env['product.product'].search([('name', '=', prodname)]).property_account_income_id
            self.prod_account_id = prodacct_obj.id

            self.price_unit = env['product.product'].search([('name', '=', prodname)]).list_price

            # Create New Partners/Customers if not exist in DB
            partner_obj = env['res.partner'].search([('name', '=', partner)])
            if not partner_obj:
                cp = CreateInvoice().ipartner(partner)
                print "Created Partner is ",cp


            self.partner_id = env['res.partner'].search([('name', '=', partner)]).id
            self.name = 'INVOICE/' + str(self.partner_id) + '/' + datetime.now().strftime('%Y-%m-%d-%H-%M')
            # Every partner must have salesperson (user_id). If not set it
            # Meaning ever sales record must include salesperson for all customers
            user_obj = env['res.partner'].search([('name', '=', partner)]).user_id
            if not user_obj:
                u_obj =  env['res.users'].search([('name', '=', row['SALESPERSON'])])
                csp = self.partner_id.sudo().write({'user_id':u_obj.id})
                print "Salesperson: ",csp, " added to partner ",self.partner_id
                user_obj = env['res.partner'].search([('name', '=', partner)]).user_id
            print "User obj: ", user_obj
            self.user_id = user_obj.id



            invoice_line_data = [
                (0, 0,
                 {
                     'product_id': self.product,
                     'quantity': row['QTY'],
                     'account_id': self.prod_account_id,
                     'name': prodname,
                     'price_unit': self.price_unit,
                     'uom_id': 1
                 }
                 )
            ]
            print ('Creating Invoice for ',partner,' with Line Data: ',invoice_line_data)
            inv = CreateInvoice().icreate(invoice_line_data)
            print ('Invoice: ',inv, ' Created!')
        except Exception, e:
            _logger.info('Exception Error: ',str(e))

        self._cr.commit()
"""
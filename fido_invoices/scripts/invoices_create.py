import xmlrpclib
from datetime import datetime
import csv,os
import logging
from xlrd import open_workbook
from random import randint


_logger = logging.getLogger(__name__)

"""
Create invoices from FIDO Daily Excel file
"""
# Command line ArgumentHandling
try:
    import argparse

    parser = argparse.ArgumentParser(description='Script for creating invoices from xls file')
    parser.add_argument('-w', '--salesfile', help='e.g -w salesfile.csv', required=True)
    args = vars(parser.parse_args())
except ImportError:
    parser = None

if not os.path.exists('./data'):
    os.makedirs('./data')

if not os.path.exists('./OUT'):
    os.makedirs('./OUT')

WBFILE = args['salesfile']
total_inv = 0
sn = esn = 0


class Daily(object):
    def __init__(self):
        self.name = ""
        self.total_inv = 0.0
        self.invoice_type = ""
        self.teller_tot = 0.0
        self.sn = self.esn = 0
        self.bank = ""
        self.teller_date = ""
        self.teller_amount = 0.0

    def csvextract(self):
        wb = open_workbook(WBFILE)

        print ('SHEETS IN SALES FILE')

        for i in range(0, wb.nsheets - 1):
            sheet = wb.sheet_by_index(i)
            # print (sheet.name)

            path = DATAFOLDER + '/%s.csv'
            with open(path % (sheet.name.replace(" ", "") + '-' + TODAY), "w") as file:
                writer = csv.writer(file, delimiter=",", quotechar='"', \
                                    quoting=csv.QUOTE_ALL, skipinitialspace=True)

                header = [cell.value for cell in sheet.row(0)]
                writer.writerow(header)

                for row_idx in range(1, sheet.nrows):
                    row = [int(cell.value) if isinstance(cell.value, float) else cell.value
                           for cell in sheet.row(row_idx)]
                    writer.writerow(row)

    def get_user(self,salesp):
        try:
            p_name = models.execute_kw(db, uid, password, 'res.users', 'search_read', [[['name', '=', salesp]]], \
                                       {'fields': ['id']})
            # Create Name on Teller as Customer if not in DB
            if not p_name:
                # p_n = models.execute_kw(db, uid, password, 'res.user', 'create', [{'name': salesp,'customer': False, 'supplier': False}])
                # assert p_n, 'SALESPERSON Creation Fails'
                raise Exception('SALESPERSON NOT EXISTING...CREATE ')
            else:
                p_n = p_name[0]['id']
            return p_n
        except Exception, e:
            print str(e)

    # Create Partner
    def create_partner(self,pname, userid):
        try:
            p_name = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[['name', '=', pname]]], \
                                       {'fields': ['id']})
            # Create Name on Teller as Customer if not in DB
            if not p_name:
                p_n = models.execute_kw(db, uid, password, 'res.partner', 'create',
                                        [{'name': pname, 'customer': True, 'supplier': False, 'user_id': userid}])
                assert p_n, 'Customer Creation Fails'
            else:
                p_n = p_name[0]['id']
            return p_n
        except Exception, e:
            print str(e)

    # Create a new Teller Record
    def create_teller(self,tellern, teller_no, userid):
        try:
            teller_name = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
                                            [[['name', '=', tellern]]], \
                                            {'fields': ['id']})
            # Create Name on Teller as Customer if not in DB
            if not teller_name:
                teller_n = models.execute_kw(db, uid, password, 'res.partner', 'create', [
                    {'name': tellern, 'customer': True, 'supplier': False, 'user_id': userid}])
                assert teller_n, 'Teller Name Creation Fails'
            else:
                teller_n = teller_name[0]['id']

            # Create Bank if not in DB

            teller_bank = models.execute_kw(db, uid, password, 'res.bank', 'search_read', [[['name', '=', self.bank]]], \
                                            {'fields': ['id']})

            if not teller_bank:
                # Create the Bank
                teller_bank = models.execute_kw(db, uid, password, 'res.bank', 'create', [{'name': self.bank}])
                assert teller_bank, 'Bank Creation Fails'
            else:
                teller_bank = teller_bank[0]['id']

            teller_rec = {'name': teller_no,
                          'teller_name': teller_n,
                          'bank': teller_bank,
                          'date': self.teller_date,
                          'teller_amount': self.teller_amount
                          }
            # Create Teller Record. Test if Teller Record exists because duplicate not allowed in fido.teller
            teller_obj = models.execute_kw(db, uid, password, 'fido.teller', 'search_read',
                                           [[['name', '=', teller_no]]], \
                                           {'fields': ['id']})
            if teller_obj:
                print 'Teller OBJ ID: ' + str(teller_obj[0]['id'])
                return teller_obj[0]['id']
            else:
                print 'Creating TELLER Record: ' + str(teller_rec)
                teller = models.execute_kw(db, uid, password, 'fido.teller', 'create', [teller_rec])
                assert teller, 'Teller not created'
            return teller
        except Exception, e:
            print str(e)

    def find_between(self,s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    def expense_imp(self):
        self.esn = self.sn = 0
        account_bill = None
        with open(EXPENSEFILE, 'rb') as csvfile:
            line = csv.DictReader(csvfile, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, \
                                  skipinitialspace=True)
            for row in line:
                try:
                    invoice_type = 'in_invoice'
                    title = row['TITLE'].strip().upper()
                    if not title:
                        continue
                    rate = row['RATE'].strip()
                    if not rate:
                        continue
                    qty = row['QTY'].strip()
                    amt = row['AMT'].strip()
                    tdate = self.find_between(WBFILE, ' ', ".xls")
                    tdate = str(tdate).replace('.', '/')
                    if ('/' not in str(tdate)) and ('.' not in str(tdate)):
                        ddt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(tdate) - 2)
                        e_date = ddt.strftime('%Y-%m-%d')
                    else:
                        e_date = (datetime.strptime(tdate, '%d/%m/%Y')).strftime('%Y-%m-%d')
                    print ('tdate: ' + str(tdate) + ' = ' + str(e_date))

                    assert e_date, 'Teller Date not good'
                    price_unit = rate

                    partner_obj = models.execute_kw(db, uid, password, 'res.partner', 'search_read', \
                                                    [[['name', '=', 'DAILY EXPENSES']]],
                                                    {'fields': ['id', 'name', 'user_id']})
                    vendor_id = partner_obj[0]['id']
                    print ('vendor id'+str(partner_obj[0]['id']))
                    assert vendor_id,'no vendor_id'

                    invoice_name = 'BILL/' + str(vendor_id) + '/' + e_date + '/' + str(randint(0, 99999))

                    account_invoice_obj = models.execute_kw(db, uid, password, 'account.invoice', 'search_read', \
                                                            [[['type', '=', invoice_type]]], {'fields': ['id', 'name']})
                    # assert account_invoice_obj,'no account_invoice_obj'
                    journal_id = 2
                    account_id = 13

                    # Product info
                    prodname = title.upper()
                    prod_obj = models.execute_kw(db, uid, password, 'product.product', 'search_read', \
                                                 [[['name', '=', prodname]]],
                                                 {'fields': ['id', 'property_account_income_id']})
                    if prod_obj:

                        product_id = prod_obj[0]['id']
                    else:
                        product_id = models.execute_kw(db, uid, password, 'product.product', 'create', \
                                                       [{'name': prodname}])
                    assert product_id, 'not valid product_id'
                    print ('prod id: '+str(product_id))

                    prod_account_id = 5

                    # assert price_unit,'not valid price_unit'

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
                    if not account_bill:
                        account_bill = models.execute_kw(db, uid, password, 'account.invoice', 'create', \
                                                                  [{'name': invoice_name,

                                                                    'journal_id': journal_id,
                                                                    'partner_id': vendor_id,
                                                                    'date_invoice': e_date,
                                                                    'date_due': e_date,
                                                                    'account_id': account_id,
                                                                    'type': invoice_type,
                                                                    'invoice_line_ids': lines}])
                        assert account_bill, 'Bill Creation Failed'
                        print ('bill Created')
                    else:
                        account_upd = models.execute_kw(db, uid, password, 'account.invoice', 'write', \
                                          [[account_bill], {'invoice_line_ids': lines}])
                        assert account_upd,'bill not updated'

                    # val_id = models.exec_workflow(db, uid, password, \
                    #                                  'account.invoice', 'invoice_open', account_invoice_customer0)
                    # assert val_id,'Invoice not validated'

                    self.total_inv = self.total_inv + (float(qty) * float(price_unit))
                    self.sn = self.sn + 1

                except Exception, e:
                    print 'Invoice Creation Error.' + ',' + title + ',' + str(e)
                    self.esn = self.esn + 1
                    raise

    def invoice_imp(self):
        self.sn = self.esn = 0
        self.total_inv = 0.0
        with open(SALESFILE, 'rb') as csvfile:
            invoice_type = 'out_invoice'
            line = csv.DictReader(csvfile, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, \
                                  skipinitialspace=True)
            for row in line:
                try:
                    tellername = row['TELLER NAME'].strip().upper()
                    teller_no = row['TELLER NO'].strip().upper()
                    partner = row['CUSTOMER NAME'].strip().upper()
                    salesperson = row['SALESPERSON'].strip().upper()
                    qty = row['QTY'].strip()

                    assert qty,'no qty for invoice'
                    price_unit = row['RATE'].strip()
                    if not teller_no:
                        if not row['QTY'] and not row['RATE']:
                            continue
                        else:
                            qty = row['QTY'].strip()
                            price_unit = row['RATE'].strip()
                            prodname = row['PRODUCT'].strip().upper()
                            prod_obj = models.execute_kw(db, uid, password, 'product.product', 'search_read', \
                                                         [[['name', '=', prodname]]],
                                                         {'fields': ['id', 'property_account_income_id']})
                            assert prod_obj, 'no prod_obj'

                            product_id = prod_obj[0]['id']
                            assert product_id, 'not valid product_id'
                            prodacct_obj = prod_obj[0]['property_account_income_id']
                            prod_account_id = prodacct_obj[0]
                            assert prod_account_id, 'not valid prod_account_id'

                            # assert price_unit,'not valid price_unit'

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
                            inv_id = models.execute_kw(db, uid, password, 'account.invoice', 'write',
                                                       [[account_invoice_customer0], { \
                                                           'invoice_line_ids': lines}])
                            assert inv_id, 'inv_id not updated'
                            continue

                    tdate = row['TELLER DATE']

                    if ('/' not in str(tdate)) and ('.' not in str(tdate)):
                        ddt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(tdate) - 2)
                        teller_date = ddt.strftime('%Y-%m-%d')
                    elif ('.' in str(tdate)):
                        teller_date = (datetime.strptime(tdate, '%d.%m.%Y')).strftime('%Y-%m-%d')
                    else:
                        teller_date = (datetime.strptime(tdate, '%d/%m/%Y')).strftime('%Y-%m-%d')
                    print ('tdate: ' + str(tdate) + ' = ' + str(teller_date))

                    assert teller_date, 'Teller Date not good'
                    self.teller_date = teller_date

                    price_unit = rate = row['RATE']
                    qty = row['QTY']

                    location = row['LOCATION'].strip()
                    invdate = row['INVOICE DATE']

                    # fix date formatting

                    if ('/' not in str(invdate)) and ('.' not in str(invdate)):
                        dt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(invdate) - 2)

                    else:
                        dt = datetime.strptime(invdate, '%d/%m/%Y')

                    DATEINVOICE = dt.strftime('%Y-%m-%d')
                    print ('invdate: ' + str(invdate) + ' = ' + str(DATEINVOICE))
                    print ('tellerdate: ' + str(teller_date) )
                    # Detect Invalid transaction
                    if not row['TELLER NO'] or qty <= 0 or price_unit == 0:
                        print row['TELLER NO'] + ' Invalid Data QTY: ' + qty + 'Rate: ' + price_unit
                        # raise Exception('Invalid Transaction - no teller_no or -ve qty or 0 Rate')
                        continue

                    partner_obj = models.execute_kw(db, uid, password, 'res.partner', 'search_read', \
                                                    [[['name', '=', partner], ['customer', '=', True]]],
                                                    {'fields': ['id', 'name', 'user_id']})
                    if not partner_obj:
                        salesp = salesperson + '-SALES'
                        user_id = self.get_user(salesp)
                        assert user_id, 'User/SALESP Validation failed'
                        partner_id = self.create_partner(partner, user_id)
                    else:
                        partner_id = partner_obj[0]['id']
                        user_id = partner_obj[0]['user_id'][0]
                        assert user_id, 'Not valid user_id or not set'
                    assert partner_id, "Partner id bad"

                    invoice_name = 'INVOICE/' + str(partner_id) + '/' + DATEINVOICE + '/' + str(randint(0, 99999))

                    account_invoice_obj = models.execute_kw(db, uid, password, 'account.invoice', 'search_read', \
                                                            [[['type', '=', invoice_type]]], {'fields': ['id', 'name']})
                    # assert account_invoice_obj,'no account_invoice_obj'
                    journal_id = 1
                    account_id = 7
                    teamid = models.execute_kw(db, uid, password, 'crm.team', 'search_read', \
                                               [[['name', '=', location]]], {'fields': ['id']})

                    assert teamid, 'Team ID/LOCATION not in DB'
                    teamid = teamid[0]['id']
                    payment_term_id = 1

                    # Product info
                    prodname = row['PRODUCT'].strip().upper()
                    prod_obj = models.execute_kw(db, uid, password, 'product.product', 'search_read', \
                                                 [[['name', '=', prodname]]],
                                                 {'fields': ['id', 'property_account_income_id']})
                    assert prod_obj, 'no prod_obj'

                    product_id = prod_obj[0]['id']
                    assert product_id, 'not valid product_id'
                    prodacct_obj = prod_obj[0]['property_account_income_id']
                    prod_account_id = prodacct_obj[0]
                    assert prod_account_id, 'not valid prod_account_id'

                    # assert price_unit,'not valid price_unit'

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


                    # DEAL With TELLER RECORD

                    teller_amount = row['TELLER AMOUNT'].strip().replace(',', '')
                    if not teller_amount:
                        teller_amount = 0.0
                    self.teller_tot = self.teller_tot + float(teller_amount)
                    self.teller_amount = teller_amount
                    bank = row['BANK'].strip().upper()
                    self.bank = bank

                    # create teller record in DB
                    teller_id = self.create_teller(tellername, teller_no, user_id)

                    assert teller_id, 'Teller Record creation fails'

                    # print 'Teller ID: ' + str(teller_id)

                    # print 'Creating Invoice for Partner '+ partner+ ' product ' +prodname+' ....'
                    account_invoice_customer0 = models.execute_kw(db, uid, password, 'account.invoice', 'create', \
                                                                  [{'name': invoice_name,
                                                                    'teller_id': teller_id,
                                                                    'reference_type': "none",
                                                                    'payment_term_id': payment_term_id,
                                                                    'journal_id': journal_id,
                                                                    'partner_id': partner_id,
                                                                    'date_invoice': DATEINVOICE,
                                                                    'account_id': account_id,
                                                                    'user_id': user_id,
                                                                    'team_id': teamid,
                                                                    'type': invoice_type,
                                                                    'invoice_line_ids': lines}])
                    assert account_invoice_customer0, 'Invoice Creation Failed'

                    print 'Invoice for Teller ' + str(self.sn+1) + ': Customer: ' + partner + ' Created Successfully!'
                    # val_id = models.exec_workflow(db, uid, password, \
                    #                                  'account.invoice', 'invoice_open', account_invoice_customer0)
                    # assert val_id,'Invoice not validated'

                    outstr = str(self.sn+1) + ',' + row['TELLER NO'] + ',' + row['TELLER NAME'] + ',' + row['BANK'] \
                             + ',' + row['CUSTOMER NAME'] + ',' + row['SALESPERSON'] + ',' + row['TELLER DATE'] + ',' + \
                             str(row['TELLER AMOUNT']) + ',' + str(row['QTY']) + ',' + str(row['RATE']) + ',' + str(
                        row['INVOICE DATE']) + \
                             ',' + row['LOCATION'] + ',' + row['BONUS'] + ',' + row['PRODUCT'] + ',' + 'SUCCESS'
                    outfile.write(outstr)

                    self.total_inv = self.total_inv + (float(qty) * float(price_unit))
                    self.sn = self.sn + 1

                except Exception, e:
                    print 'Invoice Creation Error.' + ',' + str(partner) + ',' + str(salesperson) + ',' + str(e)
                    # errstr = str(esn)+','+row['TELLER NO']+','+row['TELLER NAME']+','+row['BANK']+','+row['CUSTOMER NAME']+','+row['SALESPERSON']+','+row['TELLER DATE']+','+str(row['TELLER AMOUNT'])+','+str(row['QTY'])+','+str(row['RATE'])+','+str(row['INVOICE DATE'])+','+ str(e)
                    # errfile.write(errstr+'\n')
                    self.esn = self.esn + 1
                    raise

try:
    db = 'FPLDB'
    username = 'admin'
    password = 'N0tadm1n'
    port = '8070'
    host = 'localhost'
    url = 'http://%s:%s' % (host, port)
    models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % (url))
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})

    assert uid,'com.login failed'
    version = common.version()
    # assert version['server_version'] == '10.0','Server not 10.0'
except Exception, e:

    raise

# WBFILE = 'sales.xls'
TODAY = datetime.now().strftime('%d-%m-%Y')
DATAFOLDER = 'data'

# Create csv files from sheets in Sales Workbook

# Get  Salesperson/User

# open the INVOICE worksheet and read its data into Odoo
SALESFILE = 'data/INVOICE-' + TODAY + '.csv'
EXPENSEFILE = 'data/EXPENSES-' + TODAY + '.csv'
OUTF = '/tmp/create_invoice_out.csv'
ERRF = '/tmp/create_invoice_err.csv'
outfile = open(OUTF, 'w')
errfile = open(ERRF, 'w')

# This SFILE removes extraneous lines from INVOICE Sheet
SFILE = SALESFILE + '2'
pfile = open(SFILE, 'w')
head = 'SN,TELLER NO,TELLER NAME,BANK,CUSTOMER NAME,SALES PERSON,TELLER DATE,TELLER_AMOUNT,QTY,RATE,INVOICE DATE,REMARK'
outfile.write(head + '\n')
errfile.write(head + '\n')

# Initialise class Obj
d = Daily()

# Extract csv from xls file
d.csvextract()

# Import Invoices

d.invoice_imp()

print 'Total Invoiced: ' + "{:,}".format(d.total_inv)
print 'Teller Total Invoiced: '+ "{:,}".format(d.teller_tot)
if (d.teller_tot - d.total_inv) >0:
    print '******** POSITIVE INVOICING ************'
else:
    print '******** NEGATIVE INVOICING  ***********'
print str(d.sn) + ' Records Successful'
print str(d.esn) + ' Records Failed'
fr = (d.esn)/float(d.sn+d.esn)*100
print 'FAIL RATE: ' +"{:5,.2f}".format(fr)+'%'
print 'SUCCESS FILE: '+OUTF
print 'ERROR FILE: '+ERRF
outfile.write("{:,}".format(d.total_inv)+'\n')
errfile.close()
outfile.close()


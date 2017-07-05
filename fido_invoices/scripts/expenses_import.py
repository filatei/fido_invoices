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



try:
    db = 'FPLDB10'
    username = 'admin'
    password = 'N0tAdmin'
    port = '8071'
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

# import Expenses
d.expense_imp()

# Import Invoices


print 'Total Invoiced: ' + "{:,}".format(d.total_inv)

print str(d.sn) + ' Records Successful'
print str(d.esn) + ' Records Failed'
fr = (d.esn)/float(d.sn+d.esn)*100
print 'FAIL RATE: ' +"{:5,.2f}".format(fr)+'%'
print 'SUCCESS FILE: '+OUTF
print 'ERROR FILE: '+ERRF
outfile.write("{:,}".format(d.total_inv)+'\n')
errfile.close()
outfile.close()


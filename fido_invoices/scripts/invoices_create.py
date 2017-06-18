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




#com = xmlrpclib.ServerProxy('%s/xmlrpc/2/common'%(url))

# partner_obj =sock.execute(dbname,uid,pwd,'res.partner','search',[('name','=',partner)])
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
def csvextract():
    wb = open_workbook(WBFILE)

    print ('SHEETS IN SALES FILE')

    for i in range(0, wb.nsheets-1):
        sheet = wb.sheet_by_index(i)
        # print (sheet.name)

        path =  DATAFOLDER + '/%s.csv'
        with open( path %(sheet.name.replace(" ", "") + '-'+ TODAY), "w") as file:
            writer = csv.writer(file, delimiter=",", quotechar='"', \
                                quoting=csv.QUOTE_ALL, skipinitialspace=True)

            header = [cell.value for cell in sheet.row(0)]
            writer.writerow(header)

            for row_idx in range(1, sheet.nrows):
                row = [int(cell.value) if isinstance(cell.value, float) else cell.value
                       for cell in sheet.row(row_idx)]
                writer.writerow(row)


# Get  Salesperson/User
def get_user(salesp):
    try:
        p_name = models.execute_kw(db, uid, password, 'res.users', 'search_read', [[['name', '=', salesp]]], \
                                    {'fields': ['id']})
        # Create Name on Teller as Customer if not in DB
        if not p_name:
            # p_n = models.execute_kw(db, uid, password, 'res.user', 'create', [{'name': salesp,'customer': False, 'supplier': False}])
            #assert p_n, 'SALESPERSON Creation Fails'
            raise Exception ('SALESPERSON NOT EXISTING...CREATE ')
        else:
            p_n = p_name[0]['id']
        return p_n
    except Exception, e:
        print str(e)
        raise



#Create Partner
def create_partner(pname,userid):
    try:
        p_name = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[['name', '=', pname]]], \
                                    {'fields': ['id']})
        # Create Name on Teller as Customer if not in DB
        if not p_name:
            p_n = models.execute_kw(db, uid, password, 'res.partner', 'create', [{'name': pname,'customer': True, 'supplier': False,'user_id':userid}])
            assert p_n, 'Customer Creation Fails'
        else:
            p_n = p_name[0]['id']
        return p_n
    except Exception, e:
        print str(e)



# Create a new Teller Record
def create_teller(tellern,teller_no,userid):
    try:
        teller_name = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[['name', '=', tellername]]], \
                                    {'fields': ['id']})
        # Create Name on Teller as Customer if not in DB
        if not teller_name:
            teller_n = models.execute_kw(db, uid, password, 'res.partner', 'create', [{'name': tellern,'customer': True, 'supplier': False,'user_id':userid}])
            assert teller_n, 'Teller Name Creation Fails'
        else:
            teller_n = teller_name[0]['id']

        # Create Bank if not in DB

        teller_bank = models.execute_kw(db, uid, password, 'res.bank', 'search_read', [[['name', '=', bank]]], \
                                    {'fields': ['id']})


        if not teller_bank:
            # Create the Bank
            teller_bank = models.execute_kw(db, uid, password, 'res.bank', 'create', [{'name': bank}])
            assert teller_bank, 'Bank Creation Fails'
        else:
            teller_bank = teller_bank[0]['id']

        teller_rec = {'name': teller_no,
                      'teller_name': teller_n,
                      'bank': teller_bank,
                      'date': teller_date,
                      'teller_amount': teller_amount
                      }
        # Create Teller Record. Test if Teller Record exists because duplicate not allowed in fido.teller
        teller_obj = models.execute_kw(db, uid, password, 'fido.teller', 'search_read', [[['name', '=', teller_no]]], \
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


# open the INVOICE worksheet and read its data into Odoo
SALESFILE = 'data/INVOICE-'+ TODAY +'.csv'
OUTF = '/tmp/create_invoice_out.csv'
ERRF = '/tmp/create_invoice_err.csv'
outfile = open(OUTF,'w')
errfile = open(ERRF,'w')

# This SFILE removes extraneous lines from INVOICE Sheet
SFILE = SALESFILE + '2'
pfile = open(SFILE,'w')
head = 'SN,TELLER NO,TELLER NAME,BANK,CUSTOMER NAME,SALES PERSON,TELLER DATE,TELLER_AMOUNT,QTY,RATE,INVOICE DATE,REMARK'
outfile.write(head+'\n')
errfile.write(head+'\n')


invoice_type = 'out_invoice'
total_inv = 0
sn = esn = 0

# Extract csv from xls file
csvextract()
"""
# Reformat Invoice file for use
with open(SALESFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    head = 'SN,TELLER NO,TELLER NAME,BANK,CUSTOMER NAME,SALESPERSON,TELLER DATE,TELLER AMOUNT,QTY,RATE,INVOICE DATE,LOCATION,BONUS,PRODUCT,REMARK'
    pfile.write(head+'\n')
    for row in line:

        if row['QTY'] or row['RATE']:
            outstr = row['SN'] + ',' + row['TELLER NO'] + ',' + row['TELLER NAME'] + ',' + row['BANK'] \
                     + ',' + row['CUSTOMER NAME'] + ',' + row['SALESPERSON'] + ',' + row['TELLER DATE'] + ',' + \
                     str(row['TELLER AMOUNT'].replace(',','')) + ',' + str(row['QTY']) + ',' + str(row['RATE']) + ',' + str(row['INVOICE DATE']) + \
                     ',' + row['LOCATION']+',' + row['BONUS']+',' + row['PRODUCT']
            pfile.write(outstr+'\n')
pfile.close()
"""
dt =''
# use extracted REFORMATTED SFILE file
# need to use INVOICE FILE to extract teller data
teller_tot = 0.0
with open(SALESFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile, quotechar='"', delimiter=',',quoting=csv.QUOTE_ALL,\
                          skipinitialspace=True)
    for row in line:
        try:
            partner = row['CUSTOMER NAME'].strip().upper()
            if not partner:
                continue
            tellername = row['TELLER NAME'].strip().upper()
            if not tellername:
                continue
            teller_no = row['TELLER NO'].strip().upper()
            tdate = (row['TELLER DATE'].strip()).replace('.', '/')
            teller_date = (datetime.strptime(tdate, '%d/%m/%Y')).strftime('%Y-%m-%d')
            if not teller_date:
                continue
            salesperson = row['SALESPERSON'].strip().upper()
            price_unit = rate = row['RATE']
            qty = row['QTY']

            location = row['LOCATION'].strip()
            invdate = (row['INVOICE DATE'].strip()).replace('.','/')

            # fix date formatting
            if isinstance(invdate,int):
                dt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + invdate - 2)

            elif '/' in invdate:
                dt =  datetime.strptime(invdate,'%d/%m/%Y')
            elif '.' in invdate:
                dt = datetime.strptime(invdate, '%d.%m.%Y')

            DATEINVOICE = dt.strftime('%Y-%m-%d')
            # Detect Invalid transaction
            if not row['TELLER NO'] or qty <= 0 or price_unit == 0:
                print row['TELLER NO'] + ' Invalid Data QTY: ' + qty + 'Rate: ' + price_unit
               # raise Exception('Invalid Transaction - no teller_no or -ve qty or 0 Rate')
                continue

            partner_obj = models.execute_kw(db, uid, password,'res.partner', 'search_read', \
                                [[['name', '=', partner],['customer', '=', True]]], {'fields': ['id','name', 'user_id']})
            if not partner_obj:
                salesp = salesperson+'-SALES'
                user_id = get_user(salesp)
                assert user_id,'User/SALESP Validation failed'
                partner_id = create_partner(partner,user_id)
            else:
                partner_id = partner_obj[0]['id']
                user_id = partner_obj[0]['user_id'][0]
                assert user_id, 'Not valid user_id or not set'
            assert partner_id,"Partner id bad"


            invoice_name = 'INVOICE/' + str(partner_id) + '/' + DATEINVOICE+'/'+ str(randint(0,99999))

            account_invoice_obj = models.execute_kw(db, uid, password,'account.invoice', 'search_read', \
                                    [[['type', '=', invoice_type]]], {'fields': ['id','name']})
            # assert account_invoice_obj,'no account_invoice_obj'
            journal_id = 1
            account_id = 7
            teamid = models.execute_kw(db, uid, password,'crm.team', 'search_read', \
                                    [[['name', '=', location]]], {'fields': ['id']})

            assert teamid,'Team ID/LOCATION not in DB'
            teamid = teamid[0]['id']
            payment_term_id = 1

            # Product info
            prodname = row['PRODUCT'].strip().upper()
            prod_obj = models.execute_kw(db, uid, password, 'product.product', 'search_read', \
                                         [[['name', '=', prodname]]], {'fields': ['id','property_account_income_id']})
            assert prod_obj, 'no prod_obj'

            product_id = prod_obj[0]['id']
            assert product_id, 'not valid product_id'
            prodacct_obj = prod_obj[0]['property_account_income_id']
            prod_account_id = prodacct_obj[0]
            assert prod_account_id,'not valid prod_account_id'

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



            teller_amount = row['TELLER AMOUNT'].strip().replace(',','')
            if not teller_amount:
                teller_amount = 0.0
            teller_tot = teller_tot + float(teller_amount)
            bank = row['BANK'].strip().upper()

            # create teller record in DB
            teller_id = create_teller(tellername,teller_no,user_id)

            assert teller_id,'Teller Record creation fails'

            print 'Teller ID: ' + str(teller_id)

            print 'Creating Invoice for Partner '+ partner+ ' product ' +prodname+' ....'
            account_invoice_customer0 = models.execute_kw(db, uid, password, 'account.invoice', 'create',\
            [{'name':invoice_name,
              'teller_id':teller_id,
                'reference_type':"none",
                'payment_term_id':payment_term_id,
                'journal_id':journal_id,
                'partner_id':partner_id,
                'date_invoice':DATEINVOICE,
                'account_id':account_id,
                'user_id':user_id,
                'team_id':teamid,
                'type':invoice_type,
              'invoice_line_ids':lines}])
            assert account_invoice_customer0, 'Invoice Creation Failed'
            print 'Invoice for Teller '+str(teller_id)+': Customer: '+partner+' Created Successfully!'
            outstr = str(sn) + ',' + row['TELLER NO'] + ',' + row['TELLER NAME'] + ',' + row['BANK'] \
                     + ',' + row['CUSTOMER NAME'] + ',' + row['SALESPERSON'] + ',' + row['TELLER DATE'] + ',' + \
                     str(row['TELLER AMOUNT']) + ',' + str(row['QTY']) + ',' + str(row['RATE']) + ',' + str(row['INVOICE DATE']) + \
                     ',' + row['LOCATION'] + ',' + row['BONUS'] + ',' + row['PRODUCT'] + ','  + 'SUCCESS'
            outfile.write(outstr)

            total_inv = total_inv + (float(qty)*float(price_unit))
            sn = sn + 1

        except Exception, e:
            print 'Invoice Creation Error.' +','+ partner +','+row['SALESPERSON']+','+str(e)
            errstr = str(esn)+','+row['TELLER NO']+','+row['TELLER NAME']+','+row['BANK']+','+row['CUSTOMER NAME']+','+row['SALESPERSON']+','+row['TELLER DATE']+','+str(row['TELLER AMOUNT'])+','+str(row['QTY'])+','+str(row['RATE'])+','+str(row['INVOICE DATE'])+','+ str(e)
            errfile.write(errstr+'\n')
            esn = esn+1
            raise

print 'Total Invoiced: '+ "{:,}".format(total_inv)
print 'Teller Total Invoiced: '+ "{:,}".format(teller_tot)
if (teller_tot - total_inv) >0:
    print '******** POSITIVE INVOICING ************'
else:
    print '******** NEGATIVE INVOICING  ***********'
print str(sn) + ' Records Successful'
print str(esn) + ' Records Failed'
fr = (esn)/float(sn+esn)*100
print 'FAIL RATE: ' +"{:5,.2f}".format(fr)+'%'
print 'SUCCESS FILE: '+OUTF
print 'ERROR FILE: '+ERRF
outfile.write("{:,}".format(total_inv)+'\n')
errfile.close()
outfile.close()

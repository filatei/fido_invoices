import xmlrpclib
from datetime import datetime
import csv,os
import logging
from xlrd import open_workbook
from random import randint

_logger = logging.getLogger(__name__)

"""
Create Payroll from csv file
If Employees don't exist, create them using hr_create.py on the error file contain list of such staff
"""
# Command line ArgumentHandling
try:
    import argparse

    parser = argparse.ArgumentParser(description='Script for creating Payroll from csv file')
    parser.add_argument('-w', '--csvfile', help='e.g -w csvfile.csv', required=True)
    args = vars(parser.parse_args())
except ImportError:
    parser = None

if not os.path.exists('./OUT'):
    os.makedirs('./OUT')

WBFILE = args['csvfile']

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

# Functions Definition
def pay_staff(empname,daysabs,adv):
    try:
        emp_obj =  models.execute_kw(db, uid, password, 'hr.employee', 'search_read', \
                                  [[['name', '=', empname]]], {'fields': ['id']})
        assert emp_obj, 'employee not exist'
        pay_obj = models.execute_kw(db, uid, password, 'fido.payroll', 'search_read', \
                        [[['name', '=', empname], ['x_year', '=', year], ['f_mnth', '=', month]]],\
                        {'fields': ['id']})
        if not pay_obj:
            pay_id = models.execute_kw(db, uid, password, 'fido.payroll', 'create', \
                        [{'name': emp_obj[0]['id'],'x_year':year,'daysabsent':daysabs,'saladv':adv}])
            assert pay_id,'Pay Creation Fails'
            print 'Payroll Created for ' + empname
        else:
            pay_id = pay_obj[0]['id']
            print 'Payroll Exists. Not Created'

        # Move Workflow to Compute from Draft
        compute_id = models.exec_workflow(db, uid, password, 'fido.payroll', 'compute', pay_id)
        # assert compute_id,'Validation Failed'

        return pay_id
    except Exception, e:
        print 'Pay_Bagger Error for ' + ',' + employee + ',' + str(e)
        raise



# CONSTANTS
TODAY = datetime.now().strftime('%d-%m-%Y')
year = str(datetime.now().year)
month = datetime.now().strftime('%B')
OUTF = '/tmp/create_pay_out.csv'
ERRF = '/tmp/create_pay_err.csv'
outfile = open(OUTF,'w')
errfile = open(ERRF,'w')
print 'ERRFILE is: '+ ERRF+' and OUTF is: '+OUTF
errfile.write('SN,NAME,SALARY ADV,DAYS ABS')
outfile.write('SN,NAME,SALARY ADV,DAYS ABS')

sn = esn = 0
bags = saladv = days_abs= 0

with open(WBFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        try:
            employee = row['NAME'].strip().upper()
            assert employee,'Staff Name Empty in Source file'

            saladv = row['SALARY ADV'].strip()

            if not saladv:
                saladv = 0.0

            days_abs = row['DAYS ABS'].strip()

            if not days_abs:
                days_abs = 0

            pay_id = pay_staff(employee,days_abs,saladv)
            assert pay_id,'Staff Pay failed'
            sn = sn + 1

        except Exception, e:
            # print 'Pay Creation Error for ' + ',' + employee + ','+str(e)
            errstr = str(esn) + ',' + employee +  ',' + str(saladv) + ','+str(days_abs)+','+ str(e)
            errfile.write(errstr + '\n')
            esn = esn + 1
            raise

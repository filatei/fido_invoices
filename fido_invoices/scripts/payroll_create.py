import xmlrpclib
from datetime import datetime
from datetime import date
import csv,os
import logging
from xlrd import open_workbook
from random import randint

_logger = logging.getLogger(__name__)

"""
Create Payroll from csv file
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

def pay_bagger(empname,bagno,adv):
    try:
        emp_obj =  models.execute_kw(db, uid, password, 'hr.employee', 'search_read', \
                                  [[['name', '=', empname]]], {'fields': ['id']})
        assert emp_obj, 'employee not exist'
        item_tot = 2.5 * float(bagno)
        adv_tot = -1.0 * float(adv)
        line_ids = [(0,0,{
            'item_id':'Bagging Commission',
            'item_qty':bagno,
            'item_mult':2.5,
            'line_total':item_tot

                     }),(0,1,{
            'item_id':'Salary Advance Deduction(-ve)',
            'item_qty':adv,
            'item_mult':-1,
            'line_total':adv_tot

                     })]
        pay_tot = item_tot + adv_tot
        pay_id = models.execute_kw(db, uid, password, 'fido.payroll', 'create', \
                               [{'name': emp_obj[0]['id'],'x_year':'2017','daysabsent':0,'saladv':adv,\
                                'payroll_line_ids':line_ids,'payroll_total':pay_tot

                                 }])
        compute_id = models.exec_workflow(db, uid, password, 'fido.payroll', 'compute', pay_id)
        # assert compute_id,'Validation Failed'
        print 'Payroll Created for '+empname
        return pay_id
    except Exception, e:
        print 'Pay_Bagger Error for ' + ',' + employee + ',' + str(e)
        raise

def pay_others(empname,daysabs,adv):
    try:
        emp_obj =  models.execute_kw(db, uid, password, 'hr.employee', 'search_read', \
                                  [[['name', '=', empname]]], {'fields': ['id']})
        assert emp_obj, 'employee not exist'
        pay_obj =  models.execute_kw(db, uid, password, 'fido.payroll', 'search_read', \
                                  [[['name', '=', empname],['x_year','=',year],['f_mnth','=',month]]], {'fields': ['id']})

	if not pay_obj:

            pay_id = models.execute_kw(db, uid, password, 'fido.payroll', 'create', \
                               [{'name': emp_obj[0]['id'],'x_year':year,'daysabsent':daysabs,'saladv':adv\
                                }])
            print 'Payroll (other) Created for ' + empname
            compute_id = models.exec_workflow(db, uid, password, 'fido.payroll', 'compute', pay_id)
	else:
	    pay_id = pay_obj[0]['id'] 
            print 'Payroll Obj exists'
        return pay_id
    except Exception, e:
        print 'Pay_Other Error for ' + ',' + employee + ',' + str(e)
        raise

def contract_update(empname,kpsales,obsales,dispsales,cratesales):
    """ Update the Employee contract with live sales data"""

    try:
        contr_obj = models.execute_kw(db, uid, password, 'hr.contract', 'search_read', \
                                  [[['employee_id.name', '=', empname]]], {'fields': ['id', \
                                                                                     'name', 'employee_id',
                                                                                     'crate_sold', 'disp_sold',
                                                                                     'obbg_sold', 'kpbg_sold']})
        assert contr_obj,'Contract_obj read error'

        if len(contr_obj) > 1:
            print "Contract Before 1: ",contr_obj[1]
        else:
            print "Contract Before 0: ",contr_obj[0]
        lenc = len(contr_obj)
        contr_id = contr_obj[lenc-1]['id']

        contr_upd = models.execute_kw(db, uid, password, 'hr.contract', 'write',\
                    [[contr_id], {'crate_sold': cratesales,'disp_sold':dispsales,\
                    'obbg_sold':obsales, 'kpbg_sold':kpsales}])
        assert contr_upd,'Contract Update failes'
        print contr_upd
        contr_obj = models.execute_kw(db, uid, password, 'hr.contract', 'search_read', \
                                      [[['employee_id', '=', empname]]], {'fields': ['id', \
                                                                                     'name', 'employee_id',
                                                                                     'crate_sold', 'disp_sold',
                                                                                     'obbg_sold', 'kpbg_sold']})
        assert contr_obj, 'Contract_obj read error'

        print "Contract AFTER: ", contr_obj


    except Exception, e:
        print str(e)
        raise



TODAY = datetime.now().strftime('%d-%m-%Y')
year = str(datetime.now().year)
month = datetime.now().strftime('%B')
OUTF = '/tmp/create_pay_out.csv'
ERRF = '/tmp/create_pay_err.csv'
outfile = open(OUTF,'w')
errfile = open(ERRF,'w')
print 'ERRFILE is: '+ ERRF+' and OUTF is: '+OUTF
errfile.write('SN,NAME,BAGS,SALARY ADV,DAYS ABS')
outfile.write('SN,NAME,BAGS,SALARY ADV,DAYS ABS')

sn = esn = 0
bags = saladv = 0

with open(WBFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        try:
            employee = row['NAME'].strip().upper()
            if not employee:
                continue
            if row.has_key('BAGS'):
            	bags = row['BAGS'].strip()
            
            if row.has_key('SALARY ADV'):
                saladv = row['SALARY ADV'].strip()
            else:
		        saladv = 0.0
            if row.has_key('DAYS ABS'):
                days_abs = row['DAYS ABS'].strip()
            else:
		        days_abs = 0
            if row.has_key('DESIGNATION'):
            	job_title = row['DESIGNATION'].strip().upper()
            else:
                job_title = ""

            # contr_obj
            if row.has_key('KPANSIA SACHET SALES'):
                kpsales = float(row['KPANSIA SACHET SALES'].strip())
                sales = 1
            if row.has_key('OBUNNA SACHET SALES'):
                obsales = row['OBUNNA SACHET SALES'].strip()
                sales = 1

            if row.has_key('CRATES SALES'):
                cratesales = row['CRATES SALES'].strip()
                sales = 1
            if row.has_key('DISPENSER SALES'):
                dispsales = row['DISPENSER SALES'].strip()
                sales = 1

            if sales:
                cupd = contract_update(employee,kpsales,obsales,dispsales,cratesales)
                assert cupd,'contract update not good'
                sales = 0
            # Pay staff

            if sales or job_title:
                pay_id = pay_others(employee,days_abs,saladv)
                assert pay_id,'Other pay Failed'
                sales = 0
            else:
                pay_id = pay_bagger(employee,bags,saladv)
                assert pay_id,'Bagger Pay failed'


            sn = sn + 1

        except Exception, e:
            print 'Pay Creation Error for ' + ',' + employee + ','+str(e)
            errstr = str(esn) + ',' + employee + ',' + str(bags) + ',' + str(saladv) + ','+str(days_abs)+','+ str(e)
            errfile.write(errstr + '\n')
            esn = esn + 1
            raise

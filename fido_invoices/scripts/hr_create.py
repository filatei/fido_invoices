import xmlrpclib
from datetime import datetime
from datetime import date
import csv,os
import logging
from xlrd import open_workbook
from random import randint


_logger = logging.getLogger(__name__)
"""
Create Employees from csv file
"""
# Command line ArgumentHandling
try:
    import argparse

    parser = argparse.ArgumentParser(description='Script for creating employees from csv file')
    parser.add_argument('-w', '--csvfile', help='e.g -w csvfile.csv', required=True)
    args = vars(parser.parse_args())
except ImportError:
    parser = None

if not os.path.exists('./OUT'):
    os.makedirs('./OUT')

WBFILE = args['csvfile']

try:
    db = 'fidodb'
    username = 'admin'
    password = 'admin'
    port = '8069'
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


def create_job(job_title):
    # does it exist?
    jobid_obj = models.execute_kw(db, uid, password, 'hr.job', 'search_read',\
                                  [[['name', '=', job_title]]], {'fields': ['id']})
    if not jobid_obj:
        job_id = models.execute_kw(db, uid, password, 'hr.job', 'create', \
                               [{'name': job_title}])
    else:
        job_id = jobid_obj[0]['id']
    return job_id

def create_bank_account_number(account_no):
    # Does it exist?
    acctid_obj = models.execute_kw(db, uid, password, 'res.partner.bank', 'search_read', \
                                  [[['acc_number', '=', account_no]]], {'fields': ['id']})
    if not acctid_obj:
        acc_id = models.execute_kw(db, uid, password, 'res.partner.bank', 'create', \
                               [{'acc_number': account_no}])
    else:
        acc_id = acctid_obj[0]['id']
    return acc_id

def create_employee(empname,jobid,acctid):
    emp_obj = models.execute_kw(db, uid, password, 'hr.employee', 'search_read', \
                                  [[['name', '=', empname]]], {'fields': ['id']})
    if not emp_obj:
        emp_id = models.execute_kw(db, uid, password, 'hr.employee', 'create', \
                               [{'name': empname, 'bank_account_id': acctid, 'job_id': jobid}])
        print 'Employee  ' + employee + ' Created Successfully!'
    else:
        print 'Employee Exists: '+ employee
        emp_id = emp_obj[0]['id']
    return emp_id

def create_contract(empid,jobid):
    # Create contract in hr.contract if not exist
    hr_contract_obj = models.execute_kw(db, uid, password, 'hr.contract', 'search_read', \
                                        [[['employee_id', '=', empid]]], {'fields': ['id']})
    if not hr_contract_obj:

        contract_ref = employee + '-Contract'
        type_id = models.execute_kw(db, uid, password, 'hr.contract.type', 'search_read', \
                                    [[['name', '=', 'Employee']]], {'fields': ['id']})[0]['id']

        struct_obj = models.execute_kw(db, uid, password, 'hr.payroll.structure', 'search_read', \
                                       [[['name', '=', 'Contract']]], {'fields': ['id']})

        if not struct_obj:
            struct_id = models.execute_kw(db, uid, password, 'hr.payroll.structure', 'create', \
                                          [{'name': 'Contract', 'code': 'Contract'}])
        else:
            struct_id = struct_obj[0]['id']

        assert struct_id, 'Payroll Structure Contract Not valid'
        date_start = date.today().strftime('%Y-%m-%d')
        wage = 0.0
        if 'LOADER' in title:
            wage = 18000.00
        elif 'SUPERVISOR' in title:
            wage = 25000.00

        bagged_mult = 2.5
        kpbg_sold = 0.0
        obbg_sold = 0.0
        bagsold_mult = 1
        obbgsold_mult = 1
        kpbgsold_mult = 1
        cratesold_mult = 5
        crate_sold = 0.0
        disp_sold = 0.0
        dispsold_mult = 25
        sal_adv = loan_adv = payee = days_absent = 0.0

        hr_contract = models.execute_kw(db, uid, password, 'hr.contract', 'create', \
                                        [{'name': contract_ref, 'employee_id': emp_id, 'job_id': job_id,
                                          'type_id': type_id, 'struct_id': struct_id, \
                                          'date_start': date_start, 'wage': wage,
                                          'bagged_mult': bagged_mult, 'kpbg_sold': kpbg_sold, 'obbg_sold': obbg_sold,
                                          'bagsold_mult': bagsold_mult, 'obbgsold_mult': obbgsold_mult,
                                          'kpbgsold_mult': kpbgsold_mult,
                                          'cratesold_mult': cratesold_mult, 'crate_sold': crate_sold,
                                          'disp_sold': disp_sold, 'dispsold_mult': dispsold_mult,
                                          'sal_adv': sal_adv, 'loan_adv': loan_adv, 'payee': payee,
                                          'days_absent': days_absent \
                                          }])
        assert hr_contract, 'hr_contract creation fails'
    else:
        hr_contract = hr_contract_obj[0]['id']
        assert hr_contract, 'Contract not set for bagger'
    return hr_contract

TODAY = datetime.now().strftime('%d-%m-%Y')

OUTF = '/tmp/create_hr_out.csv'
ERRF = '/tmp/create_hr_err.csv'
outfile = open(OUTF,'w')
errfile = open(ERRF,'w')

sn = esn = acctno=0

with open(WBFILE, 'rb') as csvfile:
    line = csv.DictReader(csvfile)
    for row in line:
        try:
            employee = row['NAME'].strip().upper()
            if row.has_key('ACCOUNT NO'):
                acctno = row['ACCOUNT NO'].strip()
            else:
                acctno = row['ACCOUNT NUMBER'].strip()
            title = row['JOB TITLE'].strip()

            job_id = create_job(title)
            assert job_id, 'job title not valid'

            acct_id = create_bank_account_number(acctno)
            assert acct_id,'account id not valid'

            emp_id = create_employee(employee,job_id,acct_id)

            assert emp_id, 'Employee Creation Failed'
            contract_id = create_contract(emp_id,job_id)
            assert contract_id,'Contract Creation failed'

            outstr = str(sn) + ',' + employee + ',' + title + ',' + acctno+',' + 'SUCCESS'
            outfile.write(outstr)

            sn = sn + 1

        except Exception, e:
            print 'Employee Creation Error for ' +','+ employee +str(e)
            errstr = str(esn)+ ',' + employee + ',' + title + ',' + acctno+','+ str(e)
            errfile.write(errstr+'\n')
            esn = esn+1
            raise


print str(sn) + ' Records Successful'
print str(esn) + ' Records Failed'
fr = (esn)/float(sn+esn)*100
print 'FAIL RATE: ' +"{:5,.2f}".format(fr)+'%'
print 'SUCCESS FILE: '+OUTF
print 'ERROR FILE: '+ERRF

errfile.close()
outfile.close()
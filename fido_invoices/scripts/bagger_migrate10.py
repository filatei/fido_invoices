from __future__ import print_function, division
import json,os,ast
import xmlrpclib
from datetime import datetime
from datetime import date
import csv,os

"""
Migrate fido.bagger from Odoo 9 to Odoo 10
from __future__ import print_function
sudo su -  odoo9 -s /bin/bash 
./odoo.py shell -d <dbname>
account_invoice_obj = env['account.invoice']

"""
class Bagger(object):
    def __init__(self):
        self.name = ""
        self.year = ""
        self.month = ""
        self.bagger_line_ids = []
        self.outs = {}
        self.cn = {}
        self.models = ""
        self.common = ""
        self.db=""
        self.uid=""
        self.password= ""
        self.bname= ""
        self.bagger_id = ""

    def migrating(self):
        # read from created file and write to Odoo10

        with open(file1, 'r') as f:
            content = f.readlines()
            #self.outs = ast.literal_eval(s)
            # print ('s is'+s)
            for ln in content:
                iname ='ABIGAIL PAUL'
                self.cn = eval(ln)
                for iname, value in self.cn.iteritems():

                    fname = self.bname=self.cn[iname][0]
                    fmonth = self.cn[iname][2]
                    fyear = self.cn[iname][1]
                    b_id = self.get_bagger()
                    assert b_id, 'Bagger_id not created'
                    fido_bagger = []
                    fido_bag_id =""
                    for ik in range(0,len(self.cn[iname][3])):
                        fdate = self.cn[iname][3][ik][0]
                        fqty = self.cn[iname][3][ik][1]
                        fline = [
                            (0, 0,
                             {
                                 'fido_date': fdate,
                                 'x_quantity': fqty,

                             }
                             )
                        ]

                        print (fname+','+fmonth+','+fyear+','+fdate+','+fqty + '\n')

                        if len(fido_bagger) == 0:
                            fido_bag_id = self.models.execute_kw(self.db, self.uid, self.password, 'fido.bagger', 'create', \
                                               [{'name': b_id,'x_month':fmonth,'x_year':fyear,\
                                                 'bagger_line_ids':fline}])
                            fido_bagger.append(fido_bag_id)
                        else:
                            fido_bagger_u = self.models.execute_kw(self.db, self.uid, self.password, 'fido.bagger', 'write', [[fido_bag_id], \
                                            {'bagger_line_ids':fline}])
                        print ('fido.bagger'+str(fido_bagger))



    # create json data structure for bagger object
    def json_write(self):
        # extract data from Odoo 9 into file in dictionary format
        for k in range(0, len(bagger_obj)):

            for s in bagger_obj[k]:
                try:

                    p.name = str(s.name.name)
                    p.month = str(s.x_month)
                    p.year = str(s.x_year)

                    lenlines = len(s.bagger_line_ids)
                    p.bagger_line_ids =[]
                    for kk in range(0, lenlines):
                        bdate = str(s.bagger_line_ids[kk].fido_date)
                        bqty = str(s.bagger_line_ids[kk].x_quantity)

                        assert bdate, 'No fido date'
                        line = [bdate, bqty]
                        p.bagger_line_ids.append(line)

                    self.outs[p.name] = [p.name, p.year, p.month, p.bagger_line_ids]
                    target.write(str(self.outs))

                    target.write('\n')
                    self.outs.pop(p.name, None)
                    # print(str(self.outs[p.name])+'\n')

                except Exception, e:
                    print(str(e))
                    raise
    def login(self):
        # login to Odoo10
        try:
            self.db = 'FPLDB10'
            username = 'admin'
            self.password = 'N0tAdmin'
            port = '8071'
            host = 'localhost'
            url = 'http://%s:%s' % (host, port)
            self.models = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % (url))
            self.common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
            self.uid = self.common.authenticate(self.db, username, self.password, {})

            assert self.uid, 'com.login failed'
            version = self.common.version()
            # assert version['server_version'] == '10.0','Server not 10.0'
        except Exception, e:

            raise

    def get_bagger(self):
        # creates a bagger if not exist in hr.employee and/or return bagger_id
        # Also creates its contract if need be
        try:
            jobid_obj = self.models.execute_kw(self.db, self.uid, self.password, 'hr.job', 'search_read', \
                                          [[['name', '=', 'Bagger']]], {'fields': ['id']})

            if not jobid_obj:
                job_id = self.models.execute_kw(self.db, self.uid, self.password, 'hr.job', 'create', \
                                           [{'name': 'Bagger'}])
            else:
                job_id = jobid_obj[0]['id']

            assert job_id, 'Job id not set'
            bagger_hr_obj = self.models.execute_kw(self.db, self.uid, self.password, 'hr.employee', 'search_read', \
                                              [[['name', '=', self.bname]]], {'fields': ['id', 'name']})

            if not bagger_hr_obj:
                # Create Bagger in hr.employee
                employee_id  = self.models.execute_kw(self.db, self.uid, self.password, 'hr.employee', 'create', \
                                                [{'name': self.bname, 'job_id': job_id}])
                assert employee_id, 'Bagger Creation Fails'
                self.bagger_id = employee_id

            else:
                employee_id = bagger_hr_obj[0]['id']
                self.bagger_id = employee_id

            # Create contract in hr.contract if not exist
            hr_contract_obj = self.models.execute_kw(self.db, self.uid, self.password, 'hr.contract', 'search_read', \
                                                [[['employee_id', '=', employee_id]]], {'fields': ['id']})
            if not hr_contract_obj:

                contract_ref = self.bname + '-Contract'
                type_id = self.models.execute_kw(self.db, self.uid, self.password, 'hr.contract.type', 'search_read', \
                                            [[['name', '=', 'Employee']]], {'fields': ['id']})[0]['id']

                struct_obj = self.models.execute_kw(self.db, self.uid, self.password, 'hr.payroll.structure', 'search_read', \
                                               [[['name', '=', 'Contract']]], {'fields': ['id']})

                if not struct_obj:
                    struct_id = self.models.execute_kw(self.db, self.uid, self.password, 'hr.payroll.structure', 'create', \
                                                  [{'name': 'Contract', 'code': 'Contract'}])
                else:
                    struct_id = struct_obj[0]['id']

                assert struct_id, 'Payroll Structure Contract Not valid'
                date_start = date.today().strftime('%Y-%m-%d')
                wage = 0.0
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

                hr_contract = self.models.execute_kw(self.db, self.uid, self.password, 'hr.contract', 'create', \
                                                [{'name': contract_ref, 'employee_id': employee_id, 'job_id': job_id,
                                                  'type_id': type_id, 'struct_id': struct_id, \
                                                  'date_start': date_start, 'wage': wage,
                                                  'bagged_mult': bagged_mult, 'kpbg_sold': kpbg_sold,
                                                  'obbg_sold': obbg_sold,
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

            return employee_id
        except Exception, e:

            raise

# Main
file1 = '/tmp/bagger.txt'

try:
    os.remove(file1)
except OSError:
    pass

target = open(file1, 'w')

sn = 1
# Odoo Bagger Object
bagger_obj = env['fido.bagger'].search([],order='name asc')

# instantiate this Bagger Object
p = Bagger()

# create json_object into file1
print ('writing to file....' + file1)
p.json_write()
target.close()
p.login()
p.migrating()

print ('****    SEE '+file1)

from __future__ import print_function, division
import json,os,ast
import xmlrpclib
from datetime import datetime
from datetime import date
import csv,os

"""
Migrate fido.payroll from Odoo 9 to Odoo 10
from __future__ import print_function
sudo su -  odoo9 -s /bin/bash 
./odoo.py shell -d <dbname>
account_invoice_obj = env['account.invoice']

"""
class Payroll(object):
    def __init__(self):
        self.name = ""
        self.emp_id = ""
        self.year = ""
        self.month = ""
        self.payroll_line_ids = []
        self.outs = {}
        self.cn = {}
        self.models = ""
        self.common = ""
        self.db=""
        self.uid=""
        self.password= ""
        self.pname= ""
        self.payroll_id = ""
        self.daysab=""
        self.start_date=""
        self.end_date=""
        self.company =""
        self.saladv =""
        self.item_name =""


    def migrating(self):
        # read from created file and write to Odoo10

        with open(file1, 'r') as f:
            content = f.readlines()
            #self.outs = ast.literal_eval(s)
            # print ('s is'+s)
            for ln in content:
                try:
                    self.cn = eval(ln)
                    for iname, value in self.cn.iteritems():

                        fname = self.pname=self.cn[iname][0].strip()
                        fmonth = self.cn[iname][2].strip()
                        fyear = self.cn[iname][1].strip()
                        self.daysab = self.cn[iname][3]
                        self.saladv = self.cn[iname][4]
                        self.start_date = self.cn[iname][5]
                        self.end_date = self.cn[iname][6]
                        self.company = str(self.cn[iname][7].strip())
                        # b_id = self.get_bagger()
                        # assert b_id, 'Bagger_id not created'
                        fido_payroll = []
                        fido_pay_id =""
                        for ik in range(0,len(self.cn[iname][8])):
                            self.item_name = self.cn[iname][8][ik][0]
                            # search for item name and if not exist create it

                            item_obj = self.models.execute_kw(self.db, self.uid, self.password, 'fido.payroll.item', \
                                        'search_read', [[['name', '=', self.item_name]]], {'fields': ['id','name']})
                            if not item_obj:
                                # create item_id
                                item_id = self.models.execute_kw(self.db, self.uid, self.password, \
                                        'fido.payroll.item', 'create',[{'name': self.item_name}])
                                item_obj = self.models.execute_kw(self.db, self.uid, self.password, 'fido.payroll.item', \
                                                                  'search_read', [[['name', '=', self.item_name]]],
                                                                 {'fields': ['id','name']})
                                item_id = item_obj[0]['name']

                            else:
                                item_id = item_obj[0]['name']
                            assert item_id,'no item_id'

                            item_mult = self.cn[iname][8][ik][1]
                            item_qty = self.cn[iname][8][ik][2]
                            line_total = item_mult * item_qty
                            pline = [
                                (0, 0,
                                 {
                                     'item_id': item_id,
                                     'item_mult': item_mult,
                                     'item_qty': item_qty,
                                     'line_total':line_total,

                                 }
                                 )
                            ]

                            print (fname+','+fmonth+','+fyear+','+self.item_name+ '\n')

                            # Create Payroll
                            # get emp_id from employ_name
                            self.emp_id = self.models.execute_kw(self.db, self.uid, self.password, 'hr.employee', \
                                        'search_read', [[['name', '=', fname]]], {'fields': ['id']})

                            assert self.emp_id,'no such emp_id'
                            tstr = (self.emp_id[0]['id'], fmonth, fyear, self.daysab, self.saladv, self.start_date, self.end_date,self.company)
                            print(str(tstr))


                            if len(fido_payroll) == 0:
                                pay_rec = {'name': self.emp_id[0]['id'],
                                           'f_mnth': fmonth,
                                           'x_year': fyear,
                                           'daysabsent': self.daysab,
                                           'saladv': self.saladv,
                                           'start_date': self.start_date,
                                           'end_date': self.end_date,
                                           'company': self.company,
                                           'payroll_line_ids': pline
                                           }
                                fido_pay_id = self.models.execute_kw(self.db, self.uid, self.password, 'fido.payroll', 'create', \
                                            [pay_rec])


                                assert fido_pay_id,'payroll creation failed'
                                fido_payroll.append(fido_pay_id)
                                print('created fido.payroll' + str(fido_pay_id))
                            else:
                                fido_pay_r = self.models.execute_kw(self.db, self.uid, self.password, 'fido.payroll',
                                                'write', [[fido_pay_id], \
                                                {'payroll_line_ids': pline}])
                except Exception,e:
                    print(str(e))
                    raise

    # create json data structure for payroll object
    def json_write(self):
        # extract data from Odoo 9 into file in dictionary format
        for k in range(0, len(payroll_obj)):

            for s in payroll_obj[k]:
                try:

                    p.name = str(s.name.name)
                    p.month = str(s.f_mnth)
                    p.year = str(s.x_year)
                    p.daysab = s.daysabsent
                    p.saladv = s.saladv
                    p.start_date = s.start_date
                    p.end_date = s.end_date
                    p.company = s.company

                    lenlines = len(s.payroll_line_ids)
                    p.payroll_line_ids =[]
                    for kk in range(0, lenlines):
                        item_name = s.payroll_line_ids[kk].item_id
                        item_mult = s.payroll_line_ids[kk].item_mult
                        item_qty = s.payroll_line_ids[kk].item_qty

                        assert item_name, 'No item name'
                        line = [item_name, item_mult,item_qty]
                        p.payroll_line_ids.append(line)

                    self.outs[p.name] = [p.name, p.year, p.month,p.daysab,p.saladv,p.start_date,\
                                         p.end_date,p.company,p.payroll_line_ids]
                    target.write(str(self.outs))

                    target.write('\n')
                    self.outs.pop(p.name, None)
                    # print(str(self.outs[p.name])+'\n')

                except Exception, e:
                    print(str(e))
                    continue
                    # raise
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

# Main
file1 = '/tmp/payroll.txt'

try:
    os.remove(file1)
except OSError:
    pass

target = open(file1, 'w')

sn = 1
# Odoo Bagger Object
payroll_obj = env['fido.payroll'].search([],order='name asc')

# instantiate this Bagger Object
p = Payroll()

# create json_object into file1
print ('writing to file....' + file1)
p.json_write()
target.close()
p.login()
p.migrating()

print ('****    SEE '+file1)

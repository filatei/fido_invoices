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


    def migrate_9to10(self):
        # read from created file and write to Odoo10

        #with open(file1, 'r') as f:
        #    content = f.readlines()
        #    #self.outs = ast.literal_eval(s)
        #    # print ('s is'+s)
        #for ln in content:
        try:
            self.cn = eval(self.outs)
            for iname, value in self.cn.iteritems():

                fname = self.pname=self.cn[iname][0].strip()
                fmonth = self.cn[iname][2].strip()
                fyear = self.cn[iname][1].strip()
                self.daysab = self.cn[iname][3]
                self.saladv = self.cn[iname][4]
                self.start_date = self.cn[iname][5]
                self.end_date = self.cn[iname][6]
                self.company = str(self.cn[iname][7].strip())
                fido_payroll = []
                fido_pay_id =""
                for ik in range(0,len(self.cn[iname][8])):
                    self.item_name = self.cn[iname][8][ik][0]
                    # search for item name and if not exist create it

                    item_obj = self.models.execute_kw(self.db, self.uid, self.password, 'fido.payroll.item', \
                                        'search_read', [[['name', '=', self.item_name]]], {'fields': ['id','name']})
                    if not item_obj:
                        # create item_id
                        item_id_new = self.models.execute_kw(self.db, self.uid, self.password, \
                                        'fido.payroll.item', 'create',[{'name': self.item_name}])
                        assert item_id_new,'pay item creation failed'
                        item_obj = self.models.execute_kw(self.db, self.uid, self.password, 'fido.payroll.item', \
                                                                  'search_read', [[['name', '=', self.item_name]]],
                                                                 {'fields': ['id','name']})
                        item_id = item_obj[0]['name']
                        assert  item_id,'no item id'

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

                        })]

                    print (fname+','+fmonth+','+fyear+','+self.item_name+ '\n')

                    # Create Payroll
                    # get emp_id from employ_name
                    self.emp_id = self.models.execute_kw(self.db, self.uid, self.password, 'hr.employee', \
                                        'search_read', [[['name', '=', fname]]], {'fields': ['id']})

                    assert self.emp_id,'no such emp_id'
                    # from emp_id, extract contract details


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
                                     'write', [[fido_pay_id],  {'payroll_line_ids': pline}])
                        assert fido_pay_r,'fido payroll10 update fails'

        except Exception,e:
            print(str(e))
            raise

    def contract_update(self):
        # update odoo 10 contract for employee with Odoo 9 detais
        for k in range(0, len(payroll9_obj)):

            for s in payroll9_obj[k]:
                try:
                    # Harvest source contract details
                    emp_name = str(s.name.name).strip()
                    assert emp_name,'emp_name not good'
                    emp_obj = emp9_obj.search([('name', '=', emp_name)])
                    print (str(emp_obj) +' for employee ' + str(emp_name))
                    assert len(emp_obj) == 1, 'Emp OBJ >1 or =0'

                    emp_id = emp_obj.id
                    print ('emp name id 9 is ',emp_name)

                    contr_obj = contr9_obj.search([('employee_id', '=', emp_id)])
                    assert contr_obj, 'contr_obj not good'
                    contr_len = len(contr_obj)

                    # if more than one contract, use the last contract
                    contr_obj = contr_obj[contr_len - 1]
                    wage = contr_obj.wage
                    bag_mult = contr_obj.bagged_mult
                    crate_mult = contr_obj.cratesold_mult
                    disp_mult = contr_obj.dispsold_mult
                    kp_mult = contr_obj.kpbgsold_mult
                    ob_mult = contr_obj.obbgsold_mult
                    sal_adv = contr_obj.sal_adv
                    loan_adv = contr_obj.loan_adv
                    payee = contr_obj.payee
                    kp_qty = contr_obj.kpbg_sold
                    ob_qty = contr_obj.obbg_sold
                    disp_qty = contr_obj.disp_sold
                    crate_qty = contr_obj.crate_sold
                    s_date = contr_obj.date_start
                    e_date = contr_obj.date_end
                    ctr_name = str(emp_name).upper()+'-Contract'
                    print('contr name is ', ctr_name)

                    self.contract = {'wage': wage, 'bagged_mult': bag_mult, 'cratesold_mult': crate_mult,
                                     'dispsold_mult': disp_mult, 'kpbgsold_mult': kp_mult, 'obbgsold_mult': ob_mult,
                                     'sal_adv': sal_adv, 'loan_adv': loan_adv, 'payee': payee,
                                     'kpbg_sold': kp_qty, 'obbg_sold': ob_qty, 'disp_sold': disp_qty,
                                     'crate_sold': crate_qty, 'date_start': s_date, 'date_end': e_date,
                                     }
                    contr10_obj = self.models.execute_kw(self.db, self.uid, self.password, 'hr.contract', \
                                           'search_read', [[['name', '=', ctr_name]]], {'fields': ['id']})


                    assert contr10_obj,'contract_obj 10 not good'
                    contr10_id = contr10_obj[0]['id']

                    print ('contract 10 id ',contr10_id)
                    c_update = self.models.execute_kw(self.db, self.uid, self.password, 'hr.contract',
                                           'write', [[contr10_id], self.contract])
                    assert c_update,'contract update fails'
                    print (str(emp_name) + ' updated...'+str(c_update))
                except Exception, e:
                    print(str(e))

                    raise


    def pay_staff(self):
        try:
            #Odoo 10
            emp_name = self.name
            emp_obj = self.models.execute_kw(self.db, self.uid, self.password, 'hr.employee', 'search_read', \
                                        [[['name', '=', emp_name]]], {'fields': ['id']})
            assert emp_obj, 'employee not exist'
            pay_obj = self.models.execute_kw(self.db, self.uid, self.password, 'fido.payroll', 'search_read', \
                                        [[['name', '=', emp_name], ['x_year', '=', self.year], ['f_mnth', '=', self.month]]], \
                                        {'fields': ['id']})
            if not pay_obj:
                pay_id = self.models.execute_kw(self.db, self.uid, self.password, 'fido.payroll', 'create', \
                                           [{'name': emp_obj[0]['id'], 'x_year': self.year,'f_mnth':self.month,\
                                        'start_date':self.start_date,'end_date':self.end_date, 'daysabsent': self.daysab,
                                             'saladv': self.saladv,'company':self.company}])
                assert pay_id, 'Pay Creation Fails'
                print('Payroll Created for ' + emp_name)
            else:
                pay_id = pay_obj[0]['id']
                print ('Payroll Exists. Not Created')




            # Move Workflow to Compute from Draft
            compute_id = self.models.execute_kw(self.db, self.uid, self.password, 'fido.payroll', 'compute', pay_id)
            assert compute_id,'Validation Failed'

            return pay_id
        except Exception, e:
            print('Pay Staff Error for ' + ',' + emp_name + ',' + str(e))
            raise


    def _update_contract(self):
        # given self.contract and self.name
        try:
            ctr_name = str(self.name).upper().strip() + '-Contract'
            contr10_obj = self.models.execute_kw(self.db, self.uid, self.password, 'hr.contract', \
                                             'search_read', [[['name', '=', ctr_name]]], {'fields': ['id']})

            assert contr10_obj, 'contract_obj 10 not good'
            contr10_id = contr10_obj[0]['id']

            print('contract 10 id ', contr10_id)
            c_update = self.models.execute_kw(self.db, self.uid, self.password, 'hr.contract',
                                          'write', [[contr10_id], self.contract])
            assert c_update, 'contract update fails'
            print(str(self.name) + ' updated...' + str(c_update))
            return c_update
        except Exception, e:
            print(str(e))
            raise

    # create json data structure for payroll object
    def payroll_migrate(self):
        # extract data from Odoo 9 into file in dictionary format
        for k in range(0, len(payroll9_obj)):

            for s in payroll9_obj[k]:
                try:

                    emp_name = str(s.name.name).strip()


                    assert emp_name, 'emp_name not good'
                    # for Odoo 10 names in caps
                    self.name = emp_name.upper()
                    name = emp_name.upper()
                    self.month = str(s.f_mnth)
                    month = str(s.f_mnth)
                    self.year = str(s.x_year)
                    year = str(s.x_year)
                    self.daysab = s.daysabsent
                    daysab = s.daysabsent
                    self.saladv = s.saladv
                    saladv = s.saladv
                    self.start_date = s.start_date
                    start_date = s.start_date
                    self.end_date = s.end_date
                    end_date = s.end_date
                    self.company = str(s.company)
                    company = str(s.company)

                    lenlines = len(s.payroll_line_ids)
                    payroll_line_ids =[]
                    self.payroll_line_ids =[]

                    wage=bagged_mult=disp_sold=dispsold_mult=crate_sold=0.0
                    cratesold_mult=kpbgsold_mult=kpbg_sold=obbg_sold=obbgsold_mult=0.0

                    for kk in range(0, lenlines):
                        item_name = s.payroll_line_ids[kk].item_id
                        print ('item name: ',item_name)
                        assert item_name, 'No item name'
                        self.item_name = s.payroll_line_ids[kk].item_id
                        item_mult = s.payroll_line_ids[kk].item_mult
                        self.item_mult = s.payroll_line_ids[kk].item_mult
                        item_qty = s.payroll_line_ids[kk].item_qty
                        self.item_qty = s.payroll_line_ids[kk].item_qty

                        # can we update contract here?
                        if 'Base Salary' in item_name:
                            wage = item_qty
                        if 'Bagging Commission' in item_name:
                            bagged_mult = item_mult
                        if 'Dispenser Sales' in item_name:
                            dispsold_mult = item_mult
                            disp_sold = item_qty
                        if 'Crates Sales' in item_name:
                            cratesold_mult = item_mult
                            crate_sold = item_qty
                        if 'KP Bags' in item_name:
                            kpbgsold_mult = item_mult
                            kpbg_sold = item_qty
                        if 'OB Bags' in item_name:
                            obbgsold_mult = item_mult
                            obbg_sold = item_qty

                        line = [item_name, item_mult, item_qty]
                        payroll_line_ids.append(line)
                        self.payroll_line_ids.append(line)

                    self.contract = {'wage': wage, 'bagged_mult': bagged_mult, 'cratesold_mult': cratesold_mult,
                                     'dispsold_mult': dispsold_mult, 'kpbgsold_mult': kpbgsold_mult, 'obbgsold_mult': obbgsold_mult,
                                     'sal_adv': saladv,
                                     'kpbg_sold': kpbg_sold, 'obbg_sold': obbg_sold, 'disp_sold': disp_sold,
                                     'crate_sold': crate_sold,
                                     }
                    c_update = self._update_contract()
                    assert c_update,'contract update fails in payroll_migrate'

                    # Create Payroll in Odoo 10
                    pay_id = self.pay_staff()
                    assert pay_id,'pay fails in payroll_migrate'




                    self.outs[emp_name] = [emp_name, year, month,daysab,saladv,start_date,\
                                        end_date,company,payroll_line_ids]




                    target.write(str(self.outs))

                    target.write('\n')
                    self.outs.pop(name, None)
                    # print(str(self.outs[p.name])+'\n')

                except Exception, e:
                    print(str(e))
                    # continue
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

# Main
file1 = '/tmp/payroll.txt'

try:
    os.remove(file1)
except OSError:
    pass

target = open(file1, 'w')

sn = 1
# Odoo Bagger Object
payroll9_obj = env['fido.payroll'].search([],order='name asc')
emp9_obj = env['hr.employee'].search([],order='name asc')
contr9_obj = env['hr.contract'].search([],order='name asc')

# instantiate this Bagger Object
p = Payroll()

# create json_object into file1
print ('writing to file....' + file1)
p.login()
# p.contract_update()

p.payroll_migrate()

target.close()

print ('****    SEE '+file1)

from __future__ import print_function, division
import json,os,ast
import xmlrpclib
from datetime import datetime
from datetime import date
import csv,os

"""
Migrate invoices and vendor bills from Odoo 9 to Odoo 10

sudo su -  odoo9 -s /bin/bash 
./odoo.py shell -d <dbname>
account_invoice_obj = env['account.invoice']

"""
class Invoice(object):
    def __init__(self):
        self.name = ""
        self.emp_id = ""
        self.year = ""
        self.month = ""
        self.invoice_line_ids = []
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
        self.file = ""
        self.payroll_total = 0.0

    def validate_invoice(self):
        try:

            inv_obj = self.models.execute_kw(self.db, self.uid, self.password, 'account.invoice', \
                                          'search_read', [[['state','=','draft']]], {'fields': ['id']})
            # print('invoice obj: ' + str(inv_obj))
            for kk in range(0,len(inv_obj)):
                # Move Workflow to Validate from Draft
                inv_id = inv_obj[kk]['id']
                print('inv id to be validated: '+str(inv_id))
                val_id = self.models.exec_workflow(self.db, self.uid, self.password, \
                        'account.invoice', 'invoice_open', inv_id)
                assert val_id,'validation failed'
        except Exception,e:
            print (str(e))
            raise

        # assert compute_id,'Validation Failed'

    def vendor_create(self):
        try:
            v_name = self.vendor
            vendor_obj = self.models.execute_kw(self.db, self.uid, self.password, 'res.partner', \
                                                'search_read', [[['name', '=', v_name],['supplier','=',True]]], {'fields': ['id']})
            if not vendor_obj:
                v_id = self.models.execute_kw(self.db, self.uid, self.password, \
                                   'res.partner', 'create', [{'name': v_name, 'supplier': True,'user_id':8}])
                assert v_id,'vendor create fails'
            else:
                v_id = vendor_obj[0]['id']
            return v_id
        except Exception,e:
            print (str(e))
            raise



    def bill_migrate_9to10(self):
        # read from created file and write to Odoo10

        with open(self.file, 'r') as f:
            content = f.readlines()
            # self.outs = ast.literal_eval(s)
            # print ('s is'+s)
            for ln in content:
                try:
                    cn = eval(str(ln))
                    for iname, value in cn.iteritems():
                        pname = cn[iname][0].strip().upper()
                        self.vendor = pname
                        v_id = self.vendor_create()
                        assert v_id,'no vendor id in bill_mig9to10'
                        date_invoice = cn[iname][1]
                        date_due = date_invoice
                        salesp = cn[iname][3].strip()


                        company = str(cn[iname][4]).strip()
                        comp_obj = self.models.execute_kw(self.db, self.uid, self.password, 'res.company', \
                                                'search_read', [[['name', '=', company]]], {'fields': ['id','name']})
                        assert comp_obj,'no such company'
                        company_id = comp_obj[0]['id']
                        invoice = []
                        for ik in range(0,len(cn[iname][5])):
                            product = str(cn[iname][5][ik][0]).strip()
                            # search for item name and if not exist create it
                            if 'DISPENSER' in product:
                                product = 'DISPENSER'
                            if '50CL' in product:
                                product = 'CRATE50CL'
                            if '60CL' in product:
                                product = 'CRATE60CL'
                            if 'PUREWATER' in product:
                                product = 'PUREWATER'

                            product_obj = self.models.execute_kw(self.db, self.uid, self.password, 'product.product', \
                                                'search_read', [[['name', '=', product]]], {'fields': ['id','name','property_account_income_id']})

                            if not product_obj:
                                # create item_id
                                product_id_new = self.models.execute_kw(self.db, self.uid, self.password, \
                                                'product.product', 'create',[{'name': product,'property_account_income_id':5}])
                                assert product_id_new,'product creation failed'
                                product_obj = self.models.execute_kw(self.db, self.uid, self.password, 'product.product', \
                                                                          'search_read', [[['name', '=', product]]],
                                                                         {'fields': ['id','name','property_account_income_id']})
                                product_id = product_obj[0]['id']
                                assert  product_id,'no product id'
                                prod_acct_id = product_obj[0]['property_account_income_id'][0]
                                assert prod_acct_id, 'no product_acct_id'

                            else:
                                product_id = product_obj[0]['id']
                                assert product_id,'no product_id'
                                print ('product acct id' + str(product_obj[0]['property_account_income_id']))
                                prod_acct_id = product_obj[0]['property_account_income_id'][0]
                                assert prod_acct_id, 'no product_acct_id'

                            quantity = cn[iname][5][ik][1]
                            price_unit = cn[iname][5][ik][2]

                            pline = [
                                (0, 0,
                                {
                                    'product_id': product_id,
                                    'name':product,
                                    'account_id':prod_acct_id,
                                    'price_unit': price_unit,
                                    'quantity': quantity,


                                })]

                            print (self.vendor +','+date_invoice+','+salesp+','+ '\n')
                            print ('pline: '+str(pline))


                            assert partner_obj,'no such partner_id'

                            if len(invoice) == 0:
                                inv_rec = {'partner_id': v_id,
                                           'date_invoice': date_invoice,
                                            'date_due':date_due,
                                           'journal_id': 2,
                                           'account_id': 15,
                                           'company_id': company_id,
                                           'type':'in_invoice',
                                           'invoice_line_ids': pline,
                                           }
                                print ('inv_rec: ',str(inv_rec))
                                inv_id = self.models.execute_kw(self.db, self.uid, self.password, 'account.invoice', 'create', \
                                                    [inv_rec])


                                assert inv_id,'invoice creation failed'
                                invoice.append(inv_id)
                                print('created invoice for ' + str(pname))
                            else:
                                inv_r = self.models.execute_kw(self.db, self.uid, self.password, 'account.invoice',
                                         'write', [[inv_id],  {'invoice_line_ids': pline}])
                                assert inv_r,'Invoice update fails'
                        # Validate invoice
                        # val_id = self.models.exec_workflow(self.db, self.uid, self.password, \
                        #                          'account.invoice', 'invoice_open', inv_id)
                        # assert val_id,'Invoice not validated'

                except Exception,e:
                    print(str(e))
                    raise

    def migrate_9to10(self):
        # read from created file and write to Odoo10

        with open(self.file, 'r') as f:
            content = f.readlines()
            #self.outs = ast.literal_eval(s)
            # print ('s is'+s)
            for ln in content:
                try:
                    cn = eval(str(ln))
                    for iname, value in cn.iteritems():

                        pname = cn[iname][0].strip().upper()

                        date_invoice = cn[iname][1].strip()
                        salesp = cn[iname][2].strip()

                        team = cn[iname][3]
                        team_obj = self.models.execute_kw(self.db, self.uid, self.password, 'crm.team', \
                                               'search_read', [[['name', '=', team]]], {'fields': ['id', 'name']})
                        assert team_obj,'no such team here'
                        team_id = team_obj[0]['id']


                        company = str(cn[iname][4]).strip()
                        comp_obj = self.models.execute_kw(self.db, self.uid, self.password, 'res.company', \
                                                'search_read', [[['name', '=', company]]], {'fields': ['id','name']})
                        assert comp_obj,'no such company'
                        company_id = comp_obj[0]['id']
                        invoice = []
                        for ik in range(0,len(cn[iname][5])):
                            product = str(cn[iname][5][ik][0]).strip()
                            # search for item name and if not exist create it

                            product_obj = self.models.execute_kw(self.db, self.uid, self.password, 'product.product', \
                                                'search_read', [[['name', '=', product]]], {'fields': ['id','name','property_account_income_id']})

                            if not product_obj:
                                # create item_id
                                product_id_new = self.models.execute_kw(self.db, self.uid, self.password, \
                                                'product.product', 'create',[{'name': product,'property_account_income_id':5}])
                                assert product_id_new,'product creation failed'
                                product_obj = self.models.execute_kw(self.db, self.uid, self.password, 'product.product', \
                                                                          'search_read', [[['name', '=', product]]],
                                                                         {'fields': ['id','name','property_account_income_id']})
                                product_id = product_obj[0]['id']
                                assert  product_id,'no product id'
                                prod_acct_id = product_obj[0]['property_account_income_id'][0]
                                assert prod_acct_id, 'no product_acct_id'

                            else:
                                product_id = product_obj[0]['id']
                                assert product_id,'no product_id'
                                print ('product acct id' + str(product_obj[0]['property_account_income_id']))
                                prod_acct_id = product_obj[0]['property_account_income_id'][0]
                                assert prod_acct_id, 'no product_acct_id'

                            quantity = cn[iname][5][ik][1]
                            price_unit = cn[iname][5][ik][2]

                            pline = [
                                (0, 0,
                                {
                                    'product_id': product_id,
                                    'name':product,
                                    'account_id':prod_acct_id,
                                    'price_unit': price_unit,
                                    'quantity': quantity,


                                })]

                            print (pname+','+date_invoice+','+salesp+','+team+ '\n')
                            print ('pline: '+str(pline))

                            # Create invoice
                            # get partner_id
                            partner_obj = self.models.execute_kw(self.db, self.uid, self.password, 'res.partner', \
                                                'search_read', [[['name', '=', pname]]], {'fields': ['id']})

                            assert partner_obj,'no such partner_id'

                            if len(invoice) == 0:
                                inv_rec = {'partner_id': partner_obj[0]['id'],
                                           'date_invoice': date_invoice,
                                           'team_id':team_id,
                                           'journal_id': 1,
                                           'account_id': 7,
                                           'type': 'out_invoice',
                                           'company_id': company_id,
                                           'invoice_line_ids': pline,
                                           }
                                inv_id = self.models.execute_kw(self.db, self.uid, self.password, 'account.invoice', 'create', \
                                                    [inv_rec])


                                assert inv_id,'invoice creation failed'
                                invoice.append(inv_id)
                                print('created invoice for ' + str(pname))
                            else:
                                inv_r = self.models.execute_kw(self.db, self.uid, self.password, 'account.invoice',
                                         'write', [[inv_id],  {'invoice_line_ids': pline}])
                                assert inv_r,'Invoice update fails'
                        # Validate invoice
                        val_id = self.models.exec_workflow(self.db, self.uid, self.password, \
                                                 'account.invoice', 'invoice_open', inv_id)
                        # assert val_id,'Invoice not validated'

                except Exception,e:
                    print(str(e))
                    raise


    def bill_migrate(self):
        inv9_obj = invoice9_obj.search([('type', '=', 'in_invoice')])
        for k in range(0, len(inv9_obj)):

            for s in inv9_obj[k]:
                try:
                    partner_name = str(s.partner_id.name).strip().upper()
                    assert partner_name, 'partner_name not good'
                    print ('Partner Name: '+partner_name +'invoice_type: '+s.type)
                    # for Odoo 10 names in caps

                    name = partner_name
                    date_invoice = s.date_invoice
                    date_due = s.date_due

                    salesp = str(s.user_id.name).upper()

                    company = 'GTS LTD'
                    lenlines = len(s.invoice_line_ids)
                    invoice_line_ids = []

                    for kk in range(0, lenlines):
                        product = str(s.invoice_line_ids[kk].product_id.name).strip().upper()
                        print('product: ' + str(product) + ',' + str(lenlines))

                        # assert item_name, 'No item name'
                        quantity = s.invoice_line_ids[kk].quantity
                        price_unit = s.invoice_line_ids[kk].price_unit
                        line = [product, quantity, price_unit]
                        invoice_line_ids.append(line)

                    self.outs[name] = [partner_name, date_invoice,date_due,salesp, \
                                       company, invoice_line_ids]

                    # self.migrate_9to10()

                    target2.write(str(self.outs) + '\n')

                    # target.write('\n')
                    self.outs.pop(name, None)
                    # print(str(self.outs[p.name])+'\n')

                except Exception, e:
                    print(str(e))
                     # continue
                    raise



    # create json data structure for payroll object
    def invoice_migrate(self):
        # extract data from Odoo 9 into file in dictionary format
        # out_invoice type is customer invoice and in_invoice is vendor bill
        inv9_obj = invoice9_obj.search([('type','=','out_invoice')])
        for k in range(0, len(inv9_obj)):

            for s in inv9_obj[k]:
                try:

                    partner_name = str(s.partner_id.name).strip().upper()


                    assert partner_name, 'partner_name not good'
                    print ('Partner Name: '+partner_name +'invoice_type: '+s.type)
                    # for Odoo 10 names in caps

                    name = partner_name
                    date_invoice = s.date_invoice
                    salesp = str(s.user_id.name).upper()
                    team = str(s.team_id.name)
                    company = 'GTS LTD'



                    lenlines = len(s.invoice_line_ids)
                    invoice_line_ids =[]

                    for kk in range(0, lenlines):
                        product = str(s.invoice_line_ids[kk].product_id.name).strip().upper()
                        print ('product: '+ str(product)+','+str(lenlines))

                        # assert item_name, 'No item name'
                        quantity = s.invoice_line_ids[kk].quantity
                        price_unit = s.invoice_line_ids[kk].price_unit
                        line = [product, quantity, price_unit]
                        invoice_line_ids.append(line)



                    self.outs[name] = [partner_name, date_invoice, salesp,team,\
                                        company,invoice_line_ids]

                    # self.migrate_9to10()

                    target.write(str(self.outs)+'\n')

                    # target.write('\n')
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


    def del_invoice(self):
        try:
            inv_obj = self.models.execute_kw(self.db, self.uid, self.password, 'account.invoice', \
                                             'search_read', [[['state', '=', 'draft']]], {'fields': ['id']})
            # print('invoice obj: ' + str(inv_obj))
            for kk in range(0, len(inv_obj)):
                # Move Workflow to Validate from Draft
                inv_id = inv_obj[kk]['id']
                del_id1 = self.models.execute_kw(self.db, self.uid, self.password, 'account.invoice', \
                               'unlink', [[inv_id]])
                print ('deleting invoice id: '+ str(inv_id))
                # check if the deleted record is still in the database
                del_id = self.models.execute_kw(self.db, self.uid, self.password, 'account.invoice', \
                               'search', [[['id', '=', inv_id]]])
            assert not del_id,'not deleted'
        except Exception,e:
            print(str(e))
            raise

file1 = '/tmp/invoices.txt'

file2 = '/tmp/bill.txt'


target = open(file1, 'w')
target2 = open(file2, 'w')
sn = 1
# Odoo Bagger Object
inv = invoice9_obj = env['account.invoice'].search([],order='name asc')

partner_obj = env['res.partner'].search([],order='name asc')

# instantiate this Bagger Object
i = Invoice()

# create json_object into file1
print ('writing to file....' + file1)
i.login()
# p.contract_update()

i.invoice_migrate()
target.close()
# i.del_invoice()
i.file = file1
i.migrate_9to10()
# i.validate_invoice()
i.bill_migrate()
target2.close()
i.file = file2
i.bill_migrate_9to10()

# GTS move






print ('****    SEE '+file1)

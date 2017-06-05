# login routines
try:
    db = 'FPLDB'
    username = 'admin3'
    password = 'Adm1n3'
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


# Extract all from Odoo9 FPLDB
ofile = '/tmp/fpldb_customers.csv'
ofile2 = '/tmp/fpldb_vendors.csv'
payf = '/tmp/payroll.csv'
of = open(ofile,'w')
of2 = open(ofile2,'w')
pay = open(payf,'w')
head='SN,DBID,NAME,SALESPERSON,MOBILE,PHONE,COMPANY_TYPE,TOTAL_INVOICED'
customer = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[['customer', '=', True]]], \
                                    {'fields': ['id','name','user_id','mobile','phone','company_type','total_invoiced']})
vendor = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[['customer', '=', False]]], \
                                    {'fields': ['id','name','user_id','mobile','phone','company_type','total_invoiced']})
sn= 0
of.write(head+'\n')
of2.write(head+'\n')

for k in customer:
    sn = sn +1
    ostr = str(sn)+','+str(k.id) +','+k.name+','+str(k.user_id.name)+','+str(k.mobile)+','+str(k.phone)+','+str(k.company_type)+','+str(k.total_invoiced)
    of.write(ostr+'\n')
    print ostr
sn = 0

for k in vendor:
    sn = sn +1
    ostr = str(sn)+','+str(k.id) +','+k.name+','+str(k.user_id.name)+','+str(k.mobile)+','+str(k.phone)+','+str(k.company_type)+','+str(k.total_invoiced)
    of2.write(ostr+'\n')
    print ostr

# Payroll
payroll = env['fido.payroll'].search([])
sn = 0
headp = 'SN,DBID,NAME,MONTH,YEAR,DAYS ABSEENT,SALARY ADV,PAY REF,START DATE,END DATE,COMPANY,PAYROLL IDS'
pay.write(headp+'\n')
for k in payroll:
    sn = sn + 1
    ostr = str(sn) + ',' + str(k.id) + ',' + str(k.name.name) + ',' + str(k.f_mnth) + ',' + str(k.x_year) + ',' + str(\
        k.daysabsent) + ',' + str(k.saladv) + ',' + str(k.payroll_ref)+ ',' + str(k.start_date) \
           + ',' + str(k.end_date)+ ',' + str(k.company)
    ostr = ostr + ',' + '['
    for i in k.payroll_line_ids:
        ostr = ostr +','+str(i.item_id)+','+str(i.item_qty)+','+str(i.item_mult)+','+str(i.line_total)+'\n'
    ostr = ostr.rstrip() + ']'
    pay.write(ostr+'\n')
    print ostr

of.close()
of2.close()
pay.close()

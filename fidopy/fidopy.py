from datetime import datetime
import csv,os
import logging
from xlrd import open_workbook
from random import randint



class FidoPy():
    """
      handles all Fido Producing daily activities and data
    
    """
    def __init__(self):
        self.name = ""
        self.company = ""
        self.xlsfile = ""
        self.csvfile = ""
        self.teller_tot = 0.0
        self.datadir = "data"
        self.data = {}

    def set_xlsfile(self,xlsfile):
        self.xlsfile = xlsfile

    def set_csvfile(self,csvfile):
        self.csvfile = csvfile

    def update_data(self,dti,data):
        """ append to data list of lists"""
        if dti not in  self.data.keys():
            self.data[dti] = [data]
        else:

            self.data[dti].append(data)


    def teller_tot_update(self,tot):
        self.teller_tot = self.teller_tot + float(tot)

    def get_data(self):
        return self.data

    def get_datadir(self):
        return self.datadir

    def get_xls(self):
        """ get the daily xls file from Yenagoa"""
        return self.xlsfile

    def get_csv(self):
        """ get the resulted csv file extracted from xls file"""

        return self.csvfile

    def get_teller_tot(self):
        return self.teller_tot



    def fix_date(self,tdate):
        try:

            if ('/' not in str(tdate)) and ('.' not in str(tdate)):
                ddt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(tdate) - 2)
                return ddt.strftime('%Y-%m-%d')
            else:
                if '/' in str(tdate):
                    return (datetime.strptime(tdate, '%d/%m/%Y')).strftime('%Y-%m-%d')
                elif '.' in str(tdate):
                    return (datetime.strptime(tdate, '%d.%m.%Y')).strftime('%Y-%m-%d')
        except Exception as e:
            print (str(e))
            raise

    def xls2csv(self):
        """ extracts worksheets from the workbook into files named by worksheet names
            workbook name is set in self.xlsfile or self.set_xlsfile()
        """
        try:
            wb = open_workbook(self.get_xls())
            assert wb,'xls file not set perhaps'
            TODAY = datetime.now().strftime('%d-%m-%Y')
            # print ('SHEETS IN SALES FILE')

            for i in range(0, wb.nsheets - 1):
                sheet = wb.sheet_by_index(i)
                # print (sheet.name)

                path = self.get_datadir() + '/%s.csv'
                with open(path % (sheet.name.replace(" ", "") + '-' + TODAY), "w") as file:
                    writer = csv.writer(file, delimiter=",", quotechar='"', \
                                    quoting=csv.QUOTE_ALL, skipinitialspace=True)

                    header = [cell.value for cell in sheet.row(0)]
                    writer.writerow(header)

                    for row_idx in range(1, sheet.nrows):
                        row = [int(cell.value) if isinstance(cell.value, float) else cell.value
                               for cell in sheet.row(row_idx)]
                        writer.writerow(row)
        except Exception as e:
            print(str(e))
            raise

    def invoice_list(self):
        INV_FILE = self.get_csv()
        sn = 1
        try:
            assert INV_FILE,'Invoice csv file not set'
            with open(INV_FILE, 'rb') as csvfile:
                invoice_type = 'out_invoice'
                line = csv.DictReader(csvfile, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, \
                                  skipinitialspace=True)
                for row in line:

                    tellername = row['TELLER NAME'].strip().upper()
                    teller_no = row['TELLER NO'].strip().upper()
                    partner = row['CUSTOMER NAME'].strip().upper()
                    price_unit = rate = row['RATE']
                    qty = row['QTY']

                    if not teller_no:
                        if not rate and not qty:
                            continue
                    # Detect Invalid transaction. qty not positive or rate not +ve

                    assert qty >0 and rate >0,'qty or rate not +ve'


                    prodname = row['PRODUCT'].strip().upper()

                    salesperson = row['SALESPERSON'].strip().upper()

                    location = row['LOCATION'].strip()

                    teller_date = self.fix_date(row['TELLER DATE'])


                    # print ('tdate: ' + str(tdate) + ' = ' + str(teller_date))

                    assert teller_date, 'Teller Date not good'

                    dateinv = self.fix_date(row['INVOICE DATE'])


                    # DEAL With TELLER RECORD

                    teller_amount = row['TELLER AMOUNT'].strip().replace(',', '')
                    if not teller_amount:
                        teller_amount = 0.0
                    self.teller_tot_update(teller_amount)
                    bank = row['BANK'].strip().upper()

                    # print((sn,dateinv,partner,salesperson,prodname,rate,qty,teller_amount,teller_no,bank,teller_date,tellername,location,'\n'))
                    self.update_data(dateinv,[teller_no,teller_date,bank,tellername,partner,salesperson,prodname,rate,qty,teller_amount,location])
                    sn = sn + 1

        except Exception, e:
            print 'Invoice extraction Error.' + ',' + str(partner) + ',' + str(salesperson)\
                  + ',' + str(e)
            raise

    def get_prices(self,dt):
        self.invoice_list()
        print 'Prices for: ',dt
        print ('Customer,Teller_Amount')
        thisdata =self.data[dt]
        for k in range(0,len(thisdata)):
            print (thisdata[k][4],float(thisdata[k][9]))


def main():
    if not os.path.exists('./data'):
        os.makedirs('./data')

    if not os.path.exists('./OUT'):
        os.makedirs('./OUT')
    try:

        f = FidoPy()
        f.set_xlsfile('/home/user1/Downloads/SATURDAY 01.07.2017.xls')
        f.xls2csv()
        TODAY = datetime.now().strftime('%d-%m-%Y')
        csvfile = 'data/INVOICE-' + TODAY + '.csv'
        f.set_csvfile(csvfile)
        # f.invoice_list()
        teller_tot = f.get_teller_tot()
        # print ('Teller Totals: ',teller_tot)
        # print (f.get_data())
        f.get_prices('2017-07-01')

    except Exception as e:
        raise


main()

# if __name__ == '__main__':

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

    def set_xlsfile(self,xlsfile):
        self.xlsfile = xlsfile

    def set_csvfile(self,csvfile):
        self.csvfile = csvfile

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

    def teller_tot_update(self,tot):
        self.teller_tot = self.teller_tot + float(tot)

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
                        else:
                            qty = row['QTY'].strip()
                            price_unit = row['RATE'].strip()

                    prodname = row['PRODUCT'].strip().upper()

                    salesperson = row['SALESPERSON'].strip().upper()

                    location = row['LOCATION'].strip()

                    tdate = row['TELLER DATE']
                    if ('/' not in str(tdate)) and ('.' not in str(tdate)):
                        ddt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(tdate) - 2)
                        teller_date = ddt.strftime('%Y-%m-%d')
                    else:
                        teller_date = (datetime.strptime(tdate, '%d/%m/%Y')).strftime('%Y-%m-%d')
                    # print ('tdate: ' + str(tdate) + ' = ' + str(teller_date))

                    assert teller_date, 'Teller Date not good'

                    invdate = row['INVOICE DATE']
                    # fix date formatting

                    if ('/' not in str(invdate)) and ('.' not in str(invdate)):
                        dt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(invdate) - 2)

                    else:
                        dt = datetime.strptime(invdate, '%d/%m/%Y')

                    dateinv = dt.strftime('%Y-%m-%d')

                    # Detect Invalid transaction
                    if not row['TELLER NO'] or qty <= 0 or price_unit <= 0:
                        print row['TELLER NO'] + ' Invalid Data QTY: ' + qty + 'Rate: ' + price_unit
                        # raise Exception('Invalid Transaction - no teller_no or -ve qty or 0 Rate')
                        continue

                    # DEAL With TELLER RECORD

                    teller_amount = row['TELLER AMOUNT'].strip().replace(',', '')
                    if not teller_amount:
                        teller_amount = 0.0
                    self.teller_tot_update(teller_amount)
                    bank = row['BANK'].strip().upper()
                    print((sn,dateinv,partner,salesperson,prodname,rate,qty,teller_amount,teller_no,bank,teller_date,tellername,location))
                    print ('\n')
                    sn = sn + 1

        except Exception, e:
            print 'Invoice extraction Error.' + ',' + str(partner) + ',' + str(salesperson)\
                  + ',' + str(e)
            raise

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
        f.invoice_list()
        teller_tot = f.get_teller_tot()
        print ('Teller Totals: ',teller_tot)
    except Exception as e:
        raise


main()

# if __name__ == '__main__':

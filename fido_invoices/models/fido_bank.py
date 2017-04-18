from openerp import api, fields, models
import datetime
import time
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class fido_bank(models.Model):
    _name = 'fido.bank'
    _description = 'Model Nigerian Banks'

    name = fields.Char(string='Bank Name',required=True)
    contact = fields.Text(string='Contact Address')
    ngn_acct_no = fields.Char(string='NGN Account')
    usd_acct_no = fields.Char(string='USD Account')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Bank Name already exists !"),
    ]
from openerp import api, fields, models
from openerp.exceptions import UserError, ValidationError
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
import datetime,time,logging


_logger = logging.getLogger(__name__)

class fido_teller(models.Model):
    _name = 'fido.teller'
    _description = 'Model Bank Tellers coming to Fido'
    # invoice_id = fields.One2many('fido.invoice', 'teller_id',string='Fido Invoice Reference')
    name = fields.Char(string='Teller Number',
                           required=True)

    teller_name = fields.Many2one('res.partner', string='Name on Teller', required=True,
                store=True, domain="[('customer', '=', True)]")
    date = fields.Date(string='Teller Date', required=True, help="Teller Date.")
    teller_amount = fields.Float(string='Teller Amount', required=True, help='Teller Amount')
    bank = fields.Many2one('fido.bank', string='Bank Name',required=True)


class fido_invoice(models.Model):
    _inherit = 'account.invoice'
    #_name = 'fido.invoice'
    _description = 'Extends account.invoice to add new fields'

    date_invoice = fields.Date(string='Invoice Date', default=date.today(),store=True,
             readonly=True, states={'draft': [('readonly', False)]}, index=True,
             help="Change to current date.", copy=False)
    teller_id = fields.Many2one('fido.teller',string='Teller id', store=True,help='Unique Teller No')

    teller_amount = fields.Float(related='teller_id.teller_amount',string='Teller Amount',readonly=True,store=True)
    teller_bank = fields.Many2one(related='teller_id.bank',store=True,readonly=True,
            string='Teller Bank',track_visibility='onchange')
    teller_date = fields.Date(related='teller_id.date', string='Teller Date', store=True,
                              track_visibility='onchange',readonly=True)
    teller_name = fields.Many2one(related='teller_id.teller_name', string='Teller Name',readonly=True,
                              store=True,track_visibility='onchange')

    # the idea is to link salesperson to customer's sales person
    partner_id = fields.Many2one('res.partner', string='Partner', change_default=True,
             required=True, readonly=True,store=True, states={'draft': [('readonly', False)]},
             track_visibility='always')
    salesp = fields.Many2one(related='partner_id.user_id',string='FIDO SALESPERSON', track_visibility='onchange',
             readonly=True,store=True, states={'draft': [('readonly', False)]})

    def _teller_amount(self):
        _logger.info("*** LOGGING Processing  teller_name %s",  self.teller_name)
        self.teller_amount = self.teller_id.teller_amount

    _sql_constraints = [
        ('name_uniq', 'unique (teller_id,teller_name,teller_bank)', "Teller name/bank/id already exists !"),
    ]
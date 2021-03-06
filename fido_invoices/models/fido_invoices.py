from openerp import api, fields, models
from openerp.exceptions import UserError, ValidationError
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
import datetime,time,logging


_logger = logging.getLogger(__name__)



class fido_invoice(models.Model):
    _inherit = 'account.invoice'
    #_name = 'fido.invoice'
    _description = 'Extends account.invoice to add new fields'
    inv_line_ids = fields.Many2many('account.invoice.line', string='Invoice Lines',store=True,\
                        readonly=True, states={'draft': [('readonly', False)]}, copy=True)

    date_invoice = fields.Date(string='Invoice Date', default=date.today(),store=True,
             readonly=True, states={'draft': [('readonly', False)]}, index=True,
             help="Change to current date.", copy=False)
    teller_id = fields.Many2one('fido.teller',string='Teller id', store=True,help='Unique Teller No')

    teller_amount = fields.Float(related='teller_id.teller_amount',string='Teller Amount',readonly=True,store=True)
    teller_bank = fields.Many2one(related='teller_id.bank', string='Bank', track_visibility='onchange',\
             readonly=True,store=True)

    teller_date = fields.Date(related='teller_id.date', string='Teller Date', store=True,
                              track_visibility='onchange',readonly=True)
    teller_name = fields.Many2one(related='teller_id.teller_name', string='Teller Name',readonly=True,
                              store=True,track_visibility='onchange')

    # the idea is to link salesperson to customer's sales person
    partner_id = fields.Many2one('res.partner', string='Partner', change_default=True,
             required=True, readonly=True,store=True, states={'draft': [('readonly', False)]},
             track_visibility='always')
    user_id = fields.Many2one(related='partner_id.user_id',string='Salesperson', track_visibility='onchange',\
             readonly=True,store=True, states={'draft': [('readonly', False)]})


    def _teller_amount(self):
        self.teller_amount = self.teller_id.teller_amount

    _sql_constraints = [
        ('name_uniq', 'unique (teller_id,teller_name,teller_bank)', "Teller name/bank/id already exists !"),
    ]

"""
    # fields for derived bags
    nbags70 = fields.Float(compute='_compute_bags',  string='70 per Bag',readonly=True,
                              store=True,track_visibility='onchange')
    nbags75 = fields.Float(compute='_compute_bags', string='75 per Bag',readonly=True,
                              store=True,track_visibility='onchange')
    nbags85 = fields.Float(compute='_compute_bags',  string='85 per Bag',readonly=True,
                              store=True,track_visibility='onchange')
    nbags80 = fields.Float(compute='_compute_bags', string='80 per Bag',readonly=True,
                              store=True,track_visibility='onchange')
    nbags100 = fields.Float(compute='_compute_bags', string='100 per Bag',readonly=True,
                              store=True,track_visibility='onchange')

    product_name = fields.Float(compute='_compute_line', string='Product', readonly=True,
                           store=True, track_visibility='onchange')
"""

"""
    @api.one
    @api.depends('teller_amount')
    def _compute_bags(self):
        self.nbags70 = self.teller_amount / 70.0
        self.nbags75 = self.teller_amount / 75.0
        self.nbags80 = self.teller_amount / 80.0
        self.nbags85 = self.teller_amount / 85.0
        self.nbags100 = self.teller_amount / 100.0

    @api.one
    def _compute_line(self):
        item_obj = self.env['account.invoice']

        itemid = item_obj.search(['invoice_line_ids'])
        _logger.info("*** LOGGING Processing  account_invoice-obj %s", itemid)
        for item in itemid:
            print item
            _logger.info("*** LOGGING Processing  account_invoice-Line %s", item)

        self.product_name = self.invoice_line_ids[0].name
        self.product_qty = self.invoice_line_ids[0].quantity
        self.product_price = self.invoice_line_ids[0].price_unit
"""
from openerp import api, fields, models

class fido_teller(models.Model):
    _name = 'fido.teller'
    _description = 'Model Bank Tellers coming to Fido'
    # invoice_id = fields.One2many('fido.invoice', 'teller_id',string='Fido Invoice Reference')
    name = fields.Char(string='Teller Number',
                           required=True,store=True,help='Teller id')

    teller_name = fields.Many2one('res.partner', string='Name on Teller', required=True,
                store=True, domain="[('customer', '=', True)]")
    date = fields.Date(string='Teller Date', required=True, store=True,help="Teller Date.")
    teller_amount = fields.Float(string='Teller Amount', required=True,store=True,help='Teller Amount')
    bank = fields.Many2one('res.bank', string='Bank Name',required=True,store=True,help='Teller/POS Bank')

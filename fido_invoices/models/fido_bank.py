from openerp import api, fields, models
from openerp.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class fido_bank(models.Model):
    _name = 'fido.bank'
    _description = 'Model Nigerian Banks'

    name = fields.Char(string='Bank Name',required=True)
    contact = fields.Text(string='Contact Address')
    address = fields.Text(string='Branch Address')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Bank Name already exists !"),
    ]
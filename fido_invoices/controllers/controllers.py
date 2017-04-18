# -*- coding: utf-8 -*-
from odoo import http

# class FidoInvoices(http.Controller):
#     @http.route('/fido_invoices/fido_invoices/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fido_invoices/fido_invoices/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fido_invoices.listing', {
#             'root': '/fido_invoices/fido_invoices',
#             'objects': http.request.env['fido_invoices.fido_invoices'].search([]),
#         })

#     @http.route('/fido_invoices/fido_invoices/objects/<model("fido_invoices.fido_invoices"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fido_invoices.object', {
#             'object': obj
#         })
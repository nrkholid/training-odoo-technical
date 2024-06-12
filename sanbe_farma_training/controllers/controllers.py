# -*- coding: utf-8 -*-
# from odoo import http


# class SanbeFarmaTraining(http.Controller):
#     @http.route('/sanbe_farma_training/sanbe_farma_training', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sanbe_farma_training/sanbe_farma_training/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sanbe_farma_training.listing', {
#             'root': '/sanbe_farma_training/sanbe_farma_training',
#             'objects': http.request.env['sanbe_farma_training.sanbe_farma_training'].search([]),
#         })

#     @http.route('/sanbe_farma_training/sanbe_farma_training/objects/<model("sanbe_farma_training.sanbe_farma_training"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sanbe_farma_training.object', {
#             'object': obj
#         })


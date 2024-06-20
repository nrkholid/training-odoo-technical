from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Memberikan Nilai Default pada Field dengan Function Default Get
    def default_get(self, fields):
        result = super().default_get(fields)
        if 'user_id' in fields:
            result['salesperson_email'] = self.env.user.login
        return result

    salesperson_email = fields.Char('Salesperson Email')

    # Add New Logic then Execute Exist Function
    # def action_confirm(self):
        # New Logic Here
        # return super(SaleOrder, self).action_confirm()
    
    # Execute Exist Function then Add New Login
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        # New Logic Here
        self._send_message_to_customer()
        return res
    
    def _send_message_to_customer(self):
        message = "Send SO to Customer : {}".format(self.partner_id.name)
        self.message_post(body=message, partner_ids=self.partner_id.ids,
                          message_type='comment', subtype_xmlid='mail.mt_comment')
        return True
    
    @api.model
    def create(self, vals):
        if 'origin' in vals:
            vals['origin'] = 'Testing'
        return super(SaleOrder, self).create(vals)
    
    def write(self, vals):
        if 'origin' not in vals:
            vals['origin'] = 'Value'
        return super(SaleOrder, self).write(vals)
    
    def copy(self, default=None):
        return super(SaleOrder, self).copy(default)
    
    def unlink(self):
        if self.salesperson_email:
            raise ValidationError('Kamu tidak boleh menghapus Data ini')
        return super(SaleOrder, self).unlink()

    # Create New Logic
    # def action_confirm(self):
    #     return True

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Sale Order Line'
    
    # Overrider Compute then Add New Logic
    @api.depends('product_id')
    def _compute_name(self):
        for line in self:
            if not line.product_id:
                continue
            lang = line.order_id._get_lang()
            if lang != self.env.lang:
                line = line.with_context(lang=lang)
            name = line._get_sale_order_line_multiline_description_sale()
            if line.is_downpayment and not line.display_type:
                context = {'lang': lang}
                dp_state = line._get_downpayment_state()
                if dp_state == 'draft':
                    name = _("%(line_description)s (Draft)", line_description=name)
                elif dp_state == 'cancel':
                    name = _("%(line_description)s (Canceled)", line_description=name)
                else:
                    invoice = line._get_invoice_lines().move_id
                    if len(invoice) == 1 and invoice.payment_reference and invoice.invoice_date:
                        name = _(
                            "%(line_description)s (ref: %(reference)s on %(date)s)",
                            line_description=name,
                            reference=invoice.payment_reference,
                            date=format_date(line.env, invoice.invoice_date),
                        )
                del context
            line.name = name + " Testing"
    
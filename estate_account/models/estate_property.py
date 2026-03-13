from odoo import fields, models


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sell(self):
        invoice_vals_list = []
        for record in self:
            invoice_vals_list.append(
                {
                    "partner_id": record.buyer_id.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        fields.Command.create(
                            {
                                "name": "6% selling price",
                                "quantity": 1,
                                "price_unit": 0.06 * record.selling_price,
                            }
                        ),
                        fields.Command.create(
                            {
                                "name": "Administration fee",
                                "quantity": 1,
                                "price_unit": 100,
                            }
                        ),
                    ],
                }
            )

        self.env["account.move"].sudo().with_context(
            default_move_type="out_invoice"
        ).create(invoice_vals_list)

        return super().action_sell()

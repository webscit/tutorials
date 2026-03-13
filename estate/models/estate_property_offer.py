from datetime import timedelta

from odoo import api, exceptions, fields, models


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate property offer model"

    price = fields.Float("Price")
    status = fields.Selection(
        [("accepted", "Accepted"), ("refused", "Refused")], "Status", copy=False
    )
    partner_id = fields.Many2one("res.partner", "Buyer", required=True)
    property_id = fields.Many2one("estate.property", required=True)

    validity = fields.Integer("Validity (days)", default=7)
    date_deadline = fields.Date(
        "Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline"
    )

    _positive_price = models.Constraint(
        "CHECK(price > 0)", "An offer price must be strictly positive"
    )

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = (
                record.create_date.date() if record.create_date else fields.Date.today()
            ) + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (
                record.date_deadline - record.create_date.date()
                if record.create_date
                else fields.Date.today()
            ).days

    def action_accept(self):
        if len(self) > 1:
            raise exceptions.UserError("Only one offer can be accepted.")
        for record in self:
            record.status = "accepted"
            record.property_id.state = "offer_accepted"
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
        return True

    def action_refuse(self):
        for record in self:
            record.status = "refused"

        return True

    @api.model
    def create(self, vals_list):
        properties = [
            self.env["estate.property"].browse(record["property_id"])
            for record in vals_list
        ]
        if any(
            record["price"]
            < (min(r.price for r in property.offer_ids) if property.offer_ids else 0)
            for record, property in zip(vals_list, properties)
        ):
            raise exceptions.UserError("New offer cannot be lower than existing offer")

        for record in properties:
            if record.state == "new":
                record.state = "offer_received"

        return super().create(vals_list)

from datetime import timedelta

from odoo import api, exceptions, fields, models
from odoo.tools.float_utils import float_compare, float_is_zero


def _default_date_availability(*args):
    return fields.Date.today() + timedelta(days=365.25 / 4)


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate property model"

    name = fields.Char("Title", required=True)
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        copy=False,
        default="new",
    )

    description = fields.Text("Description")
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    property_tag_ids = fields.Many2many("estate.property.tag", string="Property Tags")

    postcode = fields.Char("Post Code")
    date_availability = fields.Date(
        "Available From", copy=False, default=_default_date_availability
    )
    expected_price = fields.Float("Expected Price", required=True)
    _positive_expected_price = models.Constraint(
        'CHECK(expected_price > 0)',
        'A property expected price must be strictly positive'
    )
    selling_price = fields.Float("Selling Price", readonly=True, copy=False)

    _positive_selling_price = models.Constraint(
        'CHECK(selling_price >= 0)',
        'A property selling price must be positive'
    )

    @api.constrains("expected_price", "selling_price")
    def _check_selling_price(self):
        for record in self:
            if not float_is_zero(self.selling_price, 2) and float_compare(self.selling_price / self.expected_price, 0.9, 4) < 0:
                raise exceptions.ValidationError("The selling price cannot be lower than 90% of the expected price.")

    bedrooms = fields.Integer("Bedrooms", default=2)
    living_area = fields.Integer("Living area (sqm)")
    facades = fields.Integer("# Facades")
    garage = fields.Boolean("Has a garage")
    garden = fields.Boolean("Has a graden")
    garden_area = fields.Integer("Garden area (sqm)")
    garden_orientation = fields.Selection(
        string="Garden orientation",
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
    )
    total_area = fields.Float("Total area (sqm)", compute="_compute_total_area")

    salesperson_id = fields.Many2one(
        "res.users", string="Salesperson", default=lambda self: self.env.user
    )
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)

    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    best_price = fields.Float("Best price", compute="_compute_best_price")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids")
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            record.best_price = max(prices) if prices else 0

    @api.onchange("garden")
    def _onchange_garden(self):
        self.garden_area = 10 if self.garden else 0
        self.garden_orientation = "north" if self.garden else ""

    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise exceptions.UserError("Sold property cannot be cancelled.")
            record.state = "cancelled"
        return True
    
    def action_sell(self):
        for record in self:
            if record.state == "cancelled":
                raise exceptions.UserError("Cancelled property cannot be sold.")
            record.state = "sold"
        return True

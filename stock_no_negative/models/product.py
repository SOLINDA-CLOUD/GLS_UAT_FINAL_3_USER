# Copyright 2015-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from email.policy import default
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    allow_negative_stock = fields.Boolean(
        help="Allow negative stock levels for the stockable products "
        "attached to this category. The options doesn't apply to products "
        "attached to sub-categories of this category.",
        string="Not Allowed Negative",
        readonly=True,
        default=False,
    )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_negative_stock = fields.Boolean(
        help="If this option is not active on this product nor on its "
        "product category and that this product is a stockable product, "
        "then the validation of the related stock moves will be blocked if "
        "the stock level becomes negative with the stock move.",
        string="Not Allowed Negative",
        readonly=True,
        default=False,
    )

class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    product_code = fields.Char(
        'PN',
        help="This vendor's product code will be used when printing a request for quotation. Keep empty to use the internal one.")

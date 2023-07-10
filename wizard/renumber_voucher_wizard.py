from odoo import api, exceptions, fields, models


class RenumberVoucherWizard(models.TransientModel):
    _name = "renumber.voucher.wizard"
    _description = "Renumber Voucher"

    word_id = fields.Many2one(
        "account.cn.voucher.word",
        required=True,
    )
    sequence_id = fields.Many2one(related="word_id.voucher_number_sequence_id")
    date_range_ids = fields.Many2many(
        "ir.sequence.date_range",
        required=True,
        domain="[('sequence_id', '=', sequence_id)]",
    )

    def renumber_voucher(self):
        pass

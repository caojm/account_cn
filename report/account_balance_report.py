import calendar
import datetime

from odoo import api, fields, models, _
from odoo.fields import Date
from odoo.tools import (
    date_utils,
    float_compare,
    float_is_zero,
    float_repr,
    format_amount,
    format_date,
    formatLang,
    get_lang,
)


class AccountBalanceReport(models.AbstractModel):
    _name = "report.account_cn.account_balance"
    _inherit = "account_cn.report.abstract"
    _description = "Account Balance"

    @api.model
    def _get_report_values(self, docids, data=None):
        if data["account_ids"]:
            accounts = self.env["account.account"].browse(data["account_ids"])
        else:
            accounts = self.env["account.account"].search([])
        max_account_code_length = data["max_account_code_length"]
        account_code_name = [
            (account.code, account.name)
            for account in accounts
            if len(account.code) <= max_account_code_length
        ]
        account_balance = self._generate_account_balance(
            data,
            account_code_name,
        )
        return {
            "data": data,
            "account_balance": account_balance,
        }

    def _get_voucher_data(
        self,
        data_type,
        company_ids,
        accounting_book_ids,
        account_code,
        exact_match,
        date_from,
        date_to,
        posted_only,
        distinguish_partner,
        partner_ids,
        voucher_type_ids,
        tag_ids,
    ):
        domain = [
            ("company_id", "in", company_ids),
            ("accounting_book_id", "in", accounting_book_ids),
        ]
        if data_type == "balance":
            domain += [("date", "<", date_from)]
        elif data_type == "amount":
            domain += [("date", ">=", date_from), ("date", "<=", date_to)]
        else:
            return False
        if exact_match:
            domain += [("account_id.code", "=", account_code)]
        else:
            domain += [("account_id.code", "=like", account_code + "%")]
        if posted_only:
            domain += [("voucher_state", "=", "posted")]
        if voucher_type_ids:
            domain += [("voucher_type_id", "in", voucher_type_ids)]
        if tag_ids:
            domain += [("tag_ids", "in", tag_ids)]

        fields = []
        groupby = []
        orderby = False
        if distinguish_partner:
            domain += [("partner_id", "in", partner_ids)]
            fields += ["partner_id"]
            groupby = ["partner_id"]
            orderby = "partner_id"
        else:
            groupby = ["company_id"]
        fields += [
            # "company_id",
            "debit:sum",
            "credit:sum",
        ]
        data = self.env["account.cn.voucher.line"].read_group(
            domain=domain,
            fields=fields,
            groupby=groupby,
            orderby=orderby,
            lazy=False,
        )
        return data

    def _generate_account_balance(self, data, accounts):
        account_balance = []
        total = {
            "account_code": False,
            "account_name": _("Total"),
            "partner_name": False,
            "opening_balance_debit": 0.0,
            "opening_balance_credit": 0.0,
            "this_amount_debit": 0.0,
            "this_amount_credit": 0.0,
            "year_amount_debit": 0.0,
            "year_amount_credit": 0.0,
            "closing_balance_debit": 0.0,
            "closing_balance_credit": 0.0,
        }
        for account in accounts:
            initial_balance_data = self._get_voucher_data(
                "balance",
                data["company_ids"],
                data["accounting_book_ids"],
                account[0],
                data["exact_match"],
                data["date_from"],
                data["date_to"],
                data["posted_only"],
                data["distinguish_partner"],
                data["partner_ids"],
                data["voucher_type_ids"],
                data["tag_ids"],
            )
            this_amount_data = self._get_voucher_data(
                "amount",
                data["company_ids"],
                data["accounting_book_ids"],
                account[0],
                data["exact_match"],
                data["date_from"],
                data["date_to"],
                data["posted_only"],
                data["distinguish_partner"],
                data["partner_ids"],
                data["voucher_type_ids"],
                data["tag_ids"],
            )
            year_amount_data = self._get_voucher_data(
                "amount",
                data["company_ids"],
                data["accounting_book_ids"],
                account[0],
                data["exact_match"],
                self._this_year_start(Date.to_date(data["date_to"])),
                data["date_to"],
                data["posted_only"],
                data["distinguish_partner"],
                data["partner_ids"],
                data["voucher_type_ids"],
                data["tag_ids"],
            )
            if initial_balance_data or this_amount_data:
                account_balance += self._make_account_balance(
                    data,
                    account,
                    initial_balance_data,
                    this_amount_data,
                    year_amount_data,
                )
                total["opening_balance_debit"] += account_balance[-1][
                    "opening_balance_debit"
                ]
                total["opening_balance_credit"] += account_balance[-1][
                    "opening_balance_credit"
                ]
                total["this_amount_debit"] += account_balance[-1]["this_amount_debit"]
                total["this_amount_credit"] += account_balance[-1]["this_amount_credit"]
                total["year_amount_debit"] += account_balance[-1]["year_amount_debit"]
                total["year_amount_credit"] += account_balance[-1]["year_amount_credit"]
                total["closing_balance_debit"] += account_balance[-1][
                    "closing_balance_debit"
                ]
                total["closing_balance_credit"] += account_balance[-1][
                    "closing_balance_credit"
                ]
            else:
                continue
        account_balance += [total]
        return account_balance

    def _make_account_balance(
        self,
        data,
        account_code_name,
        initial_balance_data,
        this_amount_data,
        year_amount_data,
    ):
        if data["distinguish_partner"]:
            account_balance = []
            partner_total = {
                "account_code": False,
                "account_name": False,
                "partner_name": _("Partner total"),
                "opening_balance_debit": 0.0,
                "opening_balance_credit": 0.0,
                "this_amount_debit": 0.0,
                "this_amount_credit": 0.0,
                "year_amount_debit": 0.0,
                "year_amount_credit": 0.0,
                "closing_balance_debit": 0.0,
                "closing_balance_credit": 0.0,
            }
            for partner_id in data["partner_ids"]:
                item = {
                    "account_code": account_code_name[0],
                    "account_name": account_code_name[1],
                    "partner_name": False,
                    "opening_balance_debit": 0.0,
                    "opening_balance_credit": 0.0,
                    "this_amount_debit": 0.0,
                    "this_amount_credit": 0.0,
                    "year_amount_debit": 0.0,
                    "year_amount_credit": 0.0,
                    "closing_balance_debit": 0.0,
                    "closing_balance_credit": 0.0,
                }
                item["partner_name"] = self.env["res.partner"].browse([partner_id]).name
                item["opening_balance_debit"] = sum(
                    map(
                        lambda x: x["debit"],
                        filter(
                            lambda y: y["partner_id"][0] == partner_id,
                            initial_balance_data,
                        ),
                    )
                )
                item["opening_balance_credit"] = sum(
                    map(
                        lambda x: x["credit"],
                        filter(
                            lambda y: y["partner_id"][0] == partner_id,
                            initial_balance_data,
                        ),
                    )
                )
                opening_balance_net = (
                    item["opening_balance_debit"] - item["opening_balance_credit"]
                )
                if opening_balance_net > 0:
                    item["opening_balance_debit"] = opening_balance_net
                    item["opening_balance_credit"] = 0.0
                elif opening_balance_net < 0:
                    item["opening_balance_debit"] = 0.0
                    item["opening_balance_credit"] = -opening_balance_net
                else:
                    item["opening_balance_debit"] = 0.0
                    item["opening_balance_credit"] = 0.0

                item["this_amount_debit"] = sum(
                    map(
                        lambda x: x["debit"],
                        filter(
                            lambda y: y["partner_id"][0] == partner_id,
                            this_amount_data,
                        ),
                    )
                )
                item["this_amount_credit"] = sum(
                    map(
                        lambda x: x["credit"],
                        filter(
                            lambda y: y["partner_id"][0] == partner_id,
                            this_amount_data,
                        ),
                    )
                )
                item["year_amount_debit"] = sum(
                    map(
                        lambda x: x["debit"],
                        filter(
                            lambda y: y["partner_id"][0] == partner_id,
                            year_amount_data,
                        ),
                    )
                )
                item["year_amount_credit"] = sum(
                    map(
                        lambda x: x["credit"],
                        filter(
                            lambda y: y["partner_id"][0] == partner_id,
                            year_amount_data,
                        ),
                    )
                )

                closing_balance_net = (
                    opening_balance_net
                    + item["this_amount_debit"]
                    - item["this_amount_credit"]
                )
                if closing_balance_net > 0:
                    item["closing_balance_debit"] = closing_balance_net
                    item["closing_balance_credit"] = 0.0
                elif closing_balance_net < 0:
                    item["closing_balance_debit"] = 0.0
                    item["closing_balance_credit"] = -closing_balance_net
                else:
                    item["closing_balance_debit"] = 0.0
                    item["closing_balance_credit"] = 0.0

                partner_total["opening_balance_debit"] += item["opening_balance_debit"]
                partner_total["opening_balance_credit"] += item[
                    "opening_balance_credit"
                ]
                partner_total["this_amount_debit"] += item["this_amount_debit"]
                partner_total["this_amount_credit"] += item["this_amount_credit"]
                partner_total["year_amount_debit"] += item["year_amount_debit"]
                partner_total["year_amount_credit"] += item["year_amount_credit"]
                partner_total["closing_balance_debit"] += item["closing_balance_debit"]
                partner_total["closing_balance_credit"] += item[
                    "closing_balance_credit"
                ]

                account_balance.append(item)
            account_balance.append(partner_total)
            return account_balance
        else:
            item = {
                "account_code": account_code_name[0],
                "account_name": account_code_name[1],
                "opening_balance_debit": 0.0,
                "opening_balance_credit": 0.0,
                "this_amount_debit": 0.0,
                "this_amount_credit": 0.0,
                "year_amount_debit": 0.0,
                "year_amount_credit": 0.0,
                "closing_balance_debit": 0.0,
                "closing_balance_credit": 0.0,
            }
            item["opening_balance_debit"] = sum(
                map(lambda x: x["debit"], initial_balance_data)
            )
            item["opening_balance_credit"] = sum(
                map(lambda x: x["credit"], initial_balance_data)
            )
            opening_balance_net = (
                item["opening_balance_debit"] - item["opening_balance_credit"]
            )
            if opening_balance_net > 0:
                item["opening_balance_debit"] = opening_balance_net
                item["opening_balance_credit"] = 0.0
            elif opening_balance_net < 0:
                item["opening_balance_debit"] = 0.0
                item["opening_balance_credit"] = -opening_balance_net
            else:
                item["opening_balance_debit"] = 0.0
                item["opening_balance_credit"] = 0.0

            item["this_amount_debit"] = sum(map(lambda x: x["debit"], this_amount_data))
            item["this_amount_credit"] = sum(
                map(lambda x: x["credit"], this_amount_data)
            )
            item["year_amount_debit"] = sum(map(lambda x: x["debit"], year_amount_data))
            item["year_amount_credit"] = sum(
                map(lambda x: x["credit"], year_amount_data)
            )

            closing_balance_net = (
                opening_balance_net
                + item["this_amount_debit"]
                - item["this_amount_credit"]
            )
            if closing_balance_net > 0:
                item["closing_balance_debit"] = closing_balance_net
                item["closing_balance_credit"] = 0.0
            elif closing_balance_net < 0:
                item["closing_balance_debit"] = 0.0
                item["closing_balance_credit"] = -closing_balance_net
            else:
                item["closing_balance_debit"] = 0.0
                item["closing_balance_credit"] = 0.0

            return [item]

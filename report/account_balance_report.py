from odoo import api, fields, models, _
from odoo.fields import Date


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
        account_code_name = {
            account.code: account.name
            for account in accounts
            if len(account.code) <= max_account_code_length
        }
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
        data,
        account_code_name,
        date_from,
        date_to,
        data_type,
    ):
        domain = [
            ("company_id", "in", data["company_ids"]),
            ("accounting_book_id", "in", data["accounting_book_ids"]),
        ]
        if data_type == "balance":
            domain += [("date", "<", date_from)]
        elif data_type == "amount":
            domain += [
                ("date", ">=", date_from),
                ("date", "<=", date_to),
            ]
        else:
            return False
        if data["posted_only"]:
            domain += [("voucher_state", "=", "posted")]
        if data["voucher_type_ids"]:
            domain += [("voucher_type_id", "in", data["voucher_type_ids"])]
        if data["tag_ids"]:
            domain += [("tag_ids", "in", data["tag_ids"])]

        fields = ["account_code"]
        groupby = ["account_code"]
        orderby = "account_code"
        if data["distinguish_partner"]:
            domain += [("partner_id", "in", data["partner_ids"])]
            fields += ["partner_id"]
            groupby += ["partner_id"]
            orderby += ", partner_id"
        fields += [
            "debit:sum",
            "credit:sum",
        ]
        if data["exact_match"]:
            account_code = list(account_code_name.keys())
            domain += [("account_code", "in", account_code)]
        else:
            account_code = self._filter_account_code(account_code_name)
            if len(account_code) == 1:
                domain += [("account_code", "=like", account_code[0] + "%")]
            else:
                for acc in account_code[:-1]:
                    domain += ["|", ("account_code", "=like", acc + "%")]
                domain += [("account_code", "=like", account_code[-1] + "%")]
        data = self.env["account.cn.voucher.line"].read_group(
            domain=domain,
            fields=fields,
            groupby=groupby,
            orderby=orderby,
            lazy=False,
        )
        return data

    def _filter_account_code(self, account_code_name):
        account_code = sorted(account_code_name.keys())
        account_code_yes = set()
        account_code_no = set()
        for ac in account_code:
            find_parent = False
            for i in range(1, len(ac)):
                if ac[:-i] in account_code_yes or ac[:-i] in account_code_no:
                    find_parent = True
                    account_code_no.add(ac)
                    break
                else:
                    continue
            if not find_parent:
                account_code_yes.add(ac)
        return sorted(account_code_yes)

    def _generate_account_balance(self, data, account_code_name):
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
        initial_balance_data = self._get_voucher_data(
            data,
            account_code_name,
            data["date_from"],
            data["date_to"],
            "balance",
        )
        this_amount_data = self._get_voucher_data(
            data,
            account_code_name,
            data["date_from"],
            data["date_to"],
            "amount",
        )
        year_amount_data = self._get_voucher_data(
            data,
            account_code_name,
            self._this_year_start(Date.to_date(data["date_to"])),
            data["date_from"],
            "amount",
        )

        account_code = sorted(account_code_name.keys())
        for ac in account_code:
            is_starts_with = lambda x: x["account_code"].startswith(ac)
            initial_balance_data_filtered = list(
                filter(is_starts_with, initial_balance_data)
            )
            this_amount_data_filtered = list(filter(is_starts_with, this_amount_data))
            year_amount_data_filtered = list(filter(is_starts_with, year_amount_data))
            if initial_balance_data_filtered or this_amount_data_filtered:
                account_balance += self._make_account_balance(
                    data,
                    (ac, account_code_name[ac]),
                    initial_balance_data_filtered,
                    this_amount_data_filtered,
                    year_amount_data_filtered,
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
            partners = {
                p.id: p.name
                for p in self.env["res.partner"].browse(data["partner_ids"])
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
                item["partner_name"] = partners[partner_id]
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

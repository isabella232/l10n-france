# -*- coding: utf-8 -*-
###############################################################################
#
#   account_statement_paybox for OpenERP
#   Copyright (C) 2013-TODAY Akretion <http://www.akretion.com>.
#   @author Florian DA COSTA <florian.dacosta@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.tools.translate import _
import datetime
from account_statement_base_import.parser.file_parser import FileParser
from csv import Dialect
from _csv import QUOTE_MINIMAL, register_dialect
from openerp.osv import osv 

def float_or_zero(val):
    """ Conversion function used to manage
    empty string into float usecase"""
    val = val.strip()
    return (float(val.replace(',', '.')) if val else 0.0)

def format_date(val):
    if '/' in val:
        return datetime.datetime.strptime(val, "%d/%m/%Y")
    else:
        return datetime.datetime.strptime(val, "%Y-%m-%d")

class paybox_dialect(Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = ';'
    quotechar = '"'
    doublequote = False
    skipinitialspace = True
    lineterminator = '\n'
    quoting = QUOTE_MINIMAL
register_dialect("paybox_dialect", paybox_dialect)


class PayboxFileParser(FileParser):
    """
    Standard parser that use a define format in csv or xls to import into a
    bank statement. This is mostely an example of how to proceed to create a new
    parser.
    """

    def __init__(self, parse_name, ftype='csv'):
        conversion_dict = {
            "Type": unicode,
            "EmailCustomer": unicode,
            "RemittancePaybox": unicode,
            "Date": format_date,
            "IdAppel": unicode,
            "Reference": unicode,
            "ShopName": unicode,
            "Amount": float_or_zero,
        }
        self.refund_amount = None
        super(PayboxFileParser,self).__init__(parse_name, ftype=ftype,
                                           extra_fields=conversion_dict,
                                           dialect=paybox_dialect)

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == 'paybox_csvparser'

    def _custom_format(self, *args, **kwargs):
        self.filebuffer = self.filebuffer.decode('iso-8859-15')
        #encode in utf-8
        self.filebuffer = self.filebuffer.encode('utf-8')

    def _pre(self, *args, **kwargs):
        split_file = self.filebuffer.split("\n")
        selected_lines = []
        for line in split_file:
            selected_lines.append(line.strip())
        self.filebuffer = "\n".join(selected_lines)

    def get_st_line_vals(self, line, *args, **kwargs):
        """
        This method must return a dict of vals that can be passed to create
        method of statement line in order to record it. It is the responsibility
        of every parser to give this dict of vals, so each one can implement his
        own way of recording the lines.
            :param:  line: a dict of vals that represent a line of result_row_list
            :return: dict of values to give to the create method of statement line,
                     it MUST contain at least:
                {
                    'name':value,
                    'date':value,
                    'amount':value,
                    'ref':value,
                    'label':value,
                    'commission_amount':value,
                }
        In this generic parser, the commission is given for every line, so we store it
        for each one.
        """
        #fill the statement name
        self.statement_name = line['RemittancePaybox']

        res = {
            'name': line["Reference"],
            'date': line["Date"],
            'amount': line['Amount'] / 100,
            'ref': '/',
            'transaction_id': line["IdAppel"],
            'label': line["Type"],
        }
        return res

    def _post(self, *args, **kwargs):
        """
        Compute the total transfer amount
        """
        res = super(PayboxFileParser, self)._post(*args, **kwargs)
        rows = []
        for row in self.result_row_list:
            if row['Type'] in ('ANU'):
               continue
            rows.append(row)
            if row['Type'] == 'CRE':
                row["Amount"] = - row["Amount"]
            elif row['Type'] == 'DEB':
                continue
            else:
                raise osv.except_osv(_("User Error"),
                    _("The bank statement imported have invalide line,"
                    " indeed the operation type %s is not supported"
                    )%row['Type'])
        self.result_row_list = rows
        self.statement_date = self.result_row_list[0]["Date"]
        return res

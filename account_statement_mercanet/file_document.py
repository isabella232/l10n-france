# -*- coding: utf-8 -*-
###############################################################################
#
#   account_statement_mercanet for OpenERP
#   Copyright (C) 2012-TODAY Akretion <http://www.akretion.com>.
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
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

from openerp.osv import orm, fields
import base64
SUBJECT_TO_PROCESS = [
    u'liste des paiements trait\xe9s',
    u"liste des operations effectu\xe9es",
]

EMAIL_FROM = u"so_send_journal_fond@sips-atos.com" 

class file_document(orm.Model):
    _inherit = "file.document"

    def _prepare_data_for_file_document(self, cr, uid, msg, context=None):
        print msg['subject']
        res = super(file_document, self).\
                _prepare_data_for_file_document(cr, uid, msg, context=context)
        if msg['from'] == EMAIL_FROM and msg['subject'] in SUBJECT_TO_PROCESS:
            vals = {
                'name': msg['subject'],
                'direction': 'input',
                'date': msg['date'],
                'ext_id': msg['message-id'],
                'datas_fname': msg['attachments'][0][0],
                'datas': base64.b64encode(msg['attachments'][0][1]),
            }
            res.append(vals)
        return res

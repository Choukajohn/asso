'''
diacamma.event package

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2016 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals
from datetime import date

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.editors import LucteriosEditor
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.tools import FORMTYPE_REFRESH, CLOSE_NO

from diacamma.accounting.models import CostAccounting, FiscalYear
from diacamma.member.models import Activity


class DegreeEditor(LucteriosEditor):

    def edit(self, xfer):
        xfer.change_to_readonly('adherent')


class ParticipantEditor(LucteriosEditor):

    def edit(self, xfer):
        xfer.change_to_readonly('contact')
        xfer.get_components('article').set_action(xfer.request, xfer.get_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        if xfer.item.article_id is None:
            xfer.remove_component('reduce')
        if xfer.item.event.event_type == 0:
            xfer.remove_component('comment')


class EventEditor(LucteriosEditor):

    def before_save(self, xfer):
        if self.item.activity_id is None:
            activities = Activity.objects.all()
            if len(activities) == 0:
                raise LucteriosException(IMPORTANT, _('No activity!'))
            self.item.activity = activities[0]

    def edit(self, xfer):
        xfer.change_to_readonly('status')
        date_end = xfer.get_components('date_end')
        date_end.set_needed(True)
        if date_end.value is None:
            date_end.value = date.today()
        event_type = xfer.get_components('event_type')
        event_type.java_script = """
var type=current.getValue();
parent.get('date_end').setVisible(type==1);
"""
        xfer.get_components('default_article').set_action(xfer.request, xfer.get_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        if xfer.item.default_article_id is None:
            xfer.remove_component('cost_accounting')
        else:
            comp = xfer.get_components("cost_accounting")
            comp.set_needed(False)
            comp.set_select_query(CostAccounting.objects.filter(Q(status=0) & (Q(year=None) | Q(year=FiscalYear.get_current()))))
            if xfer.item.id is not None:
                comp.set_value(xfer.item.cost_accounting_id)
            else:
                cost_acc = CostAccounting.objects.filter(is_default=True)
                if len(cost_acc) > 0:
                    comp.set_value(cost_acc[0].id)
                else:
                    comp.set_value(0)

    def show(self, xfer):
        participant = xfer.get_components('participant')
        participant.change_type_header('is_subscripter', 'bool')
        if self.item.status == 0:
            participant.delete_header('degree_result_simple')
            participant.delete_header('subdegree_result')
            if self.item.event_type == 0:
                participant.delete_header('comment')
        else:
            participant.delete_header('current_degree')
        img = xfer.get_components('img')
        if self.item.event_type == 1:
            participant.delete_header('degree_result_simple')
            participant.delete_header('subdegree_result')
            participant.delete_header('current_degree')
            xfer.caption = _("Show trainning/outing")
            img.set_value("/static/diacamma.event/images/outing.png")
        else:
            xfer.caption = _("Show examination")
            xfer.remove_component('date_end')
            img.set_value("/static/diacamma.event/images/degree.png")
        if xfer.item.default_article_id is None:
            xfer.remove_component('cost_accounting')

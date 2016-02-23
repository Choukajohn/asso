# -*- coding: utf-8 -*-
'''
diacamma.event view module

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

from django.utils.translation import ugettext_lazy as _
from django.utils import six

from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.xfersearch import XferSearchEditor
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage,\
    SELECT_MULTI, CLOSE_NO, FORMTYPE_MODAL, WrapAction, CLOSE_YES
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompImage,\
    XferCompSelect, XferCompMemo
from lucterios.CORE.xferprint import XferPrintAction
from lucterios.CORE.parameters import Params
from lucterios.contacts.tools import ContactSelection
from lucterios.contacts.models import Individual

from diacamma.member.views import AdherentSelection

from diacamma.event.models import Event, Organizer, Participant

MenuManage.add_sub("event.actions", "association", "diacamma.event/images/formation.png",
                   _("Events"), _("Management of events."), 80)


@ActionsManage.affect('Event', 'list')
@MenuManage.describ('event.change_event', FORMTYPE_NOMODAL, 'event.actions', _('Examination manage'))
class EventList(XferListEditor):
    icon = "formation.png"
    model = Event
    field_id = 'event'
    caption = _("Examination")


@ActionsManage.affect('Event', 'search')
@MenuManage.describ('event.change_event', FORMTYPE_NOMODAL, 'event.actions', _('To find an examination'))
class EventSearch(XferSearchEditor):
    icon = "formation.png"
    model = Event
    field_id = 'event'
    caption = _("Search examination")


@ActionsManage.affect('Event', 'edit', 'modify', 'add')
@MenuManage.describ('event.add_event')
class EventAddModify(XferAddEditor):
    icon = "formation.png"
    model = Event
    field_id = 'event'
    caption_add = _("Add examination")
    caption_modify = _("Modify examination")


@ActionsManage.affect('Event', 'show')
@MenuManage.describ('event.change_event')
class EventShow(XferShowEditor):
    icon = "formation.png"
    model = Event
    field_id = 'event'
    caption = _("Show examination")

    def fillresponse(self):
        if self.item.status == 0:
            self.action_list.insert(
                0, ('valid', _("Validation"), "images/ok.png", CLOSE_NO))
        else:
            del self.action_list[0]
        XferShowEditor.fillresponse(self)


@ActionsManage.affect('Event', 'valid')
@MenuManage.describ('event.add_event')
class EventValid(XferContainerAcknowledge):
    icon = "formation.png"
    model = Event
    field_id = 'event'
    caption = _("Validation of an examination")

    def fillresponse(self):
        self.item.can_be_valid()
        if self.getparam('SAVE') is None:
            dlg = self.create_custom()
            dlg.item = self.item
            img = XferCompImage('img')
            img.set_value(self.icon_path())
            img.set_location(0, 0, 1, 3)
            dlg.add_component(img)
            lbl = XferCompLabelForm('title')
            lbl.set_value_as_title(self.caption)
            lbl.set_location(1, 0, 6)
            dlg.add_component(lbl)
            dlg.fill_from_model(1, 1, True, ['activity', 'date'])
            lbl = XferCompLabelForm('sep')
            lbl.set_value("{[hr/]}")
            lbl.set_location(0, 4, 7)
            dlg.add_component(lbl)
            row_id = 5
            for participant in self.item.participant_set.all():
                lbl = XferCompLabelForm('name_%d' % participant.id)
                lbl.set_value_as_name(six.text_type(participant))
                lbl.set_location(0, row_id)
                dlg.add_component(lbl)

                lbl = XferCompLabelForm('current_%d' % participant.id)
                lbl.set_value(participant.current_degree)
                lbl.set_location(1, row_id)
                dlg.add_component(lbl)

                sel = XferCompSelect('degree_%d' % participant.id)
                sel.set_select_query(participant.allow_degree())
                sel.set_location(2, row_id)
                dlg.add_component(sel)

                if Params.getvalue("event-subdegree-enable") == 1:
                    sel = XferCompSelect('subdegree_%d' % participant.id)
                    sel.set_select_query(participant.allow_subdegree())
                    sel.set_location(3, row_id)
                    dlg.add_component(sel)

                edt = XferCompMemo('comment_%d' % participant.id)
                edt.set_value(participant.comment)
                edt.set_location(4, row_id)
                dlg.add_component(edt)

                row_id += 1
            dlg.add_action(self.get_action(
                _('Ok'), "images/ok.png"), {'close': CLOSE_YES, 'params': {'SAVE': 'YES'}})
            dlg.add_action(WrapAction(_('Cancel'), 'images/cancel.png'), {})
        else:
            if self.item.status == 0:
                for participant in self.item.participant_set.all():
                    participant.give_result(self.getparam('degree_%d' % participant.id, 0),
                                            self.getparam(
                                                'subdegree_%d' % participant.id, 0),
                                            self.getparam('comment_%d' % participant.id, ''))
                self.item.status = 1
                self.item.save()


@ActionsManage.affect('Event', 'delete')
@MenuManage.describ('event.delete_event')
class EventDel(XferDelete):
    icon = "formation.png"
    model = Event
    field_id = 'event'
    caption = _("Delete examination")


@ActionsManage.affect('Event', 'print')
@MenuManage.describ('event.change_event')
class EventPrint(XferPrintAction):
    icon = "formation.png"
    model = Event
    field_id = 'event'
    caption = _("Print event")
    action_class = EventShow


@MenuManage.describ('event.add_event')
class OrganizerSave(XferContainerAcknowledge):
    icon = "formation.png"
    model = Organizer
    field_id = 'organizer'
    caption_add = _("Add organizer")

    def fillresponse(self, event, pkname=''):
        contact_ids = self.getparam(pkname)
        for contact_id in contact_ids.split(';'):
            Organizer.objects.get_or_create(
                event_id=event, contact_id=contact_id)


@ActionsManage.affect('Organizer', 'add')
@MenuManage.describ('event.add_event')
class OrganizerAddModify(ContactSelection):
    icon = "formation.png"
    caption = _("Add organizer")
    mode_select = SELECT_MULTI
    select_class = OrganizerSave
    inital_model = Individual


@ActionsManage.affect('Organizer', 'delete')
@MenuManage.describ('event.add_event')
class OrganizerDel(XferDelete):
    icon = "formation.png"
    model = Organizer
    field_id = 'organizer'
    caption = _("Delete organizer")


@ActionsManage.affect('Organizer', 'responsible')
@MenuManage.describ('event.add_event')
class OrganizerResponsible(XferContainerAcknowledge):
    icon = "formation.png"
    model = Organizer
    field_id = 'organizer'
    caption = _("Responsible")

    def fillresponse(self):
        self.item.set_has_responsible()


@MenuManage.describ('event.add_event')
class ParticipantSave(XferContainerAcknowledge):
    icon = "formation.png"
    model = Participant
    field_id = 'participant'
    caption_add = _("Add participant")

    def fillresponse(self, event, adherent=()):
        for contact_id in adherent:
            Participant.objects.get_or_create(
                event_id=event, contact_id=contact_id)


@ActionsManage.affect('Participant', 'show')
@MenuManage.describ('event.change_event')
class ParticipantOpen(XferContainerAcknowledge):
    icon = "formation.png"
    model = Participant
    field_id = 'participant'
    caption_add = _("Add participant")

    def fillresponse(self):
        current_contact = self.item.contact.get_final_child()
        modal_name = current_contact.__class__.__name__
        field_id = modal_name.lower()
        self.redirect_action(ActionsManage.get_act_changed(modal_name, 'show', '', ''), {
                             'modal': FORMTYPE_MODAL, 'close': CLOSE_NO, 'params': {field_id: six.text_type(current_contact.id)}})


@ActionsManage.affect('Participant', 'add')
@MenuManage.describ('event.add_event')
class ParticipantAddModify(AdherentSelection):
    icon = "formation.png"
    caption = _("Add participant")
    mode_select = SELECT_MULTI
    select_class = ParticipantSave


@ActionsManage.affect('Participant', 'delete')
@MenuManage.describ('event.add_event')
class ParticipantDel(XferDelete):
    icon = "formation.png"
    model = Participant
    field_id = 'participant'
    caption = _("Delete participant")

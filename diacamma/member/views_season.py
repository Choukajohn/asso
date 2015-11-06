# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage,\
    SELECT_SINGLE, FORMTYPE_REFRESH, CLOSE_NO
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompSelect

from diacamma.member.models import Season, Period, Subscription, Document

MenuManage.add_sub("member.conf", "core.extensions", "", _("Member"), "", 5)


@MenuManage.describ('member.change_season', FORMTYPE_NOMODAL, 'member.conf', _('Management of seasons and subscriptions'))
class SeasonSubscription(XferListEditor):
    icon = "season.png"
    model = Season
    field_id = 'season'
    caption = _("Seasons and subscriptions")

    def fillresponse_header(self):
        self.action_grid.append(
            ('active', _("Active"), "images/ok.png", SELECT_SINGLE))
        self.new_tab(_('Season'))
        show_filter = self.getparam('show_filter', 0)
        lbl = XferCompLabelForm('lbl_showing')
        lbl.set_value_as_name(_('Show season'))
        lbl.set_location(0, 3)
        self.add_component(lbl)
        edt = XferCompSelect("show_filter")
        edt.set_select([(0, _('Near active')), (1, _('All'))])
        edt.set_value(show_filter)
        edt.set_location(1, 3)
        edt.set_action(self.request, self.get_action(),
                       {'modal': FORMTYPE_REFRESH, 'close': CLOSE_NO})
        self.add_component(edt)
        self.filter = Q()
        if show_filter == 0:
            try:
                year_ref = Season.current_season().reference_year
                designation_begin = "%d/%d" % (year_ref - 2, year_ref - 1)
                designation_end = "%d/%d" % (year_ref + 2, year_ref + 3)
                self.filter = Q(designation__gte=designation_begin) & Q(
                    designation__lte=designation_end)
            except:
                pass

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        self.new_tab(_('Subscriptions'))
        self.fill_grid(
            self.get_max_row(), Subscription, "subscription", Subscription.objects.all())


@ActionsManage.affect('Season', 'active')
@MenuManage.describ('member.change_season')
class SeasonActive(XferContainerAcknowledge):
    icon = "season.png"
    model = Season
    field_id = 'season'
    caption = _("Activate")

    def fillresponse(self):
        self.item.set_has_actif()


@ActionsManage.affect('Season', 'add')
@MenuManage.describ('member.add_season')
class SeasonAddModify(XferAddEditor):
    icon = "season.png"
    model = Season
    field_id = 'season'
    caption_add = _("Add season")
    caption_modify = _("Modify season")


@ActionsManage.affect('Season', 'show')
@MenuManage.describ('member.change_season')
class SeasonShow(XferShowEditor):
    icon = "season.png"
    model = Season
    field_id = 'season'
    caption = _("Show season")

    def fillresponse(self):
        XferShowEditor.fillresponse(self)
        self.add_action(SeasonDocummentClone.get_action(
            _('Import doc.'), 'images/ok.png'), {'close': CLOSE_NO}, 0)


@ActionsManage.affect('Document', 'add', 'edit')
@MenuManage.describ('member.change_season')
class DocummentAddModify(XferAddEditor):
    icon = "season.png"
    model = Document
    field_id = 'document'
    caption_add = _("Add document")
    caption_modify = _("Modify document")


@ActionsManage.affect('Document', 'delete')
@MenuManage.describ('member.change_season')
class DocummentDel(XferDelete):
    icon = "season.png"
    model = Document
    field_id = 'document'
    caption = _("Delete document")


@MenuManage.describ('member.change_season')
class SeasonDocummentClone(XferContainerAcknowledge):
    icon = "season.png"
    model = Season
    field_id = 'season'
    caption = _("Clone document")

    def fillresponse(self):
        self.item.clone_doc_need()


@ActionsManage.affect('Period', 'edit', 'modify', 'add')
@MenuManage.describ('member.add_season')
class PeriodAddModify(XferAddEditor):
    icon = "season.png"
    model = Period
    field_id = 'period'
    caption_add = _("Add period")
    caption_modify = _("Modify period")


@ActionsManage.affect('Period', 'delete')
@MenuManage.describ('member.add_season')
class PeriodDel(XferDelete):
    icon = "season.png"
    model = Period
    field_id = 'period'
    caption = _("Delete period")


@ActionsManage.affect('Subscription', 'edit', 'modify', 'add')
@MenuManage.describ('member.add_subscription')
class SubscriptionAddModify(XferAddEditor):
    icon = "season.png"
    model = Subscription
    field_id = 'subscription'
    caption_add = _("Add subscription")
    caption_modify = _("Modify subscription")


@ActionsManage.affect('Subscription', 'show')
@MenuManage.describ('member.change_subscription')
class SubscriptionShow(XferShowEditor):
    icon = "season.png"
    model = Subscription
    field_id = 'subscription'
    caption = _("Show subscription")


@ActionsManage.affect('Subscription', 'delete')
@MenuManage.describ('member.delete_subscription')
class SubscriptionDel(XferDelete):
    icon = "season.png"
    model = Subscription
    field_id = 'subscription'
    caption = _("Delete subscription")

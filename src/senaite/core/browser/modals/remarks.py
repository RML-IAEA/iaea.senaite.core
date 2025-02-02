# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.api.security import check_permission
from bika.lims.permissions import FieldEditAnalysisRemarks
from Products.Archetypes.event import ObjectEditedEvent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core import logger
from senaite.core.browser.modals import Modal
from zope import event


class SetAnalysisRemarksModal(Modal):
    template = ViewPageTemplateFile("templates/set_analysis_remarks.pt")

    def __init__(self, context, request):
        super(SetAnalysisRemarksModal, self).__init__(context, request)

    def __call__(self):
        if self.request.form.get("submitted", False):
            self.handle_submit(REQUEST=self.request)
        return self.template()

    def handle_submit(self, REQUEST=None):
        analyses = map(api.get_object_by_uid, self.uids)
        remarks = self.request.get("remarks")
        overwrite = self.request.form.get("overwrite") or False
        for analysis in analyses:
            self.set_remarks_for(analysis, remarks, overwrite=overwrite)

    def set_remarks_for(self, analysis, remarks, overwrite=True):
        """Set the remarks on the given analyses
        """
        logger.info("Set remarks for analysis '{}' to {}"
                    .format(analysis.getId(), remarks))
        if not check_permission(FieldEditAnalysisRemarks, analysis):
            logger.warn("Not allowed to set remarks for {}"
                        .format(analysis.getId()))
            return False
        if not overwrite:
            remarks = "{}\n{}".format(analysis.getRemarks(), remarks)
        analysis.setRemarks(api.safe_unicode(remarks))
        analysis.reindexObject()
        event.notify(ObjectEditedEvent(analysis))
        return True

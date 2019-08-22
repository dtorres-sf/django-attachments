from __future__ import unicode_literals

import os

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.urls import reverse
from django.utils.translation import ugettext
from django.views.decorators.http import require_POST
from annoying.decorators import ajax_request
from .forms import AttachmentForm
from .models import Attachment
from django.template.loader import render_to_string
from settings.models import AttachmentGroup
import logging

logger = logging.getLogger(__name__)

def add_url_for_obj(obj):
    return reverse(
        'attachments:add',
        kwargs={
            'app_label': obj._meta.app_label,
            'model_name': obj._meta.model_name,
            'pk': obj.pk,
        },
    )


def remove_file_from_disk(f):
    if getattr(
        settings, 'DELETE_ATTACHMENTS_FROM_DISK', False
    ) and os.path.exists(f.path):
        try:
            os.remove(f.path)
        except OSError:
            pass


@require_POST
@login_required
@ajax_request
def add_attachment(
    request,
    app_label,
    model_name,
    pk,
    template_name='attachments/add.html',
    extra_context=None,
):
    next_ = request.POST.get('next', '/')

    if not request.user.has_perm('attachments.add_attachment'):
        return {"success": False, "reason": "insufficient permissions"}

    model = apps.get_model(app_label, model_name)
    obj = get_object_or_404(model, pk=pk)
    form = AttachmentForm(request.POST, request.FILES)

    if form.is_valid():
        attachment = form.save(request, obj)
        name = form.cleaned_data["tags"] or None
        fa_icon = "fa-paperclip"
        if(name):
            # Get the first tag (there should really only ever be one tag)
            ag = AttachmentGroup.objects.filter(name=name[0]).first()
            fa_icon = ag.icon if ag else "fa-paperclip"

        context = {
            "attachment": attachment,
            "fa_icon": fa_icon,
        }
        html = render_to_string("attachments/attachment.html", context, request)
        return {"success": True, "html": html}
    logger.error("Error adding attachment {}".format(form.errors))
    template_context = {
        'form': form,
        'form_url': add_url_for_obj(obj),
        'next': next,
    }
    if(extra_context):
        template_context.update(extra_context)
    return {"success": False, "reason": "invalid form"}

@login_required
@ajax_request
def delete_attachment(request, attachment_pk):
    g = get_object_or_404(Attachment, pk=attachment_pk)
    success = False
    if (
        (request.user.has_perm('attachments.delete_attachment') and
        request.user == g.creator)
    or
        request.user.has_perm('attachments.delete_foreign_attachments')
    ):
        g.delete()
        success = True
    return {"success": success}

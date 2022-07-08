from django.template.loader import render_to_string

from core.models import BillingProject, Notification


def send_notification(project, title: str, short_description: str, content: str):
    notification = Notification(
        project=project,
        title=title,
        short_description=short_description,
        content=content,
        sent_status=False,
        is_read=False,
    )

    notification.save()
    notification.send()


def send_notification_from_template(project: BillingProject, title: str, short_description: str, template: str,
                                    context):
    msg_html = render_to_string(template, context=context)

    send_notification(project=project, title=title, short_description=short_description, content=msg_html)

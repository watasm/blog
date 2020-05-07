from django.core.mail import send_mail, send_mass_mail, get_connection
from Blog.celery import app
from .models import Category
from accounts.models import Preference
from Blog.settings.base import EMAIL_HOST_USER
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

import logging
from django.urls import reverse


@app.task
def send_mails():
    connection = get_connection()

    # Manually open the connection
    connection.open()
    recipient_list = []
    categories = Category.objects.filter(not_sended=True)
    if categories:
        users = User.objects.filter(profile__is_subscribed_to_the_newsletter=True)
        for user in users:
            try:
                user_categories = list()
                profile = user.profile

                preferences = profile.preferences.all()
                for preference in preferences:
                    try:
                        # try get category by preference.
                        category_preference=categories.get(name=preference.name)
                    except category_preference.DoesNotExist:
                        pass
                    else:
                        # append category name in email.
                        user_categories.append(category_preference)

                domain = Site.objects.get_current().domain
                html_content = render_to_string('blog/email.html', {'user_categories': user_categories, 'domain': domain})
                msg = EmailMultiAlternatives('Subject', html_content, EMAIL_HOST_USER, [user.email])
                msg.attach_alternative(html_content, 'text/html')
                recipient_list.append(msg)
            except:
                pass

        # Send the two emails in a single call -
        connection.send_messages(recipient_list)

        # The connection was already open so send_messages() doesn't close it.
        # We need to manually close the connection.
        connection.close()

        categories.update(not_sended = False)

from django import forms
from .models import ChatContact
from django.db.models import Q

class GroupCreateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(GroupCreateForm, self).__init__(*args, **kwargs)

        participants = []
        contacts = ChatContact.objects.select_related('user_from', 'user_to')\
        .only('user_from__id', 'user_from__first_name', 'user_from__last_name', 'user_to__id', 'user_to__first_name', 'user_to__last_name')\
        .filter(Q(user_from=self.user, status='F')|Q(user_to=self.user, status='F'))

        for contact in contacts:
            if self.user == contact.user_from:
                participants.append((contact.user_to.id, contact.user_to.get_full_name))
            else:
                participants.append((contact.user_from.id, contact.user_from.get_full_name))

        self.fields['participants'] = forms.MultipleChoiceField(choices=[(choice[0], choice[1]) for choice in participants], widget=forms.CheckboxSelectMultiple)

class GroupAddUsersForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.candidates = kwargs.pop('candidates')
        super(GroupAddUsersForm, self).__init__(*args, **kwargs)
        candidates = []
        for candidate in self.candidates:
            candidates.append((candidate.id, candidate.get_full_name))
        self.fields['candidates'] = forms.MultipleChoiceField(choices=[(choice[0], choice[1]) for choice in candidates], widget=forms.CheckboxSelectMultiple)

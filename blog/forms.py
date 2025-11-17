from django import forms


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)  # Name who send the mail
    email = forms.EmailField()  # E-Mail Address sending from
    to = forms.EmailField()  # E-Mail Address sending to
    comments = forms.CharField(
        required=False, widget=forms.Textarea
    )  # Text how to send

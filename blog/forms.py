from django import forms

from .models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)  # Name who send the mail
    email = forms.EmailField()  # E-Mail Address sending from
    to = forms.EmailField()  # E-Mail Address sending to
    comments = forms.CharField(
        required=False, widget=forms.Textarea
    )  # Text how to send


# Custom BoundField to add CSS class to comment field
class CommentBoundField(forms.BoundField):
    # CSS class for comment fields
    comment_class = "comment"

    # Override css_classes method to add custom class
    def css_classes(self, extra_classes=None):
        # Get existing classes from parent method
        result = super().css_classes(extra_classes)
        # Add custom comment class if not already present
        if self.comment_class not in result:
            result += f" {self.comment_class}"
        return result.strip()


# Form for submitting comments
class CommentForm(forms.ModelForm):
    # Use custom BoundField for comment fields
    bound_field_class = CommentBoundField

    # Meta class to specify model and fields
    class Meta:
        model = Comment
        fields = ("name", "email", "body")

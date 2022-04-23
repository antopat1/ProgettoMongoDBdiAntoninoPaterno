from django import forms
from .models import BuyOrder, SellOrder, EditDelete


class FormToPublishAskOrder(forms.ModelForm):
    class Meta:
        model = SellOrder
        fields = ['quantity', 'price']


class FormToPublishBidOrder(forms.ModelForm):
    class Meta:
        model = BuyOrder
        fields = ['quantity', 'price']


class ChoiceForm(forms.ModelForm):
    class Meta():
        model = EditDelete
        fields = "__all__"

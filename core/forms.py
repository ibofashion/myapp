from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import inlineformset_factory

from core.models import Client, Sale, SaleLine, User
from core.phone import normalize_phone

INPUT_CLASS = "w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": INPUT_CLASS, "autofocus": True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": INPUT_CLASS})
    )


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "phone"]
        error_messages = {
            "phone": {"required": "Le numéro de téléphone est requis."},
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500",
                "placeholder": "Nom du client",
                "autocomplete": "off",
            }),
            "phone": forms.TextInput(attrs={
                "class": "w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500",
                "placeholder": "Ex : 671 23 45 67",
                "autocomplete": "off",
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        return normalize_phone(phone)


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["client"]
        error_messages = {
            "client": {"required": "Un client est requis."},
        }
        widgets = {
            "client": forms.Select(attrs={"class": INPUT_CLASS}),
        }


class SaleLineForm(forms.ModelForm):
    class Meta:
        model = SaleLine
        fields = ["label", "unit_price", "quantity"]
        widgets = {
            "label": forms.TextInput(attrs={
                "class": f"{INPUT_CLASS} line-label-input", "placeholder": "Article",
            }),
            "unit_price": forms.NumberInput(attrs={
                "class": f"{INPUT_CLASS} line-price-input", "min": "0",
            }),
            "quantity": forms.NumberInput(attrs={
                "class": f"{INPUT_CLASS} line-quantity-input", "min": "1",
            }),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("La quantité doit être supérieure à zéro.")
        return quantity

    def clean_unit_price(self):
        unit_price = self.cleaned_data.get("unit_price")
        if unit_price is not None and unit_price < 0:
            raise forms.ValidationError("Le prix unitaire ne peut pas être négatif.")
        return unit_price


class PaymentForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=0,
        min_value=1,
        error_messages={
            "required": "Le montant du paiement est requis.",
            "min_value": "Le montant du paiement doit être positif.",
        },
        widget=forms.NumberInput(attrs={"class": INPUT_CLASS, "min": "1", "placeholder": "Montant reçu"}),
    )


class VendeurAccountForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": INPUT_CLASS,
            "placeholder": "Identifiant",
            "autocomplete": "off",
        })
        self.fields["password1"].widget.attrs.update({"class": INPUT_CLASS})
        self.fields["password2"].widget.attrs.update({"class": INPUT_CLASS})
        self.fields["role"].widget.attrs.update({"class": INPUT_CLASS})

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username and User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Un compte avec cet identifiant existe déjà.")
        return username


class VendeurRoleForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["role"]
        widgets = {
            "role": forms.Select(attrs={"class": "text-sm rounded-md border-gray-300"}),
        }


SaleLineFormSet = inlineformset_factory(
    Sale,
    SaleLine,
    form=SaleLineForm,
    fields=["label", "unit_price", "quantity"],
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

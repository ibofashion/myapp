import uuid

from django.db import transaction
from django.shortcuts import render

from core.forms import ClientForm, SaleForm, SaleLineFormSet
from core.models import Sale
from core.seller import get_bootstrap_seller


def home(request):
    return render(request, "core/home.html")


def client_create(request):
    success = None
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            success = client
            form = ClientForm()
    else:
        form = ClientForm()

    context = {"form": form, "success": success}

    if request.method == "POST":
        return render(request, "core/_client_form_fragment.html", context)
    return render(request, "core/client_form.html", context)


def sale_create(request):
    success = None

    if request.method == "POST":
        idempotency_key = request.POST.get("idempotency_key") or None
        existing = (
            Sale.objects.filter(idempotency_key=idempotency_key).first()
            if idempotency_key
            else None
        )

        if existing is not None:
            success = existing
            form = SaleForm()
            formset = SaleLineFormSet(instance=Sale(), prefix="lines")
        else:
            form = SaleForm(request.POST)
            formset = SaleLineFormSet(request.POST, instance=Sale(), prefix="lines")
            if form.is_valid() and formset.is_valid():
                with transaction.atomic():
                    sale = form.save(commit=False)
                    sale.seller = get_bootstrap_seller()
                    sale.idempotency_key = idempotency_key or uuid.uuid4()
                    sale.save()
                    formset.instance = sale
                    formset.save()
                success = sale
                form = SaleForm()
                formset = SaleLineFormSet(instance=Sale(), prefix="lines")
    else:
        form = SaleForm()
        formset = SaleLineFormSet(instance=Sale(), prefix="lines")

    context = {
        "form": form,
        "formset": formset,
        "success": success,
        "new_idempotency_key": uuid.uuid4(),
    }

    if request.method == "POST":
        return render(request, "core/_sale_form_fragment.html", context)
    return render(request, "core/sale_form.html", context)

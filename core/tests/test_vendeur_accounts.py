import pytest
from django.test import Client as DjangoClient
from django.urls import reverse

from core.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin():
    return User.objects.create_user(username="admin1", password="pass-admin", role="admin")


@pytest.fixture
def vendeur():
    return User.objects.create_user(username="vendeur1", password="pass-vendeur", role="vendeur")


def test_deux_comptes_roles_distincts_se_connectent_independamment():
    User.objects.create_user(username="admin1", password="pass-admin", role="admin")
    User.objects.create_user(username="vendeur1", password="pass-vendeur", role="vendeur")

    admin_client = DjangoClient()
    vendeur_client = DjangoClient()

    assert admin_client.login(username="admin1", password="pass-admin") is True
    assert vendeur_client.login(username="vendeur1", password="pass-vendeur") is True

    assert admin_client.session.session_key != vendeur_client.session.session_key


def test_admin_voit_tous_les_comptes_avec_leur_role(admin, vendeur):
    web = DjangoClient()
    web.login(username="admin1", password="pass-admin")

    response = web.get(reverse("vendeur_account_list"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "admin1" in content
    assert "vendeur1" in content


def test_un_vendeur_simple_ne_peut_pas_voir_la_liste_des_comptes(admin, vendeur):
    web = DjangoClient()
    web.login(username="vendeur1", password="pass-vendeur")

    response = web.get(reverse("vendeur_account_list"))

    assert response.status_code == 403
    assert "admin1" not in response.content.decode()


def test_creation_reussie_dun_compte_vendeur(admin):
    web = DjangoClient()
    web.login(username="admin1", password="pass-admin")

    response = web.post(
        reverse("vendeur_account_create"),
        {
            "username": "vendeur2",
            "password1": "un-mot-de-passe-solide-1",
            "password2": "un-mot-de-passe-solide-1",
            "role": "vendeur",
        },
    )

    assert response.status_code == 302
    created = User.objects.get(username="vendeur2")
    assert created.role == "vendeur"

    new_session = DjangoClient()
    assert new_session.login(username="vendeur2", password="un-mot-de-passe-solide-1") is True


def test_identifiant_deja_utilise_refuse_sans_doublon(admin, vendeur):
    web = DjangoClient()
    web.login(username="admin1", password="pass-admin")

    response = web.post(
        reverse("vendeur_account_create"),
        {
            "username": "vendeur1",
            "password1": "un-mot-de-passe-solide-1",
            "password2": "un-mot-de-passe-solide-1",
            "role": "vendeur",
        },
    )

    assert response.status_code == 200
    assert User.objects.filter(username="vendeur1").count() == 1
    assert "existe déjà" in response.content.decode()


def test_un_vendeur_simple_ne_peut_pas_creer_de_compte(admin, vendeur):
    web = DjangoClient()
    web.login(username="vendeur1", password="pass-vendeur")

    response = web.post(
        reverse("vendeur_account_create"),
        {
            "username": "vendeur2",
            "password1": "un-mot-de-passe-solide-1",
            "password2": "un-mot-de-passe-solide-1",
            "role": "vendeur",
        },
    )

    assert response.status_code == 403
    assert not User.objects.filter(username="vendeur2").exists()


def test_promotion_vendeur_vers_admin_donne_les_droits_admin(admin, vendeur):
    web = DjangoClient()
    web.login(username="admin1", password="pass-admin")

    response = web.post(reverse("vendeur_account_role_update", args=[vendeur.pk]), {"role": "admin"})

    assert response.status_code == 302
    vendeur.refresh_from_db()
    assert vendeur.role == "admin"

    promoted_session = DjangoClient()
    promoted_session.login(username="vendeur1", password="pass-vendeur")
    access_response = promoted_session.get(reverse("vendeur_account_list"))
    assert access_response.status_code == 200


def test_retrogradation_admin_vers_vendeur_retire_les_droits_admin(admin):
    other_admin = User.objects.create_user(username="admin2", password="pass-admin2", role="admin")
    web = DjangoClient()
    web.login(username="admin1", password="pass-admin")

    response = web.post(
        reverse("vendeur_account_role_update", args=[other_admin.pk]), {"role": "vendeur"}
    )

    assert response.status_code == 302
    other_admin.refresh_from_db()
    assert other_admin.role == "vendeur"

    downgraded_session = DjangoClient()
    downgraded_session.login(username="admin2", password="pass-admin2")
    access_response = downgraded_session.get(reverse("vendeur_account_list"))
    assert access_response.status_code == 403


def test_un_vendeur_simple_ne_peut_pas_changer_de_role(admin, vendeur):
    web = DjangoClient()
    web.login(username="vendeur1", password="pass-vendeur")

    response = web.post(
        reverse("vendeur_account_role_update", args=[admin.pk]), {"role": "vendeur"}
    )

    assert response.status_code == 403
    admin.refresh_from_db()
    assert admin.role == "admin"


def test_lien_comptes_vendeurs_visible_uniquement_pour_admin(admin, vendeur):
    admin_session = DjangoClient()
    admin_session.login(username="admin1", password="pass-admin")
    admin_response = admin_session.get(reverse("home"))
    assert "Comptes vendeurs" in admin_response.content.decode()

    vendeur_session = DjangoClient()
    vendeur_session.login(username="vendeur1", password="pass-vendeur")
    vendeur_response = vendeur_session.get(reverse("home"))
    assert "Comptes vendeurs" not in vendeur_response.content.decode()

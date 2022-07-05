import pytest
from web_app import models as m


@pytest.mark.django_db
def test_test(client):
    response = client.get('')
    assert response.status_code == 200

#
# @pytest.fixture
# def product():
#     product = m.Product.objects.create(
#         name="Makaron świderki",
#         kcal=300,
#         price=4.00,
#     )
#     return product

import pytest
from app import create_app, db
from models import User, GroceryList, Item


@pytest.fixture()
def app_context():
    app = create_app({"TESTING": True})
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_purchase_all_items_only_counts_newly_purchased_items(app_context):
    user_a = User(username="user-a", email="user-a@example.com")
    user_b = User(username="user-b", email="user-b@example.com")
    db.session.add_all([user_a, user_b])
    db.session.commit()

    grocery_list = GroceryList(name="Test List", created_by=user_a.id, is_shared=False)
    db.session.add(grocery_list)
    db.session.commit()

    already_purchased = Item(
        list_id=grocery_list.id,
        name="Already Purchased",
        added_by=user_a.id,
        is_purchased=True,
        purchased_by=user_b.id,
    )
    unpurchased_1 = Item(
        list_id=grocery_list.id,
        name="Need to buy",
        added_by=user_a.id,
    )
    unpurchased_2 = Item(
        list_id=grocery_list.id,
        name="Need to buy 2",
        added_by=user_a.id,
    )
    db.session.add_all([already_purchased, unpurchased_1, unpurchased_2])
    db.session.commit()

    from try_prs import purchase_all_items

    count = purchase_all_items(grocery_list.id, user_a.id)

    assert count == 2
    assert unpurchased_1.is_purchased is True
    assert unpurchased_2.is_purchased is True
    assert already_purchased.is_purchased is True
    assert already_purchased.purchased_by == user_b.id

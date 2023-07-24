from fastapi import status
from fastapi.testclient import TestClient

from src.main import app


'''
    Test all the crud apis
        Sequence of operations - 
            - Create a customer
            - Create a user for the customer
            - Create a customer display config for the customer
            - Create a display column for the customer display config
            - Update the customer display config
            - Update the display column
            - Delete the display column
            - Delete the customer display config
            - Delete the user
            - Delete the customer
'''
def test_crud_apis():
    with TestClient(app) as client:
        # expect nothing in fresh db
        response = get_all_customers(client)
        assert len(response) == 0

        # create a customer
        response = create_customer(client)
        customer_id = response["id"]

        # get customer
        response = get_all_customers(client)
        assert len(response) == 1
        assert response[0]["id"] == customer_id
        assert response[0]["name"] == "customer 1"

        # create a user
        response = create_user(client)
        user_id = response["id"]
        assert response["customer_id"] == customer_id

        # get user
        response = get_all_users(client)
        assert len(response) == 1
        assert response[0]["id"] == user_id
        assert response[0]["name"] == "foobar"

        # create a customer display config
        response = create_customer_display_config(client)
        display_config_id = response["id"]
        assert response["customer_id"] == customer_id

        # get customer display config
        response = get_all_customer_display_configs(client)
        assert len(response) == 1
        assert response[0]["id"] == display_config_id
        assert response[0]["display_name"] == "foobar"

        # create a display column
        response = create_display_column(client)
        display_column_id = response["id"]
        assert response["customer_display_configuration_id"] == display_config_id
        
        # get display columns of a config
        response = get_all_display_columns_of_config(client)
        assert len(response) == 1
        assert response[0]["id"] == display_column_id

        # update customer display config
        response = update_customer_display_config(client, display_config_id)
        assert response["is_default"] == False

        # update display column
        response = update_display_column(client, display_column_id)
        assert response["is_active"] == False

        # delete display column
        delete_display_column(client, display_column_id)
        response = get_all_display_columns_of_config(client)

        # delete customer display config
        delete_customer_display_config(client, display_config_id)
        response = get_all_customer_display_configs(client)

        # delete user
        delete_user(client, user_id)

        # delete customer
        delete_customer(client, customer_id)


# Customer Apis
def create_customer(client) -> dict:
    response = client.post("/customers/", json={"name": "customer 1", "is_active": True})
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


def get_all_customers(client) -> dict:
    response = client.get("/customers/")
    assert response.status_code == status.HTTP_200_OK
    return response.json()


def delete_customer(client, customer_id: int):
    response = client.delete(f"/customers/{customer_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


# User apis
def create_user(client) -> dict:
    response = client.post("/users/", json={"name": "foobar", "email": "foo@bar.com", "customer_id": 1})
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


def get_all_users(client) -> dict:
    response = client.get("/users/")
    assert response.status_code == status.HTTP_200_OK
    return response.json()


def delete_user(client, user_id: int):
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


# Customer Display Config Apis
def create_customer_display_config(client) -> dict:
    response = client.post("/customer-display-config/", json={"customer_id": 1, "display_name": "foobar", "is_default": True, "is_active": True, "start_year": 2015, "end_year": 2022})
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


def get_all_customer_display_configs(client) -> dict:
    response = client.get("/customer-display-config/")
    assert response.status_code == status.HTTP_200_OK
    return response.json()


def update_customer_display_config(client, display_config_id: int) -> dict:
    response = client.put(f"/customer-display-config/{display_config_id}", json={"is_default": False})
    assert response.status_code == status.HTTP_200_OK
    return response.json()


def delete_customer_display_config(client, display_config_id: int):
    response = client.delete(f"/customer-display-config/{display_config_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


# Display Column Apis
def create_display_column(client) -> dict:
    response = client.post("/display-column/", json={"customer_display_configuration_id": 1, "column_label": "Tillage Depth", "column_order": 1, "is_active": True, "data_type": "tillage_depth", "data_display_type": "slider", "data_options": ["0", "10", "1"]})
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


def get_all_display_columns_of_config(client) -> dict:
    response = client.get("/display-column/customer-config/1")
    assert response.status_code == status.HTTP_200_OK
    return response.json()


def update_display_column(client, display_column_id: int) -> dict:
    response = client.put(f"/display-column/{display_column_id}", json={"is_active": False})
    assert response.status_code == status.HTTP_200_OK
    return response.json()


def delete_display_column(client, display_column_id: int):
    response = client.delete(f"/display-column/{display_column_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
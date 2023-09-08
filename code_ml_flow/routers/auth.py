from fastapi import APIRouter, Depends, Response, status
from dependency_injector.wiring import inject, Provide

from code_ml_flow.containers import Container
from code_ml_flow.daos import UserDAO
from code_ml_flow.error import NotFoundError

auth_router = APIRouter()


@auth_router.get("/users")
@inject
def get_list(
        user_dao: UserDAO = Depends(Provide[Container.user_dao]),
):
    return user_dao.get_users()


@auth_router.get("/users/{user_id}")
@inject
def get_by_id(
        user_id: int,
        user_dao: UserDAO = Depends(Provide[Container.user_dao]),
):
    try:
        return user_dao.get_user_by_id(user_id)
    except NotFoundError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@auth_router.post("/users", status_code=status.HTTP_201_CREATED)
@inject
def add(
        user_dao: UserDAO = Depends(Provide[Container.user_dao]),
):
    return user_dao.create_user()


@auth_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def remove(
        user_id: int,
        user_dao: UserDAO = Depends(Provide[Container.user_dao]),
):
    try:
        user_dao.delete_user_by_id(user_id)
    except NotFoundError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@auth_router.get("/status")
def get_status():
    return {"status": "OK"}
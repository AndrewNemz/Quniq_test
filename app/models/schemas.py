from typing import Union, Optional
from datetime import datetime

from pydantic import BaseModel


class TaskBase(BaseModel):
    """
    Модель для базового представления задачи.
    """

    id: int
    title: str
    description: Union[str, None] = None
    created_at: datetime = datetime.now()
    updated_at: Union[datetime, None] = None


class TaskCreate(BaseModel):
    """
    Модель для представления создания задачи.
    """

    title: str
    description: Union[str, None] = None
    created_at: datetime = datetime.now()
    updated_at: Optional[datetime] = None


class TaskUpdate(BaseModel):
    """
    Модель для представления обновления задачи.
    """

    title: str
    description: Union[str, None] = None
    updated_at: datetime = datetime.now()


class Task(TaskBase):
    """
    Модель представления задачи.
    """

    user_name: str
    user_surname: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    """
    Модель для базового представления юзера.
    """

    user_name: str
    user_surname: str
    email: str


class UserCreate(UserBase):
    """
    Модель для представления создания юзера.
    """

    password: str


class User(UserBase):
    """
    Модель для представления юзера.
    """

    id: int
    tasks: list[Task] = []

    class Config:
        orm_mode = True

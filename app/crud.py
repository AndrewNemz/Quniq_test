from sqlalchemy.orm import Session
import datetime

from app.models import sql_models, schemas


def get_user(db: Session, user_id: int):
    """
    Функция для получения пользователя.
    """

    return db.query(sql_models.User).filter(
        sql_models.User.id == user_id
    ).first()


def get_user_by_email(db: Session, email: str):
    """
    Функция для получения пользователя по почте.
    """

    return db.query(sql_models.User).filter(
        sql_models.User.email == email
    ).first()


def get_user_by_password(db: Session, password: str):
    """
    Функция для получения пользователя по паролю.
    """

    return db.query(sql_models.User).filter(
        sql_models.User.hashed_password == password
    ).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Функция для получения списка пользователей.
    """

    return db.query(sql_models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    """
    Функция для создания пользователя.
    """

    fake_hashed_password = user.password + "notreallyhashed"
    db_user = sql_models.User(
        user_name=user.user_name,
        user_surname=user.user_surname,
        email=user.email,
        hashed_password=fake_hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user_task(db: Session, task: schemas.TaskCreate, user_id: int):
    """
    Функция для создания задачи.
    """

    user = db.query(sql_models.User).filter(
        sql_models.User.id == user_id
    ).first()
    db_task = sql_models.Task(
        title=task.title,
        description=task.description,
        owner_id=user_id,
        user_name=user.user_name,
        user_surname=user.user_surname
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return {
        "id": db_task.id,
        "title": db_task.title,
        "description": db_task.description,
        "user_name": user.user_name,
        "user_surname": user.user_surname
    }


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    """
    Возвращает список всех задач.
    """
    return db.query(sql_models.Task).offset(skip).limit(limit).all()


def get_user_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """
    Возвращает список всех задач конкретного пользователя.
    """

    return db.query(sql_models.Task).filter(
        sql_models.Task.owner_id == user_id
    ).offset(skip).limit(limit)


def get_task(db: Session, task_id: int):
    """
    Возвращает выбранную задачу по ее ID.
    """

    return db.query(sql_models.Task).filter(
        sql_models.Task.id == task_id
    ).first()


def get_task_by_owner_id(db: Session, user_id: int, task_id: int):
    """
    Функция для получения задачи по ее ID и ID пользователя.
    """

    return db.query(sql_models.Task).filter(
        sql_models.Task.owner_id == user_id,
        sql_models.Task.id == task_id
    ).first()


def delete_task(db: Session, task_id: int):
    """
    Удаляет объект задачи.
    """

    task = db.query(sql_models.Task).filter(
        sql_models.Task.id == task_id
    ).first()
    db.delete(task)
    db.commit()


def update_task(db: Session, task_id: int, title: str, description: str):
    """
    Обновление существующей задачи.
    """

    task = db.query(sql_models.Task).filter(
        sql_models.Task.id == task_id
    ).first()
    task.title = title
    task.description = description
    task.updated_at = datetime.datetime.now()
    db.commit()
    db.refresh(task)
    return task

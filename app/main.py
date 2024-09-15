from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from sqlalchemy.orm import Session

from app.models import sql_models, schemas
from . import crud
from app.database import SessionLocal, engine


sql_models.Base.metadata.create_all(bind=engine)
app = FastAPI()
security = HTTPBasic()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def auth_user(
        credentials: HTTPBasicCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    """
    Функция для проверки зарегестрированного пользователя.
    """

    user = crud.get_user_by_password(db, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Пользователь не зарегестрирован"
        )
    return user


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Функция для регестрации нового пользователя.
    """

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с такой почтой уже зарегестрирован."
        )
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Функция для просмотра всех пользователей.
    """

    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Функция для просмотра конкретного пользователя по его ID.
    """

    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user


@app.post("/tasks/", response_model=schemas.Task)
def create_task_for_user(
    task: schemas.TaskCreate,
    user: schemas.User = Depends(auth_user),
    db: Session = Depends(get_db)
):
    """
    Функция для создания новых задач.
    Только для зарегестрированных пользователей.
    """

    user_id = user.id
    return crud.create_user_task(
        db=db,
        task=task,
        user_id=user_id
    )


@app.get("/tasks/all/", response_model=list[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Функция для просмотра всех задач.
    Доступно для всех пользователей.
    """

    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks


@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """
    Функция для просмотра конкретной задачи по ее ID.
    Доступно для всех пользователей.
    """

    task = crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Такой задачи не найдено.")
    return task


@app.get("/tasks/", response_model=list[schemas.Task])
def read_users_tasks(
    user: schemas.User = Depends(auth_user),
    db: Session = Depends(get_db)
):
    """
    Функция для просмотра задач конкретного пользователя.
    Доступно для зарегестрированного пользователя.
    """

    tasks = crud.get_user_tasks(db, user_id=user.id)
    if tasks is None:
        raise HTTPException(
            status_code=204,
            detail="У пользователя нет задач."
        )
    return tasks


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    user: schemas.User = Depends(auth_user),
    db: Session = Depends(get_db)
):
    """
    Функция для удаления задачи.
    Доступно только автору задачи.
    """

    if not crud.get_task_by_owner_id(db=db, user_id=user.id, task_id=task_id):
        raise HTTPException(
            status_code=404,
            detail="Удаление чужой задачи запрещено!"
        )
    return crud.delete_task(db=db, task_id=task_id)


@app.patch("/tasks/{task_id}", response_model=schemas.Task)
def patch_task(
    task_id: int,
    task: schemas.TaskUpdate,
    user: schemas.User = Depends(auth_user),
    db: Session = Depends(get_db)
):
    """
    Функция для редактирования задачи.
    Доступно только автору.
    """

    if not crud.get_task_by_owner_id(db=db, user_id=user.id, task_id=task_id):
        raise HTTPException(
            status_code=404,
            detail="Редактирование чужой задачи запрещено!"
        )
    return crud.update_task(
        db=db,
        task_id=task_id,
        title=task.title,
        description=task.description
    )

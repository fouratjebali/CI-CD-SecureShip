from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from app.models import Task, TaskCreate
from app.database import init_db, get_connection, get_task_by_title_unsafe
from app.config import get_settings

app = FastAPI(title="SecureShip Task API")

@app.on_event("startup")
def startup():
    settings = get_settings()   
    print(f"Secrets loaded from Vault — DB connected")
    init_db()

@app.get("/")
def root():
    return {"status": "ok", "app": "SecureShip"}

@app.get("/tasks")
def list_tasks():
    conn = get_connection()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [dict(t) for t in tasks]

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO tasks (title, description, done) VALUES (?, ?, 0)",
        (task.title, task.description)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return {"id": task_id, **task.dict()}

@app.get("/tasks/search")
def search_task(title: str):
    # Uses the unsafe function on purpose
    results = get_task_by_title_unsafe(title)
    return [dict(r) for r in results]

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(task)

@app.put("/tasks/{task_id}/done")
def complete_task(task_id: int):
    conn = get_connection()
    conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"message": "Task marked as done"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"message": "Task deleted"}

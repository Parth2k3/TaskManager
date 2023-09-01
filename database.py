from sqlalchemy import create_engine, text
import os

my_secret = os.environ['db_conn']

engine = create_engine(my_secret,
                       connect_args={"ssl": {
                         "ssl_ca": "/etc/ssl/cert.pem"
                       }})


def login_user(username, password):
  with engine.connect() as conn:
    result = conn.execute(
      text("SELECT * FROM task_users WHERE username = :user AND password = :passw"),
      {
        "user": username,
        "passw": password
      })
    rows = result.all()
    if len(rows) == 0:
      return None
    else:
      return list(rows[0])


def getGroupId(username):
  with engine.connect() as conn:
    result1 = conn.execute(
      text("SELECT group_id FROM groups WHERE username = :username"),
      {
        "username": username
      })
    rows = result1.all()
    return list(rows[0])


def getData(group_id):
  with engine.connect() as conn:
    result1 = conn.execute(
      text("SELECT topic, date, description, uploader, task_id FROM tasks WHERE group_id = :group_id AND status = :status"),
      {
        "group_id": group_id,
        "status": 'TASK READY'
      })
    result2 = conn.execute(
      text("SELECT topic, date, description, uploader, task_id FROM tasks WHERE group_id = :group_id AND status = :status"),
      {
        "group_id": group_id,
        "status": 'IN PROGRESS'
      })
    result3 = conn.execute(
      text("SELECT topic, date, description, uploader, task_id FROM tasks WHERE group_id = :group_id AND status = :status"),
      {
        "group_id": group_id,
        "status": 'NEEDS REVIEW'
      })
    result4 = conn.execute(
      text("SELECT topic, date, description, uploader, task_id FROM tasks WHERE group_id = :group_id AND status = :status"),
      {
        "group_id": group_id,
        "status": 'DONE'
      })
    rows1 = result1.all()
    rows2 = result2.all()
    rows3 = result3.all()
    rows4 = result4.all()
    
    return {"ready": list(rows1), "progress": list(rows2), "review": list(rows3), "done": list(rows4)}
    

def moveready(id, grp, user, date):
  with engine.connect() as conn:
    conn.execute(text("UPDATE tasks SET status = 'TASK READY' where task_id = :id"),
    {
      "id": id
    })
    conn.execute(text("INSERT into updates (`group_id`, `task_id`, `user`, `description`, `date`) VALUES (:grp_id, :task_id, :user, :description, :date)"),
                {
                  "grp_id": grp,
                  "task_id": id,
                  "user": user,
                  "description": "moved a task.",
                  "date": date
                })
  return 'success'


def moveprogress(id, grp, user, date):
  with engine.connect() as conn:
    conn.execute(text("UPDATE tasks SET status = 'IN PROGRESS' where task_id = :id"),
    {
      "id": id
    })
    conn.execute(text("INSERT into updates (`group_id`, `task_id`, `user`, `description`, `date`) VALUES (:grp_id, :task_id, :user, :description, :date)"),
                {
                  "grp_id": grp,
                  "task_id": id,
                  "user": user,
                  "description": "moved a task.",
                  "date": date
                })
  return 'success'

def movereview(id, grp, user, date):
  with engine.connect() as conn:
    conn.execute(text("UPDATE tasks SET status = 'NEEDS REVIEW' where task_id = :id"),
    {
      "id": id
    })
    conn.execute(text("INSERT into updates (`group_id`, `task_id`, `user`, `description`, `date`) VALUES (:grp_id, :task_id, :user, :description, :date)"),
                {
                  "grp_id": grp,
                  "task_id": id,
                  "user": user,
                  "description": "moved a task.",
                  "date": date
                })
  return 'success'

def movedone(id, grp, user, date):
  with engine.connect() as conn:
    conn.execute(text("UPDATE tasks SET status = 'DONE' where task_id = :id"),
    {
      "id": id
    })
    conn.execute(text("INSERT into updates (`group_id`, `task_id`, `user`, `description`, `date`) VALUES (:grp_id, :task_id, :user, :description, :date)"),
                {
                  "grp_id": grp,
                  "task_id": id,
                  "user": user,
                  "description": "moved a task.",
                  "date": date
                })
  return 'success'

def getStatus(task_id):
  with engine.connect() as conn:
    result = conn.execute(text("SELECT status from tasks where task_id = :task_id"),
                {
                  "task_id": task_id
                })
    rows = list(result.all())
    return rows[0]


def edittask(task_id, user, desc, date, topic, grp, datetime):
  with engine.connect() as conn:
    conn.execute(text("UPDATE tasks set topic = :topic, description = :desc ,uploader = :user, date = :date WHERE task_id = :task_id"),
    {
      "topic": topic,
      "desc": desc,
      "user": user,
      "date": date,
      "task_id": task_id
    })
    conn.execute(text("INSERT into updates (`group_id`, `task_id`, `user`, `description`, `date`) VALUES (:grp_id, :task_id, :user, :description, :date)"),
                {
                  "grp_id": grp,
                  "task_id": task_id,
                  "user": user,
                  "description": "edited a task.",
                  "date": datetime
                })
  return 'success'


def getDataByTaskId(task_id):
  with engine.connect() as conn:
    result = conn.execute(text("SELECT topic, date, description, uploader, task_id FROM tasks WHERE task_id = :task_id"),
      {
        "task_id": task_id
      })
    return list(result.all()[0])

def getTopics(group_id):
  with engine.connect() as conn:
    result = conn.execute(text("SELECT topic, COUNT(*) AS freq from tasks WHERE group_id = :group_id group by topic "),
                         {
                           "group_id": group_id
                         })
    return list(result.all())

def getDoneTopics(group_id, topic):
  with engine.connect() as conn:
    result = conn.execute(text("SELECT count(*) as freq from tasks where topic = :topic AND group_id = :group_id AND status = :status group by topic"),
                         {
                           "topic": topic,
                           "group_id": group_id,
                           "status": 'DONE'
                         })
    return (result.all())


def getUpdates(group_id):
  with engine.connect() as conn:
    result = conn.execute(text("SELECT user, description, date FROM updates WHERE group_id = :group_id order by date DESC"),
                         {
                           "group_id": group_id
                         })

    return list(result.all())

def getUsersInGrp(group_id):
   with engine.connect() as conn:
    result = conn.execute(text("SELECT username from groups where group_id = :group_id"),
                         {
                           "group_id": group_id
                         })

    return list(result.all())


def getGroupName(group_id):
  with engine.connect() as conn:
    result = conn.execute(text("SELECT group_name from group_names where group_id = :group_id"),
                         {
                           "group_id": group_id
                         })

    return list(result.all()[0])


def getNewTaskId():
   with engine.connect() as conn:
    result = conn.execute(text("SELECT MAX(task_id) from tasks"))
    return result.all()[0]

def addtask(status, id, input, current_date, topic, grp_id, task_id, datetime):

  with engine.connect() as conn:
    conn.execute(text("INSERT INTO tasks(`group_id`, `topic`, `date`, `status`, `description`, `uploader`) values(:grp_id, :topic, :current_date, :status, :input, :id)"),
                         {
                                "topic": topic,
                                "input": input,
                                "grp_id": grp_id,
                                "current_date": current_date,
                                "status": status,
                                "id": id
                         })
    conn.execute(text("INSERT INTO updates(`group_id`, `task_id`, `user`, `description`, `date`) VALUES(:grp_id, :task_id, :user, :description, :date)"),
                {
                  "grp_id": grp_id,
                  "task_id": task_id[0],
                  "user": id,
                  "description": "added a new task.",
                  "date": datetime
                })

    return 'success'


def sendRequest(group_id, id):
  with engine.connect() as conn:
    conn.execute(text("INSERT INTO requests (`user`, `group_id`) values (:user, :group_id)"),
                {
                  "user": id,
                  "group_id": group_id
                })

def getUsersInGroups():
  with engine.connect() as conn:
    result = conn.execute(text("SELECT username FROM groups"))
    return result.all()

def getRequests(group_id):
  with engine.connect() as conn:
    result = conn.execute(text("SELECT user FROM requests WHERE group_id = :grp_id"),
                         {
                           "grp_id": group_id
                         })
    return result.all()


def acceptReq(id, grp_id, date):
  with engine.connect() as conn:
    conn.execute(text("INSERT INTO groups (`username`, `group_id`) values(:id, :grp_id)"),
                {
                  "id": id,
                  "grp_id": grp_id
                })

    conn.execute(text("INSERT INTO updates(`group_id`, `task_id`, `user`, `description`, `date`) VALUES (:group_id, :task_id, :user, :description, :date)"),
                {
                  "group_id": grp_id,
                  "task_id": 0,
                  "user": id,
                  "description": 'joined the group.',
                  "date": date
                })
    
    conn.execute(text("DELETE FROM requests WHERE user = :id AND group_id = :grp_id"),
                {
                  "id": id,
                  "grp_id": grp_id
                })
    return 'success'

def declineReq(id, grp_id):
  with engine.connect() as conn:
    conn.execute(text("DELETE FROM requests WHERE user = :id AND group_id = :grp_id"),
                {
                  "id": id,
                  "grp_id": grp_id
                })
    
    return 'success'

def leavegroup(user, grp_id, date):
  with engine.connect() as conn:
    conn.execute(text("DELETE FROM groups WHERE username = :id AND group_id = :grp_id"),
                {
                  "id": user,
                  "grp_id": grp_id
                })
    conn.execute(text("INSERT INTO updates(`group_id`, `task_id`, `user`, `description`, `date`) VALUES (:group_id, :task_id, :user, :description, :date)"),
                {
                  "group_id": grp_id,
                  "task_id": 0,
                  "user": user,
                  "description": 'left the group.',
                  "date": date
                })
    return 'success'

def creategroup(user, grp_name):
  with engine.connect() as conn:
    conn.execute(text("INSERT INTO group_names(`group_name`) VALUES (:grp_name)"),
                {
                  "grp_name": grp_name
                })
    grp_id = (conn.execute(text("SELECT group_id from group_names WHERE group_name = :grp_name"),{
      "grp_name": grp_name
    })).all()[0][0]
    print(grp_id)
    conn.execute(text("INSERT INTO groups (`username`, `group_id`) VALUES (:user, :grp_id)"),
                {
                  "user": user,
                  "grp_id":grp_id
                })
    conn.execute(text("DELETE FROM requests WHERE user = :user"),
                {
                  "user": user
                })

    return 'success'

def signup(user, pw, mail):
   with engine.connect() as conn:
    conn.execute(text("INSERT INTO task_users(`username`, `password`, `mail`) VALUES (:user, :pw, :mail)"),
                {
                  "user": user,
                  "pw": pw,
                  "mail": mail
                })
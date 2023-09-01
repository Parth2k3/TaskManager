from flask import Flask, render_template, session, redirect, request
from functools import wraps
from database import login_user, getData, getGroupId, moveready, movedone, moveprogress, movereview, getStatus, edittask, getDataByTaskId, getTopics, getDoneTopics, getUpdates, getUsersInGrp, getGroupName, getNewTaskId, addtask, sendRequest, getUsersInGroups, getRequests, acceptReq, declineReq, leavegroup, creategroup, signup
import datetime


def login_required_for_id(f):

  @wraps(f)
  def decorated_function(id, *args, **kwargs):
    if 'username' not in session or session['username'] != id:
      return redirect('/login')
    return f(id, *args, **kwargs)

  return decorated_function


app = Flask(__name__)
app.secret_key = 'secretestkey'



@app.route("/")
def home():
  return render_template("index.html")

@app.route("/signup", methods = ['GET', 'POST'])
def signuppage():
  if request.method == 'POST':
    user = request.form['username']
    pw = request.form['password']
    mail = request.form['mail']
    signup(user, pw, mail)
    return redirect('/entergroup/{}'.format(user))
  return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():

  if request.method == 'POST':
    user = request.form['username']
    pw = request.form['password']
    data = login_user(user, pw)
    users = getUsersInGroups()
    if data:
      for username in users:
        if user == username[0]:
          grp_id = getGroupId(user)
          session['groupid'] = grp_id
          session['username'] = data[0]
          return redirect('/taskboard/{}'.format(user))
      
      session['username'] = data[0]
      return redirect('/entergroup/{}'.format(user))

    else:
      print('error')

  return render_template('login.html')

@app.route('/entergroup/<id>', methods=['GET', 'POST'])

def entergroup(id):
  
  if request.method == "POST":
    group_id = request.form['group_id']
    sendRequest(group_id, id)
    return redirect('/entergroup/{}'.format(id))

  return render_template('enterGroup.html', user = id)


@app.route("/logout")
def logout():
  session['username'] = ''
  session['groupid'] = ''
  return redirect("/")


@app.route('/taskboard/<id>')
def taskboard(id):
  if session['username'] == id:
    grp_id = getGroupId(session['username'])
    data = getData(grp_id)
    topics = getTopics(grp_id)
    updates = getUpdates(grp_id)
    users = getUsersInGrp(grp_id)
    grp_name = getGroupName(grp_id)
    requests = getRequests(grp_id)
    done_topics = {}
    for element in topics:
      freq = getDoneTopics(grp_id, element[0])
      if len(freq) == 0:
        done_topics[element[0]] = 0
      else:
        done_topics[element[0]] = freq[0][0]
    return render_template('home.html', ready = data['ready'], progress = data['progress'], review = data['review'], done = data['done'], username = session['username'], topics = topics, done_topics = done_topics, updates = updates, users = users, grp_id = grp_id[0], grp_name = grp_name, requests = requests )
  else:
    return redirect('/login')


@app.route('/creategroup', methods= ['GET', 'POST'])
def creategrp():
  if request.method == 'POST':
    user = session['username']
    grp_name = request.form['group_name']
    creategroup(user, grp_name)
    return redirect('/taskboard/{}'.format(user))
  return render_template("creategroup.html")


@app.route('/accept/<user>/<grp_id>')
def accept(user, grp_id):
  print(session['username'])
  acceptReq(user, grp_id, datetime.datetime.now())
  return redirect('/taskboard/{}'.format(session['username']))


@app.route('/decline/<id>/<grp_id>')
def decline(id, grp_id):

  declineReq(id, grp_id)
  return redirect('/taskboard/{}'.format(session['username']))


@app.route('/movetoready/<task_id>/<id>')
def movereadytask(task_id):
  user = session['username']
  if getStatus(task_id) == 'TASK READY':
    return redirect('/taskboard/{}'.format(user))
  else:
    moveready(task_id, session['groupid'], session['username'], datetime.datetime.now())
    return redirect('/taskboard/{}'.format(user))


@app.route('/movetoprog/<task_id>')
def moveprogtask(task_id):
  user = session['username']
  if getStatus(task_id) == 'IN PROGRESS':
    return redirect('/taskboard/{}'.format(user))
  else:
    moveprogress(task_id, session['groupid'], session['username'], datetime.datetime.now())
    return redirect('/taskboard/{}'.format(user))


@app.route('/movetoreview/<task_id>')
def movereviewtask(task_id):
  user = session['username']
  if getStatus(task_id) == 'NEEDS REVIEW':
    return redirect('/taskboard/{}'.format(user))
  else:
    movereview(task_id, session['groupid'], session['username'], datetime.datetime.now())
    return redirect('/taskboard/{}'.format(user))


@app.route('/movetodone/<task_id>')
def moveDonetask(task_id):
  user = session['username']
  if getStatus(task_id) == 'DONE':
    return redirect('/taskboard/{}'.format(user))
  else:
    movedone(task_id, session['groupid'], session['username'], datetime.datetime.now())
    return redirect('/taskboard/{}'.format(user))


@app.route('/edittask/<task_id>/<id>', methods=['GET', 'POST'])
@login_required_for_id
def edit(id, task_id):
  data = getDataByTaskId(task_id)
  if request.method == 'POST':
    topic = request.form['topic']
    input = request.form['input']
    current_date = datetime.date.today()
    result = edittask(task_id, id, input, current_date, topic, session['groupid'], datetime.datetime.now())
    if result == 'success':
      return redirect('/taskboard/{}'.format(id))
    else:
      print('error')
      return render_template('edittask.html', task_id = task_id, username = id)
    
  return render_template('edittask.html',task = data, task_id = task_id, username = id)

@app.route('/addtask/<id>', methods=['GET', 'POST'])

def addtasks(id):
  
  if request.method == 'POST':
    status = "TASK READY"
    topic = request.form['topic']
    input = request.form['input']
    current_date = datetime.date.today()
    result = addtask(status, id, input, current_date, topic, session['groupid'], getNewTaskId(), datetime.datetime.now())
    if result == 'success':
      return redirect('/taskboard/{}'.format(id))
    else:
      print('error')
      return render_template('addtask.html',username = id)
    
  return render_template('addtask.html', username = id)


@app.route('/leavegrp/<grp_id>/<id>')
def leavegrp(id, grp_id):
  leavegroup(id, grp_id, datetime.datetime.now())
  return redirect('/entergroup/{}'.format(id))

if __name__ == '__main__':
  app.run(host='0.0.0.0', port='8080')

from dataclasses import dataclass
from typing import Optional
import toml
from flask import Flask, url_for
from flask import render_template, redirect
from flask import request
import dotenv
from basecampapi.basecampapi import Basecamp
from main import BCManager
from flask_basicauth import BasicAuth
from os import environ

dotenv.load_dotenv()

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = environ.get('APP_USER')
app.config['BASIC_AUTH_PASSWORD'] = environ.get('PASSWORD')

basic_auth = BasicAuth(app)



@dataclass
class Config:
    account_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_uri: Optional[str] = None
    refresh_token: Optional[str] = None
    project_id: Optional[str] = None
    msg_board_id: Optional[str] = None
    team = 2713

    @staticmethod
    def from_toml():
        with open('conf.toml') as f:
            data = toml.load(f)
            return Config(**data)

    def to_toml(self):
        data = self.__dict__
        with open('conf.toml', 'w') as f:
            f.write(toml.dumps(data))

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


conf = Config.from_toml()

auth_state = None
verification_link = None
bc_manager = None

if conf.account_id and conf.client_id and conf.client_secret and conf.redirect_uri and conf.refresh_token and conf.project_id and conf.msg_board_id:
    auth_state = 'authorized'
    bc_manager = BCManager(conf)
elif conf.account_id and conf.client_id and conf.client_secret and conf.redirect_uri and conf.refresh_token:
    auth_state = 'authorized'
elif conf.account_id and conf.client_id and conf.client_secret:
    try:
        bc_tmp = Basecamp(credentials=conf.to_dict())
    except Exception as e:
        auth_state = 'needs_code'
        verification_link = f"https://launchpad.37signals.com/authorization/new?type=web_server&client_id={conf.client_id}&redirect_uri={conf.redirect_uri}"
    else:
        raise Exception("No exception was raised. Expected an exception.")
else:
    auth_state = 'unauthorized'


@app.get('/')
@basic_auth.required
def index():
    if auth_state == 'needs_code':
        return redirect(verification_link)
    if auth_state == 'authorized':
        return render_template('index.html', auth_state=auth_state, team=conf.team, project_id=conf.project_id or '',
                               msg_board_id=conf.msg_board_id or '')
    return render_template('index.html', auth_state=auth_state, team=conf.team)


@app.post('/set_project')
@basic_auth.required
def set_project():
    global conf
    conf.project_id = request.form.get('project_id')
    conf.msg_board_id = request.form.get('msg_board_id')
    conf.to_toml()

    global bc_manager
    bc_manager = BCManager(conf)

    return redirect(url_for('index'))


@app.post('/set_params')
@basic_auth.required
def parse_user_args():
    global bc_manager
    account_id = request.form.get('account_id')
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')

    global conf
    conf.account_id = account_id
    conf.client_id = client_id
    conf.client_secret = client_secret
    conf.redirect_uri = f"{environ.get('HOST')}/auth"
    conf.to_toml()

    global auth_state
    auth_state = 'needs_code'

    try:
        Basecamp(credentials=conf.to_dict())
    except Exception as e:
        pass
    else:
        raise Exception("No exception was raised. Expected an exception.")

    return redirect(
        f"https://launchpad.37signals.com/authorization/new?type=web_server&client_id={conf.client_id}&redirect_uri={conf.redirect_uri}"
    )


@app.get('/auth')
@basic_auth.required
def auth():
    global auth_state
    global bc_manager
    global conf

    code = request.args.get('code')

    assert auth_state == 'needs_code'
    assert code is not None

    bc = Basecamp(credentials=conf.to_dict(), verification_code=code)
    conf.refresh_token = bc.credentials.get('refresh_token')
    conf.to_toml()

    auth_state = 'authorized'

    return redirect(url_for('index'))


@app.post('/event')
@basic_auth.required
def event():
    data = request.json
    if "eventKey" not in data:
        return "No event key provided."

    alliance = "red" if str(conf.team) in data['match']['redTeams'] else "blue"
    alliance_color = "rgb(225, 239, 252)" if alliance == "blue" else "rgb(255, 229, 229)"
    comment = f"<span style='background-color: {alliance_color};'>{data['match']['status']} for {data['match']['label']}. {conf.team} is {alliance}.</span>"

    bc_manager.post_event(comment)

    return ""


@app.post('/reset')
@basic_auth.required
def reset():
    global conf
    conf.account_id = None
    conf.client_id = None
    conf.client_secret = None
    conf.redirect_uri = None
    conf.refresh_token = None
    conf.project_id = None
    conf.msg_board_id = None
    conf.to_toml()

    return redirect(url_for('index'))


@app.post('/change_team')
@basic_auth.required
def change_team():
    global conf
    conf.team = int(request.form.get('team_num'))
    conf.to_toml()

    return redirect(url_for('index'))

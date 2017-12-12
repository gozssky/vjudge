import requests
import logging
from datetime import datetime
from manage import app, db, Problem, Role, User
from config import Config

logging.basicConfig(level=logging.INFO)

app.app_context().push()


def init_db():
    db.create_all()
    Role.insert_roles()
    admin = User.query.get(1) or User()
    admin.username = Config.FLASKY_ADMIN
    admin.password = '123456'
    db.session.add(admin)
    db.session.commit()
    admin.role_id = 3
    db.session.commit()


def crawl_problem():
    s = requests.session()
    url = Config.VJUDGE_REMOTE_URL + '/problems/'
    while url:
        r = s.get(url)
        for p in r.json()['problems']:
            oj_name = p['oj_name']
            problem_id = p['problem_id']
            problem = Problem.query.filter_by(oj_name=oj_name, problem_id=problem_id).first() or Problem()
            r2 = s.get('{}/problems/{}/{}'.format(Config.VJUDGE_REMOTE_URL, oj_name, problem_id))
            for attr in r2.json():
                if attr == 'last_update':
                    problem.last_update = datetime.fromtimestamp(r2.json()[attr])
                elif hasattr(problem, attr):
                    setattr(problem, attr, r2.json()[attr])
            db.session.add(problem)
            db.session.commit()
            logging.info('problem update: {}'.format(problem))
        url = r.json()['next']


if __name__ == '__main__':
    init_db()
    crawl_problem()

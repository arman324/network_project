import os.path
import torndb
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import os
from binascii import hexlify
import tornado.web
from tornado.options import define, options
import time

define("port", default=1105, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_database", default="tickets", help="database name")
define("mysql_user", default="arman", help="database user")
define("mysql_password", default="10101010", help="database password")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/signup", signup),
            (r"/sendTicket", sendTicket),
            (r"/getTicket", getTicket),
            (r"/retrieve", retrieve),
            (r"/closeticket", closeticket),
            (r"/changeStatusByAdmin", changeStatusByAdmin),
            (r"/response", response),
            (r".*", defaulthandler),
        ]

        settings = dict()
        super(Application, self).__init__(handlers, **settings)
        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def check_user(self,user):
        resuser = self.db.get("SELECT * from users where username = %s",user)
        if resuser:
            return True
        else :
            return False

    def check_retrieve(self, username, password):
        resuser = self.db.get("SELECT * from users where username = %s and password = %s", username, password)
        if resuser:
            return True
        else:
            return False
class response(BaseHandler):
    def post(self, *args, **kwargs):
        Token = self.get_argument('Token')
        id = self.get_argument('id')
        body = self.get_argument('body')
        user = self.db.get("SELECT * FROM users WHERE token = %s", Token)

        if not user:
            output = {'message': 'token is not available',
                      'code': '301'}
            self.write(output)
            return

        if user.role != 'admin':
            output = {'message': 'user is not admin, cannot access', 'code': '301'}
            self.write(output)
            return

        ticket = self.db.get("SELECT * from ticket where id = %s", int(id))
        if not ticket:
            output = {'message': 'ticket id is not available',
                      'code': '301'}
            self.write(output)
            return

        self.db.execute("UPDATE ticket SET response = %s  WHERE id = %s", body, id)
        self.db.execute("UPDATE ticket SET status = %s  WHERE id = %s", 'close', id)

        output = {'message': 'Response to Ticket With id -' + str(id) + '- Sent Successfully',
                  'code': 'OK'}
        self.write(output)



class changeStatusByAdmin(BaseHandler):
    def post(self, *args, **kwargs):
        Token = self.get_argument('Token')
        id = self.get_argument('id')
        statusUSER = self.get_argument('status')
        user = self.db.get("SELECT * FROM users WHERE token = %s", Token)

        if not user:
            output = {'message': 'it is not available',
                      'code': '301'}
            self.write(output)
            return

        if user.role != 'admin':
            output = {'message': 'user is not admin, cannot access',
                      'code': '301'}
            self.write(output)
            return

        ticket = self.db.get("SELECT * from ticket WHERE id = %s", int(id))
        if not ticket:
            output = {'message': 'it is not available',
                      'code': '301'}
            self.write(output)
            return

        if statusUSER == "close":
            self.db.execute("UPDATE ticket SET status = 'close'  where id = %s", id)
        elif statusUSER == "open":
            self.db.execute("UPDATE ticket SET status = 'open'  where id = %s", id)
        elif statusUSER == "in progress":
            self.db.execute("UPDATE ticket SET status = 'in progress'  where id = %s", id)

        output = {'message': 'changed successfully',
                  'code': '200'}
        self.write(output)
        return


class closeticket(BaseHandler):
    def post(self, *args, **kwargs):
        Token = self.get_argument('Token')
        id = self.get_argument('id')
        user = self.db.get("SELECT * FROM users WHERE token=%s", Token)

        if not user:
            output = {'message': 'it is not available',
                   'code': '301'}
            self.write(output)
            return

        ticket = self.db.get("SELECT * from ticket WHERE id = %s", int(id))
        if not ticket:
            output = {'message': 'it is not available',
                      'code': '301'}
            self.write(output)
            return

        if ticket.userid != user.id:
            output = {'message': 'cannot access', 'code': '301'}
            self.write(output)
            return

        self.db.execute("UPDATE ticket SET status= 'close' where id = %s",id)
        output ={'message' : 'changed successfully',
                 'code': '200'}
        self.write(output)
        return



class getTicket(BaseHandler):

    def post(self, *args, **kwargs):
        Token = self.get_argument('Token')
        user = self.db.get("SELECT * from users where token = %s",Token)

        if user.role == "admin":
            tickets = self.db.query("SELECT * from ticket")
            output = {'tickets': 'There are ' + str(len(tickets)) + ' Tickets',
                      'code': '200'}

            if len(tickets) != 0:
                for i in range(0, len(tickets)):
                    info = {'subject': tickets[i].subject,
                            'body': tickets[i].body,
                            'status': tickets[i].status,
                            'response': tickets[i].response,
                            'id': tickets[i].id}
                    output['block ' + str(i)] = info
                output['index'] = str(len(tickets))
                self.write(output)

            else:
                output = {'tickets': 'There are ' + str(len(tickets)) + ' Tickets',
                          'code': '301'}
                self.write(output)


        if user.role == "user":
            tickets = self.db.query("SElECT * from ticket where userId = %s", user.id)
            if(len(tickets) != 0):
                output = {'tickets': 'There are ' + str(len(tickets)) + ' Tickets',
                          'code': '200'}
                for i in range(0, len(tickets)):
                    info = {'subject': tickets[i].subject,
                            'body': tickets[i].body,
                            'status': tickets[i].status,
                            'response': tickets[i].response,
                            'id': tickets[i].id}
                    output['block ' + str(i)] = info
                output['index'] = str(len(tickets))
                self.write(output)

            else:
                output = {'tickets': 'There are ' + str(len(tickets)) + ' Tickets',
                          'code': '301'}
                self.write(output)


class sendTicket(BaseHandler):
    def post(self):
        token = self.get_argument('Token')
        subject = self.get_argument('subject')
        body = self.get_argument('body')

        user = self.db.get("SELECT id from users where token = %s", token)

        self.db.execute("INSERT INTO ticket (subject, body, status, userId, date, response)"
                        "VALUES (%s,%s,'open',%s,%s,'None')", subject, body, int(user.id),
                     time.strftime('%Y-%m-%d %H:%M:%S'))

        ticket_id = self.db.execute("SELECT LAST_INSERT_ID()")
        output = {'message': 'Ticket Sent Successfully',
                   'id': ticket_id,
                   'code': '200'}

        self.write(output)



class retrieve(BaseHandler):
    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        password = self.get_argument('password')

        if  self.check_retrieve(username, password):
            user = self.db.get("SELECT * from users where username = %s and password = %s", username, password)
            output = {'code': 'found',
                      'api': user.token,
                      'username': user.username}
            self.write(output)
        else:
            output = {'code': 'not found'}
            self.write(output)



class signup(BaseHandler):
    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        password = self.get_argument('password')
        firstname = self.get_argument('firstname')
        lastname = self.get_argument('lastname')
        role = self.get_argument('role')
        if not self.check_user(username):
            api_token = str(hexlify(os.urandom(16)))
            user_id = self.db.execute("INSERT INTO users (username, password, firstname, lastname, role, token) "
                                      "values (%s,%s,%s,%s,%s,%s) "
                                      , username, password, firstname, lastname, role, api_token)

            output = {'api':api_token,
                      'messsage': 'signed up successfully',
                      'code': '200'}

            self.write(output)
        else :
            output = {'message':'this username already exist', 'code': '301'}
            self.write(output)



class defaulthandler(BaseHandler):
    def get(self):
        user = self.db.get("SELECT * from users where username = 'arman'")
        self.write(user)

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
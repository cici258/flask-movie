from . import home
from flask import render_template, redirect, url_for, flash, session, request
from app.home.forms import RegisterForm, LoginForm, UserdetailForm, PwdForm, CommentForm
from app.models import User, Userlog, Preview, Tag, Movie, Comment, Moviecol
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import uuid
from app import db, app
from functools import wraps
import os
import datetime


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


# 登录装饰器
def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function

# 首页
@home.route("/<int:page>",methods=["GET"])
def index(page=None):
    tags = Tag.query.all()
    page_data = Movie.query
    tid = request.args.get("tid",0)
    if int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))
    star = request.args.get("star", 0)
    if int(star) != 0:
        page_data = page_data.filter_by(starnum=int(star))
    time = request.args.get("time", 0)
    if int(time) != 0:
        if int(time) == 1:
            page_data = page_data.order_by(Movie.addtime.desc())
        else:
            page_data = page_data.order_by(Movie.addtime.asc())
    pm = request.args.get("pm", 0)
    if int(pm) != 0:
        if int(pm) == 1:
            page_data = page_data.order_by(Movie.playnum.desc())
        else:
            page_data = page_data.order_by(Movie.playnum.asc())
    cm = request.args.get("cm", 0)
    if int(cm) != 0:
        if int(cm) == 1:
            page_data = page_data.order_by(Movie.commentnum.desc())
        else:
            page_data = page_data.order_by(Movie.commentnum.asc())

    if page is None:
        page = 1
    page = request.args.get("page",1)
    page_data = page_data.paginate(page=int(page),per_page=10)

    p = dict(
        tid=tid,
        star=star,
        time=time,
        pm=pm,
        cm=cm
    )
    return render_template("home/index.html",tags=tags,p=p,page_data=page_data)


# 登录
@home.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data["name"]).first()
        if user:
            if not user.check_pwd(data["pwd"]):
                flash("密码错误", "err")
                return redirect(url_for("home.login"))
        else:
            flash("账号不存在","err")
            return redirect(url_for("home.login"))
        session["user"] = user.name
        session["user_id"] = user.id
        userlog = Userlog(
            user_id=user.id,
            ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        return redirect(url_for("home.user", user=user))

    return render_template("home/login.html", form=form)


@home.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("id", None)
    return redirect(url_for("home.login"))


# 注册
@home.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            pwd=generate_password_hash(data["pwd"]),
            uuid=uuid.uuid4().hex
        )
        db.session.add(user)
        db.session.commit()
        flash("注册成功", "ok")
    return render_template("home/register.html", form=form)


# 会员
@home.route("/user", methods=["GET", "POST"])
@user_login_req
def user():
    form = UserdetailForm()
    user = User.query.get(int(session["user_id"]))
    form.face.validators = []
    if request.method == "GET":
        # 赋初值
        form.name.data = user.name
        form.phone.data = user.phone
        form.email.data = user.email
        form.face.data = user.face
        form.info.data = user.info

    if form.validate_on_submit():
        data = form.data
        if form.face.data != "":
            file_face = secure_filename(form.face.data.filename)
            if not os.path.exists(app.config["FACE_DIR"]):
                os.makedirs(app.config["FACE_DIR"])
                os.chmod(app.config["FACE_DIR"], "rw")
            user.face = change_filename(file_face)
            form.face.data.save(app.config["FACE_DIR"] + user.face)

        name_count = User.query.filter_by(name=data["name"]).count()
        if data["name"] != user.name and name_count == 1:
            flash("昵称已存在", "err")
            return redirect(url_for("home.user"))

        email_count = User.query.filter_by(name=data["email"]).count()
        if data["email"] != user.email and email_count == 1:
            flash("邮箱已存在", "err")
            return redirect(url_for("home.user"))

        phone_count = User.query.filter_by(name=data["phone"]).count()
        if data["phone"] != user.phone and phone_count == 1:
            flash("手机已存在", "err")
            return redirect(url_for("home.user"))

        user.name = data["name"]
        user.email = data["email"]
        user.phone = data["phone"]
        user.info = data["info"]
        db.session.add(user)
        db.session.commit()
        flash("修改成功", "ok")
        return redirect(url_for("home.user"))
    return render_template("home/user.html", form=form, user=user)


# 修改密码
@home.route("/pwd", methods=["GET", "POST"])
@user_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.get_or_404(int(session["user_id"]))
        if not user.check_pwd(data["oldpwd"]):
            flash("旧密码错误", "err")
            return redirect(url_for('home.pwd'))
        user.pwd = generate_password_hash(data["newpwd"])
        db.session.add(user)
        db.session.commit()
        flash("修改密码成功", "ok")
        return redirect(url_for('home.pwd'))
    return render_template("home/pwd.html", form=form)

# 评论记录
@home.route("/comments/<int:page>",methods=["GET","POST"])
@user_login_req
def comments(page=None):
    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == session["user_id"]
    ).order_by(
        User.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/comments.html",page_data=page_data)


# 登录日志
@home.route("/loginlog/<int:page>", methods=["GET", "POST"])
@user_login_req
def loginlog(page=None):
    if page is None:
        page = 1
    page_data = Userlog.query.join(
        User
    ).filter(
        User.id == Userlog.user_id
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/loginlog.html", page_data=page_data)

# 添加电影收藏
@home.route("/moviecol/add",methods=["GET"])
@user_login_req
def moviecol_add():
    mid = request.args.get("mid","")
    uid = request.args.get("uid", "")
    moviecol = Moviecol.query.filter_by(
        user_id=int(uid),
        movie_id=int(mid)
    ).count()
    if moviecol == 1:
        data = dict(ok=0)

    if moviecol == 0:
        moviecol = Moviecol(
            movie_id=int(mid),
            user_id=int(uid)
        )
        db.session.add(moviecol)
        db.session.commit()
        data = dict(ok=1)
    import json
    return json.dumps(data)


# 电影收藏
@home.route("/moviecol/<int:page>")
@user_login_req
def moviecol(page=None):
    if page is None:
        page = 1
    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == session["user_id"]
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page,per_page=10)
    return render_template("home/moviecol.html",page_data=page_data)



# 上映预告
@home.route("/animation")
def animation():
    data = Preview.query.all()
    return render_template("home/animation.html",data=data)

# 搜索
@home.route("/search/<int:page>")
def search(page=None):
    if page is None:
        page = 1
    key = request.args.get("key","")
    movie_count = Movie.query.filter(
        Movie.title.ilike("%" + key + "%")
    ).count()
    page_data = Movie.query.filter(
        Movie.title.ilike("%" + key + "%")
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page,per_page=10)
    return render_template("home/search.html",key=key,page_data=page_data,movie_count=movie_count)

# 电影播放
@home.route("/play/<int:id>/<int:page>",methods=["GET","POST"])  # 电影详情页
def play(id=None,page=None):
    movie = Movie.query.join(
        Tag
    ).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()

    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == movie.id,
        User.id == Comment.user_id
    ).order_by(
        User.addtime.desc()
    ).paginate(page=page, per_page=10)

    movie.playnum = movie.playnum + 1
    form = CommentForm()
    if "user" in session and form.validate_on_submit():
        data = form.data
        comment = Comment(
            content = data["content"],
            movie_id = movie.id,
            user_id = session["user_id"]
        )
        db.session.add(comment)
        db.session.commit()
        movie.commentnum = movie.commentnum + 1
        db.session.add(movie)
        db.session.commit()
        flash("添加评论成功","ok")
        return redirect(url_for('home.play',id=movie.id,page=1))
    db.session.add(movie)
    db.session.commit()
    return render_template("home/play.html",movie=movie,form=form,page_data=page_data)

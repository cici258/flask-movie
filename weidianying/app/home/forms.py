from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField, DateField, \
    SelectMultipleField, TextField
from wtforms.validators import DataRequired, ValidationError,EqualTo, Email, Regexp
from app.models import User


class RegisterForm(FlaskForm):
    name = StringField(
        label="昵称",
        validators=[
            DataRequired("请输入昵称")
        ],
        description="昵称",
        render_kw={
            "class": "form-control input-lg",
            "id": "input_name",
            "placeholder": "请输入昵称"
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码!")
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码!"
        }
    )
    repwd = PasswordField(
        label="确认密码",
        validators=[
            DataRequired("确认密码")
        ],
        description="确认密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "确认密码"
        }
    )
    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱"),
            Email("邮箱格式不正确")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入邮箱"
        }
    )
    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机"),
            Regexp("1[34578]\\d{9}",message="手机格式不正确")
        ],
        description="手机",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入手机"
        }
    )
    submit = SubmitField(
        '注册',
        render_kw={
            "class": "btn btn-lg btn-success btn-block"
        }
    )

    def validate_name(self,field):
        name = field.data
        count = User.query.filter_by(
            name=name
        ).count()
        if count == 1:
            raise ValidationError("昵称已存在！")

    def validate_email(self,field):
        email = field.data
        count = User.query.filter_by(
            email=email
        ).count()
        if count == 1:
            raise ValidationError("邮箱已存在！")

    def validate_phone(self,field):
        phone = field.data
        count = User.query.filter_by(
            phone=phone
        ).count()
        if count == 1:
            raise ValidationError("手机号已存在！")

class LoginForm(FlaskForm):
    name = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号！")
        ],
        description="账号",
        render_kw={
            "class":"form-control input-lg",
            "placeholder": "请输入账号!"
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码!")
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码!"
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-lg btn-success btn-block"
        }
    )

    def validate_account(self, field):
        account = field.data
        admin = User.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError("账号不存在")


class UserdetailForm(FlaskForm):
    name = StringField(
        label="昵称",
        validators=[
            DataRequired("请输入昵称！")
        ],
        description="昵称",
        render_kw={
            "class": "form-control",
            "placeholder": "昵称"
        }
    )
    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱!"),
            Email("邮箱格式不正确!")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control",
            "placeholder": "邮箱"
        }
    )
    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机"),
            Regexp("1[34578]\\d{9}", message="手机格式不正确")
        ],
        description="手机",
        render_kw={
            "class": "form-control",
            "placeholder": "手机"
        }
    )
    face = FileField(
        label="头像",
        validators=[
            DataRequired("请上传头像！")
        ],
        description="头像"
    )
    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("请输入简介！")
        ],
        description="简介",
        render_kw={
            "class":"form-control",
            "rows":10
        }
    )
    submit = SubmitField(
        '保存修改',
        render_kw={
            "class": "btn btn-success"
        }
    )

class PwdForm(FlaskForm):
    oldpwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("请输入旧密码!")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码!"
        }
    )
    newpwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("请输入新密码!")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码!"
        }
    )
    submit = SubmitField(
        '修改密码',
        render_kw={
            "class": "btn btn-success"
        }
    )


class CommentForm(FlaskForm):
    content = TextAreaField(
        label="内容",
        validators=[
            DataRequired("请输入内容")
        ],
        description="内容",
        render_kw={
            "id": "input_content"
        }
    )
    submit = SubmitField(
        '提交评论',
        render_kw={
            "class":"btn btn-success",
            "id": "btn sub"
        }
    )

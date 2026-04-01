import re
import time
from flask import current_app, request, jsonify, make_response
from . import passport_blue
from ... import redis_store, constants
from ...utils.captcha.captcha import captcha
from ...utils.response_code import RET, error_map

from info.libs.alibabacloud_dypnsapi.sms import SmsVerification
from info import db
from info.models import User


@passport_blue.route('/sms_code', methods=['POST'])
def sms_code():
    """发送短信验证码接口"""
    try:
        # 获取请求参数
        data = request.get_json()
        if not data:
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

        phone = data.get('mobile')
        image_code = data.get('image_code')
        image_code_id = data.get('image_code_id')

        # 参数完整性校验
        if not all([phone, image_code, image_code_id]):
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

        # 手机号格式校验
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

        # 4从 Redis 获取图片验证码
        try:
            redis_image_code_bytes = redis_store.get(f'image_code:{image_code_id}')
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

        # 5检查验证码是否存在
        if not redis_image_code_bytes:
            return jsonify(errno=RET.DATAEXIST, errmsg=u'图片验证码已过期，请刷新重试')

        # 6比较验证码
        if not redis_image_code_bytes or redis_image_code_bytes.lower() != image_code.lower():
            return jsonify(errno=RET.DATAERR, errmsg=error_map[RET.DATAERR])

        # 删除已使用的图片验证码
        try:
            redis_store.delete(f'image_code:{image_code_id}')
        except Exception as e:
            current_app.logger.error(e)

        # 8短信频率限制
        sms_limit_key = f'sms_limit:{phone}'
        try:
            last_time = redis_store.get(sms_limit_key)
            if last_time and time.time() - float(last_time) < 60:
                return jsonify(errno=RET.REQERR, errmsg=error_map[RET.REQERR])
        except Exception as e:
            current_app.logger.error(e)

        # 9调用短信发送模块
        try:
            success, msg, code = SmsVerification.send_verification_code(phone)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg=u'短信服务异常')

        if not success:
            return jsonify(errno=RET.THIRDERR, errmsg=msg)

        # 10存储短信验证码
        sms_code_key = f'sms_code:{phone}'
        try:
            redis_store.setex(sms_code_key, constants.SMS_CODE_REDIS_EXPIRES, code)
            redis_store.setex(sms_limit_key, constants.SMS_CODE_REDIS_FREQUENCY_LIMIT, time.time())
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg=u'存储验证码失败')

        return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.SERVERERR, errmsg=error_map[RET.SERVERERR])

@passport_blue.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    try:
        # 获取请求参数
        data = request.get_json()
        if not data:
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

        phone = data.get('mobile')
        sms_code = data.get('sms_code')
        password = data.get('password')

        # 参数完整性校验
        if not all([phone, sms_code, password]):
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

        # 从 Redis 获取短信验证码
        try:
            redis_sms_code = redis_store.get(f'sms_code:{phone}')
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='短信验证码获取失败')

        # 验证短信验证码是否存在
        if not redis_sms_code:
            return jsonify(errno=RET.NODATA, errmsg='短信验证码已过期，请重新获取')

        # 验证短信验证码是否正确（注意：redis 存储的是字符串）
        if redis_sms_code != sms_code:
            return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')

        # 删除已使用的短信验证码
        try:
            redis_store.delete(f'sms_code:{phone}')
        except Exception as e:
            current_app.logger.error(e)

        # 检查手机号是否已被注册
        try:
            user_exists = User.query.filter_by(mobile=phone).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库查询失败')

        if user_exists:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已注册')

        # 创建用户对象并设置属性
        user = User()
        user.nick_name = phone          # 默认使用手机号作为昵称
        user.mobile = phone
        user.password_hash = password        # 使用属性 setter，自动哈希
        user.signature = '该用户很懒，什么都没写'

        # 保存用户到数据库
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg='用户注册失败')

        # 返回成功响应
        return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.SERVERERR, errmsg=error_map[RET.SERVERERR])


@passport_blue.route('/image_code')
def image_code():
    cur_id = request.args.get('cur_id')
    if not cur_id:
        return jsonify(errno=400, errmsg='缺少 cur_id 参数'), 400

    try:
        # 生成验证码
        _, text, image_data = captcha.generate_captcha()
        # 存储验证码文本
        redis_store.set(f'image_code:{cur_id}', text)

        # 删除旧验证码
        pre_id = request.args.get('pre_id')
        if pre_id:
            redis_store.delete(f'image_code:{pre_id}')

        # 返回图片
        response = make_response(image_data)
        response.headers['Content-Type'] = 'image/png'
        return response
    except Exception as e:
        import logging
        logging.error(e)
        return jsonify(errno=500, errmsg='验证码生成失败'), 500


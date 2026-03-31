from flask import request, make_response, jsonify

from . import passport_blue
from ... import redis_store
from ...utils.captcha.captcha import captcha



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
import random
import json
import os
from alibabacloud_dypnsapi20170525.client import Client as DypnsapiClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dypnsapi20170525 import models as dypnsapi_20170525_models
from alibabacloud_tea_util import models as util_models

class SmsVerification:
    @staticmethod
    def create_client() -> DypnsapiClient:
        config = open_api_models.Config(
            access_key_id=os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID'),
            access_key_secret=os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
        )
        config.endpoint = 'dypnsapi.aliyuncs.com'
        return DypnsapiClient(config)

    @staticmethod
    def send_verification_code(phone_number: str) -> tuple:
        """
        发送验证码短信，返回 (success, message, code)
        - success: bool 是否成功
        - message: str 结果描述
        - code: str 生成的验证码（成功时返回）
        """
        client = SmsVerification.create_client()
        # 生成6位随机验证码
        code = str(random.randint(100000, 999999))
        minutes_valid = 5   # 模板中的 ${min}

        send_request = dypnsapi_20170525_models.SendSmsVerifyCodeRequest(
            phone_number=phone_number,
            sign_name='云渚科技验证平台',          # 替换成你实际能用的签名
            template_code='100001',              # 替换成你的模板CODE
            template_param=json.dumps({
                "code": code,
                "min": minutes_valid
            }),
        )

        runtime = util_models.RuntimeOptions()
        try:
            response = client.send_sms_verify_code_with_options(send_request, runtime)
            if response.body.code == 'OK':
                return True, "发送成功", code
            else:
                return False, response.body.message, None
        except Exception as error:
            return False, error, None
import os
import random
import json
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
    def send_verification_code(phone_number: str) -> None:
        client = SmsVerification.create_client()

        # 生成6位验证码，并设定有效分钟数
        code = str(random.randint(100000, 999999))
        minutes_valid = 5

        send_request = dypnsapi_20170525_models.SendSmsVerifyCodeRequest(
            phone_number=phone_number,
            sign_name='云渚科技验证平台',
            template_code='100001',  # 模板CODE
            template_param=json.dumps({
                "code": code,
                "min": minutes_valid
            }),
        )

        runtime = util_models.RuntimeOptions()
        try:
            response = client.send_sms_verify_code_with_options(send_request, runtime)
            if response.body.code == 'OK':
                print(f"验证码 {code} 已成功发送到 {phone_number}")
            else:
                print(f"发送失败: {response.body.message}")
        except Exception as error:
            if hasattr(error, 'data') and error.data:
                print(f"诊断地址: {error.data.get('Recommend')}")


if __name__ == '__main__':
    my_phone = '15877151960'
    SmsVerification.send_verification_code(my_phone)
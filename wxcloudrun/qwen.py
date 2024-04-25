import random
from http import HTTPStatus
from dashscope import Generation  # 建议dashscope SDK 的版本 >= 1.14.0
import os
import dashscope


def call_with_messages(question):
    # os.environ['DASHSCOPE_API_KEY'] = 'sk-802a9fe7c465438697be02063ccc1b01'

    dashscope.api_key = 'sk-802a9fe7c465438697be02063ccc1b01'
    """
    使用给定的消息列表调用Generation.call函数，并根据响应状态打印结果或错误信息。
    
    该函数不接受参数，并且没有返回值。
    """
    # 初始化消息列表，包含系统消息和用户消息
    messages = [{'role': 'system', 'content': '你是“千里灵犀”智能问答助手，具备客服的专业素质，你致力于提供准确无误的答案。对于非法或不适宜的问题，我将不予回答，始终坚持合法、合规及正面交流原则。'},
                {'role': 'user', 'content': question}]
    
    # 调用Generation.call函数，设置模型为"qwen-turbo"，使用随机数种子，将输出格式设置为"message"
    response = Generation.call(model="qwen-turbo",
                               messages=messages,
                               seed=random.randint(1, 10000),
                               result_format='message',max_tokens=600,enable_search=True)
    
    # 根据响应状态码打印结果或错误信息
    if response.status_code == HTTPStatus.OK:
        return response
    else:
        # 打印错误请求ID、状态码、错误码和错误信息
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))
        return None


# if __name__ == '__main__':
#     res  =call_with_messages("介绍香港移民政策")
#     print(res.output.choices[0].message.content)
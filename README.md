# yuzhenjiang_chatbot
姜小羽对话机器人

## 使用说明
1. python3.6.2
2. 安装依赖 pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
3. 下载模型文件，放在models/GPT2Chatbot目录下，功能测试模型可以见下表
4. python run_server.py --port ${PORT} 指定端口启动服务

|模型 | 百度网盘 |GoogleDrive |模型描述|
|---------|--------|--------|--------|
|dialogue_model | [百度网盘【提取码:osi6】](https://pan.baidu.com/s/1qDZ24VKLBU9GKARX9Ev65g) | [GoogleDrive](https://drive.google.com/drive/folders/1Ogz3eapvtvdY4VUcY9AEwMbNRivLKhri?usp=sharing) |使用闲聊语料训练了40个epoch，最终loss在2.0左右，继续训练的话，loss应该还能继续下降。|
|mmi_model | [百度网盘【提取码:1j88】](https://pan.baidu.com/s/1ubXGuEvY8KmwEjIVTJVLww) | [GoogleDrive](https://drive.google.com/drive/folders/1oWgKXP6VG_sT_2VMrm0xL4uOqfYwzgUP?usp=sharing) |以dialogue_model作为预训练模型，使用上述闲聊语料，训练了40个epoch，最终loss在1.8-2.2之间，继续训练的话，loss也能继续下降。|

## 接口说明
路径：/api/chatroom/v1

* 传入参数

参数名称 | 参数类型 | 示例 | 说明
---- | ---- | ---- | ----
sessionId | Long | 60018025 | 通过session_Id来区别用户，记录用户对话历史
text | String | "你好吗"

* 返回参数
```json
{
    "status": 1, //成功为1, 失败为0
    "data": {
        "sessionId": 20005, 
        "input": "你是谁",
        "output": "我是你的小宝贝啊！" //这一轮问对话生成的回答结果
    },
    "message": "success"  //接口信息，成功为success
}
```

## 模型与数据

使用基于GPT-2网络的mmi对话生成模型  
数据来自于姜贞羽对话语料
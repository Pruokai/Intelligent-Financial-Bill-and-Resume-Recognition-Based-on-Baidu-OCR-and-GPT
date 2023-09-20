# 财务票据识别
## 1.安装依赖库pandas，urllib，base64，json，datetime，time。
## 2.百度智能云API创建与获取
### 2.1 进入[百度智能云智能财务票据识别](https://cloud.baidu.com/product/ocr/multiple_invoice)，注册登录后，根据教程创建实例获取client_id和client_secret。
### 2.2 将client_id和client_secret放入财务票据识别.py代码中，代码内直接有获取access_token的代码，不需要额外去获取。
## 3.运行代码
### 3.1 代码内被我删减了一部分有关公司内容的东西，运行时可能会报错，请自行修改。
### 3.2 该代码是根据公司需求获取所需内容，增值税发票，汽车票，火车票等，如需增添其他内容，希望自行查看[智能财务票据识别技术文档](https://cloud.baidu.com/doc/OCR/s/7ktb8md0j)进行学习与修改。


# 发票识别
## 1.安装依赖库pandas，re，urllib，openai，docx2pdf，requests。
## 2.百度智能云API创建与获取
### 2.1 进入[百度智能云通用文字识别](https://cloud.baidu.com/product/ocr/general)，注册登录后，根据教程创建实例获取client_id和client_secret。
### 2.2 将client_id和client_secret放入简历文字提取.py代码中，代码内直接有获取access_token的代码，不需要额外去获取。
## 3.GPT的API获取
### 3.1 注册[chatgpt](https://chat.openai.com/)账号，申请API，这一部分是需要付费的。
### 3.2 将申请的APIkey放入GPT识别.py中。
## 4.运行代码
### 4.1 运行简历文字提取.py，基本支持各个类别简历的输入，pdf,word,jpg等。
### 4.2 运行GPT识别.py，可以根据自己的需求来自己定制prompt，以达到想要的结果。

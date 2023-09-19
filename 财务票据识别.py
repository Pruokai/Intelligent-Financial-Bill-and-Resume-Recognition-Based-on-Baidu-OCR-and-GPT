import os
import pandas as pd
import urllib.parse
import urllib
import urllib.request
import base64
import json
from datetime import datetime
import time

# client_id 为官网获取的AK， client_secret 为官网获取的SK
client_id = 'your_client_id'
client_secret = 'your_client_secret'

# 获取token
def get_token():
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + client_id + '&client_secret=' + client_secret
    request = urllib.request.Request(host)
    request.add_header('Content-Type', 'application/json; charset=UTF-8')
    response = urllib.request.urlopen(request)
    token_content = response.read()
    if token_content:
        token_info = json.loads(token_content)
        token_key = token_info['access_token']
    return token_key


#从API响应中提取相关信息的函数
def extract_invoice_info(data):
    def remove_unwanted_text(text):
        return text.split(':', 1)[-1].strip()

    words_result = data['words_result']
    type = words_result[0]['type']
    #增值税发票
    if 'vat_invoice' in type:
        result = words_result[0]['result']
        # Check if 'InvoiceCode' key exists in the result
        if 'InvoiceCode' in result:
            # Extract the invoice code value if it's available
            invoice_code = result['InvoiceCode']
            if invoice_code:
                invoice_code = invoice_code[0]['word'].strip("[]{}'")
            else:
                invoice_code = ""
        else:
            # Handle the case where 'InvoiceCode' is not available
            invoice_code = ""
        invoice_num = result['InvoiceNum'][0]['word']
        purchaser_name = result['PurchaserName'][0]['word']
        seller_name = result['SellerName'][0]['word']
        # Removing unwanted text from the '我方单位' and '对方单位' columns
        purchaser_name = remove_unwanted_text(purchaser_name)
        seller_name = remove_unwanted_text(seller_name)
        date = result['InvoiceDate'][0]['word']
        pre_tax_amount = result['TotalAmount'][0]['word']
        total_tax = result['TotalTax'][0]['word']
        invoice_type = result['InvoiceType'][0]['word']
        if '电子' in invoice_type and '专' in invoice_type:
            invoice_type = '电子专票'
        elif '电子' in invoice_type and '普' in invoice_type:
            invoice_type = '电子普票'
        elif '专' in invoice_type:
            invoice_type = '纸质专票'
        elif '普' in invoice_type:
            invoice_type = '纸质普票'

        remarks = result.get('Remarks', [])  # Get the 'Remarks' key or empty list if not available
        if remarks:
            remarks = remarks[0]['word'].strip("[]{}'")  # Extract the remark value if it's available
        else:
            remarks = ""  # Set to empty string if the remark is not available

        try:
            total_tax = float(total_tax)
        except ValueError:
            total_tax = 0.0

        try:
            pre_tax_amount = float(pre_tax_amount)
        except ValueError:
            pre_tax_amount = 0.0
        taxes = result['CommodityTaxRate']
        taxes = ' '.join([item['word'] for item in taxes]).replace('[', '').replace(']', '').replace('\'', '')

        invoice_content = result['CommodityName']
        invoice_content = ' '.join([item['word'] for item in invoice_content]).replace('[', '').replace(']', '').replace('\'', '')
        if "餐饮" in invoice_content or "运输" in invoice_content:
            invoice_purpose = "员工报销"
        else:
            invoice_purpose = "业务发票"

        # 不含税额
        total_amount = pre_tax_amount + total_tax

        return date, invoice_code, invoice_num, purchaser_name, seller_name, pre_tax_amount, taxes, total_tax, total_amount, invoice_content, invoice_type, '', '', '', invoice_purpose, remarks
    #汽车票
    elif 'taxi_receipt' in type:
        result = words_result[0]['result']
        invoice_code = result['InvoiceCode'][0]['word']
        invoice_num = result['InvoiceNum'][0]['word']
        date = result['Date'][0]['word']
        total_amount = result['Fare'][0]['word']
        total_amount = total_amount.replace('￥', '').replace('元', '')

        return date,invoice_code,invoice_num,'','','','','',total_amount,'','出租车发票','','','','员工报销',''
    #火车票
    elif 'train_ticket' in type:
        result = words_result[0]['result']
        invoice_code = result['ticket_num'][0]['word']
        date = result['date'][0]['word']
        total_amount = result['ticket_rates'][0]['word']
        total_amount = total_amount.replace('￥', '').replace('元', '')
        name = result['name'][0]['word']
        return date,invoice_code,'','',name,'','','',total_amount,'','火车票','','','','员工报销',''
    #通用机打印发票
    elif 'printed_invoice' in type:
        result = words_result[0]['result']
        if 'InvoiceCode' in result:
            # Extract the invoice code value if it's available
            invoice_code = result['InvoiceCode']
            if invoice_code:
                invoice_code = invoice_code[0]['word'].strip("[]{}'")
            else:
                invoice_code = ""
        else:
            # Handle the case where 'InvoiceCode' is not available
            invoice_code = ""
        invoice_num = result['InvoiceNum'][0]['word']
        purchaser_name = result['PurchaserName'][0]['word']
        if 'SellerName' in result:
            # Extract the invoice code value if it's available
            seller_name = result['SellerName']
            if seller_name:
                seller_name = seller_name[0]['word']
            else:
                seller_name = ""
        else:
            # Handle the case where 'InvoiceCode' is not available
            invoice_code = ""
        # Removing unwanted text from the '我方单位' and '对方单位' columns
        purchaser_name = remove_unwanted_text(purchaser_name)
        seller_name = remove_unwanted_text(seller_name)
        date = result['InvoiceDate'][0]['word']
        total_amount = result['AmountInFiguers'][0]['word']
        invoice_type = result['InvoiceType'][0]['word']
        try:
            total_amount = float(total_amount)
        except ValueError:
            total_amount = 0.0

        invoice_content = result['CommodityName']
        invoice_content = ' '.join([item['word'] for item in invoice_content]).replace('[', '').replace(']','').replace('\'', '')
        if "餐饮" in invoice_content or "运输" in invoice_content:
            invoice_purpose = "员工报销"
        else:
            invoice_purpose = "业务发票"



        return date, invoice_code, invoice_num, purchaser_name, seller_name, '', '', '', total_amount, invoice_content, invoice_type, '','','',invoice_purpose,''
    #定额发票
    elif 'quota_invoice' in type:
        result = words_result[0]['result']
        if 'invoice_code' in result:
            # Extract the invoice code value if it's available
            invoice_code = result['invoice_code']
            if invoice_code:
                invoice_code = invoice_code[0]['word'].strip("[]{}'")
            else:
                invoice_code = ""
        else:
            # Handle the case where 'InvoiceCode' is not available
            invoice_code = ""
        invoice_num = result['invoice_number'][0]['word']
        total_amount = result['invoice_rate'][0]['word']
        invoice_type = result['ServiceType'][0]['word']
        try:
            total_amount = float(total_amount)
        except ValueError:
            total_amount = 0.0


        return '', invoice_code, invoice_num, '', '', '', '', '', total_amount, '', invoice_type, '', '', '', '员工报销', ''


#处理文件夹中所有发票的功能
def process_invoice_file(file_path, file_type, access_token):
    if file_type == 'image':
        # Process image files
        with open(file_path, 'rb') as f:
            img = base64.b64encode(f.read())

        # Set the parameters for image processing
        params = {
            'image': img,
            'show': 'true'
        }
    elif file_type == 'pdf':
        # Process PDF files
        with open(file_path, 'rb') as f:
            pdf_file = base64.b64encode(f.read())

        # Set the parameters for PDF processing
        params = {
            'pdf_file': pdf_file,
            'show': 'true'
        }

    params = urllib.parse.urlencode(params).encode("utf-8")

    # Call the Baidu OCR API
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/multiple_invoice?access_token=" + access_token
    request = urllib.request.Request(url=request_url, data=params)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    response = urllib.request.urlopen(request)
    content = response.read()
    if content:
        content = content.decode('utf-8')
        data = json.loads(content)

        try:
            invoice_info = extract_invoice_info(data)
        except KeyError as e:
            print(f"Failed to recognize invoice from {file_path}: {e}")
            # Add the image details to the '备注' column
            invoice_info = (
                None, None, None, None, None, None, None, None, None, None, None, '', '', '', '',
                file_path,
            )

        return invoice_info

    return None



def convert_to_date_string(date_str):
    if date_str is None:
        return None

    try:
        # Try converting the date using the original format
        date_obj = datetime.strptime(date_str, '%Y年%m月%d日')
    except ValueError:
        try:
            # If the original format fails, try converting with the format for car tickets
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            # If both formats fail, set the date to None
            return None

    return date_obj.strftime('%Y年%m月%d日')







def process_img_invoices(folder_path, access_token):
    invoice_info_list = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(folder_path, filename)
            invoice_info = process_invoice_file(file_path, 'image', access_token)
            if invoice_info:
                # 检查invoice_info是否已存在于列表中
                if invoice_info not in invoice_info_list:
                    invoice_info_list.append(invoice_info)

                # 在连续API调用之间引入0.5秒的延迟
                time.sleep(0.5)
        elif filename.lower().endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            invoice_info = process_invoice_file(file_path, 'pdf', access_token)
            if invoice_info:
                # 检查invoice_info是否已存在于列表中
                if invoice_info not in invoice_info_list:
                    invoice_info_list.append(invoice_info)

                # 在连续API调用之间引入0.5秒的延迟
                time.sleep(0.5)
    return invoice_info_list

def determine_invoice_type(row):
    purchaser_keywords = ['公司名字']
    seller_keywords = []  # Add any keywords for the seller if needed

    try:
        purchaser = any(keyword in row['我方单位'] for keyword in purchaser_keywords)
        seller = any(keyword in row['对方单位'] for keyword in seller_keywords)
    except TypeError:
        # Handle the case where '我方单位' or '对方单位' is None
        purchaser = False
        seller = False

    if purchaser:
        return '进项发票'
    elif seller:
        return '销项发票'



def process_folder_invoices(folder_path, output_file):
    access_token = get_token()

    # Process img invoices
    img_invoices = process_img_invoices(folder_path, access_token)

    columns = [
        '开票日期', '发票代码', '发票号码', '我方单位', '对方单位', '不含税额', '税率', '税额',
        '金额', '发票内容', '发票类型', '进销属性', '申请人', '申请人部门', '发票用途', '备注',
    ]
    df = pd.DataFrame(img_invoices, columns=columns)

    # Convert the '开票日期' column to date string in the original format
    df['开票日期'] = df['开票日期'].apply(convert_to_date_string)

    # Sort the DataFrame by the '开票日期' column
    df.sort_values(by='开票日期', ascending=True, inplace=True)

    # Determine the '进销属性' based on keywords
    df['进销属性'] = df.apply(determine_invoice_type, axis=1)
    df.to_excel(output_file, index=False)

# Call the function and specify the folder path and output file name
process_folder_invoices('发票/test0', '8.0.xlsx')

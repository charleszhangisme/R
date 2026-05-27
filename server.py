
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import akshare as ak
import time
import os

app = Flask(__name__)
CORS(app)

# 基金数据缓存
fund_cache = {}
cache_time = 10  # 缓存时间（秒）

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/fund/&lt;code&gt;')
def get_fund_data(code):
    """获取单个基金数据"""
    try:
        # 尝试从东方财富LOF行情
        try:
            lof_df = ak.fund_lof_spot_em()
            fund_data = lof_df[lof_df['代码'] == code].to_dict('records')
            if fund_data:
                return jsonify({
                    'code': fund_data[0]['代码'],
                    'name': fund_data[0]['名称'],
                    'current_price': float(fund_data[0]['最新价']),
                    'latest_net_value': float(fund_data[0]['净值']),
                    'premium_rate': float(fund_data[0]['折价率']),
                    'net_value_date': fund_data[0]['净值日期'],
                    'type': 'LOF'
                })
        except:
            pass
        
        # 如果LOF没有，尝试ETF
        try:
            etf_df = ak.fund_etf_spot_em()
            fund_data = etf_df[etf_df['代码'] == code].to_dict('records')
            if fund_data:
                return jsonify({
                    'code': fund_data[0]['代码'],
                    'name': fund_data[0]['名称'],
                    'current_price': float(fund_data[0]['最新价']),
                    'latest_net_value': float(fund_data[0]['IOPV']),
                    'premium_rate': float(fund_data[0]['折价率']),
                    'net_value_date': fund_data[0]['净值日期'],
                    'type': 'ETF'
                })
        except:
            pass
        
        # 尝试获取天天基金数据
        try:
            fund_df = ak.fund_etf_sina_em(code)
            if fund_df:
                return jsonify({
                    'code': code,
                    'name': fund_df.get('名称', ''),
                    'current_price': float(fund_df.get('现价', 0)),
                    'latest_net_value': float(fund_df.get('净值', 0)),
                    'premium_rate': float(fund_df.get('溢价率', 0)),
                    'net_value_date': '',
                    'type': 'Fund'
                })
        except:
            pass
        
        return jsonify({'error': '基金数据获取失败'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/funds/refresh')
def refresh_all_funds():
    """刷新所有基金数据（获取最新行情"""
    return jsonify({'message': 'OK'})

if __name__ == '__main__':
    print('启动服务器...')
    print('访问地址: http://localhost:5001')
    print('按 Ctrl+C 停止服务器')
    app.run(host='0.0.0.0', port=5001, debug=True)

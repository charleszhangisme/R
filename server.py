
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import akshare as ak
import os

app = Flask(__name__)
CORS(app)

# 获取当前文件所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    """提供主页面"""
    try:
        return send_from_directory(BASE_DIR, 'index.html')
    except:
        return "index.html 文件未找到，请确保与 server.py 在同一目录下", 404

@app.route('/api/fund/<code>')
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
        except Exception as e:
            print(f"LOF数据获取失败: {e}")
        
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
        except Exception as e:
            print(f"ETF数据获取失败: {e}")
        
        return jsonify({'error': f'未找到基金代码 {code} 的数据'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/funds/batch', methods=['POST'])
def get_batch_funds():
    """批量获取基金数据"""
    from flask import request
    codes = request.json.get('codes', [])
    results = []
    
    for code in codes:
        try:
            # LOF
            try:
                lof_df = ak.fund_lof_spot_em()
                fund_data = lof_df[lof_df['代码'] == code].to_dict('records')
                if fund_data:
                    results.append({
                        'code': fund_data[0]['代码'],
                        'name': fund_data[0]['名称'],
                        'current_price': float(fund_data[0]['最新价']),
                        'latest_net_value': float(fund_data[0]['净值']),
                        'premium_rate': float(fund_data[0]['折价率']),
                        'net_value_date': fund_data[0]['净值日期'],
                        'type': 'LOF'
                    })
                    continue
            except:
                pass
            
            # ETF
            try:
                etf_df = ak.fund_etf_spot_em()
                fund_data = etf_df[etf_df['代码'] == code].to_dict('records')
                if fund_data:
                    results.append({
                        'code': fund_data[0]['代码'],
                        'name': fund_data[0]['名称'],
                        'current_price': float(fund_data[0]['最新价']),
                        'latest_net_value': float(fund_data[0]['IOPV']),
                        'premium_rate': float(fund_data[0]['折价率']),
                        'net_value_date': fund_data[0]['净值日期'],
                        'type': 'ETF'
                    })
                    continue
            except:
                pass
        except Exception as e:
            print(f"获取基金 {code} 失败: {e}")
    
    return jsonify(results)

if __name__ == '__main__':
    print('=' * 50)
    print('基金溢价率计算工具服务器')
    print('=' * 50)
    print(f'index.html 路径: {os.path.join(BASE_DIR, "index.html")}')
    print(f'访问地址: http://localhost:5001')
    print('按 Ctrl+C 停止服务器')
    print('=' * 50)
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)

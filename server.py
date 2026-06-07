import http.server
import urllib.request
import urllib.parse
import json
import re

PORT = 8977

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 代理网易云搜索
        if self.path.startswith('/api/search?'):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            keywords = q.get('s', [''])[0]
            if not keywords:
                self.send_json({'error': 'need s param'}, 400)
                return
            
            url = f'https://music.163.com/api/search/get?type=1&s={urllib.parse.quote(keywords)}&limit=15'
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36',
                    'Referer': 'https://music.163.com/',
                }
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = resp.read()
                    self.send_json(json.loads(data))
            except Exception as e:
                self.send_json({'error': str(e)}, 502)
            return

        # 代理获取歌曲播放URL
        if self.path.startswith('/api/url?'):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            sid = q.get('id', [''])[0]
            if not sid:
                self.send_json({'error': 'need id param'}, 400)
                return
            
            url = f'https://music.163.com/api/song/enhance/player/url?id={sid}&br=128000'
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36',
                    'Referer': 'https://music.163.com/',
                }
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = resp.read()
                    self.send_json(json.loads(data))
            except Exception as e:
                self.send_json({'error': str(e)}, 502)
            return

        # 其他静态文件
        return super().do_GET()

    def send_json(self, obj, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def log_message(self, format, *args):
        pass  # 安静一点

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), ProxyHandler)
    print(f'🎵 Music Share Server → http://localhost:{PORT}')
    server.serve_forever()

import requests
import json

# 這裡先寫死一組你的資料，之後可以改成別人的
payload = {
    "name": "YUCHIAOCHUN",
    "birth": "1983-09-08",
    "gender": "F",
}

# 呼叫你自己的 API
resp = requests.post(
    "http://127.0.0.1:8000/api/v1/calc",
    json=payload,
    timeout=10,
)

print("狀態碼:", resp.status_code)
print("原始回應文字:", resp.text)

# 如果確定有回到 JSON，就解析出來
data = resp.json()
numbers = data["numbers"]

print("\n==== 喬鈞文化數字核心 ====")
print("生命道路 Life Path :", numbers["life_path"])
print("命運數 Destiny     :", numbers["destiny"])
print("靈魂數 Soul        :", numbers["soul"])
print("人格數 Personality :", numbers["personality"])
print("成熟數 Maturity    :", numbers["maturity"])

from locust import HttpUser, TaskSet, task, between

class QueryTaskSet(TaskSet):
    @task
    def query_api(self):
        # 模拟请求数据
        payload = {
            "query": "What are the regulations on pineapple production in Benin?",
        }
        # 发送 POST 请求到目标 API
        with self.client.post("/query", json=payload, catch_response=True) as response:
            # 验证响应状态码是否为 200
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code {response.status_code}")

class QueryUser(HttpUser):
    # 定义用户行为
    tasks = [QueryTaskSet]
    # 每个用户请求的等待时间（随机 1 到 5 秒）
    wait_time = between(1, 5)
    # API 基础 URL
    host = "https://eej22ko8bc.execute-api.eu-north-1.amazonaws.com/newstage"

## locust -f test_highconcurrency.py

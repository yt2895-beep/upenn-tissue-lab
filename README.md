
## 运行截图
![Swagger UI](docs/swagger.png)
![前端上传页](docs/frontend.png)

## 如何扩展至 10× 用户
- 文件存 S3 + 预签名 URL 直传，后端只负责任务调度  
- Celery + Redis 队列横向扩容 worker 容器  
- viewer 静态部署到 Vercel/CloudFront，边缘缓存  

## 测试与监控
- 单元：pytest 覆盖 `/jobs` API；jest 测试前端组件  
- E2E：Playwright 脚本上传 DICOM → 断言进度条 100%  
- 生产：Prometheus `/metrics` + Grafana 看板，任务失败率 >5% 报警  

## Screenshots
![Swagger UI](docs/swagger.png)<img width="446" height="240" alt="image" src="https://github.com/user-attachments/assets/282c1c38-932a-4d84-ac35-c7f3158e9afd" />

![Frontend Upload](docs/frontend.png)

## Scaling to 10× Users
- Store files in S3 with pre-signed URLs; backend only schedules tasks  
- Horizontally scale Celery workers with Redis queue  
- Deploy viewer to Vercel/CloudFront for edge caching  

## Testing & Monitoring
- Unit: pytest for `/jobs` API; jest for React components  
- E2E: Playwright script uploads DICOM and asserts 100% progress  
- Prod: Prometheus `/metrics` + Grafana dashboard; alert if failure rate >5%  

## 30s Demo Video
[Watch on Loom](https://www.loom.com/share/f051cfbbc0a248fabce75ac4b880532f?sid=9ef644eb-9d55-4ae7-9e53-6688ae75702c)

## Current Status & Known Issues
| Item | Status |

| Multi-window upload / viewer | ✅ Complete and demo-ready |

| Sidebar UI (TissueLab style) | ✅ Complete 

| Local development | ⚠️ Requires Node 20 LTS (Node 22 triggers Next.js internal 500) 

| Remote demo | ✅ Pushed and browsable |

## Quick Try (no local install needed)
1. Browse the source: [GitHub Repository](https://github.com/yt2895-beep/upenn-tissue-lab   )  
2. Download ZIP → extract → follow the steps below to run locally.

## Local Setup (Node 20)
```bash
nvm use 20          # or nvm-windows
npm install
npm run dev

## Pending Features & Implementation Plan

> These modules are ’not yet committed‘; the section serves as the next-sprint PRD and technical blueprint.

## WebSocket Real-Time Progress  
Replace front-end polling with push.  
- FastAPI native `WebSocketEndpoint` at `/ws/{client_id}`  
- React hook `useWebSocket` reconnects automatically  
- Falls back to polling if socket drops  

Key snippet
```python
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    await manager.send_json(client_id, {"job_id": jid, "progress": p})
```

Estimated effort: 2 h

---

## Redis Token-Bucket Rate-Limit  
Protect `POST /jobs` from burst traffic.  
- Decorator reads `x-user-id`, stores sliding-window counters in Redis  
- Returns `429` + `Retry-After` when limit exceeded  
- Front-end shows toast and disables button  

Key snippet
```python
def rate_limit(max_req: int = 10, window: int = 60):
    async def wrapper(request: Request, *args, **kwargs):
        user = request.headers.get("x-user-id", "anon")
        key = f"rl:{user}"
        pipe = redis.pipeline()
        now = int(time.time())
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zcard(key)
        pipe.zadd(key, {now: now})
        pipe.expire(key, window)
        *_, count, _, _ = pipe.execute()
        if int(count) >= max_req:
            return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})
        return await func(request, *args, **kwargs)
    return wrapper
```

Estimated effort**: 1 h

---

## DAG Workflow Visualiser  
Let users compose pipelines like *Blur → Resize → Segment*.  
- Front-end: `react-flow` drag-and-drop canvas  
- Export JSON graph → back-end topological sort (`networkx`)  
- Execute via `Celery chain` / `group`; progress per node pushed over WebSocket  

Execution flow 
1. User exports DAG JSON  
2. Back-end `nx.topological_sort(G)` yields order  
3. `chain(blur.s(), resize.s(), segment.s()).apply_async()`  
4. Each node completion → `redis.publish(f"task_update:{job_id}", node_state)`  

Estimated effort: 4 h

---

## TotalSegmentator Integration  
GPU-based anatomical segmentation for 3-D NIfTI.  
- Worker image adds `TotalSegmentator` wheel + weights  
- Task outputs `mask.nii.gz` → uploaded to MinIO → pre-signed URL  
- Viewer loads mask as extra layer with adjustable opacity  

Docker layer  
```dockerfile
FROM python:3.11-slim
RUN apt update && apt install -y python3-dev build-essential
RUN pip install TotalSegmentator
COPY ./worker /app
CMD ["celery", "-A", "tasks", "worker"]
```

Estimated effort: 3 h

---

## Unit & E2E Testing  
Reach ≥ 80 % coverage and reliable user-path guardrails.  

Unit 
- Back-end: `pytest --cov=app --cov-fail-under=80`  
  - Parametrised tests for all `/jobs` states  
- Front-end: `jest --coverage` on upload component error boundary  

E2E
- Playwright script:  
  1. `page.goto('/upload')`  
  2. `page.setInputFiles('input[type="file"]', 'sample.dcm')`  
  3. `await expect(page.locator('[data-testid=progress]')).toHaveText('100%')`  
- Runs in GitHub Actions on every push + nightly cron  

Estimated effort: 2 h + 1 h CI

---

## Production Monitoring  
Prometheus + Grafana stack already containerised; add business-level alerts.  

Metrics
```
queue_depth               // gauge
worker_active_tasks       // gauge
task_latency_seconds      // histogram
task_failures_total       // counter
```

Alerts 
- P95 latency > 30 s  
- Failure rate > 5 % for 5 min  
- Queue depth > 100 tasks  

Notification channel: Slack/DingTalk webhook  

---

## Post-MVP Scaling Roadmap (10× Users)

Week 1 – S3 pre-signed URL direct upload  
- Benefit: back-end bandwidth ↓ 90 %  

Week 2 – Celery worker HPA on Kubernetes  
- Benefit: concurrent tasks ↑ 10×  

Week 3 – Viewer static deploy on CloudFront  
- Benefit: global edge latency < 200 ms  

Week 4 – TotalSegmentator GPU node pool  
- Benefit: 3-D segmentation wall-time ↓ 80 %  

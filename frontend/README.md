# TissueLab Frontend — Next.js 13 (App Router)

## 技术栈
- Next.js 13 App Router  
- TypeScript  
- Tailwind CSS  
- Axios  

## 快速启动
```bash
npm install        # 首次
npm run dev        # 启动开发服务器 http://localhost:3000
```

## 功能
- 单文件上传（PNG/JPG/DICOM/NIfTI，后缀由后端校验）  
- 实时进度条：轮询 `GET /jobs/{job_id}` 每秒更新  
- 多用户隔离：通过 Header `X-User-ID: user123`（可改）

## 运行效果
```
Redeem Image Uploader
选择文件 → test.png → Upload & Process
Job ID: 55883e49-5ef3-42ce-a3d8-cee582c431d4
Status: SUCCEEDED
```

## 与后端接口对应
| 前端调用 | 方法 | 后端 URL | 说明 |
| -------- | ---- | -------- | ---- |
| 上传文件 | POST | `http://localhost:8000/jobs` | `FormData` 含 `files` |
| 查询进度 | GET  | `http://localhost:8000/jobs/{job_id}` | 轮询直到 `SUCCEEDED / FAILED` |

## 项目结构
```
frontend/
├─ app/page.tsx       # 上传 & 进度页（客户端组件）
├─ public/            # 静态资源
├─ package.json
└─ README.md
```

## 可继续扩展
- 支持多文件同时上传  
- WebSocket 代替轮询  
- Viewer 组件：显示 DICOM/NIfTI 图像与遮罩


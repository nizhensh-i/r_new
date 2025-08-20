#!/bin/bash

# 启动后端服务
cd backend
echo "启动后端服务..."
python manage.py runserver &
BACKEND_PID=$!

# 启动前端服务
cd ../frontend
echo "启动前端服务..."
npm run dev &
FRONTEND_PID=$!

# 等待用户按下Ctrl+C
echo "服务已启动，按Ctrl+C停止"
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
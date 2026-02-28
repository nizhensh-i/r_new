source ./frontend/deploy/front.sh
source ./backend/backend.sh

function run_container() {
  echo "传入参数为:  $1"
  cmd_front=""
  cmd_backend=""
  remote_cmd_front=""
  remote_cmd_backend="docker rm -f rank_backend;docker rmi nizhenshi/rank_backend;docker load -i rank_backend.tar;docker run --name rank_backend -v /home/ubuntu/user/rank/data.db:/home/ustc/data.db -d -p 6000:5000 nizhenshi/rank_backend;"
  
  # #生产
  # docker run --name rank_backend -v /root/user/rank/data.db:/home/ustc/data.db 5001:5000 -d -p nizhenshi/rank_backend;
  
  # 本地mac
  # docker run --name rank_backend -v /Users/nizhenshi/Documents/proj/rank_new/backend/scores/2025/data.db:/home/ustc/data.db  -d -p  5001:5000 nizhenshi/rank_backend;

  # # 不挂载
  # docker run --name rank_backend -d -p 5001:5000 nizhenshi/rank_backend;
  if [ $1 == "front" ];then
    cmd_front=$remote_cmd_front
  elif [ $1 == "backend" ]; then
    cmd_backend=$remote_cmd_backend
  elif [ $1 == "all" ]; then
    cmd_front=$remote_cmd_front
    cmd_backend=$remote_cmd_backend
  fi
  echo "cmd_front:" $cmd_front
  echo "cmd_backend:" $cmd_backend
  ssh $ROMOTE_USER@$ROMOTE_HOST "cd /home/ubuntu/user;$cmd_front $cmd_backend"
  if [[ $? -eq 0 ]];then
    echo "执行成功"
  else
    echo "执行失败"
  fi
}


function deploy_front(){
  front_to_remote
}

function deploy_backend() {
    backend_to_remote
    backend=$!
    wait $backend
    run_container "backend"
}

function deploy() {
    front_to_remote &
    front=$!
    backend_to_remote &
    backend=$!
    wait $front
    wait $backend
    run_container "backend"
}

deploy
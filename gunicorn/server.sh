Date=$(date +%Y%m%d%H%M)

if [ "$1" = "stop" ]; then
    echo "停止 Web 服务"
    ps aux|grep gunicorn|grep -v gunicorn|awk '{print $2}'|xargs kill -9
    exit
fi

WORKER_NUM=4

if [ ! -z "$1" ]; then
    WORKER_NUM=$1
fi

echo "启动 $WORKER_NUM 个 Web 服务进程..."

#    --worker-class=gevent \
CUDA_VISIBLE_DEVICES=0 gunicorn \
    --workers=$WORKER_NUM \
    --bind=0.0.0.0:8080 \
    --preload=true \
    server:app

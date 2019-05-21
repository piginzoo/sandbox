docker run --name=coolq --rm -p 9000:9000  -p 5700:5700 -v $(pwd)/coolq.pro:/home/user/coolq \
   -e VNC_PASSWD=123456 -e COOLQ_ACCOUNT=25473936 richardchien/cqhttp:latest

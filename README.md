docker run -d -e "TELEGRAM_TOKEN=" --restart always --mount type=bind,source=/home/ec2-user/takemymoney_bot/db,target=/usr/src/app/db siarheiurbanovich/take-my-byn:v1.0

To start the application execute code below in the same directory with docker-compose.yml  
`docker compose build master-container secondaries-container-1`  
`docker compose up`

To stop the application and clean after:  
`docker compose down --rmi all`

Test requests:  
`curl -X GET 127.0.0.1:5000`  
`curl -X POST  127.0.0.1:5000 -d "msg=msg1"`  
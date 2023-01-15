To start docker member with CP Subsystem run  
`docker run -it --network hazelcast-network --rm -e HZ_CLUSTERNAME=massive_counter -e HAZELCAST_CONFIG=hazelcast-docker.xml -v %cd%/hazelcast-docker.xml:/opt/hazelcast/hazelcast-docker.xml -p 5701:5701 hazelcast/hazelcast`

To start second member  
`docker run -it --network hazelcast-network --rm -e HZ_CLUSTERNAME=massive_counter -e HAZELCAST_CONFIG=hazelcast-docker.xml -v %cd%/hazelcast-docker.xml:/opt/hazelcast/hazelcast-docker.xml -p 5702:5701 hazelcast/hazelcast`

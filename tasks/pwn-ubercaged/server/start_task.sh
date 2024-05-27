sudo ./build_docker.sh
export PATH="$PATH:/usr/local/go/bin"
DOCKER_API_VERSION=1.40 go run server.go
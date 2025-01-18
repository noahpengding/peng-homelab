from app.services.updater.docker_checker import Docker_Checker

if __name__ == "__main__":
    d = Docker_Checker()
    print(d.check_image("alpine:latest", "alpine:latest"))
    print(d.check_image("alpine:latest", "alpine:3.10"))
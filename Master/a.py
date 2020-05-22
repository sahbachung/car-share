from .cloud import CloudCursor


def main():
    cu = CloudCursor(credentials="car-share/Master/credentials.oauth.json", token="car-share/Master/token.pickle")
    print(cu)


if __name__ == "__main__":
    main()
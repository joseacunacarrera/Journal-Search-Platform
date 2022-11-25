from loader import Loader

if __name__ == "__main__":
    loader = Loader('127.0.0.1', 'mypass', 'root', 'mydb', '123', '127.0.0.1', 'user', 'loader_queue_out')
    loader.load()
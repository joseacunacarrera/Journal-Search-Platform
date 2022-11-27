from loader import Loader
import os

if __name__ == "__main__":

    url_mariadb = os.getenv("URL_MARIADB")
    pass_mariadb = os.getenv("PASS_MARIADB")
    user_mariadb = os.getenv("USER_MARIADB")
    db_name = os.getenv("DB_NAME")
    rabbit_pass = os.getenv("RABBIT_PASS")
    rabbit_host = os.getenv("RABBIT_HOST")
    rabbit_user = os.getenv("RABBIT_USER")
    rabbit_queue_out = os.getenv("RABBIT_QUEUE_OUT")
    pod_name = os.getenv('HOSTNAME')
    
    loader = Loader(url_mariadb=url_mariadb,
                    pass_mariadb=pass_mariadb,
                    user_mariadb=user_mariadb,
                    db_name=db_name,
                    rabbit_pass=rabbit_pass,
                    rabbit_host=rabbit_host,
                    rabbit_user=rabbit_user,
                    rabbit_queue_out=rabbit_queue_out,
                    pod_name=pod_name)
    loader.load()
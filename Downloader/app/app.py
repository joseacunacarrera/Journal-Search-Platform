from downloader import Downloader
import os

if __name__ == "__main__":

    url_mariadb = os.getenv("URL_MARIADB")
    pass_mariadb = os.getenv("PASS_MARIADB")
    user_mariadb = os.getenv("USER_MARIADB")
    db_name = os.getenv("DB_NAME")
    rabbit_pass = os.getenv("RABBIT_PASS")
    rabbit_host = os.getenv("RABBIT_HOST")
    rabbit_user = os.getenv("RABBIT_USER")
    elastic_user = os.getenv("ELASTIC_USER")
    elastic_pass = os.getenv("ELASTIC_PASS")
    elastic_host = os.getenv("ELASTIC_HOST")
    rabbit_queue_in = os.getenv("RABBIT_QUEUE_IN")
    rabbit_queue_out = os.getenv("RABBIT_QUEUE_OUT")
    pod_name = os.getenv('HOSTNAME')

    downloader = Downloader(url_mariadb=url_mariadb,
                            pass_mariadb=pass_mariadb,
                            user_mariadb=user_mariadb,
                            db_name=db_name,
                            rabbit_pass=rabbit_pass,
                            rabbit_host=rabbit_host,
                            rabbit_user=rabbit_user,
                            elastic_user=elastic_user,
                            elastic_pass=elastic_pass,
                            elastic_host=elastic_host,
                            rabbit_queue_in=rabbit_queue_in,
                            rabbit_queue_out=rabbit_queue_out,
                            pod_name=pod_name)
    downloader.download()

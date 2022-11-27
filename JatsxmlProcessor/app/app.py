from jatsxml import JatsxmlProcessor

if __name__ == "__main__":
    jatsxml = JatsxmlProcessor(url_mariadb='127.0.0.1',
                            pass_mariadb='mypass',
                            user_mariadb='root',
                            db_name='mydb',
                            rabbit_pass='123',
                            rabbit_host='127.0.0.1',
                            rabbit_user='user',
                            elastic_user='elastic',
                            elastic_pass='mypass',
                            elastic_host='127.0.0.1',
                            rabbit_queue_in='detailsdownloader_queue_out',
                            rabbit_queue_out='jatsxml_queue_out')
    jatsxml.process()
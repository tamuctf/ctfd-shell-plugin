import pika
import json
import subprocess

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='shell_queue', durable=True)

def callback(ch, method, properties, body):
    msg = json.loads(body)
    print(" [x] Received %r" % msg)

    if msg[0] == "add":
    	add_user_func(msg[1], msg[2])
    elif msg[0] == "change":
    	change_user_func(msg[1], msg[2])

    ch.basic_ack(delivery_tag = method.delivery_tag)

def add_user_func(name, password):
	subprocess.call(["docker", "exec", "shell-server", "./add_user.py", name , password])
	
def change_user_func(name, password):
	subprocess.call(["docker", "exec", "shell-server", "./change_user_pass.py", name , password])

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue='shell_queue')

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
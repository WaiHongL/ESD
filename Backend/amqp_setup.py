import amqp_connection

def create_notification_queue(channel):
    print('amqp_setup:create_notification_queue')
    queue_name = 'Notification_Log'
    channel.queue_declare(queue=queue_name, durable=True) # 'durable' makes the queue survive broker restarts
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='purchase.notification')
        # bind the queue to the exchange via the key
        # 'routing_key=purchase.notification' => would be matched
    
def create_notification_queue_2(channel):
    print('amqp_setup:create_notification_queue_2')
    queue_name = 'Notification_Log_Fail'
    channel.queue_declare(queue=queue_name, durable=True) # 'durable' makes the queue survive broker restarts
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='fail.notification')
        # bind the queue to the exchange via the key
        # 'routing_key=fail.notification' =>would be matched
    

def create_refund_queue(channel):
    print('amqp_setup:create_notification_queue_2')
    queue_name = 'Notification_Refund'
    channel.queue_declare(queue=queue_name, durable=True) # 'durable' makes the queue survive broker restarts
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='refund.notification')
        # bind the queue to the exchange via the key
        # 'routing_key=refund.notification' =>would be matched
# function to create Error queue
def create_error_queue(channel):
    print('amqp_setup:create_error_queue')
    e_queue_name = 'Error'
    channel.queue_declare(queue=e_queue_name, durable=True) # 'durable' makes the queue survive broker restarts
    #bind Error queue
    channel.queue_bind(exchange=exchangename, queue=e_queue_name, routing_key='*.error')
        # bind the queue to the exchange via the key
        # any routing_key with two words and ending with '.error' will be matched
    
exchangename = "order_topic" # exchange name
exchangetype="topic" # use a 'topic' exchange to enable interaction
connection = amqp_connection.create_connection() 
channel = connection.channel()
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True) 
print('amqp_setup:create queues')
create_error_queue(channel)
create_notification_queue(channel)
create_notification_queue_2(channel)
create_refund_queue(channel)

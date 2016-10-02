def printer(event):
    print('PRINT REACTION', event['data'])

def print_with_delay(event):
    import time
    time.sleep(5)
    print('PRINT DELAYED REACTION', event['data'])

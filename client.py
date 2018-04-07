import time
from pyModbusTCP.client import ModbusClient

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 502

c = ModbusClient()

c.host(SERVER_HOST)
c.port(SERVER_PORT)


def to_binary_string(num):
    return ""


def bin_string_to_int(str):
    return 0


def get_num_records(status):
    """Gets the number of records of the log to be retrieved. Takes the two
    register values that represent the 32 bit integer log size, turns them
    into their binary representation, concatenates them, and then returns the
    integer that that 32 bit number represents."""
    higher_order = to_binary_string(status[0])
    lower_order = to_binary_string(status[1])
    num_records = bin_string_to_int(higher_order + lower_order)
    return num_records


def engage_log(log_n):
    """First step. Engage the log. log_n is the log to be engaged.
    Only supports the historical logs 1-3, currently."""
    if not c.is_open():
        if not c.open():
                print("Unable to connect to " + SERVER_HOST + ":"
                      + str(SERVER_PORT))
        if c.is_open():
            # Read the contents of the specific logs status block
            log_status_block = c.read_holding_registers(51032, 16)
            # Store the number of records used, the record size, and log
            num_records = get_num_records(log_status_block)
            record_size = log_status_block[3]
            log_availability = log_status_block[6]
            if log_availability != 0:
                print("Log number " + log_n + " is not available!\n")


def test():
    while True:
        if not c.is_open():
            if not c.open():
                print("Unable to connect to " + SERVER_HOST + ":"
                      + str(SERVER_PORT))

        if c.is_open():
            regs = c.read_holding_registers(999, 125)
            if regs:
                print(str(regs))

        time.sleep(2)

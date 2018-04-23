from pyModbusTCP.client import ModbusClient
from collections import namedtuple

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 502


def connect():
    """Connects to the defined HOST AND PORT. returns the client"""
    c = ModbusClient()
    c.host(SERVER_HOST)
    c.port(SERVER_PORT)
    if not c.is_open():
        if not c.open():
            raise Exception("Unable to connect to " + SERVER_HOST + ":"
                            + str(SERVER_PORT))
    return c


def engage_log(log_n, s):
    """First step. Engage the log. log_n is the log to be engaged. Has
    only been tested with historical logs. s is the type of log to retrieve.
    0 is a normal record, 1 is timestamp only, 2 is complete memory image."""
    c = connect()
    if c.is_open():
        log_status_addr = get_log_status_addr(log_n)
        log_status_block = get_log_status_block(c, log_status_addr)
        # Store the record size and log availability
        record_size = get_record_size(log_status_block)
        log_availability = get_log_availability(log_status_block)
        max_records = get_max_records(log_status_block)
        # Check that the log is available
        if log_availability != 0:
            raise Exception("Log number " + log_n + " is not available!\n")
        # write to 0xC34f (1 register) specifying the log to be engage and
        # desired mode
        write_to_engage(c, log_n, 1, s)
        # this step latches the oldest record to index 0, and locks
        # the log so that only this port can retrieve the log until disengaged.
        # verify log is engaged:
        verify_engaged(c, log_status_addr)
        # write the retrieval information
        records_per_window  = write_retrieval(c, record_size)
        # after this, we should be in the clear to retrieve the records
        return c, log_status_block, record_size, records_per_window, max_records


def get_current_port(client):
    """Returns the value stored in the session com port register"""
    return client.read_holding_registers(4499, 1)


def get_first_timestamp(status):
    """Extracts the year, month, day, hour, minute, and second of the 
    first timestamp record and then packs it all into a namedtuple, which
    is returned.
    NOTE: This will not work until we implement the proper masks
    for each of the date formats """
    # first byte of r1 is the year, second is the month
    r1 = status[6]
    # first byte of r2 is the day, second is hour
    r2 = status[7]
    # first byte of r3 is the minute, second is second (heh)
    r3 = status[8]
    year = get_year(r1)
    month = get_month(r1)
    day = get_day(r2)
    hour = get_hour(r2)
    minute = get_min(r3)
    second = get_sec(r3)
    timestamp = namedtuple('timestamp', ['year', 'month', 'day', 'hour', 'minute', 'second'])
    t = timestamp(year, month, day, hour, minute, second) 
    return t

 def get_last_timestamp(status):
    """Extracts the year, month, day, hour, minute, and second of the 
    last timestamp record and then packs it all into a namedtuple, which
    is returned.
    NOTE: This will not work until we implement the proper masks
    for each of the date formats """
    # first byte of r1 is the year, second is the month
    r1 = status[9]
    # first byte of r2 is the day, second is hour
    r2 = status[10]
    # first byte of r3 is the minute, second is second (heh)
    r3 = status[11]
    year = get_year(r1)
    month = get_month(r1)
    day = get_day(r2)
    hour = get_hour(r2)
    minute = get_min(r3)
    second = get_sec(r3)
    timestamp = namedtuple('timestamp', ['year', 'month', 'day', 'hour', 'minute', 'second'])
    t = timestamp(year, month, day, hour, minute, second) 
    return t
   

def disengage_log(client, log_n):
    """To disengage the log, write the log number log_n (log to be disengaged) to
    the log index and 0 to the enable bit [0xC34F, 1 register]"""
    log_str = to_binary_string(log_n, 8)
    # e is the enable bit--setting it to 0 disengages the log
    e = "0"
    # s doesn't really matter here, so it's all 0's I guess
    s = "0000000"
    msg = bin_string_to_int(log_str + e + s)
    client.write_single_register(49999, msg) 

def get_log(log_n, log_t=0):
    """log_n is the log to be retrieved. s is the type of log to retrieve.
    s is, by default, 0."""
    client, log_status, record_size, records_per_window, max_records = engage_log(log_n, log_t)
    records = retrieve_records(client, records_per_window, max_records)
    disengage_log(log_n)


def get_log_availability(status):
    """Returns the log availability of the status provided."""
    return status[5]


def get_log_status_addr(log_n):
    """Returns the register address of log_n"""
    if log_n == 0:
        # system log (0xC747)
        log_status_addr = 51015
    elif log_n == 1:
        # alarm (which is #1, but actually comes before system log)
        # hex address C737
        log_status_addr = 50999
    elif log_n == 2:
        # hist log 1 (0xC757)
        log_status_addr = 51031
    elif log_n == 3:
        # hist log 2 (0xC767)
        log_status_addr = 51047
    elif log_n == 4:
        # hist log 3 (0xC777)
        log_status_addr = 51063
    elif log_n == 5:
        # I/O Change log (0x787
        log_status_addr = 51079
    else:
        raise Exception("Unsupported log number!\n")
    return log_status_addr


def get_log_status_block(client, addr):
    """Retrieves the whole log status block from the address provided. Returns a
    list."""
    return client.read_holding_registers(addr, 16)

def get_max_records(status):
    """Works just like get_num_records, but different locations are loaded
    from the status block"""
    higher_order = to_binary_string(status[0], 16)
    lower_order = to_binary_string(status[1], 16)
    max_records = bin_string_to_int(higher_order + lower_order)
    return max_records


def get_num_records(status):
    """Gets the number of records of the log to be retrieved. Takes the two
    register values that represent the 32 bit integer log size, turns them
    into their binary representation (as a string), concatenates them, 
    and then returns the decimal value that that 32 bit number represents."""
    higher_order = to_binary_string(status[2], 16)
    lower_order = to_binary_string(status[3], 16)
    num_records = bin_string_to_int(higher_order + lower_order)
    return num_records


def get_record_size(status):
    """Returns the value stored in the record size register of the given log
    status block"""
    return status[4]

def get_window_block(client):
    """Reads the window block where logs are retrieved. This block starts at
    0xC351 and is 125 registers long. The first half of the first register
    is the window status, the second half of that register plus the next
    register is the offset of the first record in the window, and the other
    123 registers are the window where the log is retrieved.
    We pull the record index and the window in one request to minimize 
    communication time and to ensure that the record index matches the data 
    in the data window returned.
    Space in the window after the last specified record (RecordSize * RecordsPerWindow)
    is padded with 0xFF, and can be safely discarded."""
    window_block = client.read_holding_registers(50001, 125)
    return window_block

def get_window_status(block):
    """Retrieves the value stored in 0xC351 (50001), converts it to a binarys
    string, gets the higher half of it, and then returns the decimal version of
    that number, which is the window status.
    The other half of this register is part 1 of three of the offset of the first
    record in the window"""
    bin_str = to_binary_string(block[0], 16)
    window_status = bin_string_to_int(bin_str[:8])
    return window_status


def get_record_index(block):
    """Record index is a 254 bit record number. It's stored across 1 and a half
    registers, starting at the lower order bits of the first register at 0xC351 
    (50001), and then contiuing into the two bytes of the second register.
    The logs first record is latched as a reference point when the session is 
    enabled.
    This offset is a record index relative to that point. Value provided is the 
    relative index of the whole or partial record that begins the window."""
    r1 = to_binary_string(block[0], 16)
    higher_order = r1[8:]
    lower_order = to_binary_string(block[1], 16)
    record_index = bin_string_to_int(higher_order + lower_order)
    return record_index


def get_record_window(block, rec_size, rec_pw):
    """Space in the window after the last specified record (RecordSize x RPW)
    is padded with 0xFF, and can be safely discarded"""
    last_rec = rec_size * rec_pw
    record = block[2:last_rec + 1] # slicing is inclusive, exclusive, hence plus 1
    return record


def retrieve_records(client, rpw, max_recs):
    """Retrieve the records."""
    # Read the record index and window. We read the index and window in 1 
    # request to minimize communication time and to ensure that the record 
    # index matches the data in the data window returned.
    # records is a list of lists, each list representing the window of records
    records = []
    remaining_records = max_recs
    window_block = get_window_block(client)
    window_status = get_window_status(window_block)
    expected_record_index = 0
    while remaining_records >= 0:
        window_block = get_window_block(client)
        window_status = get_window_status(window_block)
        while window_status == 0xFF:
            # if window status is 0xFF, repeat the request
            window_block = get_window_block(client)
            window_status = get_window_status(window_block)
        if window_status == 0:
            # verify that the record index incremented by RecordsPerWindow.
            # The record index of the retrieved window is the index of the first 
            # value will increase by RecordsPerWindow each time the window is read,
            # so it should be 0, N, Nx2, ..., for each window retrieved.
            actual_record_index = get_record_index(window_block)
            if actual_record_index == expected_record_index:
                # add this to list of windows of records
                records.append(get_record_window(window_block))
                remaining_records -= rpw
                if remaining_records <= 0:
                    # if there are no remaining records, go to step 3 (disengage)
                    return records
                # Compute the next expected record index by adding RPW to current
                # expected record index. If this value is greater than the number
                # of records, resize the window so it only contains the remaining
                # records and go to step 1d (write record retrieval information),
                # where the records per window will be the same as the remaining
                # records
                # we have auto increment set to 1 by default, so we do not have to
                # call write_retrieval every time with our new expected index. 
                expected_record_index += rpw
                if expected_record_index > max_recs:
                    # We manually write to the retrieval here to change the rpw size
                    rpw = remaining_records
                    write_retrieval(client, rpw)
            else:
                # record index does not match the expected record index. Rewrite
                # the record index, where the record index will be the same as the
                # expected record index. This will tell the meter to repeat the 
                # records you were expecting.
                write_retrieval(client, rpw, expected_record_index)


def verify_engaged(client, addr):
    """Verify that the log availability register is equal to the session com
    port"""
    log_status_block = get_log_status_block(client, addr)
    log_availability = get_log_availability(log_status_block)
    # the communication port that we are currently connected to.
    current_port = get_current_port(client)
    # log_availability is a number that will indicate which port is currently
    # engaged with the log.
    if(log_availability != current_port):
        Exception("This port is not currently engaged! Try again.\n")


def write_to_engage(client, log_n, e, s):
    # n - log number:
    #       0-system
    #       1-alarm
    #       2-hist-log1
    #       3-hist-log2
    #       4-hist-log3
    #       5-I/O changes
    n_str = to_binary_string(log_n, 8)

    # e - retrieval session enable (or disable)
    # s - sssssss is what to retrieve
    #       0- normal record
    #       1- timestamps only
    #       2- complete memory image
    log_enable_msg = bin_string_to_int(n_str + str(e) + to_binary_string(s, 7))
    client.write_single_register(49999, log_enable_msg)


def write_retrieval(client, record_size, record_index=0):
    """Writes to the retrieval header registers"""
    # compute the number of records per window, as follows:
    if(record_size != 0):
        records_per_window = (246 // record_size)
    else:
        records_per_window = 0
    # write the records per window, the number of repeats (1), and record
    # index (0)
    # FORMAT: wwwwwwww snnnnnnn
    #   w - records per window
    #   s - number of repeats.
    #   n - record index
    # by default, number of repeats is a feature we will not be using. It
    # is associated with the modbus code 0x23, which is a specific register
    # reading function that we don't really need. We start reading at the
    # 0th record index.
    rpw_str = to_binary_string(records_per_window, 8)
    ind_str = to_binary_string(record_index, 7)
    msg = bin_string_to_int(rpw_str + "1" + ind_str)
    # after this write, the meter knows the formatting of the log to be
    # retrieved
    client.write_single_register(50000, msg)
    return records_per_window



####################
# HELPER FUNCTIONS #
####################


def to_binary_string(num, bl):
    """Helper function to convert a number into its binary string
    representation. bl is the bit length, to add appropriate padding"""
    bs = bin(num)[2:] # 2 is to remove '0x' from beginning of string
    while len(bs) < bl:
        bs = "0" + bs

    return bs


def bin_string_to_int(str):
    """Helper function to convert a binary string into its decimal
    representation"""
    return int(str, 2)

def get_year(reg):
    """Year is the first byte of the register in range (0-99), + 2000"""
    # NOTE WE HAVE TO IMPLEMENT THE BIT MASKING FOR THIS (0x7F)
    # HIGH BITS OF EACH TIME STAMP BYTE ARE USED AS FLAGS TO RECORD METER
    # STATE INFO @ TIME OF TIMESTAMP--THESE SHOULD BE MASKED OUT UNLESS 
    # NEEDED
    bin_str = to_binary_string(reg, 16)
    mid = (len(bin_str) + 1) // 2
    year = bin_string_to_int(bin_str[:mid]) + 2000
    return year


def get_month(reg):
    """Months is second byte of the register, in range (1-12)"""
    # NOTE WE HAVE TO IMPLEMENT THE BIT MASKING FOR THIS (0x0F)
    # HIGH BITS OF EACH TIME STAMP BYTE ARE USED AS FLAGS TO RECORD METER
    # STATE INFO @ TIME OF TIMESTAMP--THESE SHOULD BE MASKED OUT UNLESS 
    # NEEDED
    bin_str = to_binary_string(reg, 16)
    mid = (len(bin_str) + 1) // 2
    month = bin_string_to_int(bin_str[mid:])
    return month


def get_day(reg):
    # NOTE WE HAVE TO IMPLEMENT THE BIT MASKING FOR THIS (0x1F)
    # HIGH BITS OF EACH TIME STAMP BYTE ARE USED AS FLAGS TO RECORD METER
    # STATE INFO @ TIME OF TIMESTAMP--THESE SHOULD BE MASKED OUT UNLESS 
    # NEEDED
    bin_str = to_binary_string(reg, 16)
    mid = (len(bin_str) + 1) // 2
    day = bin_string_to_int(bin_str[:mid])
    return day

def get_hour(reg):
    # NOTE WE HAVE TO IMPLEMENT THE BIT MASKING FOR THIS (0x1F)
    # HIGH BITS OF EACH TIME STAMP BYTE ARE USED AS FLAGS TO RECORD METER
    # STATE INFO @ TIME OF TIMESTAMP--THESE SHOULD BE MASKED OUT UNLESS 
    # NEEDED
    bin_str = to_binary_string(reg, 16)
    mid = (len(bin_str) + 1) // 2
    hour = bin_string_to_int(bin_str[mid:])
    return hour


def get_min(reg):
    # NOTE WE HAVE TO IMPLEMENT THE BIT MASKING FOR THIS (0x7F)
    # HIGH BITS OF EACH TIME STAMP BYTE ARE USED AS FLAGS TO RECORD METER
    # STATE INFO @ TIME OF TIMESTAMP--THESE SHOULD BE MASKED OUT UNLESS 
    # NEEDED
    bin_str = to_binary_string(reg, 16)
    mid = (len(bin_str) + 1) // 2
    minute = bin_string_to_int(bin_str[:mid])
    return minute

def get_sec(reg):
    # NOTE WE HAVE TO IMPLEMENT THE BIT MASKING FOR THIS (0x3F)
    # HIGH BITS OF EACH TIME STAMP BYTE ARE USED AS FLAGS TO RECORD METER
    # STATE INFO @ TIME OF TIMESTAMP--THESE SHOULD BE MASKED OUT UNLESS 
    # NEEDED
    bin_str = to_binary_string(reg, 16)
    mid = (len(bin_str) + 1) // 2
    sec = bin_string_to_int(bin_str[mid:])
    return sec



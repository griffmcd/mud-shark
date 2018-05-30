from pyModbusTCP.client import ModbusClient
from collections import namedtuple


def connect(host, port):
    """Connects to the defined HOST AND PORT. returns the client"""
    c = ModbusClient()
    c.host(host)
    c.port(port)
    if not c.is_open():
        if not c.open():
            raise Exception()
    return c

# LOG METHODS #


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


def engage_log(c, log_n, s):
    """First step. Engage the log. log_n is the log to be engaged. s is the
    type of log to retrieve.
    0 is a normal record, 1 is timestamp only, 2 is complete memory image."""
    log = namedtuple('log', ['num', 'status', 'record_size',
                             'records_per_window', 'max_records'])
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
    records_per_window = write_retrieval(c, record_size)
    # after this, we should be in the clear to retrieve the records
    log_vals = log(log_n, log_status_block, record_size, records_per_window,
                   max_records)
    return log_vals


def get_log(client, log_n, log_t=0):
    """log_n is the log to be retrieved. s is the type of log to retrieve.
    s is, by default, 0.
    There are three stages to retrieving a log: Engaging it, retrieving
    the records, and then disengaging the log. Returns a list of records."""
    if client.is_open():
        log = engage_log(client, log_n, log_t)
        records = retrieve_records(client, log.records_per_window,
                                   log.max_records, log.record_size)
        disengage_log(client, log_n)
        client.close()
        return records


def program_log(client, log_n, regs, interval, sectors=5):
    """Takes log number to program(2, 3, 4 for hist log 1, 2, and 3), a list
    of registers to log, [OPTIONALLY] the number of sectors to allocate to
    that log (0-15, they are shared among all three logs) and the interval
    at which the meter should record the log. """
    # write the first register, which contains the number of registers in the
    # high byte and the number of sectors allocated to this log in the low
    # byte
    addr = get_hist_log_addr(log_n)
    num_regs = len(regs)
    nr_str = to_binary_string(num_regs, 8)
    sec_str = to_binary_string(sectors, 8)
    fst_reg = bin_string_to_int(nr_str + sec_str)
    client.write_single_register(addr, fst_reg)
    # Write the second register, which contains the interval. The high byte
    # of this register is the window status, which is read only.
    addr += 1
    client.write_single_register(addr, interval)
    # Now we need to write the actual list of registers to the block
    # sequentially after this in the register list.
    addr += 1
    for reg in regs:
        client.write_single_register(addr, reg)
        addr += 1
    # Go through the rest of these registers and fill them with 0xFF to denote
    # they are not used
    # 117 is total number of registers, we start from the diff between that and
    # the number of registers used
    addr += 1
    for i in range(len(regs), 117):
        client.write_single_register(addr, 0xFF)
        addr += 1


def retrieve_records(client, rpw, max_recs, rec_size):
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
            # value will increase by RecordsPerWindow each time the window
            # is read,
            # so it should be 0, N, Nx2, ..., for each window retrieved.
            actual_record_index = get_record_index(window_block)
            if actual_record_index == expected_record_index:
                # add this to list of windows of records
                records = records + get_record_window(window_block, rec_size,
                                                      rpw)
                remaining_records -= rpw
                if remaining_records <= 0:
                    # if there are no remaining records, disengage
                    return records
                """ Compute the next expected record index by adding RPW to
                current expected record index. If this value is greater than
                the number of records, resize the window so it only contains
                the remaining records and go to step 1d (write record
                retrieval information), where the records per window will be
                the same as the remaining records.
                we have auto increment set to 1 by default, so we do not have
                to call write_retrieval every time with our new expected index.
                """
                expected_record_index += rpw
                if expected_record_index > max_recs:
                    # We manually write to the retrieval here to change the
                    # rpw size
                    rpw = remaining_records
                    expected_record_index -= remaining_records
                    write_retrieval(client, rpw, expected_record_index)
            else:
                """
                record index does not match the expected record index. Rewrite
                the record index, where the record index will be the same as
                the expected record index. This will tell the meter to repeat
                the records you were expecting. """
                write_retrieval(client, rpw, expected_record_index)


# CLIENT FUNCTIONS #

def get_current_port(client):
    """Returns the value stored in the session com port register"""
    return client.read_holding_registers(4499, 1)


def get_log_status_block(client, addr):
    """Retrieves the whole log status block from the address provided. Returns a
    list."""
    return client.read_holding_registers(addr, 16)


def get_window_block(client):
    """Reads the window block where logs are retrieved. This block starts at
    0xC351 and is 125 registers long. The first half of the first register
    is the window status, the second half of that register plus the next
    register is the offset of the first record in the window, and the other
    123 registers are the window where the log is retrieved.
    We pull the record index and the window in one request to minimize
    communication time and to ensure that the record index matches the data
    in the data window returned.
    Space in the window after the last specified record
    (RecordSize * RecordsPerWindow)
    is padded with 0xFF, and can be safely discarded."""
    window_block = client.read_holding_registers(50001, 125)
    return window_block


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


def write_retrieval(client, record_size, record_index=0):
    """Writes to the retrieval header registers, starting at 0xc350-0xc352"""
    records_per_window = get_records_per_window(record_size)
    """
    high byte of 0xC350 is the records per window or the records per batch
    depending on the most significant bit of the low byte. We use windows
    by default (this does not support batches).
    The most significant bit of the low byte is the flag that controls records
    per window/batch. Always 0.
    last seven bits of 0xc350 is the number of repeats. 1 is auto-increment,
    2-8 if it supports function code 0x23, which we do not. Always 1.

    auto increment feature: every time we retrieve a window of records, the
    meter will automatically increment the index and load the next window
    """
    rpw_str = to_binary_string(records_per_window, 8)
    msg = bin_string_to_int(rpw_str + "00000001")
    # after this write, the meter knows the formatting of the log to be
    # retrieved
    client.write_single_register(50000, msg)
    # Now we write the index in 0xc351-2. This is two registers, but the high
    # nibble of the first register is the window status, and is read-only.
    # So we really have 24 bits for the record index.
    ind_str = to_binary_string(record_index, 32)
    fst_reg = bin_string_to_int(ind_str[:16])
    snd_reg = bin_string_to_int(ind_str[16:])
    client.write_single_register(50001, fst_reg)
    client.write_single_register(50002, snd_reg)
    return records_per_window


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


# LOG STATUS FUNCTIONS #
def get_log_availability(status):
    """Returns the log availability of the status provided."""
    return status[5]


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


def get_records_per_window(record_size):
    """Record size is always at least 1--when a log is cleared, a dummy
    record is placed in the first location. This way, we do not have to
    worry about division by zero errors. However, until we have everything
    up and running, we will keep this check here."""
    if(record_size == 0):
        records_per_window = 1
    else:
        records_per_window = 246 // record_size
    return records_per_window


# BLOCK FUNCTIONS #
def get_record_window(block, rec_size, rec_pw):
    """Space in the window after the last specified record (RecordSize x RPW)
    is padded with 0xFF, and can be safely discarded"""
    last_rec = rec_size * rec_pw
    record = block[2:last_rec + 1]
    return record


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


def get_window_status(block):
    """Retrieves the value stored in 0xC351 (50001), converts it to a binarys
    string, gets the higher half of it, and then returns the decimal version of
    that number, which is the window status.
    The other half of this register is part 1 of three of the offset of the
    first record in the window"""
    bin_str = to_binary_string(block[0], 16)
    window_status = bin_string_to_int(bin_str[:8])
    return window_status

# HELPER FUNCTIONS #


# ADDRESS HELPER
def get_hist_log_addr(log_n):
    if log_n == 2:
        # hist log 1 (0x7917)
        addr = 30999
    elif log_n == 3:
        # hist log 2 (0x79D7)
        addr = 31191
    elif log_n == 4:
        # hist log 3 (0x7A97)
        addr = 31383
    else:
        raise Exception("Unsupported log_n!\n")
    return addr


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


# CONVERTING BINARY / INTS #
def to_binary_string(num, bl):
    """Helper function to convert a number into its binary string
    representation. bl is the bit length, to add appropriate padding"""
    bs = bin(num)[2:]  # 2 is to remove '0x' from beginning of string
    while len(bs) < bl:
        bs = "0" + bs

    return bs


def bin_string_to_int(str):
    """Helper function to convert a binary string into its decimal
    representation"""
    return int(str, 2)


# TIMESTAMP HELPERS #
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

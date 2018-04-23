import random
from pyModbusTCP.client import ModbusClient

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 502

c = ModbusClient()
c.host(SERVER_HOST)
c.port(SERVER_PORT)


def init_fixed_data_block():
    """Registers 0-46 (0x0000-0x002E) is the Fixed Data section. Detail's the
    meter's fixed info. This is not information we need to access (except
    later to determine the specific meter we are accessing).
    We populate all these registers currently with the value of 1, to indicate
    this is the first block in the map."""
    for i in range(0, 47):
        c.write_single_register(i, 1)


def init_int_readings_block():
    """Registers 278-304 (0x0116-0x0130) is the Integer Readings Block. We will
    not be accessing these directly at any point--they are included only for
    completeness of the ModMap. We have code (commented out) to assign
    (integer) values based on the ranges specified in the Modbus Map, but for
    now we just want to fill it with 2, to denote this is the second block in
    the map."""
    for i in range(279, 305):
        c.write_single_register(i, 2)
    # for i in range(279, 287):
    #     c.write_single_register(i, random.randint(0, 9999))
    # for i in range(287, 290):
    #     c.write_single_register(i, random.randint(-9999, 9999))
    # c.write_single_register(290, random.randint(0, 9999))
    # c.write_single_register(291, random.randint(-1000, 1000))
    # c.write_single_register(292, random.randint(0, 9999))
    # for i in range(293, 299):
    #     c.write_single_register(i, random.randint(-9999, 9999))
    # for i in range(299, 302):
    #     c.write_single_register(i, random.randint(0, 9999))
    # for i in range(302, 305):
    #     c.write_single_register(i, random.randint(-1000, 1000))


def init_primary_readings_block():
    """Occupies registers 999-1064 (0x03E7-0x0428). Primary readings block.
    We also will not be reading these directly, but the device itself directly
    reads from these when a new log entry is created. We fill these with the
    number 3, to denote this is the third block in the map. """
    for i in range(999, 1065):
        c.write_single_register(i, 3)


def init_primary_energy_block():
    """Primary Energy Block occupies registers 1499-1620 (0x5DB-0x654). We will
    not be reading these registers directly, but they are registers that the
    meter can log. We fill these with number 4, to denote this is the fourth
    block in the map."""
    for i in range(1499, 1621):
        c.write_single_register(i, 4)


def init_primary_demand_block():
    """Primary Demand Block occupies registers 1996-2062 (0x07CC-080E). Just
    like the previous two, we do not read these directly, but they can be used
    by the meter in the logging process. We fill these with number 5, to denote
    this is the fifth block in the map."""
    for i in range(1996, 2063):
        c.write_single_register(i, 5)


def init_uncompensated_readings_block():
    """Uncompensated Readings Block occupies registers 2999-3102 (0x0BB7-0x0C1E).
    Like the previous blocks, we do not actually read from these directly, but
    are used internally by the meter itself. We fill these with number 6, to
    denote this is the sixth block in the map."""
    for i in range(2999, 3103):
        c.write_single_register(i, 6)


def init_phase_angle_block():
    """Phase angle block occupies registers 4099-4104 (0x1003-0x1008). We do
    not ever access these directly, and are included just for completion. We
    fill these with number 7, to denote this is the seventh block in the map.
    """
    for i in range(4099, 4105):
        c.write_single_register(i, 7)


def init_status_block():
    """Status block occupies registers 4499-4511 (0x1193-119F). We will be
    accessing the status block. Contains Port ID, Meter Status, Limits Status,
    Time Since Reset, Meter On Time, Current Date & Time, Clock Sync Status,
    and Current Day of Week. We fill these with 8's currently, to denote its
    the 8th block in the map, but we will be populating this with values as
    needed."""
    for i in range(4499, 4512):
        c.write_single_register(i, 8)


def init_THD_block():
    """THD block occupies registers 5999-6874 (0x176F-0x1ADA). We do not
    access these directly. We fill these with the number 9, to denote this as
    the 9th block in the map."""
    for i in range(5999, 6875):
        c.write_single_register(i, 9)


def init_short_term_primary_min_block():
    """Short Term Primary Minimum block occupies registers 7975-7998 (0x1F27
    to 0x1F3E). We do not access these directly. We denote them 10 because
    they are the tenth block."""
    for i in range(7975, 7999):
        c.write_single_register(i, 10)


def init_primary_min_block():
    """Primary Minimum Block occupies registers 7999-8094 (0x1F3F-0x1F9E).
    We do not access these directly. Denoted 11 for the 11th block."""
    for i in range(7999, 8095):
        c.write_single_register(i, 11)


def init_primary_min_timestamp_block():
    """Primary Minimum Timestamp Block occupies registers 8399-8560 (0x20CF to
    0x2176). We do not access these directly. Denoted 12 for 12th block."""
    for i in range(8399, 8561):
        c.write_single_register(i, 12)


def init_short_term_primary_max_block():
    """Short Term Primary Maximum Block occupies registers 8975-8998 (0x230F
    to 0x2326). We do not access these directly. Denoted 13 for 13th block."""
    for i in range(8975, 8999):
        c.write_single_register(i, 13)


def init_primary_max_block():
    """Primary Maximum Block occupies registers 8999-9094 (0x2327 to 0x2386).
    We do not access these directly. Denoted 14 for 14th block."""
    for i in range(8999, 9095):
        c.write_single_register(i, 14)


def init_primary_max_timestamp_block():
    """Primary Maximum Timestamp Block occupies registers 9399-9560 (0x24B7
    to 0x2558). We do not access these directly. Denoted 15 for 15th block."""
    for i in range(9399, 9561):
        c.write_single_register(i, 15)


def init_option_card_1_block():
    """Starts at 9999 (0x270F) and ends at 10226 (0x27F2). We do not write
    these directly. Denoted 16 for 16th block."""
    for i in range(9999, 10227):
        c.write_single_register(i, 16)


def init_option_card_2_block():
    """starts at 10999 (0x2AF7) and ends at 11226 (0x2BDA). We do not write
    these directly. Denoted 17 for 17th block."""
    for i in range(10999, 11129):
        c.write_single_register(i, 17)


def init_accumulators_block():
    """Accumulators block starts at 11999 (0x2EDF) and ends at 12030 (0x2EFE).
    We do note write these directly. Denoted 18 for 18th block."""
    for i in range(11999, 12031):
        c.write_single_register(i, 18)


def init_resets_block():
    """Resets Block starts at 19999 (0x4E1F) and ends at 20014 (0x4E2E).
    We do not write these directly. Denoted 19 for 19th block."""
    for i in range(19999, 20015):
        c.write_single_register(i, 19)


def init_commands_section_block():
    """Commands Section block starts at 30013 (0x753D) and ends at 30282 (0x764A).
    We will be probably reading from some of these. Denoted by 20 for the 20th
    block."""
    for i in range(30013, 30283):
        c.write_single_register(i, 20)


def init_log_setups_block():
    """Log Setups Block starts at 30999 (0x7917) and ends at 31606 (0x7B76).
    We will definitely be reading and writing to these. Denoted by 21 for 21st
    block."""
    for i in range(30999, 31607):
        c.write_single_register(i, 21)

def init_prog_settings_opt_card_1_block():
    """Option Card #1 Setups Block starts at 31999 (0x7CFF) and ends at 32574
    (0x7F3E). """
    for i in range(31999, 32575):
        c.write_single_register(i, 22)

def init_digital_io_pulse_block():
    """Settings registers for Digital I/O Pulse Output Card. Starts at 32000 
    (0x7d00) and ends at 32062 (0x7d3e)."""
    for i in range(32000, 32063):
        c.write_single_register(i, 23)

def init_digital_io_relay_block():
    """Settings registers for digital I/O Relay Card. Starts at 32063 (0x7d3f)
    and ends at 32574 (0x7f3e). """
    for i in range(32063, 32575):
        c.write_single_register(i, 24)

def init_option_card_2_setups_block():
    """ Programmable Settings for Option Card 2. Starts at 32999 (0x80E7) and
    ends at 33574 (0x8326). """
    for i in range(32999, 33575):
        c.write_single_register(i, 25)

def init_overlays_option_card_2_block():
    """ Overlays etc for option card 2 programming. Starts at 33000 (0x80E8) 
    and ends at 33574 (0x8326). """
    for i in range(33000, 33575):
        c.write_single_register(i, 26)

def init_secondary_readings_block():
    """ Secondary block begins at 40000 (0x9C40) and ends at 40099 (0x9Ca3). """
    for i in range(40000, 40100):
        c.write_single_register(i, 27)

def init_log_retrieval_block():
    """ Log retrieval block starts at 49996 (0xc34c) and ends at 50125 (0xc3cd). """
    for i in range(49996, 50126):
        c.write_single_register(i, 28)

def init_log_status_block():
    """ Log status block starts at 50999 (0xc737) and ends at 51126 (0xc7b6). """
    for i in range(50999, 51127):
        c.write_single_register(i, 29)
    c.write_single_register(51036, 0)

def init():
    c.open()
    init_fixed_data_block()
    init_int_readings_block()
    init_primary_readings_block()
    init_primary_energy_block()
    init_primary_demand_block()
    init_uncompensated_readings_block()
    init_phase_angle_block()
    init_status_block()
    init_THD_block()
    init_short_term_primary_min_block()
    init_primary_min_block()
    init_primary_min_timestamp_block()
    init_short_term_primary_max_block()
    init_primary_max_block()
    init_primary_max_timestamp_block()
    init_option_card_1_block()
    init_option_card_2_block()
    init_accumulators_block()
    init_resets_block()
    init_commands_section_block()
    init_log_setups_block()
    init_prog_settings_opt_card_1_block()
    init_digital_io_pulse_block()
    init_digital_io_relay_block()
    init_option_card_2_setups_block()
    init_overlays_option_card_2_block()
    init_secondary_readings_block()
    init_log_status_block()
    init_log_retrieval_block()
    c.close()


init()

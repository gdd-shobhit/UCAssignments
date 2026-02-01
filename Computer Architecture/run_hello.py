from m5.objects import *
import m5

# L1 Cache Definitions
class L1ICache(Cache):
    size = "32KiB"
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

class L1DCache(Cache):
    size = "32KiB"
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

# System
system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]

# CPU
system.cpu = TimingSimpleCPU()

# Caches
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()

# Bus
system.membus = SystemXBar()

# CPU -> Cache
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

# Cache -> Bus
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# Interrupts
system.cpu.createInterruptController()
# X86 interrupt wiring
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Memory Controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]

# Correct bus connection
system.mem_ctrl.port = system.membus.mem_side_ports

# Since se.py is deprecated, we manually set up the workload here
system.workload = SEWorkload.init_compatible("./tests/hello")
process = Process()
process.cmd = ["./tests/hello"]
system.cpu.workload = process
system.cpu.createThreads()

# Simulate
root = Root(full_system=False, system=system)
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print(
    f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}"
)
